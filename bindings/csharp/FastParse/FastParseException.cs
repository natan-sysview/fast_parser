namespace FastParse;

public sealed class FastParseException : Exception
{
    public FastParseException(int status, int nativeStatus, string message)
        : base($"FastParse failed with status {status}/{nativeStatus}: {message}")
    {
        Status = status;
        NativeStatus = nativeStatus;
    }

    public int Status { get; }

    public int NativeStatus { get; }
}
