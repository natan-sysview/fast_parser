import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";

const source = [
  "import javax.swing.*;",
  "class Demo extends JPanel {",
  "  JButton button = new JButton(\"OK\");",
  "  void initComponents() {",
  "    button.addActionListener(e -> setVisible(true));",
  "    setLayout(new java.awt.BorderLayout());",
  "    add(button, java.awt.BorderLayout.CENTER);",
  "  }",
  "}",
  "",
].join("\n");

const queries = [
  "queries/highlights.scm",
  "queries/tags.scm",
  "queries/swing.scm",
];

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "javaswing-query-"));
const file = path.join(tmp, "Demo.java");
const treeSitter = "tree-sitter";

try {
  fs.writeFileSync(file, source, "utf8");
  for (const query of queries) {
    const result = spawnSync(treeSitter, ["query", "--quiet", query, file], {
      stdio: "inherit",
      shell: process.platform === "win32",
    });
    if (result.error) {
      console.error(result.error);
    }
    if (result.status !== 0) {
      process.exitCode = result.status ?? 1;
      break;
    }
  }
} finally {
  fs.rmSync(tmp, { recursive: true, force: true });
}
