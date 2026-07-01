import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const strictPublic = process.argv.includes("--strict-public");

const requiredFiles = [
  "grammar.js",
  "tree-sitter.json",
  "package.json",
  "package-lock.json",
  "README.md",
  "CHANGELOG.md",
  "CONTRIBUTING.md",
  "SECURITY.md",
  "LICENSE",
  ".github/workflows/ci.yml",
  ".github/workflows/release.yml",
  ".github/workflows/npm-publish.yml",
  ".github/dependabot.yml",
  ".github/pull_request_template.md",
  "scripts/check-release.mjs",
  "scripts/demo.mjs",
  "scripts/smoke-parse.mjs",
  "scripts/check-queries.mjs",
  "examples/README.md",
  "examples/swing-showcase.java",
  "docs/demo.md",
  "docs/dependency-policy.md",
  "queries/highlights.scm",
  "queries/tags.scm",
  "queries/swing.scm",
  "src/parser.c",
  "src/grammar.json",
  "src/node-types.json",
  "src/tree_sitter/parser.h",
  "docs/nodes.md",
  "docs/parser-list.md",
  "docs/publication.md",
  "docs/releases/0.1.0-alpha.md",
];

function readJson(relativePath) {
  return JSON.parse(fs.readFileSync(path.join(root, relativePath), "utf8"));
}

function fileText(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

const errors = [];

for (const relativePath of requiredFiles) {
  if (!fs.existsSync(path.join(root, relativePath))) {
    errors.push(`missing required file: ${relativePath}`);
  }
}

if (errors.length === 0) {
  const packageJson = readJson("package.json");
  const packageLock = readJson("package-lock.json");
  const treeSitter = readJson("tree-sitter.json");
  const parserC = fileText("src/parser.c");
  const parserList = fileText("docs/parser-list.md");
  const dependabot = fileText(".github/dependabot.yml");

  const grammar = treeSitter.grammars?.[0] ?? {};
  const metadata = treeSitter.metadata ?? {};
  const links = metadata.links ?? {};
  const rootLock = packageLock.packages?.[""] ?? {};
  const bindings = treeSitter.bindings ?? {};
  const abiMatch = parserC.match(/#define\s+LANGUAGE_VERSION\s+(\d+)/);
  const abiVersion = abiMatch ? Number(abiMatch[1]) : null;

  if (packageJson.name !== "tree-sitter-javaswing") {
    errors.push("package.json name must be tree-sitter-javaswing");
  }
  if (grammar.name !== "javaswing") {
    errors.push("tree-sitter.json grammar name must be javaswing");
  }
  if (grammar.scope !== "source.javaswing") {
    errors.push("tree-sitter.json scope must be source.javaswing");
  }
  if (!grammar["file-types"]?.includes("java")) {
    errors.push("tree-sitter.json file-types must include java");
  }
  if (metadata.version !== packageJson.version) {
    errors.push("tree-sitter.json metadata.version must match package.json version");
  }
  if (rootLock.name !== packageJson.name || rootLock.version !== packageJson.version) {
    errors.push("package-lock root package must match package.json name and version");
  }
  if (packageJson.devDependencies?.["tree-sitter-cli"] !== "0.25.10") {
    errors.push("tree-sitter-cli must be pinned exactly to 0.25.10");
  }
  if (rootLock.devDependencies?.["tree-sitter-cli"] !== "0.25.10") {
    errors.push("package-lock root tree-sitter-cli dependency must be pinned exactly to 0.25.10");
  }
  if (!dependabot.includes('dependency-name: "tree-sitter-cli"')) {
    errors.push("Dependabot must ignore automated tree-sitter-cli upgrades");
  }
  if (bindings.c !== true) {
    errors.push("tree-sitter.json must advertise the C binding");
  }
  for (const binding of ["go", "node", "python", "rust", "swift"]) {
    if (bindings[binding] !== false) {
      errors.push(`tree-sitter.json must not advertise unavailable ${binding} binding`);
    }
  }
  if (!links.upstream) {
    errors.push("tree-sitter.json metadata.links.upstream is required");
  }
  if (abiVersion !== 15) {
    errors.push(`src/parser.c LANGUAGE_VERSION must be 15, found ${abiVersion}`);
  }
  if (!parserList.includes(`ABI version: \`${abiVersion}\``)) {
    errors.push("docs/parser-list.md must document the generated parser ABI version");
  }
  if (strictPublic) {
    if (!links.repository) {
      errors.push("tree-sitter.json metadata.links.repository is required in strict public mode");
    }
    if (!packageJson.repository?.url) {
      errors.push("package.json repository.url is required in strict public mode");
    }
    if (!packageJson.bugs?.url) {
      errors.push("package.json bugs.url is required in strict public mode");
    }
    if (!packageJson.homepage) {
      errors.push("package.json homepage is required in strict public mode");
    }
    if (links.repository && packageJson.repository?.url && !packageJson.repository.url.includes(links.repository.replace(/\/$/, ""))) {
      errors.push("package.json repository.url must point to the tree-sitter.json repository");
    }
  }
}

if (errors.length > 0) {
  for (const error of errors) {
    console.error(`- ${error}`);
  }
  process.exit(1);
}

console.log(strictPublic ? "public metadata check: ok" : "metadata check: ok");
