# COBOL/400 Screen And Printer Clauses

## Rule Name

`cobol400_screen_printer`

## Purpose

Recognize COBOL/400 procedure statements observed in the Cementera inventory
without broadening generic statement recovery.

## Included Forms

```cobol
DISPLAY "TITLE" AT 0724.
```

```cobol
DISPLAY
    "TOTAL A RECEBER IMPOSSIVEL !!!" AT 2315
    "SUGERIDO==>>" AT 2347 WITH HIGHLIGHT.
```

```cobol
WRITE REGIMP FORMAT IS "RDET01" ADD 1 TO KLIN.
```

```cobol
WRITE REG-TELA006 FORMAT "RODAPE" INDICATORS ARE INDICADOR.
```

```cobol
READ MFF900 FORMAT IS 'MFF900T0'
     INDICATORS ARE MFF900T0-I-INDIC.
```

## Excluded Forms

- Full AS/400 DDS grammar.
- Printer/display file definitions outside COBOL procedure statements.
- Arbitrary trailing words after `WRITE`.

## Local Syntax

- `DISPLAY` accepts a compact numeric screen coordinate after `AT`.
- `DISPLAY` accepts repeated positioned items, each with its own `AT` and
  optional `WITH` clause.
- `WRITE` accepts a `FORMAT [IS] <literal-or-identifier>` phrase and a narrow
  `ADD <number-or-identifier> TO <identifier>` line-counter phrase.
- `WRITE` and `READ` accept `INDICATORS [ARE] <identifier>` for display-file
  indicator areas.
- `READ` accepts `FORMAT [IS] <literal-or-identifier>` before the indicators
  phrase.

## Corpus

- `display with compact screen position`
- `display multiple positioned items`
- `write printer format with add line counter`
- `write format with indicators`
- `read with indicators`
- `read format with indicators`

## Audit Basis

Initial Cementera validation found repeated errors around:

```cobol
DISPLAY "..." AT 0724
WRITE REGIMP FORMAT IS "RDET01" ADD 1 TO KLIN.
```

Baseline before this rule:

- `baselines/2026-08-20-before-cementera-cobol400-repairs`
- Cementera validation DB:
  `runs/candidate_compare_current_cementera_cobol_20260820.sqlite`
