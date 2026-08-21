# JSF Backend Rule Audit

Date: 2026-08-20

## Scope

Added JavaServer Faces backend support to the Java frameworks grammar.

Included:

- `javax.faces.*` and `jakarta.faces.*` imports.
- `org.primefaces.*` imports.
- JSF annotations such as `ManagedBean`, `ManagedProperty`, `ViewScoped`,
  `SessionScoped`, `ApplicationScoped`, `FacesConverter`, and
  `FacesValidator`.
- CDI `Named` / `Inject` as backing-bean support.
- Grammar nodes for unambiguous JSF backend types, JSF constructors, JSF static
  fields, explicit `FacesContext` calls, PrimeFaces backend types,
  PrimeFaces constructors, and PrimeFaces backend API calls.
- Query captures for annotated classes, contract classes, contract methods,
  constructors, static fields, types, imports, annotations, and explicit backend
  API calls.

Excluded:

- Monex-specific Java classes.
- Static-import call attribution for bare `getCurrentInstance()`, because it
  can refer to either JSF `FacesContext` or PrimeFaces `RequestContext`.
- Ambiguous bare Java type names such as `Validator`, `Application`,
  `Resource`, `Renderer`, `StateManager`, `ActionListener`, and `Converter`
  when there is no stronger local JSF evidence.

## Validation

Corpus:

- `tree-sitter test`: 7/7 passed.

PrimeFaces Java inventory:

- Source root:
  `/Users/natanbarronlugo/Desktop/Proyectos/componentes/monex-java/primefaces`
- Inventory files: 196.
- Hard failures: 0.
- Files with `ERROR`: 0.
- Total `ERROR` nodes: 0.
- Files with `MISSING`: 0.
- Total `MISSING` nodes: 0.
- MessagePack diagnostics:
  `runs/jsf_backend_completion_primefaces_validation.msgpack`

Full Java inventory regression:

- Inventory files: 3706.
- Hard failures: 0.
- Files with `ERROR`: 0.
- Total `ERROR` nodes: 0.
- Files with `MISSING`: 0.
- Total `MISSING` nodes: 0.
- MessagePack diagnostics:
  `runs/jsf_backend_completion_all_java_frameworks_validation.msgpack`

FastParse extension validation:

- Extension:
  `/Users/natanbarronlugo/Desktop/Proyectos/javaswing/assessment_csharp/native/tree-sitter-multi-parser-lab/bin/libfastparse_language_java_frameworks.dylib`
- Query:
  `/Users/natanbarronlugo/Desktop/Proyectos/javaswing/assessment_csharp/native/tree-sitter-multi-parser-lab/extensions/java-frameworks/queries/frameworks.scm`
- Inventory files: 3706.
- Workers: 8.
- Parsed OK: 3706.
- Hard parse failures: 0.
- Files with `ERROR`: 0.
- Files with `MISSING`: 0.
- Query failures: 0.
- Files with framework captures: 3422.
- Output DB:
  `runs/java_frameworks_fastparse_validation_jsf_backend_completion.sqlite`
- Report:
  `audits/java_frameworks_fastparse_validation_jsf_backend_completion.md`

Query audit, PrimeFaces root:

- Inventory files: 196.
- Files with any framework capture: 106.
- Query failures: 0.

JSF/PrimeFaces captures:

| Capture | Count | Files |
| --- | ---: | ---: |
| `framework.jsf.annotated_class.annotation` | 24 | 14 |
| `framework.jsf.annotated_class.name` | 24 | 14 |
| `framework.jsf.import` | 62 | 20 |
| `framework.jsf.type` | 41 | 9 |
| `framework.jsf.annotation` | 37 | 15 |
| `framework.jsf.contract_method.name` | 13 | 4 |
| `framework.jsf.contract_method.parameter_type` | 13 | 4 |
| `framework.jsf.constructor` | 8 | 4 |
| `framework.jsf.contract_class.name` | 4 | 4 |
| `framework.jsf.extended_type` | 3 | 3 |
| `framework.jsf.implemented_type` | 1 | 1 |
| `framework.jsf.qualified_type` | 6 | 1 |
| `framework.jsf.context_call.target` | 3 | 1 |
| `framework.jsf.context_call.method` | 3 | 1 |
| `framework.jsf.static_field.target` | 2 | 1 |
| `framework.jsf.static_field.name` | 2 | 1 |
| `framework.primefaces.import` | 23 | 11 |
| `framework.primefaces.type` | 55 | 10 |
| `framework.primefaces.constructor` | 10 | 4 |
| `framework.primefaces.backend_call.target` | 5 | 3 |
| `framework.primefaces.backend_call.method` | 5 | 3 |

Query audit, original Mifel framework root:

- Inventory files: 2264.
- Files with any framework capture: 1824.
- Query failures: 0.
- JSF captures after ambiguity correction: 0.
- Regression detail: a previous draft captured a real
  `javax.validation.Validator` as JSF. `Validator` is now intentionally generic
  unless stronger local JSF evidence is present.
- PrimeFaces closure detail: the validation pass found real backend uses of
  `DefaultMenuItem`, `DefaultMenuModel`, `DefaultSubMenu`, `DynamicMenuModel`,
  `MenuElement`, `MenuModel`, and `SelectEvent`; those are now represented by
  `primefaces_backend_type`.
- Imported type closure: 0 missing imported `org.primefaces.*` simple type
  names in the current Java backend corpus.

## Decision

Stable for backend JSF/PrimeFaces evidence in Java source files.
