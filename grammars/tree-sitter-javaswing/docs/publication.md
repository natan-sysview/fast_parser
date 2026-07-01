# Publication Plan

This grammar was developed inside a private parser lab. The public repository must receive only the grammar payload, not local evidence or private source-derived artifacts.

## Public Payload

Copy these paths to the standalone public repository:

- `.editorconfig`
- `.gitattributes`
- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`
- `.github/workflows/npm-publish.yml`
- `.github/ISSUE_TEMPLATE/`
- `.gitignore`
- `.npmignore`
- `LICENSE`
- `README.md`
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `grammar.js`
- `package.json`
- `package-lock.json`
- `tree-sitter.json`
- `scripts/check-release.mjs`
- `scripts/demo.mjs`
- `scripts/smoke-parse.mjs`
- `scripts/check-queries.mjs`
- `examples/`
- `docs/demo.md`
- `docs/dependency-policy.md`
- `docs/nodes.md`
- `docs/parser-list.md`
- `docs/publication.md`
- `docs/releases/`
- `queries/`
- `src/`
- `test/corpus/`

Copy `docs/rule-catalogs/` only after a privacy pass removes private paths, project names, and source-derived snippets.

Do not copy:

- `audits/`
- `baselines/`
- `runs/`
- `diagnostics/`
- `tools/`
- validation databases
- MessagePack dumps
- local inventory files
- private source snippets, paths, project names, or generated reports derived from client source
- unsanitized rule catalogs

## Repository Metadata

Current public repository:

```text
https://github.com/natan-sysview/tree-sitter-javaswing
```

Before each release:

1. Confirm `tree-sitter.json` metadata links point to the public repository.
2. Confirm `package.json` repository, bugs, and homepage point to the public repository.
3. Keep version values aligned between `tree-sitter.json` and `package.json`.
4. Confirm `CHANGELOG.md` and `docs/releases/` match the intended tag.
5. Confirm `docs/parser-list.md` has public commit and release details.
6. Run the CI workflow on the public repository.

Inside the private parser lab, this can be prepared with:

```sh
python3 tools/prepare_public_repository.py /path/to/tree-sitter-javaswing \
  --repo-url https://github.com/OWNER/tree-sitter-javaswing \
  --author-name "PUBLIC MAINTAINER" \
  --author-email maintainer@example.com \
  --force \
  --validate
```

The script copies only the whitelisted payload, updates repository metadata in the destination, runs the privacy scan, and runs the npm validation gates.

Before preparing the public repository, the lab can run:

```sh
python3 tools/check_public_release_readiness.py
```

After preparing a public clone, the same check runs in strict mode through `tools/prepare_public_repository.py --validate`.

The public repository CI also runs:

```sh
npm run metadata:check:public
```

The public repository also includes:

- `.github/workflows/release.yml`: validates tag pushes and creates or updates a GitHub pre-release from `docs/releases/`.
- `.github/workflows/npm-publish.yml`: manually publishes npm packages after maintainers configure npm credentials.

## Validation Gates

Before tagging a release:

```sh
npm ci
npm run ci:check
```

Then inspect the tarball output from `npm pack --dry-run` and confirm it does not include private lab paths or artifacts.

Also review `CONTRIBUTING.md`, `SECURITY.md`, `.github/pull_request_template.md`, and `.github/ISSUE_TEMPLATE/` to confirm they ask for synthetic minimized examples instead of private source.

## Release Steps

For the first alpha:

```sh
git tag -a v0.1.0-alpha.1 -m "v0.1.0-alpha.1"
git push origin v0.1.0-alpha.1
```

Tag pushes run the release workflow. The workflow validates the package and creates or updates a GitHub pre-release from `docs/releases/0.1.0-alpha.md`.

If npm trusted publishing is configured, publish with an alpha tag from the manual `Publish npm` workflow.

Repository maintainers should configure npm Trusted Publisher for:

- Owner: `natan-sysview`
- Repository: `tree-sitter-javaswing`
- Workflow filename: `npm-publish.yml`
- Allowed action: `npm publish`

The workflow uses GitHub Actions OIDC (`id-token: write`), Node 24, latest npm, and `npm publish --provenance --access public`.

Manual local publish remains possible:

```sh
npm publish --tag alpha
```

Do not publish npm packages from a dirty worktree or before the GitHub CI is green.

## Private Evidence Policy

Private inventory validation can be mentioned only as aggregate metrics, for example:

- total files parsed;
- number of parse failures;
- total `ERROR` and `MISSING` nodes;
- number of normalized inputs.

Do not publish raw file paths, snippets, hashes, SQLite databases, audit CSVs, or source-derived samples from private inventories.
