# Rule Catalog: jsf_backend

## Purpose

Detect JavaServer Faces backend evidence in Java source files.

This rule covers Java-side JSF syntax: imports, framework annotations, core JSF
types, CDI annotations commonly used as JSF backing beans, and PrimeFaces
backend API usage.

## Official Basis

- Jakarta Faces API package catalog:
  https://jakarta.ee/specifications/faces/4.0/apidocs/jakarta/faces/package-summary
- Jakarta `FacesContext` API:
  https://jakarta.ee/specifications/faces/4.0/apidocs/jakarta/faces/context/facescontext
- JavaServer Faces 2.3 / `javax.faces` package catalog:
  https://javaee.github.io/javaserverfaces/docs/2.3/javadocs/overview-summary.html

## Included Forms

### Import roots

- `javax.faces.*`
- `jakarta.faces.*`
- `org.primefaces.*`
- `javax.inject.*`
- `jakarta.inject.*`

### JSF annotations

- Bean/scopes: `ManagedBean`, `ManagedProperty`, `NoneScoped`,
  `RequestScoped`, `SessionScoped`, `ApplicationScoped`, `ViewScoped`,
  `CustomScoped`
- Injection maps: `ApplicationMap`, `FlowMap`, `HeaderMap`, `HeaderValuesMap`,
  `InitParameterMap`, `RequestCookieMap`, `RequestMap`,
  `RequestParameterMap`, `RequestParameterValuesMap`, `SessionMap`, `ViewMap`
- Components/behavior: `FacesComponent`, `FacesBehavior`
- Conversion/validation: `FacesConverter`, `FacesValidator`
- Events/resources/flow: `ListenerFor`, `ListenersFor`, `NamedEvent`,
  `ResourceDependency`, `ResourceDependencies`, `FlowScoped`

### CDI annotations used by JSF backing beans

- `Named`
- `Inject`

### Grammar nodes

- `jsf_backend_type`: unambiguous JSF backend types such as `FacesContext`,
  `ExternalContext`, `ExternalContextFactory`, `FacesMessage`, `UIComponent`,
  `SystemEventListener`, `PhaseListener`, `UIViewRoot`, `SelectItem`,
  `NavigationHandler`, `ViewHandler`, and wrapper/factory types.
- `jsf_backend_generic_type`: JSF backend types with Java type arguments.
- `jsf_context_method_invocation`: static `FacesContext` entry points such as
  `FacesContext.getCurrentInstance(...)`, `responseComplete(...)`,
  `renderResponse(...)`, and context accessors.
- `jsf_backend_static_field_access`: static fields on unambiguous JSF backend
  types, for example `FacesMessage.SEVERITY_INFO`.
- `jsf_backend_object_creation_expression`: constructors such as
  `new FacesMessage(...)`.
- `primefaces_backend_type`, `primefaces_backend_generic_type`,
  `primefaces_backend_method_invocation`, and
  `primefaces_backend_object_creation_expression` for backend Java API usage.
- PrimeFaces backend model/event types observed in real Java source:
  `DefaultMenuItem`, `DefaultMenuModel`, `DefaultSubMenu`,
  `DynamicMenuModel`, `MenuElement`, `MenuModel`, `SelectEvent`,
  `DefaultStreamedContent`, `StreamedContent`, `LazyDataModel`,
  `DefaultTreeNode`, `TreeNode`, `RequestContext`, and `PrimeFaces`.

### Query captures

- JSF imports, annotations, qualified types, type nodes, constructors, static
  fields, context calls, annotated backend classes, implemented/extended
  official backend contracts, and contract methods with JSF parameter types.
- PrimeFaces imports, backend types, constructors, and backend API calls.

## Excluded Forms

- Client-specific Monex classes such as `ManagedBeanMonex` or
  `UtilidadesFaces`.
- Semantic links between external view expressions and Java bean methods.
- Bare ambiguous Java type names when the local source text cannot prove they
  are JSF. Examples intentionally kept generic: `Validator`, `Application`,
  `Resource`, `Renderer`, `StateManager`, `ActionListener`, and `Converter`.

## Local Syntax Supported

- Regular imports and static imports.
- Marker annotations such as `@ViewScoped`.
- Annotations with arguments such as `@ManagedBean(name = "sesionControlador")`
  and `@FacesConverter(value = "seguMenuConverter")`.
- Fully-qualified annotation names under `javax.faces` or `jakarta.faces`.
- Fully-qualified type references under `javax.faces`, `jakarta.faces`, and
  `org.primefaces`.
- `extends` and `implements` clauses when the type is locally unambiguous, such
  as `ExternalContextFactory`, `SystemEventListener`, or `PhaseListener`.
- JSF contract methods such as `getAsObject`, `getAsString`, `validate`,
  `processEvent`, `beforePhase`, `afterPhase`, and `isListenerForSource` when
  the method signature includes JSF backend parameter types.

## Known Semantic Limits

The grammar cannot prove that `@Named` is serving a JSF page, nor can it resolve
custom superclasses or injected beans. Those are intentionally handled as query
or audit evidence, not as parser semantics.

Static-import calls named `getCurrentInstance(...)` are not captured as JSF calls
by themselves because the same local call name can come from JSF `FacesContext`
or PrimeFaces `RequestContext`. The static import line remains captured as an
import; call attribution belongs in a semantic pass that can link imports.

Bare `Validator` is intentionally not a `jsf_backend_type`. A regression audit
found a real `javax.validation.Validator` field in the non-JSF framework
inventory, so this grammar only classifies validator classes through stronger
JSF evidence such as `@FacesValidator` and method signatures that contain
`FacesContext` / `UIComponent`.

Bare `Application` and `Converter` are also intentionally generic unless
stronger local syntax identifies the JSF contract. The real JSF backend corpus
still captures those files through imports, JSF annotations, implemented
contracts, and method signatures.

## Corpus Basis

The rule is based on official JavaServer Faces / Jakarta Faces API package
families and on the Monex PrimeFaces inventory root:

`/Users/natanbarronlugo/Desktop/Proyectos/componentes/monex-java/primefaces`

Observed examples include `@ManagedBean`, `@ViewScoped`, `@SessionScoped`,
`@FacesConverter`, `@ManagedProperty`, `FacesContext`, static
`FacesContext.getCurrentInstance`, `RequestContext`, `ExternalContextFactory`,
`SystemEventListener`, `FacesMessage`, and PrimeFaces model types.

## Audit Summary

- Corpus: 7/7 passed.
- PrimeFaces Java inventory: 196 files, 0 hard failures, 0 `ERROR`, 0
  `MISSING`.
- Full Java/frameworks inventory: 3706 files, 0 hard failures, 0 `ERROR`, 0
  `MISSING`.
- PrimeFaces query audit: 196 files, 106 files with captures, 0 query failures.
- Mifel framework regression query audit: 2264 files, 1824 files with captures,
  0 query failures, 0 JSF false positives after removing ambiguous bare types.
- PrimeFaces imported type closure: all observed `org.primefaces.*` imported
  simple type names in the current Java backend corpus are represented by
  `primefaces_backend_type`.
