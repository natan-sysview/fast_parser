namespace FastParse;

/// <summary>
/// Exception thrown when the native FastParse call fails.
/// </summary>
public sealed class FastParseException : Exception
{
    /// <summary>
    /// Creates a native parse exception.
    /// </summary>
    /// <param name="status">Status returned by the exported C function.</param>
    /// <param name="nativeStatus">Status stored in the native result.</param>
    /// <param name="message">Native error detail.</param>
    public FastParseException(int status, int nativeStatus, string message)
        : base($"FastParse failed with status {status}/{nativeStatus}: {message}")
    {
        Status = status;
        NativeStatus = nativeStatus;
    }

    /// <summary>Status returned by the exported C function.</summary>
    public int Status { get; }

    /// <summary>Status stored in the native result.</summary>
    public int NativeStatus { get; }
}
