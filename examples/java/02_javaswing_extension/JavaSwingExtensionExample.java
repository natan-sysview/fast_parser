import dev.fastparse.FastParseClient;
import dev.fastparse.LanguageExtensionLoadResult;
import dev.fastparse.ParseOptions;
import dev.fastparse.ParseResult;

import java.io.File;

/**
 * Standalone Java 8+ example for the Windows JavaSwing distribution kit.
 * Run it from the kit root through run-example.bat.
 */
public final class JavaSwingExtensionExample {
    public static void main(String[] args) {
        String extensionPath = args.length > 0
                ? args[0]
                : "extensions" + File.separator + "javaswing" + File.separator
                        + "native" + File.separator + "win-x64" + File.separator
                        + "fastparse_language_javaswing.dll";

        String source = "import javax.swing.JButton;\n"
                + "import javax.swing.JFrame;\n"
                + "class SwingApp {\n"
                + "  void showUi() {\n"
                + "    JFrame frame = new JFrame(\"FastParse\");\n"
                + "    frame.add(new JButton(\"Run\"));\n"
                + "    frame.pack();\n"
                + "  }\n"
                + "}\n";

        try (FastParseClient client = FastParseClient.open()) {
            LanguageExtensionLoadResult extension = client.loadLanguageExtension(extensionPath);
            if (!"javaswing".equals(extension.getLanguage())) {
                throw new IllegalStateException("Expected the javaswing extension, got: " + extension.getLanguage());
            }
            if (!client.languageAvailable("javaswing")) {
                throw new IllegalStateException("The javaswing grammar was not registered");
            }

            ParseResult result = client.parseText(source, ParseOptions.builder()
                    .language("javaswing")
                    .pretty(true)
                    .build());

            System.out.println("FastParse version: " + client.version());
            System.out.println("Native core: " + client.loadedCorePath());
            System.out.println("Extension: " + extension.getDisplayName());
            System.out.println("AST nodes: " + result.getNodeCount());
            System.out.println(result.asUtf8String());
        }
    }
}
