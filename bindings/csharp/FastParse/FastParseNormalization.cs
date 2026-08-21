namespace FastParse;

/// <summary>
/// Source normalization modes applied in native memory before Tree-sitter parses the source.
/// </summary>
public enum FastParseNormalization
{
    /// <summary>Apply safe language-specific legacy cleanup when FastParse knows it is appropriate.</summary>
    AutoSafe = 0,

    /// <summary>Do not alter source bytes before parsing.</summary>
    None = 1,

    /// <summary>Apply COBOL fixed-format legacy cleanup and conservative parser-view repairs.</summary>
    CobolFixedLegacy = 2
}
