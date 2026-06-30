# Query Catalog: framework_query_families

## Purpose

Classify framework evidence exposed by `framework_usage_evidence` into practical framework families without adding risky reserved identifiers to `grammar.js`.

This catalog belongs to the query layer:

`queries/frameworks.scm`

The consolidated public support matrix is documented in `framework_support_matrix.md`.

## Why Queries Instead Of Grammar For Calls

Framework calls and constructors often use names that are legal Java identifiers and type identifiers:

- `JAXBContext`
- `DriverManager`
- `Jwts`
- `XStream`
- `builder`

Early tests showed that promoting those names into grammar tokens can create parse regressions in real Java code. Queries are the safer layer for name-based recognition because the Java grammar parses first, then the query labels matched shapes.

## Families

| Family | Captures |
| --- | --- |
| Spring Boot / Spring MVC | `framework.spring.import`, `framework.spring.annotation`, `framework.spring.call.*`, `framework.spring.constructor` |
| Spring Security | `framework.security.import`, `framework.security.annotation` |
| Hibernate / JPA | `framework.jpa.import`, `framework.jpa.annotation`, `framework.hibernate.import` |
| JDBC | `framework.jdbc.import`, `framework.jdbc.connection_string`, `framework.jdbc.call.*`, `framework.jdbc.constructor` |
| Axis / Axis2 | `framework.axis.import`, `framework.axis.qualified_type` |
| JAXB | `framework.jaxb.import`, `framework.jaxb.annotation`, `framework.jaxb.call.*` |
| JAX-WS / SOAP annotations | `framework.jaxws.import`, `framework.jaxws.annotation` |
| JAX-RS | `framework.jaxrs.import`, `framework.jaxrs.annotation` |
| JasperReports | `framework.jasper.import`, `framework.jasper.call.*` |
| BouncyCastle | `framework.bouncycastle.import`, `framework.bouncycastle.constructor` |
| JJWT | `framework.jjwt.import`, `framework.jjwt.call.*` |
| Springfox | `framework.springfox.import`, `framework.springfox.annotation`, `framework.springfox.constructor` |
| XStream | `framework.xstream.import`, `framework.xstream.constructor`, `framework.xstream.call.*` |
| Oracle driver | `framework.oracle_driver.import`, `framework.oracle_driver.connection_string`, `framework.oracle_driver.driver_class`, `framework.oracle_driver.constructor`, `framework.oracle_driver.qualified_type` |
| SQL Server driver | `framework.sqlserver_driver.import`, `framework.sqlserver_driver.connection_string`, `framework.sqlserver_driver.driver_class`, `framework.sqlserver_driver.constructor`, `framework.sqlserver_driver.qualified_type` |
| Lombok | `framework.lombok.import`, `framework.lombok.annotation` |
| Jackson / Gson | `framework.jackson.import`, `framework.jackson.annotation`, `framework.jackson.constructor`, `framework.gson.import`, `framework.gson.constructor` |
| Logging | `framework.logging.import` |
| Apache Commons | `framework.apache_commons.import`, `framework.apache_commons.qualified_type`, `framework.apache_commons.qualified_access` |
| Servlet | `framework.servlet.import` |
| Bean Validation | `framework.validation.import`, `framework.validation.annotation` |
| JUnit / Mockito | `framework.junit.import`, `framework.junit.annotation`, `framework.mockito.import`, `framework.mockito.annotation` |
| Swagger | `framework.swagger.import`, `framework.swagger.annotation` |
| AspectJ | `framework.aspectj.import`, `framework.aspectj.annotation` |
| Transactions | `framework.transaction.import`, `framework.transaction.annotation` |
| Apache HTTP / Axiom | `framework.apache_http.import`, `framework.apache_http.call.*`, `framework.apache_axiom.import`, `framework.apache_axiom.qualified_type` |
| Mail / Crypto | `framework.mail.import`, `framework.crypto.import`, `framework.crypto.call.*` |
| iText / JFree | `framework.itext.import`, `framework.jfree.import` |
| Firebase | `framework.firebase.import`, `framework.firebase.call.*` |
| Google Auth | `framework.google_auth.import` |
| Netty / Reactor Netty | `framework.netty.import` |
| org.json | `framework.json.import`, `framework.json.constructor` |
| Thumbnailator | `framework.thumbnailator.import` |
| JOSE / Jasypt | `framework.nimbus_jose.import`, `framework.nimbus_jose.call.*`, `framework.jose4j.import`, `framework.jose4j.constructor`, `framework.jasypt.import`, `framework.jasypt.constructor` |
| Jasypt Spring Boot | `framework.jasypt_spring_boot.import`, `framework.jasypt_spring_boot.annotation` |
| Javax/Jakarta annotation | `framework.javax_annotation.import`, `framework.javax_annotation.annotation` |
| JBoss Logging | `framework.jboss_logging.import` |

## Current Private Framework Audit

Audit artifact:

`audits/framework_query_family_audit.md`

Summary:

- Inventory files: 2264
- Files with any framework capture: 1824
- Query failures: 0
- Query runtime: 212.57 seconds

Top captures:

| Capture | Count | Files |
| --- | ---: | ---: |
| `framework.axis.qualified_type` | 28003 | 54 |
| `framework.apache_axiom.qualified_type` | 7772 | 40 |
| `framework.jaxb.annotation` | 3288 | 393 |
| `framework.spring.annotation` | 2332 | 515 |
| `framework.spring.import` | 2217 | 626 |
| `framework.jpa.annotation` | 2143 | 132 |
| `framework.lombok.annotation` | 1981 | 993 |
| `framework.lombok.import` | 1887 | 979 |
| `framework.jaxb.import` | 1680 | 417 |
| `framework.validation.annotation` | 1148 | 226 |
| `framework.jackson.annotation` | 1128 | 195 |
| `framework.validation.import` | 479 | 235 |
| `framework.jackson.import` | 382 | 236 |
| `framework.jpa.import` | 293 | 103 |
| `framework.xstream.annotation` | 221 | 23 |
| `framework.jdbc.import` | 174 | 108 |
| `framework.swagger.annotation` | 171 | 41 |
| `framework.logging.import` | 159 | 104 |
| `framework.swagger.import` | 93 | 42 |
| `framework.gson.constructor` | 84 | 38 |
| `framework.security.annotation` | 67 | 33 |
| `framework.security.import` | 63 | 41 |
| `framework.gson.import` | 54 | 44 |
| `framework.axis.import` | 45 | 33 |
| `framework.jaxws.annotation` | 59 | 5 |
| `framework.jackson.constructor` | 42 | 19 |
| `framework.itext.import` | 40 | 7 |
| `framework.crypto.import` | 34 | 9 |
| `framework.xstream.import` | 34 | 27 |
| `framework.apache_commons.import` | 31 | 27 |
| `framework.apache_commons.qualified_access` | 1351 | 24 |
| `framework.apache_commons.qualified_type` | 1336 | 19 |
| `framework.jaxws.import` | 26 | 7 |
| `framework.jaxrs.annotation` | 25 | 11 |
| `framework.servlet.import` | 24 | 19 |
| `framework.spring.constructor` | 24 | 17 |
| `framework.aspectj.import` | 19 | 4 |
| `framework.crypto.call.method` | 18 | 8 |
| `framework.mail.import` | 19 | 3 |
| `framework.jdbc.constructor` | 15 | 15 |
| `framework.jaxrs.import` | 11 | 11 |
| `framework.apache_http.import` | 9 | 2 |
| `framework.jboss_logging.import` | 9 | 9 |
| `framework.firebase.import` | 8 | 4 |
| `framework.transaction.import` | 7 | 7 |
| `framework.apache_axiom.import` | 5 | 2 |
| `framework.jose4j.import` | 5 | 1 |
| `framework.aspectj.annotation` | 8 | 2 |
| `framework.hibernate.annotation` | 5 | 2 |
| `framework.xstream.constructor` | 5 | 4 |
| `framework.bouncycastle.constructor` | 4 | 3 |
| `framework.jasypt.constructor` | 4 | 2 |
| `framework.jasypt.import` | 4 | 2 |
| `framework.nimbus_jose.import` | 4 | 1 |
| `framework.jfree.import` | 3 | 3 |
| `framework.netty.import` | 3 | 1 |
| `framework.apache_http.call.method` | 2 | 2 |
| `framework.firebase.call.method` | 2 | 2 |
| `framework.jose4j.constructor` | 2 | 1 |
| `framework.junit.annotation` | 1 | 1 |
| `framework.google_auth.import` | 1 | 1 |
| `framework.json.constructor` | 1 | 1 |
| `framework.json.import` | 1 | 1 |
| `framework.jasypt_spring_boot.annotation` | 1 | 1 |
| `framework.jasypt_spring_boot.import` | 1 | 1 |
| `framework.javax_annotation.annotation` | 1 | 1 |
| `framework.javax_annotation.import` | 1 | 1 |
| `framework.nimbus_jose.call.method` | 1 | 1 |
| `framework.thumbnailator.import` | 1 | 1 |

Observed low-volume families:

- JasperReports: imports and calls exist, mainly in a small number of files.
- BouncyCastle: imports and constructors exist.
- JJWT: imports and calls exist in one file.
- Springfox: import, annotation, and constructor evidence exists in one file.
- SQL Server driver: driver class constants are now captured by query.
- JUnit imports exist in three files; Mockito query support exists, but this Mifel audit did not produce Mockito captures.
- Swagger annotations and imports are now captured separately from Springfox.
- `@ToString.Exclude` is captured through `framework_scoped_annotation_name`.
- JAX-RS annotations such as `@Context` are captured separately from JAX-WS SOAP annotations.
- Official low-volume annotations discovered in Mifel are now covered: Spring async/config/test annotations, JPA lifecycle annotations, JAX-WS generated-service annotations, XStream implicit collections, Swagger responses, Hibernate annotations, Lombok `@SuperBuilder`, Jasypt Spring Boot, and `@PostConstruct`.
- Query-only call and constructor coverage now includes `new Gson(...)`, `new ObjectMapper(...)`, Spring `RestTemplate`/`Jaxb2Marshaller`, JDBC template constructors, `Cipher.getInstance(...)`, Apache `HttpClients.custom(...)`, Firebase credentials/messaging calls, Jasypt constructors, and JOSE/JWE constructors/calls.
- Additional low-volume third-party import roots now covered: `javax.activation`, Logback, Netty/Reactor Netty, Google Auth, `org.json`, and Thumbnailator.
- Generated SOAP clients that use fully-qualified Axis2/Axiom types are now covered without changing `grammar.js`.
- Apache Commons fully-qualified calls such as `org.apache.commons.lang.StringUtils...` are now covered by query.
- Driver class constants such as Oracle and SQL Server driver class names are now covered by query.
- The latest false-negative audit reviewed 2224 non-wrapper framework Java files, found 1822 files with framework text evidence, and found 0 likely family misses.
- Client-local annotations and Java base annotations remain excluded from official framework captures.

## Expansion Rules

Add a new query capture when:

- The shape is already parsed cleanly by Java grammar.
- The capture can be explained by local source text.
- The family and capture name are stable.
- The query can be audited against the full inventory with 0 query failures.

Promote a query shape into `grammar.js` only when:

- It cannot collide with ordinary Java identifiers.
- It adds a useful named node not available from Java generic syntax.
- Corpus and full-inventory validation stay at 0 introduced `ERROR` nodes.
