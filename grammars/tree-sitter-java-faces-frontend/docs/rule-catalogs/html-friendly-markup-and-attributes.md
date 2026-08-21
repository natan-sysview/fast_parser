# HTML-Friendly Markup and Attributes

## Purpose

Jakarta Faces can attach server-side behavior to otherwise ordinary XHTML
elements. Treating the page as plain XML would hide this frontend structure,
so these names receive dedicated nodes.

## Rules

- `faces_element` recognizes conventional `faces:` and `jsf:` element forms.
- `faces_attribute` recognizes `faces:*` and `jsf:*` attributes.
- `passthrough_attribute` recognizes `pt:*` attributes.
- EL inside any of these values is parsed using the regular EL rules.

Examples include `jsf:id`, `jsf:value`, `faces:action`, and client-side
pass-through values such as `pt:placeholder` or `pt:data-*`.

## Why local names are open

HTML-friendly and pass-through attributes are extensible by design. A finite
hard-coded list would reject valid HTML attributes and future additions. The
grammar therefore classifies the namespace family and preserves the complete
local name.

## Boundary

Whether a specific attribute is legal on a specific HTML element is semantic
validation and is outside the parser. Namespace aliases other than the
conventional prefixes remain `qualified_attribute` until a semantic layer
resolves their declarations.

## Sources

- [Jakarta Faces 4.0 specification](https://jakarta.ee/specifications/faces/4.0/jakarta-faces-4.0)
- [Jakarta Faces 4.1 VDL documentation](https://jakarta.ee/specifications/faces/4.1/vdldoc/)
