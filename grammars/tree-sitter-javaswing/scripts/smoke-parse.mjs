import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";

const source = [
  "import javax.swing.*;",
  "class Smoke extends JFrame {",
  "  private final JButton saveButton = new JButton(\"Save\");",
  "  Smoke() {",
  "    setLayout(new java.awt.BorderLayout());",
  "    saveButton.addActionListener(event -> setVisible(false));",
  "    add(saveButton, java.awt.BorderLayout.SOUTH);",
  "    javax.swing.SwingUtilities.invokeLater(() -> setVisible(true));",
  "  }",
  "}",
  "",
].join("\n");

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "javaswing-parse-"));
const file = path.join(tmp, "Smoke.java");

try {
  fs.writeFileSync(file, source, "utf8");
  const treeSitter = "tree-sitter";
  const result = spawnSync(treeSitter, ["parse", "--quiet", file], {
    stdio: "inherit",
    shell: process.platform === "win32",
  });
  if (result.error) {
    console.error(result.error);
  }
  process.exitCode = result.status ?? 1;
} finally {
  fs.rmSync(tmp, { recursive: true, force: true });
}
