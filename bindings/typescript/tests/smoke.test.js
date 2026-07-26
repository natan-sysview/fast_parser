const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const {
  FastParseClient,
  Field,
  OutputFormat
} = require("../dist");

const source = "class Demo { void run() { System.out.println(\"ok\"); } }";

test("parse Java JSON", () => {
  const parser = new FastParseClient();
  const result = parser.parseText(source);
  const document = result.json();
  assert.equal(document.language, "java");
  assert.ok(result.nodeCount > 0);
});

test("parse Java binary and decode", () => {
  const parser = new FastParseClient();
  const result = parser.parseText(source, {
    outputFormat: OutputFormat.Binary,
    fields: Field.All
  });
  const document = result.binaryDocument();
  assert.equal(document.format, "tsmp-binary");
  assert.equal(document.schemaVersion, 1);
  assert.ok(document.nodeCount > 0);
});

test("parse Java structural relationships", () => {
  const parser = new FastParseClient();
  const result = parser.parseText(source, {
    outputFormat: OutputFormat.Binary,
    fields: [
      "id",
      "parent_id",
      "rule",
      "field_name",
      "child_index",
      "is_named",
      "depth"
    ]
  });
  const document = result.binaryDocument();
  const methodName = document.nodes.find(
    (node) => node.rule === "identifier" && node.fieldName === "name"
  );
  assert.ok(methodName);
  assert.ok(methodName.parentId);
  assert.equal(methodName.isNamed, true);
  assert.ok(methodName.depth > 0);
});

test("query Java captures", () => {
  const parser = new FastParseClient();
  const result = parser.queryText(
    source,
    "(method_declaration name: (identifier) @method.name) @method",
    {
      fields: ["capture_name", "rule", "text", "range", "byte_range", "pattern_index"]
    }
  );
  const document = result.json();
  assert.equal(document.language, "java");
  assert.ok(document.captureCount >= 2);
});

test("stats summary skips output copy", () => {
  const parser = new FastParseClient();
  const summary = parser.parseTextSummary(source, { outputFormat: "stats" });
  assert.equal(summary.outputLength, 0);
  assert.ok(summary.nodeCount > 0);
});

test("load JavaSwing extension by explicit path when available", (t) => {
  const extensionPath = path.resolve(__dirname, "../../../bin/libfastparse_language_javaswing.dylib");
  if (!fs.existsSync(extensionPath)) {
    t.skip("local JavaSwing extension native library is not built");
    return;
  }

  const parser = new FastParseClient();
  const load = parser.loadLanguageExtension(extensionPath);
  assert.equal(load.language, "javaswing");
  assert.equal(parser.languageAvailable("javaswing"), true);

  const ast = parser.parseText(
    "import javax.swing.JButton; class Demo { JButton button; }",
    { language: "javaswing" }
  ).json();
  assert.equal(ast.language, "javaswing");
  assert.ok(ast.nodeCount > 0);
});
