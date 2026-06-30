; Framework evidence query layer.
; Grammar nodes cover safe syntax-level evidence. Queries split that evidence
; by framework family and add name-based call/constructor detections without
; reserving Java identifiers in grammar.js.

; ---------------------------------------------------------------------------
; Imports
; ---------------------------------------------------------------------------

((framework_import_declaration
  name: (framework_qualified_name) @framework.spring.import)
 (#match? @framework.spring.import "^org\\.springframework\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.security.import)
 (#match? @framework.security.import "^org\\.springframework\\.security\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.jpa.import)
 (#match? @framework.jpa.import "^(javax|jakarta)\\.persistence\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.hibernate.import)
 (#match? @framework.hibernate.import "^org\\.hibernate\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.jdbc.import)
 (#match? @framework.jdbc.import "^(java|javax)\\.sql\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.axis.import)
 (#match? @framework.axis.import "^org\\.apache\\.axis2?\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.jaxb.import)
 (#match? @framework.jaxb.import "^(javax|jakarta)\\.xml\\.bind\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.jaxws.import)
 (#match? @framework.jaxws.import "^(javax|jakarta)\\.(xml\\.ws|jws)\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.jasper.import)
 (#match? @framework.jasper.import "^net\\.sf\\.jasperreports\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.bouncycastle.import)
 (#match? @framework.bouncycastle.import "^org\\.bouncycastle\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.jjwt.import)
 (#match? @framework.jjwt.import "^io\\.jsonwebtoken\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.springfox.import)
 (#match? @framework.springfox.import "^springfox\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.xstream.import)
 (#match? @framework.xstream.import "^com\\.thoughtworks\\.xstream\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.lombok.import)
 (#match? @framework.lombok.import "^lombok\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.jackson.import)
 (#match? @framework.jackson.import "^com\\.fasterxml\\.jackson\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.gson.import)
 (#match? @framework.gson.import "^com\\.google\\.gson\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.logging.import)
 (#match? @framework.logging.import "^(org\\.slf4j|org\\.apache\\.log4j|org\\.apache\\.logging\\.log4j|ch\\.qos\\.logback)\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.apache_commons.import)
 (#match? @framework.apache_commons.import "^org\\.apache\\.commons\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.apache_http.import)
 (#match? @framework.apache_http.import "^org\\.apache\\.http\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.apache_axiom.import)
 (#match? @framework.apache_axiom.import "^org\\.apache\\.axiom\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.swagger.import)
 (#match? @framework.swagger.import "^io\\.swagger\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.aspectj.import)
 (#match? @framework.aspectj.import "^org\\.aspectj\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.jboss_logging.import)
 (#match? @framework.jboss_logging.import "^org\\.jboss\\.logging\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.servlet.import)
 (#match? @framework.servlet.import "^(javax|jakarta)\\.servlet\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.mail.import)
 (#match? @framework.mail.import "^(javax|jakarta)\\.(mail|activation)\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.crypto.import)
 (#match? @framework.crypto.import "^javax\\.crypto\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.jaxrs.import)
 (#match? @framework.jaxrs.import "^(javax|jakarta)\\.ws\\.rs\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.transaction.import)
 (#match? @framework.transaction.import "^(javax|jakarta)\\.transaction\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.validation.import)
 (#match? @framework.validation.import "^(javax|jakarta)\\.validation\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.junit.import)
 (#match? @framework.junit.import "^(org\\.junit|junit\\.framework)\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.mockito.import)
 (#match? @framework.mockito.import "^org\\.mockito\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.itext.import)
 (#match? @framework.itext.import "^com\\.itextpdf\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.firebase.import)
 (#match? @framework.firebase.import "^com\\.google\\.firebase\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.google_auth.import)
 (#match? @framework.google_auth.import "^com\\.google\\.auth\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.netty.import)
 (#match? @framework.netty.import "^(io|reactor)\\.netty\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.json.import)
 (#match? @framework.json.import "^org\\.json\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.thumbnailator.import)
 (#match? @framework.thumbnailator.import "^net\\.coobird\\.thumbnailator\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.nimbus_jose.import)
 (#match? @framework.nimbus_jose.import "^com\\.nimbusds\\.jose\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.jose4j.import)
 (#match? @framework.jose4j.import "^org\\.jose4j\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.jasypt.import)
 (#match? @framework.jasypt.import "^org\\.jasypt\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.jasypt_spring_boot.import)
 (#match? @framework.jasypt_spring_boot.import "^com\\.ulisesbocchio\\.jasyptspringboot\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.jfree.import)
 (#match? @framework.jfree.import "^org\\.jfree\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.javax_annotation.import)
 (#match? @framework.javax_annotation.import "^(javax|jakarta)\\.annotation\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.oracle_driver.import)
 (#match? @framework.oracle_driver.import "^oracle\\.(jdbc|sql)\\."))

((framework_import_declaration
  name: (framework_qualified_name) @framework.sqlserver_driver.import)
 (#match? @framework.sqlserver_driver.import "^com\\.microsoft\\.sqlserver\\.jdbc\\."))

; ---------------------------------------------------------------------------
; Fully-qualified type references.
; Generated SOAP clients often use framework class names directly instead of
; imports, for example `extends org.apache.axis2.client.Stub`.
; ---------------------------------------------------------------------------

((scoped_type_identifier) @framework.axis.qualified_type
 (#match? @framework.axis.qualified_type "^org\\.apache\\.axis2?\\."))

((scoped_type_identifier) @framework.apache_axiom.qualified_type
 (#match? @framework.apache_axiom.qualified_type "^org\\.apache\\.axiom\\."))

((scoped_type_identifier) @framework.apache_commons.qualified_type
 (#match? @framework.apache_commons.qualified_type "^org\\.apache\\.commons\\."))

((field_access) @framework.apache_commons.qualified_access
 (#match? @framework.apache_commons.qualified_access "^org\\.apache\\.commons\\."))

((scoped_type_identifier) @framework.oracle_driver.qualified_type
 (#match? @framework.oracle_driver.qualified_type "^oracle\\.(jdbc|sql)\\."))

((scoped_type_identifier) @framework.sqlserver_driver.qualified_type
 (#match? @framework.sqlserver_driver.qualified_type "^com\\.microsoft\\.sqlserver\\.jdbc\\."))

; Driver class names are commonly stored as configuration constants.

((string_literal) @framework.oracle_driver.driver_class
 (#match? @framework.oracle_driver.driver_class "\"oracle\\.jdbc\\."))

((string_literal) @framework.sqlserver_driver.driver_class
 (#match? @framework.sqlserver_driver.driver_class "\"com\\.microsoft\\.sqlserver\\.jdbc\\."))

; ---------------------------------------------------------------------------
; Annotations
; ---------------------------------------------------------------------------

((framework_marker_annotation
  name: (_) @framework.spring.annotation)
 (#match? @framework.spring.annotation "^(SpringBootApplication|Controller|RestController|ControllerAdvice|RestControllerAdvice|Service|Repository|Component|ComponentScan|Autowired|Bean|Configuration|Qualifier|Value|DependsOn|Primary|PropertySource|Scope|ConfigurationProperties|EnableTransactionManagement|EnableJpaRepositories|EnableAsync|EnableScheduling|EnableCaching|Async|Scheduled|Cacheable|CacheEvict|CrossOrigin|ExceptionHandler|RequestMapping|GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestBody|RequestHeader|RequestParam|PathVariable|ResponseStatus|ResponseBody|Query|Param|Modifying|Transactional|SpringBootTest|Validated|DateTimeFormat)$"))

((framework_annotation
  name: (_) @framework.spring.annotation)
 (#match? @framework.spring.annotation "^(SpringBootApplication|Controller|RestController|ControllerAdvice|RestControllerAdvice|Service|Repository|Component|ComponentScan|Autowired|Bean|Configuration|Qualifier|Value|DependsOn|Primary|PropertySource|Scope|ConfigurationProperties|EnableTransactionManagement|EnableJpaRepositories|EnableAsync|EnableScheduling|EnableCaching|Async|Scheduled|Cacheable|CacheEvict|CrossOrigin|ExceptionHandler|RequestMapping|GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestBody|RequestHeader|RequestParam|PathVariable|ResponseStatus|ResponseBody|Query|Param|Modifying|Transactional|SpringBootTest|Validated|DateTimeFormat)$"))

((framework_marker_annotation
  name: (_) @framework.security.annotation)
 (#match? @framework.security.annotation "^(EnableWebSecurity|EnableGlobalMethodSecurity|PreAuthorize|PostAuthorize)$"))

((framework_annotation
  name: (_) @framework.security.annotation)
 (#match? @framework.security.annotation "^(EnableWebSecurity|EnableGlobalMethodSecurity|PreAuthorize|PostAuthorize)$"))

((framework_marker_annotation
  name: (_) @framework.jpa.annotation)
 (#match? @framework.jpa.annotation "^(Entity|Table|Id|Column|GeneratedValue|SequenceGenerator|NamedQuery|PersistenceContext|Temporal|Lob|PrePersist|PreUpdate|IdClass|Basic|UniqueConstraint|EmbeddedId|ManyToOne|OneToMany|OneToOne|ManyToMany|JoinColumn|JoinTable|Transient|Embeddable|Embedded|MappedSuperclass)$"))

((framework_annotation
  name: (_) @framework.jpa.annotation)
 (#match? @framework.jpa.annotation "^(Entity|Table|Id|Column|GeneratedValue|SequenceGenerator|NamedQuery|PersistenceContext|Temporal|Lob|PrePersist|PreUpdate|IdClass|Basic|UniqueConstraint|EmbeddedId|ManyToOne|OneToMany|OneToOne|ManyToMany|JoinColumn|JoinTable|Transient|Embeddable|Embedded|MappedSuperclass)$"))

((framework_marker_annotation
  name: (_) @framework.hibernate.annotation)
 (#match? @framework.hibernate.annotation "^(GenericGenerator|Nationalized|Type)$"))

((framework_annotation
  name: (_) @framework.hibernate.annotation)
 (#match? @framework.hibernate.annotation "^(GenericGenerator|Nationalized|Type)$"))

((framework_marker_annotation
  name: (_) @framework.jaxb.annotation)
 (#match? @framework.jaxb.annotation "^(XmlRootElement|XmlElement|XmlElementDecl|XmlElementRef|XmlElementWrapper|XmlAccessorType|XmlAttribute|XmlType|XmlSeeAlso|XmlSchemaType|XmlRegistry)$"))

((framework_annotation
  name: (_) @framework.jaxb.annotation)
 (#match? @framework.jaxb.annotation "^(XmlRootElement|XmlElement|XmlElementDecl|XmlElementRef|XmlElementWrapper|XmlAccessorType|XmlAttribute|XmlType|XmlSeeAlso|XmlSchemaType|XmlRegistry)$"))

((framework_marker_annotation
  name: (framework_qualified_annotation_name) @framework.jaxb.annotation)
 (#match? @framework.jaxb.annotation "^(javax|jakarta)\\.xml\\.bind\\.annotation\\."))

((framework_annotation
  name: (framework_qualified_annotation_name) @framework.jaxb.annotation)
 (#match? @framework.jaxb.annotation "^(javax|jakarta)\\.xml\\.bind\\.annotation\\."))

((framework_marker_annotation
  name: (_) @framework.jaxws.annotation)
 (#match? @framework.jaxws.annotation "^(WebService|WebMethod|WebParam|WebResult|RequestWrapper|ResponseWrapper|WebEndpoint|WebServiceClient|WebFault|SOAPBinding)$"))

((framework_annotation
  name: (_) @framework.jaxws.annotation)
 (#match? @framework.jaxws.annotation "^(WebService|WebMethod|WebParam|WebResult|RequestWrapper|ResponseWrapper|WebEndpoint|WebServiceClient|WebFault|SOAPBinding)$"))

((framework_marker_annotation
  name: (_) @framework.jaxrs.annotation)
 (#match? @framework.jaxrs.annotation "^(Path|GET|POST|PUT|DELETE|Produces|Consumes|Context)$"))

((framework_annotation
  name: (_) @framework.jaxrs.annotation)
 (#match? @framework.jaxrs.annotation "^(Path|GET|POST|PUT|DELETE|Produces|Consumes|Context)$"))

((framework_marker_annotation
  name: (_) @framework.lombok.annotation)
 (#match? @framework.lombok.annotation "^(Data|Getter|Setter|Builder|SuperBuilder|NoArgsConstructor|AllArgsConstructor|RequiredArgsConstructor|ToString(?:\\.[A-Za-z_][A-Za-z0-9_]*)?|EqualsAndHashCode(?:\\.[A-Za-z_][A-Za-z0-9_]*)?|Log4j2|Slf4j)$"))

((framework_annotation
  name: (_) @framework.lombok.annotation)
 (#match? @framework.lombok.annotation "^(Data|Getter|Setter|Builder|SuperBuilder|NoArgsConstructor|AllArgsConstructor|RequiredArgsConstructor|ToString(?:\\.[A-Za-z_][A-Za-z0-9_]*)?|EqualsAndHashCode(?:\\.[A-Za-z_][A-Za-z0-9_]*)?|Log4j2|Slf4j)$"))

((framework_marker_annotation
  name: (_) @framework.jackson.annotation)
 (#match? @framework.jackson.annotation "^(JsonProperty|JsonAlias|JsonGetter|JsonSetter|JsonCreator|JsonSerialize|JsonDeserialize|JsonIgnore|JsonIgnoreProperties|JsonInclude|JsonFormat)$"))

((framework_annotation
  name: (_) @framework.jackson.annotation)
 (#match? @framework.jackson.annotation "^(JsonProperty|JsonAlias|JsonGetter|JsonSetter|JsonCreator|JsonSerialize|JsonDeserialize|JsonIgnore|JsonIgnoreProperties|JsonInclude|JsonFormat)$"))

((framework_marker_annotation
  name: (_) @framework.gson.annotation)
 (#match? @framework.gson.annotation "^SerializedName$"))

((framework_annotation
  name: (_) @framework.gson.annotation)
 (#match? @framework.gson.annotation "^SerializedName$"))

((framework_marker_annotation
  name: (_) @framework.xstream.annotation)
 (#match? @framework.xstream.annotation "^(XStreamAlias|XStreamImplicit)$"))

((framework_annotation
  name: (_) @framework.xstream.annotation)
 (#match? @framework.xstream.annotation "^(XStreamAlias|XStreamImplicit)$"))

((framework_marker_annotation
  name: (_) @framework.swagger.annotation)
 (#match? @framework.swagger.annotation "^(Api|ApiOperation|ApiParam|ApiResponse|ApiResponses)$"))

((framework_annotation
  name: (_) @framework.swagger.annotation)
 (#match? @framework.swagger.annotation "^(Api|ApiOperation|ApiParam|ApiResponse|ApiResponses)$"))

((framework_marker_annotation
  name: (_) @framework.aspectj.annotation)
 (#match? @framework.aspectj.annotation "^(Aspect|Around|Before|Pointcut)$"))

((framework_annotation
  name: (_) @framework.aspectj.annotation)
 (#match? @framework.aspectj.annotation "^(Aspect|Around|Before|Pointcut)$"))

((framework_marker_annotation
  name: (_) @framework.validation.annotation)
 (#match? @framework.validation.annotation "^(NotNull|NotBlank|NotEmpty|Size|Min|Max|Pattern|Valid|Email|Positive|Negative|Length|Constraint)$"))

((framework_annotation
  name: (_) @framework.validation.annotation)
 (#match? @framework.validation.annotation "^(NotNull|NotBlank|NotEmpty|Size|Min|Max|Pattern|Valid|Email|Positive|Negative|Length|Constraint)$"))

((framework_marker_annotation
  name: (_) @framework.validation.annotation)
 (#match? @framework.validation.annotation "^Validated$"))

((framework_annotation
  name: (_) @framework.validation.annotation)
 (#match? @framework.validation.annotation "^Validated$"))

((framework_marker_annotation
  name: (_) @framework.transaction.annotation)
 (#match? @framework.transaction.annotation "^Transactional$"))

((framework_annotation
  name: (_) @framework.transaction.annotation)
 (#match? @framework.transaction.annotation "^Transactional$"))

((framework_marker_annotation
  name: (_) @framework.javax_annotation.annotation)
 (#match? @framework.javax_annotation.annotation "^PostConstruct$"))

((framework_annotation
  name: (_) @framework.javax_annotation.annotation)
 (#match? @framework.javax_annotation.annotation "^PostConstruct$"))

((framework_marker_annotation
  name: (_) @framework.jasypt_spring_boot.annotation)
 (#match? @framework.jasypt_spring_boot.annotation "^EnableEncryptableProperties$"))

((framework_annotation
  name: (_) @framework.jasypt_spring_boot.annotation)
 (#match? @framework.jasypt_spring_boot.annotation "^EnableEncryptableProperties$"))

((framework_marker_annotation
  name: (_) @framework.junit.annotation)
 (#match? @framework.junit.annotation "^(Test|Before|After|BeforeEach|AfterEach|BeforeAll|AfterAll|RunWith|ExtendWith)$"))

((framework_annotation
  name: (_) @framework.junit.annotation)
 (#match? @framework.junit.annotation "^(Test|Before|After|BeforeEach|AfterEach|BeforeAll|AfterAll|RunWith|ExtendWith)$"))

((framework_marker_annotation
  name: (_) @framework.mockito.annotation)
 (#match? @framework.mockito.annotation "^(Mock|InjectMocks|Spy|Captor)$"))

((framework_annotation
  name: (_) @framework.mockito.annotation)
 (#match? @framework.mockito.annotation "^(Mock|InjectMocks|Spy|Captor)$"))

((framework_marker_annotation
  name: (_) @framework.springfox.annotation)
 (#match? @framework.springfox.annotation "^EnableSwagger2$"))

((framework_annotation
  name: (_) @framework.springfox.annotation)
 (#match? @framework.springfox.annotation "^EnableSwagger2$"))

; ---------------------------------------------------------------------------
; Literals
; ---------------------------------------------------------------------------

((jdbc_connection_string) @framework.jdbc.connection_string)

((jdbc_connection_string) @framework.oracle_driver.connection_string
 (#match? @framework.oracle_driver.connection_string "^\"jdbc:oracle:"))

((jdbc_connection_string) @framework.sqlserver_driver.connection_string
 (#match? @framework.sqlserver_driver.connection_string "^\"jdbc:sqlserver:"))

; ---------------------------------------------------------------------------
; Calls and constructors kept as query-only heuristics.
; ---------------------------------------------------------------------------

((method_invocation
  object: (identifier) @framework.spring.call.target
  name: (identifier) @framework.spring.call.method)
 (#eq? @framework.spring.call.target "SpringApplication")
 (#eq? @framework.spring.call.method "run"))

((method_invocation
  object: (identifier) @framework.jdbc.call.target
  name: (identifier) @framework.jdbc.call.method)
 (#eq? @framework.jdbc.call.target "DriverManager")
 (#eq? @framework.jdbc.call.method "getConnection"))

((object_creation_expression
  type: (type_identifier) @framework.jdbc.constructor)
 (#match? @framework.jdbc.constructor "^(JdbcTemplate|NamedParameterJdbcTemplate)$"))

((method_invocation
  object: (identifier) @framework.jaxb.call.target
  name: (identifier) @framework.jaxb.call.method)
 (#eq? @framework.jaxb.call.target "JAXBContext")
 (#eq? @framework.jaxb.call.method "newInstance"))

((object_creation_expression
  type: (type_identifier) @framework.spring.constructor)
 (#match? @framework.spring.constructor "^(RestTemplate|Jaxb2Marshaller)$"))

((method_invocation
  object: (identifier) @framework.jasper.call.target
  name: (identifier) @framework.jasper.call.method)
 (#match? @framework.jasper.call.target "^(JasperFillManager|JasperExportManager|JasperCompileManager)$")
 (#match? @framework.jasper.call.method "^(fillReport|exportReportToPdf|exportReportToPdfFile|compileReport)$"))

((method_invocation
  object: (identifier) @framework.jjwt.call.target
  name: (identifier) @framework.jjwt.call.method)
 (#eq? @framework.jjwt.call.target "Jwts")
 (#match? @framework.jjwt.call.method "^(builder|parser|parserBuilder)$"))

((method_invocation
  object: (identifier) @framework.xstream.call.target
  name: (identifier) @framework.xstream.call.method)
 (#eq? @framework.xstream.call.target "XStream")
 (#match? @framework.xstream.call.method "^(toXML|fromXML)$"))

((method_invocation
  object: (identifier) @framework.apache_http.call.target
  name: (identifier) @framework.apache_http.call.method)
 (#eq? @framework.apache_http.call.target "HttpClients")
 (#match? @framework.apache_http.call.method "^(createDefault|custom)$"))

((method_invocation
  object: (identifier) @framework.crypto.call.target
  name: (identifier) @framework.crypto.call.method)
 (#eq? @framework.crypto.call.target "Cipher")
 (#eq? @framework.crypto.call.method "getInstance"))

((method_invocation
  object: (identifier) @framework.firebase.call.target
  name: (identifier) @framework.firebase.call.method)
 (#eq? @framework.firebase.call.target "FirebaseMessaging")
 (#eq? @framework.firebase.call.method "getInstance"))

((method_invocation
  object: (identifier) @framework.firebase.call.target
  name: (identifier) @framework.firebase.call.method)
 (#eq? @framework.firebase.call.target "GoogleCredentials")
 (#eq? @framework.firebase.call.method "fromStream"))

((method_invocation
  object: (identifier) @framework.nimbus_jose.call.target
  name: (identifier) @framework.nimbus_jose.call.method)
 (#eq? @framework.nimbus_jose.call.target "JWEObject")
 (#eq? @framework.nimbus_jose.call.method "parse"))

((object_creation_expression
  type: (type_identifier) @framework.xstream.constructor)
 (#eq? @framework.xstream.constructor "XStream"))

((object_creation_expression
  type: (type_identifier) @framework.jackson.constructor)
 (#eq? @framework.jackson.constructor "ObjectMapper"))

((object_creation_expression
  type: (type_identifier) @framework.gson.constructor)
 (#eq? @framework.gson.constructor "Gson"))

((object_creation_expression
  type: (type_identifier) @framework.bouncycastle.constructor)
 (#eq? @framework.bouncycastle.constructor "BouncyCastleProvider"))

((object_creation_expression
  type: (type_identifier) @framework.springfox.constructor)
 (#eq? @framework.springfox.constructor "Docket"))

((object_creation_expression
  type: (type_identifier) @framework.oracle_driver.constructor)
 (#eq? @framework.oracle_driver.constructor "OracleDataSource"))

((object_creation_expression
  type: (type_identifier) @framework.sqlserver_driver.constructor)
 (#eq? @framework.sqlserver_driver.constructor "SQLServerDataSource"))

((object_creation_expression
  type: (type_identifier) @framework.jasypt.constructor)
 (#match? @framework.jasypt.constructor "^(PooledPBEStringEncryptor|SimpleStringPBEConfig)$"))

((object_creation_expression
  type: (type_identifier) @framework.jose4j.constructor)
 (#eq? @framework.jose4j.constructor "JsonWebEncryption"))

((object_creation_expression
  type: (type_identifier) @framework.json.constructor)
 (#eq? @framework.json.constructor "JSONObject"))
