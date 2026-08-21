# COBOL 0.1.1 Preview 1 Publish Validation - 2026-08-21

## Scope

FastParse COBOL extension built from this repository:

`bin/libfastparse_language_cobol.dylib`

Core library:

`bin/libfastparse.dylib`

Candidate version:

`0.1.1-preview.1`

Layout normalization:

`normal-fixed`

## Tree-sitter Corpus

`tree-sitter test`

| Metric | Count |
| --- | ---: |
| Total parses | 300 |
| Successful parses | 300 |
| Failed parses | 0 |

## CTest

`ctest --test-dir build-cobol-0.1.1-preview.1 -C Release --output-on-failure`

| Test | Result |
| --- | --- |
| tsmp_c_smoke | Passed |
| tsmp_c_extension_smoke | Passed |

## NuGet Version Decision

A local COBOL language package built against `FastParser 0.1.0` failed the COBOL EBCDIC smoke. The release candidate is therefore versioned as `0.1.1-preview.1` for both the FastParser core and `FastParser.Language.Cobol`, so the published COBOL package depends on a core that includes the current COBOL normalization path.

Local `.NET` test execution compiled but could not run on this machine because only the .NET 10 runtime is installed and the C# testhost targets .NET 9. The GitHub release workflow installs .NET 8/9 and is expected to run the C# suite there.

## Carlos

Run DB:

`experimental-grammars/tree-sitter-cobol/runs/candidate_compare_fastparser_repo_0_1_1_preview1_carlos_20260821.sqlite`

| Metric | Count |
| --- | ---: |
| Files | 91 |
| Parsed OK | 91 |
| Hard failures | 0 |
| Files with ERROR | 0 |
| ERROR nodes | 0 |
| Files with MISSING | 0 |
| MISSING nodes | 0 |
| Elapsed | 0.648s |

## Cementera

Run DB:

`experimental-grammars/tree-sitter-cobol/runs/candidate_compare_fastparser_repo_0_1_1_preview1_cementera_20260821.sqlite`

| Metric | Count |
| --- | ---: |
| Files | 4,169 |
| Parsed OK | 4,169 |
| Hard failures | 0 |
| Files with ERROR | 0 |
| ERROR nodes | 0 |
| Files with MISSING | 0 |
| MISSING nodes | 0 |
| Elapsed | 27.813s |

## Decision

The repository-built COBOL extension validates cleanly against the Carlos and Cementera inventories used for this release candidate.
