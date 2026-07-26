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

    /// <summary>Include the Tree-sitter query capture name, for example method.name.</summary>
    CaptureName = 1u << 9,

    /// <summary>Include the matched Tree-sitter query pattern index.</summary>
    PatternIndex = 1u << 10,

    /// <summary>Include the Tree-sitter field name connecting the node to its direct parent.</summary>
    FieldName = 1u << 11,

    /// <summary>Include the zero-based Tree-sitter child index within the direct parent.</summary>
    ChildIndex = 1u << 12,

    /// <summary>Include whether the node is named by the Tree-sitter grammar.</summary>
    Named = 1u << 13,

    /// <summary>Include the zero-based node depth, where the root is depth zero.</summary>
    Depth = 1u << 14,

    /// <summary>Request all supported fields.</summary>
    All = 0xFFFFFFFFu
}
