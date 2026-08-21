# PrimeFaces Extension Families

## Scope

PrimeFaces is not part of the Jakarta Faces standard library. It is included as
an explicit extension family because the inventory is a PrimeFaces application
and framework-aware nodes are useful to downstream analyzers.

## Grammar nodes

- `primefaces_element` for the conventional `p:*` family
- `primefaces_extensions_element` for `pe:*` and the observed legacy/custom
  alias `poue:*`

The local tag name is intentionally open-ended. PrimeFaces catalogs vary by
version and edition; parsing should remain stable across upgrades. The grammar
classifies the family while preserving each complete tag name, attribute, and
embedded EL expression.

## Other component libraries

Customer and third-party prefixes such as `mnx`, `monex`, and `fmnx` are
represented as `qualified_element`. They are not folded into PrimeFaces or the
official Jakarta Faces catalog.

## Boundary

The parser does not validate widget availability, PrimeFaces version,
JavaScript widget variables, AJAX behavior, or server-side component classes.
Those are semantic concerns for an indexer built on top of this syntax tree.

## Sources

- [PrimeFaces VDL documentation](https://primefaces.github.io/primefaces/vdldoc/)
- [PrimeFaces Extensions project](https://github.com/primefaces-extensions/primefaces-extensions)
