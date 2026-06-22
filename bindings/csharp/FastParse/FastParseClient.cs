using System.Runtime.InteropServices;
using System.Text;

namespace FastParse;

public sealed unsafe class FastParseClient : IDisposable
{
    private readonly nint _library;
    private readonly VersionDelegate _version;
    private readonly ParseDelegate _parse;
    private readonly ResultFreeDelegate _resultFree;
    private bool _disposed;

    public FastParseClient(string? libraryPath = null)
    {
        LibraryPath = libraryPath ?? DefaultLibraryPath();
        _library = NativeLibrary.Load(
            LibraryPath,
            typeof(FastParseClient).Assembly,
            DllImportSearchPath.SafeDirectories);
        _version = LoadFunction<VersionDelegate>("fastparse_version", "tsmp_version");
        _parse = LoadFunction<ParseDelegate>("fastparse_parse", "tsmp_parse");
        _resultFree = LoadFunction<ResultFreeDelegate>("fastparse_result_free", "tsmp_result_free");
    }

    public string LibraryPath { get; }

    public string Version => Marshal.PtrToStringUTF8((nint)_version()) ?? string.Empty;

    public ParseResult ParseBytes(ReadOnlySpan<byte> source, ParseOptions? options = null)
    {
        var (data, nodeCount, format, _) = ParseNative(source, options ?? ParseOptions.JsonAll, copyData: true);
        return new ParseResult(data, nodeCount, format);
    }

    public ParseSummary ParseBytesSummary(ReadOnlySpan<byte> source, ParseOptions? options = null)
    {
        var (_, nodeCount, format, outputLength) = ParseNative(source, options ?? ParseOptions.JsonAll, copyData: false);
        return new ParseSummary(outputLength, nodeCount, format);
    }

    public ParseResult ParseText(string source, ParseOptions? options = null, Encoding? encoding = null)
    {
        encoding ??= Encoding.UTF8;
        return ParseBytes(encoding.GetBytes(source), options);
    }

    public ParseSummary ParseTextSummary(string source, ParseOptions? options = null, Encoding? encoding = null)
    {
        encoding ??= Encoding.UTF8;
        return ParseBytesSummary(encoding.GetBytes(source), options);
    }

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

        NativeResult nativeResult = default;
        int status;

        try
        {
            fixed (byte* sourcePtr = source)
            {
                status = _parse(
                    source.IsEmpty ? null : sourcePtr,
                    (nuint)source.Length,
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
            FreeUtf8(includeRules);
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

    private static string DefaultLibraryPath()
    {
        var explicitPath =
            Environment.GetEnvironmentVariable("FASTPARSE_LIBRARY_PATH") ??
            Environment.GetEnvironmentVariable("TSMP_LIBRARY_PATH");
        if (!string.IsNullOrWhiteSpace(explicitPath))
        {
            return explicitPath;
        }

        var fileName = OperatingSystem.IsMacOS()
            ? "libfastparse.dylib"
            : OperatingSystem.IsWindows()
                ? "fastparse.dll"
                : "libfastparse.so";

        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            var directCandidate = Path.Combine(directory.FullName, fileName);
            if (File.Exists(directCandidate))
            {
                return directCandidate;
            }

            var candidate = Path.Combine(directory.FullName, "bin", fileName);
            if (File.Exists(candidate))
            {
                return candidate;
            }

            directory = directory.Parent;
        }

        return fileName;
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
    private delegate void ResultFreeDelegate(NativeResult* result);

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
    private struct NativeResult
    {
        public int Status;
        public byte* Data;
        public nuint Length;
        public nuint NodeCount;
        public byte* ErrorMessage;
    }
}
