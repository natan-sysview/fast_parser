using System.Buffers.Binary;
using System.Collections.Concurrent;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;
using FastParse;

var root = FindProjectRoot();
var options = RunnerOptions.Parse(args, root);

if (!File.Exists(options.InventoryDb))
{
    Console.Error.WriteLine($"ERROR: inventory DB does not exist: {options.InventoryDb}");
    return 2;
}

if (!File.Exists(options.LibraryPath))
{
    Console.Error.WriteLine($"ERROR: FastParse library does not exist: {options.LibraryPath}");
    return 2;
}

if (options.Recreate && File.Exists(options.OutputDb))
{
    File.Delete(options.OutputDb);
}

Directory.CreateDirectory(Path.GetDirectoryName(options.OutputDb)!);

var inventory = LoadInventory(options.InventoryDb, options.Limit);
if (inventory.Count == 0)
{
    Console.Error.WriteLine("No Java files found in inventory.");
    return 2;
}

using var probe = new FastParseClient(options.LibraryPath);
Console.WriteLine($"Library      : {probe.Version}");
Console.WriteLine($"Inventory DB : {options.InventoryDb}");
Console.WriteLine($"Output DB    : {options.OutputDb}");
Console.WriteLine($"Files        : {inventory.Count}");
Console.WriteLine($"Threads      : {options.Workers}");

using (var db = SqliteDb.Open(options.OutputDb))
{
    CreateSchema(db, recreate: options.Recreate);
}

var queue = new BlockingCollection<WriteMessage>(boundedCapacity: options.QueueCapacity);
var writerStats = new WriterStats();
var writer = Task.Run(() => WriteDatabase(options.OutputDb, queue, writerStats, options.CommitEveryRows));
var parserByThread = new ThreadLocal<FastParseClient>(() => new FastParseClient(options.LibraryPath), trackAllValues: true);
var started = Stopwatch.StartNew();
var parsed = 0;
var failed = 0;
var sourceBytes = 0L;
var binaryBytes = 0L;
var totalNodes = 0L;

var parallelOptions = new ParallelOptions { MaxDegreeOfParallelism = options.Workers };
Parallel.ForEach(
    inventory,
    parallelOptions,
    item =>
    {
        var fileStarted = Stopwatch.StartNew();
        try
        {
            var source = File.ReadAllBytes(item.AbsolutePath);
            var parser = parserByThread.Value!;
            var result = parser.ParseBytes(source, new ParseOptions
            {
                Language = "java",
                Format = FastParseFormat.Binary,
                Fields = FastParseField.All,
                IncludeTokens = false,
                Pretty = false
            });

            var parsedFile = new ParsedFileMessage(
                item,
                SourceBytes: source.LongLength,
                NodeCount: checked((long)result.NodeCount),
                AstBinaryBytes: result.Data.LongLength,
                ElapsedMs: fileStarted.Elapsed.TotalMilliseconds);
            queue.Add(parsedFile);

            var batch = new List<AstNodeRow>(options.NodeBatchSize);
            FastParseBinaryStream.ReadNodes(result.Data, item, node =>
            {
                batch.Add(node);
                if (batch.Count >= options.NodeBatchSize)
                {
                    queue.Add(new NodeBatchMessage(batch));
                    batch = new List<AstNodeRow>(options.NodeBatchSize);
                }
            });

            if (batch.Count > 0)
            {
                queue.Add(new NodeBatchMessage(batch));
            }

            Interlocked.Increment(ref parsed);
            Interlocked.Add(ref sourceBytes, source.LongLength);
            Interlocked.Add(ref binaryBytes, result.Data.LongLength);
            Interlocked.Add(ref totalNodes, checked((long)result.NodeCount));

            var done = Volatile.Read(ref parsed) + Volatile.Read(ref failed);
            if (options.ProgressEvery > 0 && done % options.ProgressEvery == 0)
            {
                Console.WriteLine(
                    $"Progress     : {done}/{inventory.Count} " +
                    $"ok={Volatile.Read(ref parsed)} errors={Volatile.Read(ref failed)} " +
                    $"elapsed={started.Elapsed.TotalSeconds:F3}s");
            }
        }
        catch (Exception ex)
        {
            Interlocked.Increment(ref failed);
            queue.Add(new ErrorMessage(item, fileStarted.Elapsed.TotalMilliseconds, ex.ToString()));
        }
    });

queue.CompleteAdding();
await writer;

foreach (var parser in parserByThread.Values)
{
    parser.Dispose();
}

using (var db = SqliteDb.Open(options.OutputDb))
{
    CreateIndexes(db);
}

started.Stop();
Console.WriteLine($"Parsed OK    : {parsed}");
Console.WriteLine($"Errors       : {failed}");
Console.WriteLine($"Source bytes : {sourceBytes}");
Console.WriteLine($"Binary bytes : {binaryBytes}");
Console.WriteLine($"Nodes        : {totalNodes}");
Console.WriteLine($"AST rows     : {writerStats.NodeRows}");
Console.WriteLine($"Elapsed      : {started.Elapsed.TotalSeconds:F3}s");
Console.WriteLine($"Files/sec    : {parsed / Math.Max(started.Elapsed.TotalSeconds, 0.001):F1}");
Console.WriteLine($"Nodes/sec    : {totalNodes / Math.Max(started.Elapsed.TotalSeconds, 0.001):F1}");

return failed == 0 ? 0 : 1;

static string FindProjectRoot()
{
    var current = new DirectoryInfo(Directory.GetCurrentDirectory());
    while (current is not null)
    {
        if (IsProjectRoot(current.FullName))
        {
            return current.FullName;
        }

        current = current.Parent;
    }

    var directory = new DirectoryInfo(AppContext.BaseDirectory);
    while (directory is not null)
    {
        if (IsProjectRoot(directory.FullName))
        {
            return directory.FullName;
        }

        directory = directory.Parent;
    }

    return Directory.GetCurrentDirectory();
}

static bool IsProjectRoot(string directory)
{
    return File.Exists(Path.Combine(directory, "CMakeLists.txt")) &&
        Directory.Exists(Path.Combine(directory, "bindings", "csharp")) &&
        Directory.Exists(Path.Combine(directory, "data"));
}

static List<JavaFileItem> LoadInventory(string dbPath, int limit)
{
    using var db = SqliteDb.OpenReadOnly(dbPath);
    var sql = """
        SELECT
            id,
            project_id,
            project_name,
            absolute_path,
            root_relative_path,
            project_relative_path,
            file_name,
            package_name,
            size_bytes,
            line_count,
            sha256
        FROM java_files
        ORDER BY project_name, project_relative_path
        """;
    if (limit > 0)
    {
        sql += " LIMIT " + limit;
    }

    using var statement = db.Prepare(sql);
    var items = new List<JavaFileItem>();
    while (statement.Step() == SqliteResult.Row)
    {
        items.Add(new JavaFileItem(
            InventoryFileId: statement.ColumnInt64(0),
            ProjectId: statement.ColumnInt64(1),
            ProjectName: statement.ColumnText(2),
            AbsolutePath: statement.ColumnText(3),
            RootRelativePath: statement.ColumnText(4),
            ProjectRelativePath: statement.ColumnText(5),
            FileName: statement.ColumnText(6),
            PackageName: statement.ColumnText(7),
            SizeBytes: statement.ColumnInt64(8),
            LineCount: statement.ColumnInt64(9),
            Sha256: statement.ColumnText(10)));
    }

    return items;
}

static void CreateSchema(SqliteDb db, bool recreate)
{
    db.Exec("PRAGMA journal_mode = WAL");
    db.Exec("PRAGMA synchronous = NORMAL");
    db.Exec("PRAGMA temp_store = MEMORY");
    db.Exec("PRAGMA cache_size = -262144");

    if (recreate)
    {
        db.Exec("DROP TABLE IF EXISTS ast_nodes");
        db.Exec("DROP TABLE IF EXISTS java_files");
        db.Exec("DROP TABLE IF EXISTS parse_errors");
    }

    db.Exec("""
        CREATE TABLE IF NOT EXISTS java_files (
            inventory_file_id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL,
            project_name TEXT NOT NULL,
            absolute_path TEXT NOT NULL,
            root_relative_path TEXT NOT NULL,
            project_relative_path TEXT NOT NULL,
            file_name TEXT NOT NULL,
            package_name TEXT NOT NULL,
            source_bytes INTEGER NOT NULL,
            line_count INTEGER NOT NULL,
            sha256 TEXT NOT NULL,
            node_count INTEGER NOT NULL,
            ast_binary_bytes INTEGER NOT NULL,
            elapsed_ms REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS ast_nodes (
            id INTEGER PRIMARY KEY,
            inventory_file_id INTEGER NOT NULL,
            project_name TEXT NOT NULL,
            absolute_path TEXT NOT NULL,
            file_name TEXT NOT NULL,
            node_id INTEGER,
            parent_id INTEGER,
            rule TEXT NOT NULL,
            text TEXT NOT NULL,
            text_bytes INTEGER NOT NULL,
            start_line INTEGER,
            start_column INTEGER,
            end_line INTEGER,
            end_column INTEGER,
            start_byte INTEGER,
            end_byte INTEGER,
            child_count INTEGER,
            children_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS parse_errors (
            id INTEGER PRIMARY KEY,
            inventory_file_id INTEGER NOT NULL,
            project_name TEXT NOT NULL,
            absolute_path TEXT NOT NULL,
            elapsed_ms REAL NOT NULL,
            error TEXT NOT NULL
        );
        """);
}

static void CreateIndexes(SqliteDb db)
{
    db.Exec("""
        CREATE INDEX IF NOT EXISTS idx_ast_nodes_inventory_file
            ON ast_nodes(inventory_file_id);
        CREATE INDEX IF NOT EXISTS idx_ast_nodes_project
            ON ast_nodes(project_name);
        CREATE INDEX IF NOT EXISTS idx_ast_nodes_rule
            ON ast_nodes(rule);
        CREATE INDEX IF NOT EXISTS idx_ast_nodes_parent
            ON ast_nodes(inventory_file_id, parent_id);
        CREATE INDEX IF NOT EXISTS idx_ast_nodes_range
            ON ast_nodes(inventory_file_id, start_line, start_column);
        CREATE INDEX IF NOT EXISTS idx_java_files_project
            ON java_files(project_name);
        CREATE INDEX IF NOT EXISTS idx_java_files_file_name
            ON java_files(file_name);
        """);
}

static void WriteDatabase(
    string outputDb,
    BlockingCollection<WriteMessage> queue,
    WriterStats stats,
    int commitEveryRows)
{
    using var db = SqliteDb.Open(outputDb);
    db.Exec("PRAGMA journal_mode = WAL");
    db.Exec("PRAGMA synchronous = NORMAL");
    db.Exec("BEGIN IMMEDIATE");

    using var fileInsert = db.Prepare("""
        INSERT OR REPLACE INTO java_files(
            inventory_file_id,
            project_id,
            project_name,
            absolute_path,
            root_relative_path,
            project_relative_path,
            file_name,
            package_name,
            source_bytes,
            line_count,
            sha256,
            node_count,
            ast_binary_bytes,
            elapsed_ms
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """);

    using var nodeInsert = db.Prepare("""
        INSERT INTO ast_nodes(
            inventory_file_id,
            project_name,
            absolute_path,
            file_name,
            node_id,
            parent_id,
            rule,
            text,
            text_bytes,
            start_line,
            start_column,
            end_line,
            end_column,
            start_byte,
            end_byte,
            child_count,
            children_json
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """);

    using var errorInsert = db.Prepare("""
        INSERT INTO parse_errors(
            inventory_file_id,
            project_name,
            absolute_path,
            elapsed_ms,
            error
        )
        VALUES(?, ?, ?, ?, ?)
        """);

    var rowsSinceCommit = 0L;
    foreach (var message in queue.GetConsumingEnumerable())
    {
        switch (message)
        {
            case ParsedFileMessage parsedFile:
                InsertFile(fileInsert, parsedFile);
                stats.FileRows++;
                break;
            case NodeBatchMessage nodeBatch:
                foreach (var node in nodeBatch.Nodes)
                {
                    InsertNode(nodeInsert, node);
                }

                stats.NodeRows += nodeBatch.Nodes.Count;
                rowsSinceCommit += nodeBatch.Nodes.Count;
                break;
            case ErrorMessage error:
                InsertError(errorInsert, error);
                stats.ErrorRows++;
                rowsSinceCommit++;
                break;
        }

        if (rowsSinceCommit >= commitEveryRows)
        {
            db.Exec("COMMIT");
            db.Exec("BEGIN IMMEDIATE");
            rowsSinceCommit = 0;
        }
    }

    db.Exec("COMMIT");
}

static void InsertFile(SqliteStatement statement, ParsedFileMessage file)
{
    statement.ResetAndClear();
    var item = file.Item;
    statement.BindInt64(1, item.InventoryFileId);
    statement.BindInt64(2, item.ProjectId);
    statement.BindText(3, item.ProjectName);
    statement.BindText(4, item.AbsolutePath);
    statement.BindText(5, item.RootRelativePath);
    statement.BindText(6, item.ProjectRelativePath);
    statement.BindText(7, item.FileName);
    statement.BindText(8, item.PackageName);
    statement.BindInt64(9, file.SourceBytes);
    statement.BindInt64(10, item.LineCount);
    statement.BindText(11, item.Sha256);
    statement.BindInt64(12, file.NodeCount);
    statement.BindInt64(13, file.AstBinaryBytes);
    statement.BindDouble(14, file.ElapsedMs);
    statement.StepDone();
}

static void InsertNode(SqliteStatement statement, AstNodeRow node)
{
    statement.ResetAndClear();
    statement.BindInt64(1, node.InventoryFileId);
    statement.BindText(2, node.ProjectName);
    statement.BindText(3, node.AbsolutePath);
    statement.BindText(4, node.FileName);
    statement.BindNullableInt64(5, node.NodeId);
    statement.BindNullableInt64(6, node.ParentId);
    statement.BindText(7, node.Rule);
    statement.BindText(8, node.Text);
    statement.BindInt64(9, node.TextBytes);
    statement.BindNullableInt64(10, node.StartLine);
    statement.BindNullableInt64(11, node.StartColumn);
    statement.BindNullableInt64(12, node.EndLine);
    statement.BindNullableInt64(13, node.EndColumn);
    statement.BindNullableInt64(14, node.StartByte);
    statement.BindNullableInt64(15, node.EndByte);
    statement.BindNullableInt64(16, node.ChildCount);
    statement.BindText(17, node.ChildrenJson);
    statement.StepDone();
}

static void InsertError(SqliteStatement statement, ErrorMessage error)
{
    statement.ResetAndClear();
    statement.BindInt64(1, error.Item.InventoryFileId);
    statement.BindText(2, error.Item.ProjectName);
    statement.BindText(3, error.Item.AbsolutePath);
    statement.BindDouble(4, error.ElapsedMs);
    statement.BindText(5, error.Error);
    statement.StepDone();
}

sealed record RunnerOptions(
    string InventoryDb,
    string OutputDb,
    string LibraryPath,
    int Workers,
    int Limit,
    bool Recreate,
    int NodeBatchSize,
    int QueueCapacity,
    int CommitEveryRows,
    int ProgressEvery)
{
    public static RunnerOptions Parse(string[] args, string root)
    {
        var inventoryDb = Path.Combine(root, "data", "java_swing_inventory.sqlite");
        var outputDb = Path.Combine(root, "data", "fastparse_java_ast_nodes_csharp.sqlite");
        var libraryPath = Path.Combine(root, "bin", OperatingSystem.IsMacOS() ? "libfastparse.dylib" : OperatingSystem.IsWindows() ? "fastparse.dll" : "libfastparse.so");
        var workers = Math.Min(12, Environment.ProcessorCount);
        var limit = 0;
        var recreate = true;
        var nodeBatchSize = 2_000;
        var queueCapacity = 128;
        var commitEveryRows = 50_000;
        var progressEvery = 100;

        for (var i = 0; i < args.Length; i++)
        {
            var arg = args[i];
            string Next() => i + 1 < args.Length ? args[++i] : throw new ArgumentException($"Missing value for {arg}");
            switch (arg)
            {
                case "--inventory-db":
                    inventoryDb = Path.GetFullPath(Next());
                    break;
                case "--out-db":
                    outputDb = Path.GetFullPath(Next());
                    break;
                case "--lib":
                    libraryPath = Path.GetFullPath(Next());
                    break;
                case "--workers":
                    workers = int.Parse(Next());
                    break;
                case "--limit":
                    limit = int.Parse(Next());
                    break;
                case "--no-recreate":
                    recreate = false;
                    break;
                case "--node-batch-size":
                    nodeBatchSize = int.Parse(Next());
                    break;
                case "--queue-capacity":
                    queueCapacity = int.Parse(Next());
                    break;
                case "--commit-every-rows":
                    commitEveryRows = int.Parse(Next());
                    break;
                case "--progress-every":
                    progressEvery = int.Parse(Next());
                    break;
                case "--help":
                    Console.WriteLine("""
                        FastParse.InventoryToSqliteExample

                        Options:
                          --inventory-db PATH
                          --out-db PATH
                          --lib PATH
                          --workers N
                          --limit N
                          --no-recreate
                          --node-batch-size N
                          --queue-capacity N
                          --commit-every-rows N
                          --progress-every N
                        """);
                    Environment.Exit(0);
                    break;
                default:
                    throw new ArgumentException($"Unknown argument: {arg}");
            }
        }

        return new RunnerOptions(
            InventoryDb: Path.GetFullPath(inventoryDb),
            OutputDb: Path.GetFullPath(outputDb),
            LibraryPath: Path.GetFullPath(libraryPath),
            Workers: Math.Max(1, workers),
            Limit: Math.Max(0, limit),
            Recreate: recreate,
            NodeBatchSize: Math.Max(1, nodeBatchSize),
            QueueCapacity: Math.Max(1, queueCapacity),
            CommitEveryRows: Math.Max(1, commitEveryRows),
            ProgressEvery: progressEvery);
    }
}

sealed record JavaFileItem(
    long InventoryFileId,
    long ProjectId,
    string ProjectName,
    string AbsolutePath,
    string RootRelativePath,
    string ProjectRelativePath,
    string FileName,
    string PackageName,
    long SizeBytes,
    long LineCount,
    string Sha256);

sealed record ParsedFileMessage(
    JavaFileItem Item,
    long SourceBytes,
    long NodeCount,
    long AstBinaryBytes,
    double ElapsedMs) : WriteMessage;

sealed record NodeBatchMessage(List<AstNodeRow> Nodes) : WriteMessage;

sealed record ErrorMessage(JavaFileItem Item, double ElapsedMs, string Error) : WriteMessage;

abstract record WriteMessage;

sealed class WriterStats
{
    public long FileRows;
    public long NodeRows;
    public long ErrorRows;
}

sealed record AstNodeRow(
    long InventoryFileId,
    string ProjectName,
    string AbsolutePath,
    string FileName,
    long? NodeId,
    long? ParentId,
    string Rule,
    string Text,
    long TextBytes,
    long? StartLine,
    long? StartColumn,
    long? EndLine,
    long? EndColumn,
    long? StartByte,
    long? EndByte,
    long? ChildCount,
    string ChildrenJson);

static class FastParseBinaryStream
{
    public static void ReadNodes(byte[] data, JavaFileItem item, Action<AstNodeRow> onNode)
    {
        var reader = new MsgPackReader(data);
        var topCount = reader.ReadMapLength();
        for (var i = 0; i < topCount; i++)
        {
            var key = reader.ReadString();
            if (key != "nodes")
            {
                reader.Skip();
                continue;
            }

            var nodeCount = reader.ReadArrayLength();
            for (var nodeIndex = 0; nodeIndex < nodeCount; nodeIndex++)
            {
                onNode(ReadNode(ref reader, item));
            }
        }

        if (!reader.End)
        {
            throw new FormatException("Trailing MessagePack bytes.");
        }
    }

    private static AstNodeRow ReadNode(ref MsgPackReader reader, JavaFileItem item)
    {
        long? nodeId = null;
        long? parentId = null;
        var rule = string.Empty;
        var text = string.Empty;
        long textBytes = 0;
        long? startLine = null;
        long? startColumn = null;
        long? endLine = null;
        long? endColumn = null;
        long? startByte = null;
        long? endByte = null;
        long? childCount = null;
        var childrenJson = "[]";

        var fieldCount = reader.ReadMapLength();
        for (var i = 0; i < fieldCount; i++)
        {
            var field = reader.ReadString();
            switch (field)
            {
                case "id":
                    nodeId = checked((long)reader.ReadUInt());
                    break;
                case "parentId":
                    parentId = reader.TryReadNil() ? null : checked((long)reader.ReadUInt());
                    break;
                case "rule":
                    rule = reader.ReadString();
                    break;
                case "text":
                {
                    var bytes = reader.ReadBin();
                    textBytes = bytes.Length;
                    text = Encoding.UTF8.GetString(bytes);
                    break;
                }
                case "startLine":
                    startLine = checked((long)reader.ReadUInt());
                    break;
                case "startColumn":
                    startColumn = checked((long)reader.ReadUInt());
                    break;
                case "endLine":
                    endLine = checked((long)reader.ReadUInt());
                    break;
                case "endColumn":
                    endColumn = checked((long)reader.ReadUInt());
                    break;
                case "startByte":
                    startByte = checked((long)reader.ReadUInt());
                    break;
                case "endByte":
                    endByte = checked((long)reader.ReadUInt());
                    break;
                case "childCount":
                    childCount = checked((long)reader.ReadUInt());
                    break;
                case "children":
                    childrenJson = ReadChildrenJson(ref reader);
                    break;
                default:
                    reader.Skip();
                    break;
            }
        }

        return new AstNodeRow(
            item.InventoryFileId,
            item.ProjectName,
            item.AbsolutePath,
            item.FileName,
            nodeId,
            parentId,
            rule,
            text,
            textBytes,
            startLine,
            startColumn,
            endLine,
            endColumn,
            startByte,
            endByte,
            childCount,
            childrenJson);
    }

    private static string ReadChildrenJson(ref MsgPackReader reader)
    {
        var count = reader.ReadArrayLength();
        if (count == 0)
        {
            return "[]";
        }

        var builder = new StringBuilder();
        builder.Append('[');
        for (var i = 0; i < count; i++)
        {
            if (i > 0)
            {
                builder.Append(',');
            }

            builder.Append('{');
            var fieldCount = reader.ReadMapLength();
            var wrote = false;
            for (var fieldIndex = 0; fieldIndex < fieldCount; fieldIndex++)
            {
                var key = reader.ReadString();
                if (key == "rule")
                {
                    AppendJsonProperty(builder, "rule", reader.ReadString(), ref wrote);
                }
                else if (key == "text")
                {
                    var bytes = reader.ReadBin();
                    AppendJsonProperty(builder, "text", Encoding.UTF8.GetString(bytes), ref wrote);
                    AppendJsonProperty(builder, "text_bytes", bytes.Length.ToString(), ref wrote, rawValue: true);
                }
                else
                {
                    reader.Skip();
                }
            }

            builder.Append('}');
        }

        builder.Append(']');
        return builder.ToString();
    }

    private static void AppendJsonProperty(
        StringBuilder builder,
        string name,
        string value,
        ref bool wrote,
        bool rawValue = false)
    {
        if (wrote)
        {
            builder.Append(',');
        }

        wrote = true;
        AppendJsonString(builder, name);
        builder.Append(':');
        if (rawValue)
        {
            builder.Append(value);
        }
        else
        {
            AppendJsonString(builder, value);
        }
    }

    private static void AppendJsonString(StringBuilder builder, string value)
    {
        builder.Append('"');
        foreach (var ch in value)
        {
            switch (ch)
            {
                case '"':
                    builder.Append("\\\"");
                    break;
                case '\\':
                    builder.Append("\\\\");
                    break;
                case '\b':
                    builder.Append("\\b");
                    break;
                case '\f':
                    builder.Append("\\f");
                    break;
                case '\n':
                    builder.Append("\\n");
                    break;
                case '\r':
                    builder.Append("\\r");
                    break;
                case '\t':
                    builder.Append("\\t");
                    break;
                default:
                    if (ch < ' ')
                    {
                        builder.Append("\\u");
                        builder.Append(((int)ch).ToString("x4"));
                    }
                    else
                    {
                        builder.Append(ch);
                    }

                    break;
            }
        }

        builder.Append('"');
    }
}

ref struct MsgPackReader
{
    private readonly ReadOnlySpan<byte> _data;
    private int _index;

    public MsgPackReader(ReadOnlySpan<byte> data)
    {
        _data = data;
        _index = 0;
    }

    public bool End => _index == _data.Length;

    public bool TryReadNil()
    {
        if (Peek() != 0xC0)
        {
            return false;
        }

        _index++;
        return true;
    }

    public ulong ReadUInt()
    {
        var code = ReadByte();
        if (code <= 0x7F)
        {
            return code;
        }

        return code switch
        {
            0xCC => ReadByte(),
            0xCD => ReadUInt16(),
            0xCE => ReadUInt32(),
            0xCF => ReadUInt64(),
            _ => throw new FormatException($"Expected unsigned integer, got 0x{code:X2}.")
        };
    }

    public string ReadString()
    {
        var code = ReadByte();
        var length = code switch
        {
            >= 0xA0 and <= 0xBF => code & 0x1F,
            0xD9 => ReadByte(),
            0xDA => ReadUInt16(),
            0xDB => checked((int)ReadUInt32()),
            _ => throw new FormatException($"Expected string, got 0x{code:X2}.")
        };

        return Encoding.UTF8.GetString(ReadBytes(length));
    }

    public ReadOnlySpan<byte> ReadBin()
    {
        var code = ReadByte();
        var length = code switch
        {
            0xC4 => ReadByte(),
            0xC5 => ReadUInt16(),
            0xC6 => checked((int)ReadUInt32()),
            _ => throw new FormatException($"Expected bin, got 0x{code:X2}.")
        };

        return ReadBytes(length);
    }

    public int ReadMapLength()
    {
        var code = ReadByte();
        return code switch
        {
            >= 0x80 and <= 0x8F => code & 0x0F,
            0xDE => ReadUInt16(),
            0xDF => checked((int)ReadUInt32()),
            _ => throw new FormatException($"Expected map, got 0x{code:X2}.")
        };
    }

    public int ReadArrayLength()
    {
        var code = ReadByte();
        return code switch
        {
            >= 0x90 and <= 0x9F => code & 0x0F,
            0xDC => ReadUInt16(),
            0xDD => checked((int)ReadUInt32()),
            _ => throw new FormatException($"Expected array, got 0x{code:X2}.")
        };
    }

    public void Skip()
    {
        var code = Peek();
        if (code <= 0x7F || code is 0xC0 or 0xC2 or 0xC3)
        {
            _index++;
            return;
        }

        if (code >= 0xA0 && code <= 0xBF)
        {
            _index++;
            SkipBytes(code & 0x1F);
            return;
        }

        if (code >= 0x90 && code <= 0x9F)
        {
            _index++;
            for (var i = 0; i < (code & 0x0F); i++)
            {
                Skip();
            }

            return;
        }

        if (code >= 0x80 && code <= 0x8F)
        {
            _index++;
            for (var i = 0; i < (code & 0x0F) * 2; i++)
            {
                Skip();
            }

            return;
        }

        _index++;
        switch (code)
        {
            case 0xCC:
            case 0xD0:
                SkipBytes(1);
                break;
            case 0xCD:
            case 0xD1:
                SkipBytes(2);
                break;
            case 0xCE:
            case 0xD2:
                SkipBytes(4);
                break;
            case 0xCF:
            case 0xD3:
                SkipBytes(8);
                break;
            case 0xC4:
            case 0xD9:
                SkipBytes(ReadByte());
                break;
            case 0xC5:
            case 0xDA:
                SkipBytes(ReadUInt16());
                break;
            case 0xC6:
            case 0xDB:
                SkipBytes(checked((int)ReadUInt32()));
                break;
            case 0xDC:
                for (var i = 0; i < ReadUInt16(); i++) Skip();
                break;
            case 0xDD:
                for (var i = 0; i < checked((int)ReadUInt32()); i++) Skip();
                break;
            case 0xDE:
                for (var i = 0; i < ReadUInt16() * 2; i++) Skip();
                break;
            case 0xDF:
                for (var i = 0; i < checked((int)ReadUInt32()) * 2; i++) Skip();
                break;
            default:
                throw new FormatException($"Unsupported MessagePack code 0x{code:X2}.");
        }
    }

    private byte Peek()
    {
        if (_index >= _data.Length)
        {
            throw new FormatException("Unexpected end of MessagePack payload.");
        }

        return _data[_index];
    }

    private byte ReadByte()
    {
        var value = Peek();
        _index++;
        return value;
    }

    private ushort ReadUInt16()
    {
        return BinaryPrimitives.ReadUInt16BigEndian(ReadBytes(sizeof(ushort)));
    }

    private uint ReadUInt32()
    {
        return BinaryPrimitives.ReadUInt32BigEndian(ReadBytes(sizeof(uint)));
    }

    private ulong ReadUInt64()
    {
        return BinaryPrimitives.ReadUInt64BigEndian(ReadBytes(sizeof(ulong)));
    }

    private ReadOnlySpan<byte> ReadBytes(int length)
    {
        if (length < 0 || _index + length > _data.Length)
        {
            throw new FormatException("Unexpected end of MessagePack payload.");
        }

        var value = _data.Slice(_index, length);
        _index += length;
        return value;
    }

    private void SkipBytes(int length)
    {
        _ = ReadBytes(length);
    }
}

sealed class SqliteDb : IDisposable
{
    private nint _handle;

    private SqliteDb(nint handle)
    {
        _handle = handle;
    }

    public static SqliteDb Open(string path)
    {
        return Open(path, SqliteOpenFlags.ReadWrite | SqliteOpenFlags.Create | SqliteOpenFlags.FullMutex);
    }

    public static SqliteDb OpenReadOnly(string path)
    {
        return Open(path, SqliteOpenFlags.ReadOnly | SqliteOpenFlags.FullMutex);
    }

    private static SqliteDb Open(string path, int flags)
    {
        var rc = Native.sqlite3_open_v2(path, out var handle, flags, null);
        if (rc != SqliteResult.Ok)
        {
            var message = handle == 0 ? "cannot open sqlite database" : Native.ErrorMessage(handle);
            if (handle != 0)
            {
                Native.sqlite3_close(handle);
            }

            throw new InvalidOperationException(message);
        }

        return new SqliteDb(handle);
    }

    public void Exec(string sql)
    {
        var rc = Native.sqlite3_exec(_handle, sql, 0, 0, out var error);
        if (rc != SqliteResult.Ok)
        {
            var message = error == 0 ? Native.ErrorMessage(_handle) : Marshal.PtrToStringUTF8(error) ?? "sqlite error";
            if (error != 0)
            {
                Native.sqlite3_free(error);
            }

            throw new InvalidOperationException(message);
        }
    }

    public SqliteStatement Prepare(string sql)
    {
        var rc = Native.sqlite3_prepare_v2(_handle, sql, -1, out var statement, 0);
        if (rc != SqliteResult.Ok)
        {
            throw new InvalidOperationException(Native.ErrorMessage(_handle));
        }

        return new SqliteStatement(_handle, statement);
    }

    public void Dispose()
    {
        if (_handle == 0)
        {
            return;
        }

        Native.sqlite3_close(_handle);
        _handle = 0;
    }
}

sealed class SqliteStatement : IDisposable
{
    private readonly nint _db;
    private nint _statement;

    public SqliteStatement(nint db, nint statement)
    {
        _db = db;
        _statement = statement;
    }

    public SqliteResult Step()
    {
        return Native.sqlite3_step(_statement);
    }

    public void StepDone()
    {
        var rc = Step();
        if (rc != SqliteResult.Done)
        {
            throw new InvalidOperationException($"sqlite step failed: {rc} {Native.ErrorMessage(_db)}");
        }
    }

    public void ResetAndClear()
    {
        Native.sqlite3_reset(_statement);
        Native.sqlite3_clear_bindings(_statement);
    }

    public void BindInt64(int index, long value)
    {
        Check(Native.sqlite3_bind_int64(_statement, index, value));
    }

    public void BindNullableInt64(int index, long? value)
    {
        if (value is null)
        {
            Check(Native.sqlite3_bind_null(_statement, index));
            return;
        }

        BindInt64(index, value.Value);
    }

    public void BindDouble(int index, double value)
    {
        Check(Native.sqlite3_bind_double(_statement, index, value));
    }

    public void BindText(int index, string value)
    {
        var bytes = Encoding.UTF8.GetBytes(value);
        Check(Native.sqlite3_bind_text(_statement, index, bytes, bytes.Length, Native.SqliteTransient));
    }

    public long ColumnInt64(int index)
    {
        return Native.sqlite3_column_int64(_statement, index);
    }

    public string ColumnText(int index)
    {
        var pointer = Native.sqlite3_column_text(_statement, index);
        if (pointer == 0)
        {
            return string.Empty;
        }

        var length = Native.sqlite3_column_bytes(_statement, index);
        var bytes = new byte[length];
        Marshal.Copy(pointer, bytes, 0, length);
        return Encoding.UTF8.GetString(bytes);
    }

    public void Dispose()
    {
        if (_statement == 0)
        {
            return;
        }

        Native.sqlite3_finalize(_statement);
        _statement = 0;
    }

    private void Check(SqliteResult rc)
    {
        if (rc != SqliteResult.Ok)
        {
            throw new InvalidOperationException($"sqlite bind failed: {rc} {Native.ErrorMessage(_db)}");
        }
    }
}

static class Native
{
    public static readonly nint SqliteTransient = new(-1);

    [DllImport("sqlite3", CallingConvention = CallingConvention.Cdecl)]
    public static extern SqliteResult sqlite3_open_v2(
        string filename,
        out nint db,
        int flags,
        string? vfs);

    [DllImport("sqlite3", CallingConvention = CallingConvention.Cdecl)]
    public static extern SqliteResult sqlite3_close(nint db);

    [DllImport("sqlite3", CallingConvention = CallingConvention.Cdecl)]
    public static extern nint sqlite3_errmsg(nint db);

    [DllImport("sqlite3", CallingConvention = CallingConvention.Cdecl)]
    public static extern SqliteResult sqlite3_exec(
        nint db,
        string sql,
        nint callback,
        nint firstArg,
        out nint errorMessage);

    [DllImport("sqlite3", CallingConvention = CallingConvention.Cdecl)]
    public static extern void sqlite3_free(nint value);

    [DllImport("sqlite3", CallingConvention = CallingConvention.Cdecl)]
    public static extern SqliteResult sqlite3_prepare_v2(
        nint db,
        string sql,
        int sqlBytes,
        out nint statement,
        nint tail);

    [DllImport("sqlite3", CallingConvention = CallingConvention.Cdecl)]
    public static extern SqliteResult sqlite3_step(nint statement);

    [DllImport("sqlite3", CallingConvention = CallingConvention.Cdecl)]
    public static extern SqliteResult sqlite3_finalize(nint statement);

    [DllImport("sqlite3", CallingConvention = CallingConvention.Cdecl)]
    public static extern SqliteResult sqlite3_reset(nint statement);

    [DllImport("sqlite3", CallingConvention = CallingConvention.Cdecl)]
    public static extern SqliteResult sqlite3_clear_bindings(nint statement);

    [DllImport("sqlite3", CallingConvention = CallingConvention.Cdecl)]
    public static extern SqliteResult sqlite3_bind_int64(nint statement, int index, long value);

    [DllImport("sqlite3", CallingConvention = CallingConvention.Cdecl)]
    public static extern SqliteResult sqlite3_bind_double(nint statement, int index, double value);

    [DllImport("sqlite3", CallingConvention = CallingConvention.Cdecl)]
    public static extern SqliteResult sqlite3_bind_null(nint statement, int index);

    [DllImport("sqlite3", CallingConvention = CallingConvention.Cdecl)]
    public static extern SqliteResult sqlite3_bind_text(
        nint statement,
        int index,
        byte[] value,
        int bytes,
        nint destructor);

    [DllImport("sqlite3", CallingConvention = CallingConvention.Cdecl)]
    public static extern long sqlite3_column_int64(nint statement, int index);

    [DllImport("sqlite3", CallingConvention = CallingConvention.Cdecl)]
    public static extern nint sqlite3_column_text(nint statement, int index);

    [DllImport("sqlite3", CallingConvention = CallingConvention.Cdecl)]
    public static extern int sqlite3_column_bytes(nint statement, int index);

    public static string ErrorMessage(nint db)
    {
        return Marshal.PtrToStringUTF8(sqlite3_errmsg(db)) ?? "sqlite error";
    }
}

static class SqliteOpenFlags
{
    public const int ReadOnly = 0x00000001;
    public const int ReadWrite = 0x00000002;
    public const int Create = 0x00000004;
    public const int FullMutex = 0x00010000;
}

enum SqliteResult
{
    Ok = 0,
    Row = 100,
    Done = 101
}
