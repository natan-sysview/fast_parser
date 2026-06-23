namespace FastParse;

/// <summary>
/// Output format produced by the native FastParse parser.
/// </summary>
public enum FastParseFormat
{
    /// <summary>Structured JSON AST output.</summary>
    Json = 1,

    /// <summary>Flat CSV rows for tabular pipelines.</summary>
    Csv = 2,

    /// <summary>Count nodes without copying output bytes.</summary>
    Stats = 3,

    /// <summary>Binary MessagePack AST output.</summary>
    Binary = 4
}
