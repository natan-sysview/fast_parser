const { FastParseClient, OutputFormat } = require("@natan-sysview/fastparse");

const parser = new FastParseClient();
const source = "class Demo { void run() { System.out.println(\"ok\"); } }";

const json = parser.parseText(source).json();
console.log("Language:", json.language);
console.log("Nodes:", json.nodeCount);

const query = parser.queryText(
  source,
  "(method_declaration name: (identifier) @method.name) @method",
  { fields: ["capture_name", "rule", "text", "range", "byte_range"] }
).json();
console.log("Captures:", query.captureCount);

const binary = parser.parseText(source, { outputFormat: OutputFormat.Binary }).binaryDocument();
console.log("Binary schema:", binary.schemaVersion);
