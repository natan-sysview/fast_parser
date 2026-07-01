using System.Runtime.InteropServices;
using System.Text;

namespace FastParse;

/// <summary>
/// Managed C# client for the native FastParse C ABI.
/// </summary>
public sealed unsafe class FastParseClient : IDisposable
{
    private readonly nint _library;
    private readonly VersionDelegate _version;
    private readonly ParseDelegate _parse;
    private readonly ParseV2Delegate? _parseV2;
    private readonly QueryDelegate _query;
    private readonly ResultFreeDelegate _resultFree;
    private readonly LoadLanguageExtensionDelegate _loadLanguageExtension;
    private readonly LanguageAvailableDelegate _languageAvailable;
    private readonly LanguageLoadResultFreeDelegate _languageLoadResultFree;
    private bool _disposed;

    /// <summary>
    /// Loads the native FastParse library.
    /// </summary>
    /// <param name="libraryPath">
    /// Optional explicit path to <c>libfastparse.dylib</c>, <c>libfastparse.so</c>, or <c>fastparse.dll</c>.
    /// Normal NuGet use does not require this parameter.
    /// </param>
    public FastParseClient(string? libraryPath = null)
    {
        (_library, LibraryPath) = LoadNativeLibrary(libraryPath);
        _version = LoadFunction<VersionDelegate>("fastparse_version", "tsmp_version");
        _parse = LoadFunction<ParseDelegate>("fastparse_parse", "tsmp_parse");
        _parseV2 = TryLoadFunction<ParseV2Delegate>("fastparse_parse_v2", "tsmp_parse_v2");
        _query = LoadFunction<QueryDelegate>("fastparse_query", "tsmp_query");
        _resultFree = LoadFunction<ResultFreeDelegate>("fastparse_result_free", "tsmp_result_free");
        _loadLanguageExtension = LoadRequiredFunction<LoadLanguageExtensionDelegate>("fastparse_load_language_extension");
        _languageAvailable = LoadRequiredFunction<LanguageAvailableDelegate>("fastparse_language_available");
        _languageLoadResultFree = LoadRequiredFunction<LanguageLoadResultFreeDelegate>("fastparse_language_load_result_free");
    }

    /// <summary>Path or library name used to load the native FastParse library.</summary>
    public string LibraryPath { get; }

    /// <summary>Native FastParse C API version string.</summary>
    public string Version => Marshal.PtrToStringUTF8((nint)_version()) ?? string.Empty;

    /// <summary>
    /// Returns whether a parse language is currently available in the native registry.
    /// </summary>
    /// <param name="language">Canonical language name such as <c>java</c> or <c>cobol</c>.</param>
    public bool LanguageAvailable(string language)
    {
        EnsureNotDisposed();
        var nativeLanguage = StringToUtf8(language);
        try
        {
            return _languageAvailable((byte*)nativeLanguage) != 0;
        }
        finally
        {
            FreeUtf8(nativeLanguage);
        }
    }

    /// <summary>
    /// Loads a native FastParse language extension from an explicit dynamic library path.
    /// Load extensions before starting concurrent parse workers.
    /// </summary>
    /// <param name="path">Path to a FastParse language extension dynamic library.</param>
    public LanguageExtensionLoadResult LoadLanguageExtension(string path)
    {
        EnsureNotDisposed();
        var nativePath = StringToUtf8(path);
        NativeLanguageLoadResult result = default;
        int status;
        try
        {
            status = _loadLanguageExtension((byte*)nativePath, &result);
            if (status != 0 || result.Status != 0)
            {
                var message = NativeString(result.ErrorMessage);
                throw new FastParseException(status, result.Status, string.IsNullOrWhiteSpace(message) ? "no error detail" : message);
            }

            return new LanguageExtensionLoadResult
            {
                Language = NativeString(result.Language),
                DisplayName = NativeString(result.DisplayName)
            };
        }
        finally
        {
            _languageLoadResultFree(&result);
            FreeUtf8(nativePath);
        }
    }

    /// <summary>
    /// Loads a FastParse language extension installed by a package manager.
    /// For example, <c>FastParser.Language.Python</c> can be loaded with <c>LoadBundledLanguage("python")</c>.
    /// </summary>
    /// <param name="language">Canonical language name such as <c>python</c> or <c>cobol</c>.</param>
    public LanguageExtensionLoadResult LoadBundledLanguage(string language)
    {
        EnsureNotDisposed();
        if (LanguageAvailable(language))
        {
            return new LanguageExtensionLoadResult { Language = language, DisplayName = language };
        }

        var candidates = BundledLanguageExtensionCandidates(language).Distinct().ToArray();
        var errors = new List<string>();
        foreach (var candidate in candidates)
        {
            if (!File.Exists(candidate))
            {
                errors.Add($"{candidate}: missing");
                continue;
            }

            try
            {
                var result = LoadLanguageExtension(candidate);
                if (!LanguageAvailable(language))
                {
                    throw new FastParseException(0, 0, $"extension loaded {result.Language}, but {language} is still unavailable");
                }

                return result;
            }
            catch (Exception ex) when (ex is DllNotFoundException or BadImageFormatException or FastParseException)
            {
                errors.Add($"{candidate}: {ex.GetType().Name}: {ex.Message.Split('\n')[0]}");
            }
        }

        var message = new StringBuilder()
            .AppendLine($"Unable to load bundled FastParse language extension '{language}'.")
            .AppendLine($"Install package: FastParser.Language.{ToPackageLanguageName(language)}")
            .AppendLine($"OS: {RuntimeInformation.OSDescription}")
            .AppendLine($"Architecture: {RuntimeInformation.ProcessArchitecture}")
            .AppendLine($"AppContext.BaseDirectory: {AppContext.BaseDirectory}")
            .AppendLine("Tried:")
            .AppendLine(string.Join(Environment.NewLine, errors.Select(error => $"  - {error}")))
            .ToString();
        throw new DllNotFoundException(message);
    }

    /// <summary>
    /// Parses source bytes and copies output bytes into managed memory.
    /// </summary>
    /// <param name="source">Source code bytes.</param>
    /// <param name="options">Parse options. Defaults to full JSON AST output.</param>
    /// <returns>A full parse result containing output bytes.</returns>
    public ParseResult ParseBytes(ReadOnlySpan<byte> source, ParseOptions? options = null)
    {
        var (data, nodeCount, format, _) = ParseNative(source, options ?? ParseOptions.JsonAll, copyData: true);
        return new ParseResult(data, nodeCount, format);
    }

    /// <summary>
    /// Parses source bytes and returns counts/lengths without copying output bytes.
    /// </summary>
    /// <param name="source">Source code bytes.</param>
    /// <param name="options">Parse options. Defaults to full JSON AST output.</param>
    /// <returns>A summary result without output bytes.</returns>
    public ParseSummary ParseBytesSummary(ReadOnlySpan<byte> source, ParseOptions? options = null)
    {
        var (_, nodeCount, format, outputLength) = ParseNative(source, options ?? ParseOptions.JsonAll, copyData: false);
        return new ParseSummary(outputLength, nodeCount, format);
    }

    /// <summary>
    /// Encodes source text and parses it.
    /// </summary>
    /// <param name="source">Source code text.</param>
    /// <param name="options">Parse options. Defaults to full JSON AST output.</param>
    /// <param name="encoding">Encoding used to convert text to bytes. Defaults to UTF-8.</param>
    /// <returns>A full parse result containing output bytes.</returns>
    public ParseResult ParseText(string source, ParseOptions? options = null, Encoding? encoding = null)
    {
        encoding ??= Encoding.UTF8;
        return ParseBytes(encoding.GetBytes(source), options);
    }

    /// <summary>
    /// Encodes source text and returns counts/lengths without copying output bytes.
    /// </summary>
    /// <param name="source">Source code text.</param>
    /// <param name="options">Parse options. Defaults to full JSON AST output.</param>
    /// <param name="encoding">Encoding used to convert text to bytes. Defaults to UTF-8.</param>
    /// <returns>A summary result without output bytes.</returns>
    public ParseSummary ParseTextSummary(string source, ParseOptions? options = null, Encoding? encoding = null)
    {
        encoding ??= Encoding.UTF8;
        return ParseBytesSummary(encoding.GetBytes(source), options);
    }

    /// <summary>
    /// Parses source bytes, executes a Tree-sitter query, and copies query output bytes into managed memory.
    /// </summary>
    /// <param name="source">Source code bytes.</param>
    /// <param name="query">Tree-sitter query text.</param>
    /// <param name="options">Query options. Defaults to Java JSON capture output.</param>
    /// <returns>A full query result containing output bytes.</returns>
    public ParseResult QueryBytes(ReadOnlySpan<byte> source, string query, QueryOptions? options = null)
    {
        var queryBytes = Encoding.UTF8.GetBytes(query);
        var (data, captureCount, format, _) = QueryNative(source, queryBytes, options ?? QueryOptions.JsonDefault, copyData: true);
        return new ParseResult(data, captureCount, format);
    }

    /// <summary>
    /// Parses source bytes, executes a Tree-sitter query, and returns counts/lengths without copying output bytes.
    /// </summary>
    /// <param name="source">Source code bytes.</param>
    /// <param name="query">Tree-sitter query text.</param>
    /// <param name="options">Query options. Defaults to Java JSON capture output.</param>
    /// <returns>A summary result. <see cref="ParseSummary.NodeCount"/> is the capture count.</returns>
    public ParseSummary QueryBytesSummary(ReadOnlySpan<byte> source, string query, QueryOptions? options = null)
    {
        var queryBytes = Encoding.UTF8.GetBytes(query);
        var (_, captureCount, format, outputLength) = QueryNative(source, queryBytes, options ?? QueryOptions.JsonDefault, copyData: false);
        return new ParseSummary(outputLength, captureCount, format);
    }

    /// <summary>
    /// Encodes source text, executes a Tree-sitter query, and copies query output bytes into managed memory.
    /// </summary>
    /// <param name="source">Source code text.</param>
    /// <param name="query">Tree-sitter query text.</param>
    /// <param name="options">Query options. Defaults to Java JSON capture output.</param>
    /// <param name="encoding">Encoding used to convert source text to bytes. Defaults to UTF-8.</param>
    /// <returns>A full query result containing output bytes.</returns>
    public ParseResult QueryText(string source, string query, QueryOptions? options = null, Encoding? encoding = null)
    {
        encoding ??= Encoding.UTF8;
        return QueryBytes(encoding.GetBytes(source), query, options);
    }

    /// <summary>
    /// Encodes source text, executes a Tree-sitter query, and returns counts/lengths without copying output bytes.
    /// </summary>
    /// <param name="source">Source code text.</param>
    /// <param name="query">Tree-sitter query text.</param>
    /// <param name="options">Query options. Defaults to Java JSON capture output.</param>
    /// <param name="encoding">Encoding used to convert source text to bytes. Defaults to UTF-8.</param>
    /// <returns>A summary result. <see cref="ParseSummary.NodeCount"/> is the capture count.</returns>
    public ParseSummary QueryTextSummary(string source, string query, QueryOptions? options = null, Encoding? encoding = null)
    {
        encoding ??= Encoding.UTF8;
        return QueryBytesSummary(encoding.GetBytes(source), query, options);
    }

    /// <summary>
    /// Frees the loaded native library handle.
    /// </summary>
    public void Dispose()
    {
        if (_disposed)
        {
            return;
        }

        NativeLibrary.Free(_library);
        _disposed = true;
    }

    private (byte[] Data, ulong NodeCount, FastParseFormat Format, ulong OutputLength) ParseNative(
        ReadOnlySpan<byte> source,
        ParseOptions options,
        bool copyData)
    {
        EnsureNotDisposed();

        var language = StringToUtf8(options.Language);
        var includeRules = StringToUtf8(options.IncludeRules);
        var nativeOptions = new NativeOptions
        {
            Language = language,
            Format = (int)options.Format,
            IncludeRules = includeRules,
            Fields = (uint)options.Fields,
            IncludeTokens = options.IncludeTokens ? 1 : 0,
            Pretty = options.Pretty ? 1 : 0
        };
        var nativeOptionsV2 = new NativeOptionsV2
        {
            Language = language,
            Format = (int)options.Format,
            IncludeRules = includeRules,
            Fields = (uint)options.Fields,
            IncludeTokens = options.IncludeTokens ? 1 : 0,
            Pretty = options.Pretty ? 1 : 0,
            Normalization = (int)options.Normalization
        };

        NativeResult nativeResult = default;
        int status;

        try
        {
            fixed (byte* sourcePtr = source)
            {
                if (_parseV2 is not null)
                {
                    status = _parseV2(
                        source.IsEmpty ? null : sourcePtr,
                        (nuint)source.Length,
                        &nativeOptionsV2,
                        &nativeResult);
                }
                else
                {
                    if (options.Normalization != FastParseNormalization.AutoSafe)
                    {
                        throw new FastParseException(0, 0, "native FastParse library does not support explicit normalization options");
                    }

                    status = _parse(
                        source.IsEmpty ? null : sourcePtr,
                        (nuint)source.Length,
                        &nativeOptions,
                        &nativeResult);
                }
            }

            if (status != 0 || nativeResult.Status != 0)
            {
                var message = NativeString(nativeResult.ErrorMessage);
                throw new FastParseException(status, nativeResult.Status, string.IsNullOrWhiteSpace(message) ? "no error detail" : message);
            }

            var outputLength = nativeResult.Length;
            var data = Array.Empty<byte>();
            if (copyData && nativeResult.Data != null && outputLength > 0)
            {
                if (outputLength > int.MaxValue)
                {
                    throw new FastParseException(status, nativeResult.Status, "native output is too large for a managed byte array");
                }

                data = new byte[(int)outputLength];
                Marshal.Copy((nint)nativeResult.Data, data, 0, data.Length);
            }

            return (data, (ulong)nativeResult.NodeCount, options.Format, (ulong)outputLength);
        }
        finally
        {
            _resultFree(&nativeResult);
            FreeUtf8(language);
            FreeUtf8(includeRules);
        }
    }

    private (byte[] Data, ulong CaptureCount, FastParseFormat Format, ulong OutputLength) QueryNative(
        ReadOnlySpan<byte> source,
        ReadOnlySpan<byte> query,
        QueryOptions options,
        bool copyData)
    {
        EnsureNotDisposed();

        var language = StringToUtf8(options.Language);
        var nativeOptions = new NativeQueryOptions
        {
            Language = language,
            Format = (int)options.Format,
            Fields = (uint)options.Fields,
            MaxMatches = options.MaxMatches,
            MaxCaptures = options.MaxCaptures,
            IncludePattern = options.IncludePattern ? 1 : 0,
            Pretty = options.Pretty ? 1 : 0,
            Normalization = (int)options.Normalization
        };

        NativeResult nativeResult = default;
        int status;

        try
        {
            fixed (byte* sourcePtr = source)
            fixed (byte* queryPtr = query)
            {
                status = _query(
                    source.IsEmpty ? null : sourcePtr,
                    (nuint)source.Length,
                    query.IsEmpty ? null : queryPtr,
                    (nuint)query.Length,
                    &nativeOptions,
                    &nativeResult);
            }

            if (status != 0 || nativeResult.Status != 0)
            {
                var message = NativeString(nativeResult.ErrorMessage);
                throw new FastParseException(status, nativeResult.Status, string.IsNullOrWhiteSpace(message) ? "no error detail" : message);
            }

            var outputLength = nativeResult.Length;
            var data = Array.Empty<byte>();
            if (copyData && nativeResult.Data != null && outputLength > 0)
            {
                if (outputLength > int.MaxValue)
                {
                    throw new FastParseException(status, nativeResult.Status, "native output is too large for a managed byte array");
                }

                data = new byte[(int)outputLength];
                Marshal.Copy((nint)nativeResult.Data, data, 0, data.Length);
            }

            return (data, (ulong)nativeResult.NodeCount, options.Format, (ulong)outputLength);
        }
        finally
        {
            _resultFree(&nativeResult);
            FreeUtf8(language);
        }
    }

    private T LoadFunction<T>(string preferredName, string fallbackName)
        where T : Delegate
    {
        if (!NativeLibrary.TryGetExport(_library, preferredName, out var symbol))
        {
            symbol = NativeLibrary.GetExport(_library, fallbackName);
        }

        return Marshal.GetDelegateForFunctionPointer<T>(symbol);
    }

    private T? TryLoadFunction<T>(string preferredName, string fallbackName)
        where T : Delegate
    {
        if (!NativeLibrary.TryGetExport(_library, preferredName, out var symbol) &&
            !NativeLibrary.TryGetExport(_library, fallbackName, out symbol))
        {
            return null;
        }

        return Marshal.GetDelegateForFunctionPointer<T>(symbol);
    }

    private T LoadRequiredFunction<T>(string name)
        where T : Delegate
    {
        var symbol = NativeLibrary.GetExport(_library, name);
        return Marshal.GetDelegateForFunctionPointer<T>(symbol);
    }

    private void EnsureNotDisposed()
    {
        if (_disposed)
        {
            throw new ObjectDisposedException(nameof(FastParseClient));
        }
    }

    private static nint StringToUtf8(string? value)
    {
        return string.IsNullOrEmpty(value)
            ? 0
            : Marshal.StringToCoTaskMemUTF8(value);
    }

    private static void FreeUtf8(nint value)
    {
        if (value != 0)
        {
            Marshal.FreeCoTaskMem(value);
        }
    }

    private static string NativeString(byte* value)
    {
        return value == null ? string.Empty : Marshal.PtrToStringUTF8((nint)value) ?? string.Empty;
    }

    private static (nint Handle, string LoadedFrom) LoadNativeLibrary(string? libraryPath)
    {
        var candidates = libraryPath is null
            ? DefaultLibraryCandidates()
            : new[] { libraryPath };
        var errors = new List<string>();

        foreach (var candidate in candidates.Distinct())
        {
            if (string.IsNullOrWhiteSpace(candidate))
            {
                continue;
            }

            try
            {
                var handle = NativeLibrary.Load(
                    candidate,
                    typeof(FastParseClient).Assembly,
                    DllImportSearchPath.AssemblyDirectory | DllImportSearchPath.SafeDirectories);
                return (handle, candidate);
            }
            catch (Exception ex) when (ex is DllNotFoundException or BadImageFormatException)
            {
                errors.Add($"{candidate}: {ex.GetType().Name}: {ex.Message.Split('\n')[0]}");
            }
        }

        var message = new StringBuilder()
            .AppendLine("Unable to load the native FastParse library.")
            .AppendLine($"OS: {RuntimeInformation.OSDescription}")
            .AppendLine($"Architecture: {RuntimeInformation.ProcessArchitecture}")
            .AppendLine($"AppContext.BaseDirectory: {AppContext.BaseDirectory}")
            .AppendLine("Tried:")
            .AppendLine(string.Join(Environment.NewLine, errors.Select(error => $"  - {error}")))
            .ToString();
        throw new DllNotFoundException(message);
    }

    private static IEnumerable<string> DefaultLibraryCandidates()
    {
        var explicitPath =
            Environment.GetEnvironmentVariable("FASTPARSE_LIBRARY_PATH") ??
            Environment.GetEnvironmentVariable("TSMP_LIBRARY_PATH");
        if (!string.IsNullOrWhiteSpace(explicitPath))
        {
            yield return explicitPath;
            yield break;
        }

        var fileName = NativeFileName();
        var rid = RuntimeIdentifier();
        yield return "fastparse";
        yield return fileName;

        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            var directCandidate = Path.Combine(directory.FullName, fileName);
            if (File.Exists(directCandidate))
            {
                yield return directCandidate;
            }

            var candidate = Path.Combine(directory.FullName, "bin", fileName);
            if (File.Exists(candidate))
            {
                yield return candidate;
            }

            var ridCandidate = Path.Combine(directory.FullName, "runtimes", rid, "native", fileName);
            if (File.Exists(ridCandidate))
            {
                yield return ridCandidate;
            }

            directory = directory.Parent;
        }
    }

    private static string NativeFileName()
    {
        return OperatingSystem.IsMacOS()
            ? "libfastparse.dylib"
            : OperatingSystem.IsWindows()
                ? "fastparse.dll"
                : "libfastparse.so";
    }

    private static string LanguageExtensionFileName(string language)
    {
        var canonical = CanonicalLanguageName(language);
        return OperatingSystem.IsMacOS()
            ? $"libfastparse_language_{canonical}.dylib"
            : OperatingSystem.IsWindows()
                ? $"fastparse_language_{canonical}.dll"
                : $"libfastparse_language_{canonical}.so";
    }

    private static string RuntimeIdentifier()
    {
        var platform = OperatingSystem.IsMacOS()
            ? "osx"
            : OperatingSystem.IsWindows()
                ? "win"
                : "linux";
        var arch = RuntimeInformation.ProcessArchitecture switch
        {
            Architecture.Arm64 => "arm64",
            Architecture.X64 => "x64",
            _ => RuntimeInformation.ProcessArchitecture.ToString().ToLowerInvariant()
        };
        return $"{platform}-{arch}";
    }

    private static IEnumerable<string> BundledLanguageExtensionCandidates(string language)
    {
        var canonical = CanonicalLanguageName(language);
        var envName = $"FASTPARSE_LANGUAGE_{canonical.ToUpperInvariant()}_PATH";
        var explicitPath = Environment.GetEnvironmentVariable(envName);
        if (!string.IsNullOrWhiteSpace(explicitPath))
        {
            yield return explicitPath;
            yield break;
        }

        var fileName = LanguageExtensionFileName(canonical);
        var rid = RuntimeIdentifier();
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            yield return Path.Combine(directory.FullName, "runtimes", rid, "native", fileName);
            yield return Path.Combine(directory.FullName, "fastparse", "languages", canonical, "native", rid, fileName);
            yield return Path.Combine(directory.FullName, "fastparse", "languages", canonical, "runtimes", rid, "native", fileName);
            yield return Path.Combine(directory.FullName, fileName);
            directory = directory.Parent;
        }
    }

    private static string CanonicalLanguageName(string language)
    {
        var canonical = language.Trim().ToLowerInvariant().Replace("-", "_");
        if (string.IsNullOrWhiteSpace(canonical))
        {
            throw new ArgumentException("Language is required.", nameof(language));
        }

        return canonical;
    }

    private static string ToPackageLanguageName(string language)
    {
        var canonical = CanonicalLanguageName(language);
        if (canonical == "javaswing")
        {
            return "JavaSwing";
        }

        return string.Join('.', canonical.Split('_', StringSplitOptions.RemoveEmptyEntries).Select(part => char.ToUpperInvariant(part[0]) + part[1..]));
    }

    [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
    private delegate byte* VersionDelegate();

    [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
    private delegate int ParseDelegate(
        byte* source,
        nuint sourceLen,
        NativeOptions* options,
        NativeResult* result);

    [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
    private delegate int ParseV2Delegate(
        byte* source,
        nuint sourceLen,
        NativeOptionsV2* options,
        NativeResult* result);

    [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
    private delegate int QueryDelegate(
        byte* source,
        nuint sourceLen,
        byte* query,
        nuint queryLen,
        NativeQueryOptions* options,
        NativeResult* result);

    [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
    private delegate void ResultFreeDelegate(NativeResult* result);

    [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
    private delegate int LoadLanguageExtensionDelegate(byte* path, NativeLanguageLoadResult* result);

    [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
    private delegate int LanguageAvailableDelegate(byte* language);

    [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
    private delegate void LanguageLoadResultFreeDelegate(NativeLanguageLoadResult* result);

    [StructLayout(LayoutKind.Sequential)]
    private struct NativeOptions
    {
        public nint Language;
        public int Format;
        public nint IncludeRules;
        public uint Fields;
        public int IncludeTokens;
        public int Pretty;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct NativeOptionsV2
    {
        public nint Language;
        public int Format;
        public nint IncludeRules;
        public uint Fields;
        public int IncludeTokens;
        public int Pretty;
        public int Normalization;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct NativeQueryOptions
    {
        public nint Language;
        public int Format;
        public uint Fields;
        public nuint MaxMatches;
        public nuint MaxCaptures;
        public int IncludePattern;
        public int Pretty;
        public int Normalization;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct NativeResult
    {
        public int Status;
        public byte* Data;
        public nuint Length;
        public nuint NodeCount;
        public byte* ErrorMessage;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct NativeLanguageLoadResult
    {
        public int Status;
        public byte* Language;
        public byte* DisplayName;
        public byte* ErrorMessage;
    }
}
