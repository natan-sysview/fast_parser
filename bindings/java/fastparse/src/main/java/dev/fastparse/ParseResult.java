package dev.fastparse;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;

/** FastParse output copied into JVM-owned memory. */
public final class ParseResult {
    private final byte[] data;
    private final long nodeCount;
    private final FastParseFormat format;

    ParseResult(byte[] data, long nodeCount, int nativeFormat) {
        this.data = data == null ? new byte[0] : data;
        this.nodeCount = nodeCount;
        this.format = formatFromNative(nativeFormat);
    }

    public byte[] getBytes() {
        return Arrays.copyOf(data, data.length);
    }

    public int getLength() { return data.length; }
    public long getNodeCount() { return nodeCount; }
    public FastParseFormat getFormat() { return format; }

    /** Decode textual formats as UTF-8. Do not call for BINARY MessagePack output. */
    public String asUtf8String() {
        return new String(data, StandardCharsets.UTF_8);
    }

    private static FastParseFormat formatFromNative(int value) {
        for (FastParseFormat format : FastParseFormat.values()) {
            if (format.nativeValue() == value) {
                return format;
            }
        }
        return FastParseFormat.JSON;
    }
}
