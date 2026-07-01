# Security Policy

`tree-sitter-javaswing` is a parser grammar. Security reports are most likely to involve denial-of-service style parser behavior, unsafe package contents, or accidental publication of private data.

## Supported Versions

Security support starts with the first public alpha release.

| Version | Supported |
| --- | --- |
| `0.1.x` | Yes, after public release |

## Reporting A Vulnerability

After the public repository exists, use the repository security advisory flow when available. If advisories are not enabled, open a minimal public issue only when the report does not expose sensitive details.

Do not include private source code, local paths, validation databases, production snippets, credentials, account data, or source-derived examples in public reports.

## Private Data

If a report involves accidental private data exposure, avoid posting the data publicly. Describe the affected public artifact, package, release, or commit and wait for maintainer guidance.

## Parser Behavior Reports

For parser hangs, crashes, or excessive resource use, provide a synthetic minimized sample that reproduces the behavior. If the original input is private, reduce it to a public-safe shape before reporting.
