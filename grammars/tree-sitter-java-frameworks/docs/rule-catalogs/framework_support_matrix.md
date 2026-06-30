# Framework Support Matrix

Date: 2026-06-30

This matrix is the public-safe support contract for `tree-sitter-java-frameworks` and the FastParse `java-frameworks` extension.

The grammar is intentionally split into two layers:

- Grammar nodes expose local syntax that is safe to recognize while parsing Java.
- Queries classify framework families and name-based usage after Java has parsed successfully.

This avoids reserving ordinary Java identifiers such as `DriverManager`, `JAXBContext`, `ObjectMapper`, `Jwts`, `XStream`, or `Docket` as grammar tokens.

## Support Levels

| Level | Meaning |
| --- | --- |
| Grammar | Exposed as named Tree-sitter nodes such as `framework_import_declaration`, `framework_annotation`, or `jdbc_connection_string`. |
| Query | Exposed by `queries/frameworks.scm` captures after parsing. |
| Audit | Observed in private enterprise inventories as aggregate metrics only. No private source is part of this catalog. |
| Synthetic corpus | Covered by public-safe examples under `test/corpus/`. |

## Family Matrix

| Framework family | Grammar evidence | Query captures | Public corpus | Status |
| --- | --- | --- | --- | --- |
| Spring Boot / Spring MVC | `org.springframework...` imports, Spring annotations | `framework.spring.import`, `framework.spring.annotation`, `framework.spring.call.*`, `framework.spring.constructor` | `framework_usage_evidence`, `framework_extended_annotations`, `framework_library_imports` | Stable first-rule support |
| Spring Security | Spring Security imports, security annotations | `framework.security.import`, `framework.security.annotation` | `framework_modern_and_negative_annotations` | Stable first-rule support |
| Hibernate / JPA | `javax.persistence...`, `jakarta.persistence...`, `org.hibernate...`, JPA/Hibernate annotations | `framework.jpa.import`, `framework.jpa.annotation`, `framework.hibernate.import`, `framework.hibernate.annotation` | `framework_usage_evidence`, `framework_extended_annotations`, `framework_modern_and_negative_annotations` | Stable first-rule support |
| JDBC | `java.sql...`, `javax.sql...`, JDBC URL literals | `framework.jdbc.import`, `framework.jdbc.connection_string`, `framework.jdbc.call.*`, `framework.jdbc.constructor` | `framework_usage_evidence` | Stable first-rule support |
| Axis / Axis2 | `org.apache.axis...`, `org.apache.axis2...` imports | `framework.axis.import`, `framework.axis.qualified_type` | `framework_usage_evidence` | Stable first-rule support |
| JAXB | `javax.xml.bind...`, `jakarta.xml.bind...`, JAXB annotations | `framework.jaxb.import`, `framework.jaxb.annotation`, `framework.jaxb.call.*` | `framework_usage_evidence`, `framework_extended_annotations`, `framework_modern_and_negative_annotations` | Stable first-rule support |
| JAX-WS / SOAP | `javax.xml.ws...`, `jakarta.xml.ws...`, `javax.jws...`, `jakarta.jws...`, SOAP annotations | `framework.jaxws.import`, `framework.jaxws.annotation` | `framework_extended_annotations` | Stable first-rule support |
| JAX-RS | `javax.ws.rs...`, `jakarta.ws.rs...`, resource annotations | `framework.jaxrs.import`, `framework.jaxrs.annotation` | `framework_extended_annotations`, `framework_modern_and_negative_annotations` | Stable first-rule support |
| JasperReports | `net.sf.jasperreports...` imports | `framework.jasper.import`, `framework.jasper.call.*` | `framework_usage_evidence` | Stable query support |
| BouncyCastle | `org.bouncycastle...` imports | `framework.bouncycastle.import`, `framework.bouncycastle.constructor` | `framework_usage_evidence` | Stable query support |
| JJWT | `io.jsonwebtoken...` imports | `framework.jjwt.import`, `framework.jjwt.call.*` | `framework_usage_evidence` | Stable query support |
| Springfox / Swagger | `springfox...`, `io.swagger...`, Swagger annotations | `framework.springfox.import`, `framework.springfox.annotation`, `framework.springfox.constructor`, `framework.swagger.import`, `framework.swagger.annotation` | `framework_usage_evidence`, `framework_extended_annotations`, `framework_modern_and_negative_annotations` | Stable query support |
| XStream | `com.thoughtworks.xstream...` imports and annotations | `framework.xstream.import`, `framework.xstream.annotation`, `framework.xstream.constructor`, `framework.xstream.call.*` | `framework_usage_evidence`, `framework_extended_annotations` | Stable query support |
| Oracle driver | `oracle.jdbc...`, `oracle.sql...`, JDBC Oracle literals | `framework.oracle_driver.import`, `framework.oracle_driver.connection_string`, `framework.oracle_driver.driver_class`, `framework.oracle_driver.constructor`, `framework.oracle_driver.qualified_type` | `framework_usage_evidence` | Stable query support |
| SQL Server driver | `com.microsoft.sqlserver.jdbc...`, JDBC SQL Server literals | `framework.sqlserver_driver.import`, `framework.sqlserver_driver.connection_string`, `framework.sqlserver_driver.driver_class`, `framework.sqlserver_driver.constructor`, `framework.sqlserver_driver.qualified_type` | `framework_usage_evidence` | Stable query support |
| Lombok | `lombok...` imports and annotations | `framework.lombok.import`, `framework.lombok.annotation` | `framework_usage_evidence`, `framework_extended_annotations`, `framework_modern_and_negative_annotations` | Stable first-rule support |
| Jackson / Gson | Jackson/Gson imports and annotations | `framework.jackson.import`, `framework.jackson.annotation`, `framework.jackson.constructor`, `framework.gson.import`, `framework.gson.constructor` | `framework_usage_evidence`, `framework_extended_annotations`, `framework_library_imports` | Stable query support |
| Logging | SLF4J, Log4j, Logback imports and Lombok logging annotations | `framework.logging.import` | `framework_usage_evidence`, `framework_library_imports`, `framework_modern_and_negative_annotations` | Stable query support |
| Apache Commons / HTTP / Axiom | Apache package imports and selected fully-qualified references | `framework.apache_commons.*`, `framework.apache_http.*`, `framework.apache_axiom.*` | `framework_usage_evidence`, `framework_library_imports` | Stable query support |
| Servlet / Mail / Activation / Crypto | Official Java EE/Jakarta and crypto imports | `framework.servlet.import`, `framework.mail.import`, `framework.crypto.import`, `framework.crypto.call.*` | `framework_usage_evidence`, `framework_library_imports` | Stable query support |
| Bean Validation / Hibernate Validator | Validation imports and annotations | `framework.validation.import`, `framework.validation.annotation` | `framework_usage_evidence`, `framework_extended_annotations`, `framework_modern_and_negative_annotations` | Stable first-rule support |
| JUnit / Mockito | Test imports and test/mock annotations | `framework.junit.import`, `framework.junit.annotation`, `framework.mockito.import`, `framework.mockito.annotation` | `framework_usage_evidence`, `framework_modern_and_negative_annotations` | Stable first-rule support |
| AspectJ / Transactions | AspectJ and transaction imports/annotations | `framework.aspectj.import`, `framework.aspectj.annotation`, `framework.transaction.import`, `framework.transaction.annotation` | `framework_extended_annotations`, `framework_modern_and_negative_annotations` | Stable first-rule support |
| iText / JFree / Firebase / Google Auth | Official third-party import roots | `framework.itext.import`, `framework.jfree.import`, `framework.firebase.import`, `framework.firebase.call.*`, `framework.google_auth.import` | `framework_library_imports` | Stable query support |
| Netty / Reactor Netty / org.json / Thumbnailator | Official third-party import roots and selected constructors | `framework.netty.import`, `framework.json.import`, `framework.json.constructor`, `framework.thumbnailator.import` | `framework_library_imports` | Stable query support |
| JOSE / Jasypt | JOSE and Jasypt imports, constructors, and selected calls | `framework.nimbus_jose.*`, `framework.jose4j.*`, `framework.jasypt.*`, `framework.jasypt_spring_boot.*` | `framework_library_imports`, `framework_extended_annotations` | Stable query support |
| Javax/Jakarta annotation | Lifecycle/config annotation imports and annotations | `framework.javax_annotation.import`, `framework.javax_annotation.annotation` | `framework_extended_annotations`, `framework_library_imports` | Stable first-rule support |
| JBoss Logging | JBoss logging imports | `framework.jboss_logging.import` | Query-only, covered by query catalog | Stable query support |

## Negative Contract

The grammar intentionally keeps these as ordinary Java unless there is explicit supported framework evidence:

- JDK and Java base imports such as `java.util.List`.
- Java base annotations such as `@Override`, `@SuppressWarnings`, `@Target`, and `@Retention`.
- Client-local annotations and packages.
- Variable, field, or method names that merely resemble a framework without a supported import, annotation, literal, constructor, or fully-qualified usage shape.
- Indirect inheritance or dependency graph evidence that requires project-wide symbol resolution.

The corpus case `framework_modern_and_negative_annotations` verifies that `@Override` remains a normal `marker_annotation` while nearby supported framework annotations become `framework_marker_annotation` or `framework_annotation`.

## Validation Evidence

Current public registry validation:

- GitHub Actions release run `28475170176`: success.
- PyPI `fastparse-language-java-frameworks` version `0.1.0rc32`: published and smoke-tested.
- NuGet `FastParser.Language.JavaFrameworks` version `0.1.0-preview.32`: published and smoke-tested.
- Published smoke matrix: Linux x64, Windows x64, macOS x64, macOS arm64.

Private inventory evidence is documented only as aggregate counts in `framework_usage_evidence.md` and `framework_query_families.md`.

## Stable Release Gate

A non-preview release is appropriate when all of the following are true:

- Corpus tests pass after the final corpus additions.
- Query syntax checks pass for `queries/frameworks.scm`.
- FastParse extension package smoke tests pass locally or in CI.
- Public package registry smokes pass for PyPI and NuGet.
- Public docs avoid private source snippets, local paths, hashes, databases, and diagnostics.

As of the `0.1.0-preview.32` public validation and the local stable gate, the extension is ready for the first `v0.1.0` stable tag.
