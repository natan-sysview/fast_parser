# Rule Catalog: framework_usage_evidence

## Purpose

Expose safe syntax-level evidence of common Java framework usage while preserving normal Java parsing behavior.

This rule is intentionally conservative. It adds grammar nodes only where the source text gives local, unambiguous framework evidence:

- Framework imports.
- Framework annotations.
- JDBC connection string literals.

Name-based method calls and constructors are handled by `queries/frameworks.scm`, not by grammar tokens, because class names such as `JAXBContext`, `DriverManager`, or `XStream` are also valid Java identifiers and type names. Reserving them in `grammar.js` causes parse regressions in real code.

## Included Framework Families

| Family | Grammar evidence | Query evidence |
| --- | --- | --- |
| Spring Boot / Spring MVC | `org.springframework...` imports, Spring annotations | `SpringApplication.run(...)` |
| Spring Security | Spring imports, security annotations | Security call patterns should be expanded by query |
| Hibernate / JPA | `javax.persistence...`, `jakarta.persistence...`, `org.hibernate...`, JPA annotations | Entity-manager patterns can be added by query |
| JDBC | `java.sql...`, `javax.sql...` imports, `jdbc:*` literals | `DriverManager.getConnection(...)` |
| Axis / Axis2 | `org.apache.axis...`, `org.apache.axis2...` imports | Stub/service calls can be added by query |
| JAXB javax/jakarta | XML binding imports, JAXB annotations | `JAXBContext.newInstance(...)` |
| JasperReports | `net.sf.jasperreports...` imports | `JasperFillManager.fillReport(...)`, export/compile calls |
| BouncyCastle | `org.bouncycastle...` imports | `new BouncyCastleProvider()` |
| JJWT | `io.jsonwebtoken...` imports | `Jwts.builder()`, `Jwts.parserBuilder()` |
| Springfox | `springfox...` imports, `@EnableSwagger2` | `new Docket(...)` |
| XStream | `com.thoughtworks.xstream...` imports | `new XStream()`, `xstream.toXML(...)` |
| Oracle / SQL Server drivers | `oracle.jdbc...`, `oracle.sql...`, `com.microsoft.sqlserver.jdbc...` imports, JDBC literals | datasource/driver constructors by query |
| Lombok | `lombok...` imports, Lombok annotations | query capture only |
| Jackson / Gson | `com.fasterxml.jackson...`, `com.google.gson...` imports, Jackson annotations | query capture only |
| Logging | `org.slf4j...`, Log4j imports | query capture only |
| Servlet / Bean Validation | servlet and validation imports, validation annotations | query capture only |
| JUnit / Mockito | JUnit/Mockito imports and annotations | query capture only |
| Swagger / AspectJ / JAX-RS | Swagger, AspectJ, JAX-RS and transaction imports/annotations | query capture only |
| Jasypt Spring Boot / javax.annotation | official imports and lifecycle/config annotations | query capture only |
| Logback / Netty / Google Auth / org.json / Thumbnailator | official third-party import roots | query capture only |

## Grammar Nodes

- `framework_import_declaration`
- `framework_qualified_name`
- `framework_marker_annotation`
- `framework_annotation`
- `framework_annotation_identifier`
- `framework_qualified_annotation_name`
- `jdbc_connection_string`

## Supported Syntax Shapes

```java
import org.springframework.web.bind.annotation.RestController;
import javax.persistence.Entity;
import java.sql.DriverManager;
import oracle.jdbc.OracleDriver;

@RestController
@Entity(name = "Customer")
class CustomerController {}

String url = "jdbc:oracle:thin:@localhost:1521/XEPDB1";
```

Additional official annotations now covered by corpus include:

- Spring: `@ComponentScan`, `@PropertySource`, `@EnableAsync`, `@Async`, `@RestControllerAdvice`, `@ExceptionHandler`, `@PathVariable`, `@SpringBootTest`, `@Validated`, `@DateTimeFormat`, `@Primary`, `@Scope`.
- JPA/Hibernate: `@PersistenceContext`, `@Lob`, `@PrePersist`, `@PreUpdate`, `@IdClass`, `@Basic`, `@UniqueConstraint`, `@GenericGenerator`, `@Nationalized`, `@Type`.
- JAXB/JAX-WS/JAX-RS: `@XmlElementWrapper`, `@ResponseWrapper`, `@WebEndpoint`, `@WebServiceClient`, `@WebFault`, `@SOAPBinding`, `@Context`.
- Lombok/XStream/Swagger/Validation: `@SuperBuilder`, `@XStreamImplicit`, `@ApiResponse`, `@ApiResponses`, `@Length`, `@Constraint`.
- Other official library annotations: `@PostConstruct`, `@EnableEncryptableProperties`.
- Low-volume third-party imports now covered: `javax.activation...`, `ch.qos.logback...`, `io.netty...`, `reactor.netty...`, `com.google.auth...`, `org.json...`, `net.coobird.thumbnailator...`.

## Excluded From Grammar

These are intentionally excluded from grammar rules and handled by queries:

- `Jwts.builder()`
- `DriverManager.getConnection(...)`
- `JAXBContext.newInstance(...)`
- `new XStream()`
- `new BouncyCastleProvider()`
- `new Docket(...)`

Reason: making `Jwts`, `DriverManager`, `JAXBContext`, `XStream`, etc. grammar tokens can break valid Java declarations, variables, and field accesses. Queries can recognize those shapes after Java has parsed them normally.

Also intentionally excluded from the official grammar:

- Client-local annotations such as `client.local.annotations.AuditLog` and `DomainSpecificLength`.
- Java base annotations such as `@Override`, `@SuppressWarnings`, `@Target`, and `@Retention`.
- Raw-scan false positives from strings or text fragments, for example `@fecha`, `@alias`, or `@tarjeta`.
- Build-tool wrapper sources and Java base/JDK APIs such as Maven wrapper imports, `javax.net`, `javax.imageio`, and project-local packages.

## Known Semantic Limits

- The grammar does not resolve Maven/Gradle dependencies.
- The grammar does not infer framework usage through indirect inheritance.
- The grammar does not prove that a simple annotation such as `@Entity` comes from JPA if there is no import context. It only records the local syntactic evidence.
- Query-based detections are name-based and should be audited for false positives.

## Validation Summary

Corpus:

- `framework_usage_evidence`: passed.
- `java_frameworks_smoke`: passed.

Inventory audit against the private framework Java corpus:

- Files: 2264
- Parsed: 2264
- Files with `ERROR`: 0
- Files with `MISSING`: 0
- CR-only Java sources are handled by ending `line_comment` at either `\r` or `\n`; this fixed the previous inherited `ApplicationLoggingAspect.java` `MISSING`.

Node matches:

| Node | Count | Files |
| --- | ---: | ---: |
| `framework_annotation` | 20418 | 1672 |
| `framework_qualified_name` | 7866 | 1795 |
| `framework_import_declaration` | 7862 | 1793 |
| `framework_marker_annotation` | 4562 | 1383 |
| `framework_scoped_annotation_name` | 1 | 1 |

Query family audit:

- Audit artifact: `audits/framework_query_family_audit.md`
- Inventory files: 2264
- Files with any framework capture: 1824
- Query failures: 0
- Latest false-negative audit: `audits/framework_false_negative_audit.md`
- Latest official annotation gap audit: `audits/framework_official_annotation_gap_audit.md`
- Latest CR line-ending repair audit: `audits/framework_cr_line_comment_repair_audit.md`
- Latest false-positive audit: `audits/framework_false_positive_audit.md`
- Cross-inventory encoding validation: `audits/framework_cross_inventory_encoding_validation.md`

Top family captures:

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
| `framework.logging.import` | 157 | 104 |
| `framework.swagger.import` | 93 | 42 |
| `framework.security.annotation` | 67 | 33 |
| `framework.security.import` | 63 | 41 |
| `framework.gson.import` | 54 | 44 |
| `framework.axis.import` | 45 | 33 |
| `framework.itext.import` | 40 | 7 |
| `framework.jaxws.annotation` | 59 | 5 |
| `framework.crypto.import` | 34 | 9 |
| `framework.xstream.import` | 34 | 27 |
| `framework.apache_commons.import` | 31 | 27 |
| `framework.apache_commons.qualified_access` | 1351 | 24 |
| `framework.apache_commons.qualified_type` | 1336 | 19 |
| `framework.jaxws.import` | 26 | 7 |
| `framework.servlet.import` | 24 | 19 |
| `framework.aspectj.import` | 19 | 4 |
| `framework.mail.import` | 16 | 2 |
| `framework.jaxrs.import` | 11 | 11 |
| `framework.jaxrs.annotation` | 25 | 11 |
| `framework.apache_http.import` | 9 | 2 |
| `framework.jboss_logging.import` | 9 | 9 |
| `framework.firebase.import` | 8 | 4 |
| `framework.transaction.import` | 7 | 7 |
| `framework.apache_axiom.import` | 5 | 2 |
| `framework.jose4j.import` | 5 | 1 |
| `framework.aspectj.annotation` | 5 | 2 |
| `framework.hibernate.annotation` | 5 | 2 |
| `framework.jasypt_spring_boot.annotation` | 1 | 1 |
| `framework.javax_annotation.annotation` | 1 | 1 |
| `framework.jasypt.import` | 4 | 2 |
| `framework.nimbus_jose.import` | 4 | 1 |
| `framework.jfree.import` | 3 | 3 |
| `framework.jaxrs.import` | 11 | 11 |
| `framework.transaction.import` | 7 | 7 |
| `framework.aspectj.annotation` | 5 | 2 |

False-negative audit:

- Non-wrapper framework Java files reviewed: 2224.
- Files with framework text evidence: 1822.
- Likely framework-family misses: 0.
- Query failures: 0.

Decision: stable as a first framework evidence rule. Expand method/constructor and fully-qualified-name coverage through queries first; only promote a shape into grammar if it can be recognized without reserving ordinary Java identifiers.
