using System.Buffers.Binary;
using System.Text;

namespace FastParse;

public static class FastParseMessagePack
{
    public static FastParseBinaryDocument Decode(ReadOnlySpan<byte> data)
    {
        var reader = new Reader(data);
        var document = reader.ReadDocument();
        if (!reader.End)
        {
            throw new FormatException("Trailing MessagePack bytes.");
        }

        return document;
    }

    private ref struct Reader
    {
        private readonly ReadOnlySpan<byte> _data;
        private int _index;

        public Reader(ReadOnlySpan<byte> data)
        {
            _data = data;
            _index = 0;
        }

        public bool End => _index == _data.Length;

        public FastParseBinaryDocument ReadDocument()
        {
            var count = ReadMapLength();
            var format = string.Empty;
            var schemaVersion = 0UL;
            var language = string.Empty;
            IReadOnlyList<FastParseBinaryNode> nodes = Array.Empty<FastParseBinaryNode>();
            var nodeCount = 0UL;

            for (var i = 0; i < count; i++)
            {
                var key = ReadString();
                switch (key)
                {
                    case "format":
                        format = ReadString();
                        break;
                    case "schemaVersion":
                        schemaVersion = ReadUInt();
                        break;
                    case "language":
                        language = ReadString();
                        break;
                    case "nodes":
                        nodes = ReadNodes();
                        break;
                    case "nodeCount":
                        nodeCount = ReadUInt();
                        break;
                    default:
                        Skip();
                        break;
                }
            }

            return new FastParseBinaryDocument
            {
                Format = format,
                SchemaVersion = schemaVersion,
                Language = language,
                Nodes = nodes,
                NodeCount = nodeCount
            };
        }

        private IReadOnlyList<FastParseBinaryNode> ReadNodes()
        {
            var count = ReadArrayLength();
            var nodes = new FastParseBinaryNode[count];
            for (var i = 0; i < count; i++)
            {
                nodes[i] = ReadNode();
            }

            return nodes;
        }

        private FastParseBinaryNode ReadNode()
        {
            var count = ReadMapLength();
            ulong? id = null;
            ulong? parentId = null;
            string? rule = null;
            byte[]? text = null;
            ulong? startLine = null;
            ulong? startColumn = null;
            ulong? endLine = null;
            ulong? endColumn = null;
            ulong? startByte = null;
            ulong? endByte = null;
            ulong? childCount = null;
            IReadOnlyList<FastParseBinaryChild> children = Array.Empty<FastParseBinaryChild>();

            for (var i = 0; i < count; i++)
            {
                var key = ReadString();
                switch (key)
                {
                    case "id":
                        id = ReadUInt();
                        break;
                    case "parentId":
                        parentId = TryReadNil() ? null : ReadUIntAfterPeek();
                        break;
                    case "rule":
                        rule = ReadString();
                        break;
                    case "text":
                        text = ReadBin();
                        break;
                    case "startLine":
                        startLine = ReadUInt();
                        break;
                    case "startColumn":
                        startColumn = ReadUInt();
                        break;
                    case "endLine":
                        endLine = ReadUInt();
                        break;
                    case "endColumn":
                        endColumn = ReadUInt();
                        break;
                    case "startByte":
                        startByte = ReadUInt();
                        break;
                    case "endByte":
                        endByte = ReadUInt();
                        break;
                    case "childCount":
                        childCount = ReadUInt();
                        break;
                    case "children":
                        children = ReadChildren();
                        break;
                    default:
                        Skip();
                        break;
                }
            }

            return new FastParseBinaryNode
            {
                Id = id,
                ParentId = parentId,
                Rule = rule,
                Text = text,
                StartLine = startLine,
                StartColumn = startColumn,
                EndLine = endLine,
                EndColumn = endColumn,
                StartByte = startByte,
                EndByte = endByte,
                ChildCount = childCount,
                Children = children
            };
        }

        private IReadOnlyList<FastParseBinaryChild> ReadChildren()
        {
            var count = ReadArrayLength();
            var children = new FastParseBinaryChild[count];
            for (var i = 0; i < count; i++)
            {
                children[i] = ReadChild();
            }

            return children;
        }

        private FastParseBinaryChild ReadChild()
        {
            var count = ReadMapLength();
            string? rule = null;
            byte[]? text = null;

            for (var i = 0; i < count; i++)
            {
                var key = ReadString();
                switch (key)
                {
                    case "rule":
                        rule = ReadString();
                        break;
                    case "text":
                        text = ReadBin();
                        break;
                    default:
                        Skip();
                        break;
                }
            }

            return new FastParseBinaryChild
            {
                Rule = rule,
                Text = text
            };
        }

        private bool TryReadNil()
        {
            if (Peek() != 0xC0)
            {
                return false;
            }

            _index++;
            return true;
        }

        private ulong ReadUIntAfterPeek()
        {
            return ReadUInt();
        }

        private ulong ReadUInt()
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

        private string ReadString()
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

            var bytes = ReadBytes(length);
            return Encoding.UTF8.GetString(bytes);
        }

        private byte[] ReadBin()
        {
            var code = ReadByte();
            var length = code switch
            {
                0xC4 => ReadByte(),
                0xC5 => ReadUInt16(),
                0xC6 => checked((int)ReadUInt32()),
                _ => throw new FormatException($"Expected bin, got 0x{code:X2}.")
            };

            return ReadBytes(length).ToArray();
        }

        private int ReadMapLength()
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

        private int ReadArrayLength()
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

        private void Skip()
        {
            var code = Peek();
            if (code <= 0x7F || code == 0xC0 || code == 0xC2 || code == 0xC3)
            {
                _index++;
                return;
            }

            if (code >= 0xA0 && code <= 0xBF)
            {
                _index++;
                _index += code & 0x1F;
                return;
            }

            if (code >= 0x90 && code <= 0x9F)
            {
                _index++;
                var count = code & 0x0F;
                for (var i = 0; i < count; i++) Skip();
                return;
            }

            if (code >= 0x80 && code <= 0x8F)
            {
                _index++;
                var count = code & 0x0F;
                for (var i = 0; i < count * 2; i++) Skip();
                return;
            }

            _index++;
            switch (code)
            {
                case 0xCC:
                    _index += 1;
                    break;
                case 0xCD:
                    _index += 2;
                    break;
                case 0xCE:
                    _index += 4;
                    break;
                case 0xCF:
                    _index += 8;
                    break;
                case 0xC4:
                    _index += ReadByte();
                    break;
                case 0xC5:
                    _index += ReadUInt16();
                    break;
                case 0xC6:
                    _index += checked((int)ReadUInt32());
                    break;
                case 0xD9:
                    _index += ReadByte();
                    break;
                case 0xDA:
                    _index += ReadUInt16();
                    break;
                case 0xDB:
                    _index += checked((int)ReadUInt32());
                    break;
                case 0xDC:
                {
                    var count = ReadUInt16();
                    for (var i = 0; i < count; i++) Skip();
                    break;
                }
                case 0xDD:
                {
                    var count = checked((int)ReadUInt32());
                    for (var i = 0; i < count; i++) Skip();
                    break;
                }
                case 0xDE:
                {
                    var count = ReadUInt16();
                    for (var i = 0; i < count * 2; i++) Skip();
                    break;
                }
                case 0xDF:
                {
                    var count = checked((int)ReadUInt32());
                    for (var i = 0; i < count * 2; i++) Skip();
                    break;
                }
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
            var value = BinaryPrimitives.ReadUInt16BigEndian(ReadBytes(sizeof(ushort)));
            return value;
        }

        private uint ReadUInt32()
        {
            var value = BinaryPrimitives.ReadUInt32BigEndian(ReadBytes(sizeof(uint)));
            return value;
        }

        private ulong ReadUInt64()
        {
            var value = BinaryPrimitives.ReadUInt64BigEndian(ReadBytes(sizeof(ulong)));
            return value;
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
    }
}
