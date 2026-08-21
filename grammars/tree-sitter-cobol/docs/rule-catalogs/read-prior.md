# READ PRIOR

## Rule Name

`read_statement`

## Purpose

Recognize indexed/sequential `READ file PRIOR` statements used to read the previous record.

## Included Form

```cobol
READ TOTCAIXA PRIOR AT END
    GO ERRO-2
END-READ.
```

## Excluded Forms

- Runtime navigation semantics.
- Non-READ uses of `PRIOR`.

## Corpus

- `read prior at end`

## Audit Basis

Observed in Cementera residuals `PCXA006.cbl` and `PCXA007.cbl`.
