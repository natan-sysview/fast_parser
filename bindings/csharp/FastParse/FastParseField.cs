namespace FastParse;

[Flags]
public enum FastParseField : uint
{
    DefaultAll = 0,
    Id = 1u << 0,
    ParentId = 1u << 1,
    Rule = 1u << 2,
    Text = 1u << 3,
    Range = 1u << 4,
    ByteRange = 1u << 5,
    ChildCount = 1u << 6,
    Children = 1u << 7,
    All = 0xFFFFFFFFu
}
