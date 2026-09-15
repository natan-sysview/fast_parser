import dev.fastparse.FastParseClient;
import dev.fastparse.FastParseField;
import dev.fastparse.ParseOptions;
import dev.fastparse.ParseResult;

public class ParseStringExample {
    public static void main(String[] args) {
        String core = args.length > 0 ? args[0] : null;
        String jni = args.length > 1 ? args[1] : null;
        try (FastParseClient client = core == null ? FastParseClient.open() : FastParseClient.open(core, jni)) {
            String source = "class Hello { void run() { System.out.println(\"hi\"); } }";
            ParseOptions options = ParseOptions.builder()
                    .language("java")
                    .fields(FastParseField.ALL)
                    .build();
            ParseResult result = client.parseText(source, options);
            System.out.println("FastParse version: " + client.version());
            System.out.println("Node count: " + result.getNodeCount());
            System.out.println("JSON bytes: " + result.getLength());
            System.out.println(result.asUtf8String());
        }
    }
}
