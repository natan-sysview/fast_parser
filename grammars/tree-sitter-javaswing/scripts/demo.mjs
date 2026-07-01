import { spawnSync } from "node:child_process";

const treeSitter = "tree-sitter";
const example = "examples/swing-showcase.java";

function run(args) {
  const result = spawnSync(treeSitter, args, {
    stdio: "inherit",
    shell: process.platform === "win32",
  });
  if (result.error) {
    console.error(result.error);
  }
  if (result.status !== 0) {
    process.exit(result.status ?? 1);
  }
}

console.log(`Parsing ${example}`);
run(["parse", example]);

console.log("\nSwing query captures");
run(["query", "queries/swing.scm", example]);
