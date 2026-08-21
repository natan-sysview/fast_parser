# Composite Components

## Purpose

Composite components define reusable Faces UI components in XHTML. Their
interface and implementation are frontend architecture, so they receive a
dedicated `composite_component_element` family instead of generic XML nodes.

## Official tags

`actionSource`, `attribute`, `clientBehavior`, `editableValueHolder`,
`extension`, `facet`, `implementation`, `insertChildren`, `insertFacet`,
`interface`, `renderFacet`, and `valueHolder`.

The corpus covers interface declarations, attributes, facets, implementation
content, rendered facets, and child insertion. EL such as `#{cc.attrs.value}`
is parsed structurally inside the implementation.

## Consumer-side components

Applications consume composite components using a namespace URI associated
with a resource library. Since the prefix is application-defined, those uses
are represented by `qualified_element`; their full qualified tag name and
attributes remain available for later namespace resolution.

## Boundary

The grammar does not inspect resource-library folders, infer component
contracts from Java classes, or verify that declared facets and attributes are
used correctly.

## Source

- [Jakarta Faces 4.1 VDL composite tags](https://jakarta.ee/specifications/faces/4.1/vdldoc/cc/tld-summary.html)
