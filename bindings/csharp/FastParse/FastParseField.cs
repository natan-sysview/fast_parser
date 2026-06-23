namespace FastParse;

/// <summary>
/// Field flags that control which AST fields FastParse includes in the output.
/// </summary>
[Flags]
public enum FastParseField : uint
{
    /// <summary>Use the native default field set.</summary>
    DefaultAll = 0,

    /// <summary>Include the node id.</summary>
    Id = 1u << 0,

    /// <summary>Include the parent node id.</summary>
    ParentId = 1u << 1,

    /// <summary>Include the Tree-sitter grammar rule name.</summary>
    Rule = 1u << 2,

    /// <summary>Include the original source bytes/text for the node.</summary>
    Text = 1u << 3,

    /// <summary>Include start/end line and column positions.</summary>
    Range = 1u << 4,

    /// <summary>Include start/end byte offsets.</summary>
    ByteRange = 1u << 5,

    /// <summary>Include the number of child nodes.</summary>
    ChildCount = 1u << 6,

    /// <summary>Include child rule/text summaries when supported by the output format.</summary>
    Children = 1u << 7,

    /// <summary>Include Tree-sitter parse diagnostic fields such as isError, isMissing, and hasError.</summary>
    Diagnostics = 1u << 8,

    /// <summary>Request all supported fields.</summary>
    All = 0xFFFFFFFFu
}
