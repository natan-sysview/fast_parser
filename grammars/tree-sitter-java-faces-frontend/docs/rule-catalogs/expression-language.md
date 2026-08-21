# Jakarta Expression Language

## Purpose

Expression Language is parsed as syntax rather than opaque attribute text.
Both deferred (`#{...}`) and immediate (`${...}`) forms are recognized in
element text and quoted attribute values, including multiple expressions mixed
with literal text.

## Covered syntax

- Identifiers, booleans, `null`, integers, decimals, exponents, and strings
- Property access, safe bracket indexing, method calls, and chained calls
- Namespaced functions such as `fn:length(items)`
- Unary `not`, `!`, `empty`, unary plus, and unary minus
- Multiplication, division (`/` or `div`), modulo (`%` or `mod`), addition,
  subtraction, and string concatenation (`+=`)
- Relational, equality, logical AND/OR, `instanceof`, and ternary expressions
- XML-escaped operators such as `&lt;`, `&gt;`, and `&amp;&amp;`
- Assignment and semicolon-separated expression sequences
- Lambda parameters, lambda bodies, and invocation
- List, set, and map collection literals

## Grammar nodes

- `expression_language`, `deferred_expression`, and `immediate_expression`
- `el_property_access`, `el_index_access`, `el_method_call`, and
  `el_function_call`
- `el_unary_expression`, `el_binary_expression`, `el_ternary_expression`, and
  `el_assignment_expression`
- `el_lambda_expression`, `el_invocation_expression`, and
  `el_sequence_expression`
- `el_list_literal`, `el_set_literal`, and `el_map_literal`

## Important lexical decision

A qualified EL name is scanned as a function name only when followed by `(`.
This prevents the colon in a no-whitespace ternary expression from being
mistaken for the colon in `prefix:function(...)`.

## Boundary

The grammar does not resolve beans, Java types, methods, variables, converters,
validators, or function libraries. Those require application and runtime
metadata. It guarantees a structural AST for supported EL syntax.

## Source

- [Jakarta Expression Language 6.0 specification](https://jakarta.ee/specifications/expression-language/6.0/jakarta-expression-language-spec-6.0)
