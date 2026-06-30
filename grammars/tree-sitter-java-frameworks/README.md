# tree-sitter-java-frameworks

Experimental Java-derived Tree-sitter grammar for detecting framework usage in Java source code.

This grammar starts from `tree-sitter-java` and adds conservative framework evidence nodes for syntax that can be recognized locally:

- framework imports
- framework annotations
- JDBC connection string literals

Name-based framework calls and constructors are classified in queries instead of grammar rules when promoting the name to syntax would risk breaking ordinary Java parsing.

## Scope

Covered framework families include:

- Spring Boot, Spring MVC, Spring Security
- Hibernate and JPA
- JDBC and common database drivers
- Axis, Axis2, JAXB, JAX-WS, JAX-RS
- JasperReports
- BouncyCastle, JJWT, JOSE
- Springfox and Swagger
- XStream
- Lombok
- Jackson and Gson
- logging frameworks
- Apache Commons, Apache HTTP, Axiom
- Servlet, Mail, Activation, Crypto
- Bean Validation and Hibernate Validator
- JUnit and Mockito
- AspectJ
- iText, JFree, Firebase, Google Auth
- Netty, Reactor Netty, org.json, Thumbnailator
- Jasypt and Jasypt Spring Boot

Client-specific annotations, packages, wrappers, and inheritance conventions are intentionally out of scope for the official/common grammar. Put those in a separate client profile or extension grammar.

## Syntax Nodes

Primary framework evidence nodes:

- `framework_import_declaration`
- `framework_qualified_name`
- `framework_marker_annotation`
- `framework_annotation`
- `framework_annotation_identifier`
- `framework_qualified_annotation_name`
- `framework_scoped_annotation_name`
- `jdbc_connection_string`

## Queries

Framework family classification lives in:

- `queries/frameworks.scm`

Editor queries:

- `queries/highlights.scm`
- `queries/injections.scm`
- `queries/tags.scm`

## Development

Generate parser artifacts:

```sh
tree-sitter generate
```

Run corpus tests:

```sh
tree-sitter test
```

Run full inventory validation with encoding normalization:

```sh
./tools/validate_framework_inventory.py --threads 8
```

Run framework query audit:

```sh
./tools/audit_framework_queries.py
```

Package smoke checks:

```sh
npm pack --dry-run
cargo test
cargo package --allow-dirty --no-verify
```

## Validation Status

Current local validation evidence is stored under `audits/`.

Latest readiness summary:

- `audits/framework_readiness_summary.md`

Latest full inventory validation:

- `audits/framework_inventory_validation.md`
- `audits/framework_inventory_validation.json`
- `audits/framework_inventory_validation.msgpack`

## Known Limits

- The grammar does not resolve type bindings, Maven/Gradle dependencies, dependency injection graphs, or indirect inheritance.
- Instance calls such as `mapper.writeValueAsString(...)` are only safely classifiable when semantic type information is available; this grammar avoids guessing.
- Final public repository and module paths must be set before a real public release.
- Private corpus reports under `audits/` and `baselines/` may contain local paths or private aggregate evidence and are not public-release artifacts without sanitization.

## License

MIT, inherited from `tree-sitter-java`.
