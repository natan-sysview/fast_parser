# Tree-sitter Java Faces Frontend

Tree-sitter grammar for Jakarta Faces/JavaServer Faces frontend sources. It
parses Facelets XHTML, embedded Jakarta Expression Language, official Faces
tag families, composite components, HTML-friendly markup, PrimeFaces, JSTL,
and generic application component libraries.

## Node families

- `facelets_element`: conventional `ui:*` tags.
- `jsf_html_element`: conventional `h:*` components.
- `jsf_core_element`: conventional `f:*` tags.
- `composite_component_element`: conventional `cc:*` definitions.
- `faces_element`: HTML-friendly `faces:*` and `jsf:*` elements.
- `primefaces_element`: conventional `p:*` components.
- `primefaces_extensions_element`: `pe:*` and compatible extension aliases.
- `jstl_element`: conventional `c:*` control tags.
- `qualified_element`: vendor and application component libraries.
- `xml_element`: ordinary XHTML/XML elements.
- `deferred_expression` and `immediate_expression`: structural Jakarta EL.

## Tree-sitter validation

```sh
npm install
npm test
```

The corpus covers standard Faces families, composite components,
HTML-friendly attributes, pass-through attributes, PrimeFaces extensions,
JSTL, Jakarta EL operators/lambdas/collections, and inherited XML behavior.

## FastParse

The native extension is under `extensions/java-faces-frontend` and uses the
canonical FastParse language name `java-faces-frontend`.

From the repository root:

```sh
cmake -S . -B build-java-faces-frontend -DCMAKE_BUILD_TYPE=Release
cmake --build build-java-faces-frontend --config Release \
  --target tsmp fastparse_language_java_faces_frontend
python scripts/validate_java_faces_frontend_extension.py
```

The validator loads the extension, parses MessagePack, checks diagnostics and
named rules, executes a Tree-sitter query, and repeats parsing concurrently.

## Boundaries

Tree-sitter parses syntax. It does not resolve managed beans, Java methods,
runtime converters/validators, schemas, tag-library classes, or dependency
versions. XML namespace aliases that do not use conventional prefixes remain
lossless qualified nodes for a later semantic resolution layer.

See `docs/rule-catalogs` for official catalogs and rule boundaries, and
`docs/validation.md` for the current evidence.
