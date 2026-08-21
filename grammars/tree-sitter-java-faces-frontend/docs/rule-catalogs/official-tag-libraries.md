# Official Jakarta Faces Tag Libraries

## Classification model

Dedicated nodes classify the conventional prefixes used by the official
Jakarta Faces libraries. The complete Jakarta Faces 4.1 VDL catalog is listed
below. The grammar intentionally accepts any local tag name in each family so
older Faces releases and forward-compatible additions remain parseable.

XML namespace aliases are arbitrary. Tree-sitter cannot resolve an alias to a
namespace URI at parse time, so a library written with a non-conventional alias
is retained as `qualified_element`. A semantic indexing layer may later use
`namespace_declaration` nodes to reclassify it.

## HTML components (`h`)

Grammar node: `jsf_html_element`.

`body`, `button`, `column`, `commandButton`, `commandLink`, `commandScript`,
`dataTable`, `doctype`, `form`, `graphicImage`, `head`, `inputFile`,
`inputHidden`, `inputSecret`, `inputText`, `inputTextarea`, `link`, `message`,
`messages`, `outputFormat`, `outputLabel`, `outputLink`, `outputScript`,
`outputStylesheet`, `outputText`, `panelGrid`, `panelGroup`,
`selectBooleanCheckbox`, `selectManyCheckbox`, `selectManyListbox`,
`selectManyMenu`, `selectOneListbox`, `selectOneMenu`, and `selectOneRadio`.

## Core tags (`f`)

Grammar node: `jsf_core_element`.

`actionListener`, `ajax`, `attribute`, `attributes`, `convertDateTime`,
`converter`, `convertNumber`, `event`, `facet`, `importConstants`,
`loadBundle`, `metadata`, `param`, `passThroughAttribute`,
`passThroughAttributes`, `phaseListener`, `selectItem`, `selectItemGroup`,
`selectItemGroups`, `selectItems`, `setPropertyActionListener`, `subview`,
`validateBean`, `validateDoubleRange`, `validateLength`, `validateLongRange`,
`validateRegex`, `validateRequired`, `validateWholeBean`, `validator`,
`valueChangeListener`, `view`, `viewAction`, `viewParam`, and `websocket`.

## Facelets templating (`ui`)

Grammar node: `facelets_element`.

`component`, `composition`, `debug`, `decorate`, `define`, `fragment`,
`include`, `insert`, `param`, `remove`, and `repeat`.

## Composite components (`cc`)

Grammar node: `composite_component_element`.

`actionSource`, `attribute`, `clientBehavior`, `editableValueHolder`,
`extension`, `facet`, `implementation`, `insertChildren`, `insertFacet`,
`interface`, `renderFacet`, and `valueHolder`.

## HTML-friendly elements (`faces` or `jsf`)

Grammar node: `faces_element`.

The standard VDL family contains `element`. The grammar accepts both common
prefix spellings because applications use `faces:` for elements and often
`jsf:` for HTML-friendly attributes.

## Pass-through attributes (`pt`)

Grammar node: `passthrough_attribute`.

The local name is intentionally open-ended: pass-through attributes represent
arbitrary client-side attributes rather than a finite Faces component catalog.

## JSTL core (`c`)

Grammar node: `jstl_element`.

`catch`, `choose`, `forEach`, `if`, `otherwise`, `set`, and `when`.

JSTL is standardized separately from Jakarta Faces, but it is part of the
official Facelets VDL documentation and is commonly evaluated while a view is
built.

## JSTL functions (`fn`)

These appear as `el_function_call` within Expression Language rather than as
elements: `contains`, `containsIgnoreCase`, `endsWith`, `escapeXml`, `indexOf`,
`join`, `length`, `replace`, `split`, `startsWith`, `substring`,
`substringAfter`, `substringBefore`, `toLowerCase`, `toUpperCase`, and `trim`.

## Source

- [Jakarta Faces 4.1 VDL all tags](https://jakarta.ee/specifications/faces/4.1/vdldoc/alltags-frame.html)
