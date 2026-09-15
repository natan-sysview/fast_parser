package dev.fastparse;

public final class FastParseSmoke {
    private FastParseSmoke() {}

    public static void main(String[] args) {
        String core = args.length > 0 ? args[0] : null;
        String jni = args.length > 1 ? args[1] : null;
        try (FastParseClient client = core == null ? FastParseClient.open() : FastParseClient.open(core, jni)) {
            String source = "class Hello { void run() { System.out.println(\"hi\"); } }";
            ParseResult ast = client.parseText(source, ParseOptions.builder().build());
            ParseResult diagnostics = client.parseText(source, ParseOptions.builder().format(FastParseFormat.DIAGNOSTICS).build());
            ParseResult binary = client.parseText(source, ParseOptions.builder().format(FastParseFormat.BINARY).build());
            ParseResult query = client.queryText(source, "(method_declaration name: (identifier) @method.name)", QueryOptions.builder().build());

            String astText = ast.asUtf8String();
            String diagnosticsText = diagnostics.asUtf8String();
            String queryText = query.asUtf8String();

            if (!client.languageAvailable("java")) {
                throw new IllegalStateException("java language is not available");
            }
            if (ast.getNodeCount() <= 0 || ast.getLength() <= 0 || !astText.contains("method_declaration")) {
                throw new IllegalStateException("AST smoke failed");
            }
            if (!diagnosticsText.contains("\"hasErrors\":false")) {
                throw new IllegalStateException("diagnostics smoke failed: " + diagnosticsText);
            }
            if (binary.getFormat() != FastParseFormat.BINARY || binary.getLength() <= 0) {
                throw new IllegalStateException("binary smoke failed");
            }
            if (!queryText.contains("method.name") || !queryText.contains("run")) {
                throw new IllegalStateException("query smoke failed: " + queryText);
            }

            System.out.println("version=" + client.version());
            System.out.println("core=" + client.loadedCorePath());
            System.out.println("javaAvailable=" + client.languageAvailable("java"));
            System.out.println("astFormat=" + ast.getFormat());
            System.out.println("astNodes=" + ast.getNodeCount());
            System.out.println("astBytes=" + ast.getLength());
            System.out.println("diagnosticsBytes=" + diagnostics.getLength());
            System.out.println("binaryBytes=" + binary.getLength());
            System.out.println("queryCaptures=" + query.getNodeCount());
            System.out.println(astText.substring(0, Math.min(200, ast.getLength())));
        }
    }
}
