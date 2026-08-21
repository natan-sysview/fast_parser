# COBOL/400 FD Optional Period

## Rule Name

`file_description_entry` optional period with `cobol400_word`

## Purpose

Recognize file descriptions where `FD`/`SD` names include underscores or omit the period before the first `01` record description.

## Basis

Cementera residual audits show repeated File Section forms:

- `FD FECA_SFP.` followed by `01 REG-FECA_SFP.`
- `FD ARQBANCO` followed directly by `01 REG01.`
- `FD RELCHQ50` followed directly by `01 REGIMP PIC X(90).`

## Included Forms

- FD/SD entry names with underscores.
- FD/SD entries with or without a period before `record_description_list`.

## Excluded Forms

- Optional periods for arbitrary data-description entries outside FD/SD headers.
- General underscore identifiers outside FD/SD names and `SELECT` assignment targets.

## Corpus

- `test/corpus/cobol400_fd_optional_period.txt`

## Audit Notes

Added after Cementera validation `runs/candidate_compare_current_cementera_database_assignment_20260820.sqlite`, where many `FILE_CONTROL_IO` samples were actually File Section `FD` declarations with omitted periods or underscore names.
