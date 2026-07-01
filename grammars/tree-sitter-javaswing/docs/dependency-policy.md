# Dependency Policy

This grammar keeps parser generation reproducible by pinning `tree-sitter-cli` exactly.

Do not merge automated `tree-sitter-cli` upgrades as ordinary dependency bumps. A CLI upgrade can change generated parser artifacts, ABI behavior, parse tables, query behavior, or package contents even when `grammar.js` does not change.

## tree-sitter-cli Upgrade Process

Use this process for deliberate CLI upgrades:

1. Update `tree-sitter-cli` in `package.json` and `package-lock.json`.
2. Run `npm ci`.
3. Run `npm run generate`.
4. Review generated diffs in:
   - `src/parser.c`
   - `src/grammar.json`
   - `src/node-types.json`
5. Run `npm run ci:check`.
6. Run a fresh clone validation after pushing.
7. Document the CLI upgrade in `CHANGELOG.md`.
8. Confirm the release workflow and tag CI are green before publishing.

Generated artifact changes are acceptable only when reviewed as a grammar/toolchain change, not as a blind dependency update.

## GitHub Actions Updates

GitHub Actions updates may be handled by Dependabot when CI is green. If an action major version changes behavior, review the workflow logs across Linux, macOS, and Windows before merging.

## npm Runtime Dependencies

This package currently has no runtime npm dependencies. Any new runtime dependency should be justified in the pull request and included in the public package review.
