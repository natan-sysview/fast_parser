# Facelets Document Structure

## Purpose

This rule family preserves the XML/XHTML document structure required by
Facelets while exposing framework-aware element nodes. It covers XML
declarations, doctypes, processing instructions, comments, CDATA, entities,
namespaces, attributes, mixed content, empty elements, and matching start/end
tags.

## Grammar nodes

- `document`, `prolog`, `XMLDecl`, and `doctypedecl`
- `xml_element` for unqualified XML/XHTML elements
- `qualified_element` for namespaced libraries that are not assigned a
  dedicated framework family
- `namespace_declaration`, `qualified_attribute`, and `plain_attribute`
- `CharData`, `CDSect`, references, comments, and processing instructions

The external scanner maintains a stack of element names. A closing tag must
match its opening tag; malformed closing names are exposed through an error
node instead of silently accepting invalid nesting.

## Supported document styles

- XHTML Facelets pages and templates
- XML-style self-closing tags
- HTML5-friendly Facelets markup serialized as XHTML
- JSPX-style qualified roots used by legacy Faces applications
- Embedded script/style text, including CDATA sections

## Boundary

The grammar validates source structure, not XML schemas, tag-library
descriptors, component availability, or browser HTML semantics. It deliberately
keeps unknown namespaces as `qualified_element` so vendor and application
component libraries remain lossless and queryable.

## Sources

- [Jakarta Faces 4.1 specification](https://jakarta.ee/specifications/faces/4.1/jakarta-faces-4.1.pdf)
- [Jakarta Faces 4.1 VDL documentation](https://jakarta.ee/specifications/faces/4.1/vdldoc/)
