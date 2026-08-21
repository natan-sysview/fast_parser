;; Document structure

"xml" @keyword
["version" "encoding" "standalone"] @property
(EncName) @string.special
(VersionNum) @number
["yes" "no"] @boolean

(doctypedecl "DOCTYPE" @keyword)
(doctypedecl (Name) @type)
(PI (PITarget) @keyword)
(XmlModelPI "xml-model" @keyword)
(StyleSheetPI "xml-stylesheet" @keyword)
(Comment) @comment

;; Framework element families

(facelets_start_tag name: (tag_name) @tag.builtin)
(facelets_end_tag name: (tag_name) @tag.builtin)
(facelets_empty_element name: (tag_name) @tag.builtin)

(jsf_html_start_tag name: (tag_name) @tag)
(jsf_html_end_tag name: (tag_name) @tag)
(jsf_html_empty_element name: (tag_name) @tag)

(jsf_core_start_tag name: (tag_name) @tag.builtin)
(jsf_core_end_tag name: (tag_name) @tag.builtin)
(jsf_core_empty_element name: (tag_name) @tag.builtin)

(composite_component_start_tag name: (tag_name) @type)
(composite_component_end_tag name: (tag_name) @type)
(composite_component_empty_element name: (tag_name) @type)

(faces_start_tag name: (tag_name) @tag.builtin)
(faces_end_tag name: (tag_name) @tag.builtin)
(faces_empty_element name: (tag_name) @tag.builtin)

(primefaces_start_tag name: (tag_name) @tag)
(primefaces_end_tag name: (tag_name) @tag)
(primefaces_empty_element name: (tag_name) @tag)

(primefaces_extensions_start_tag name: (tag_name) @tag)
(primefaces_extensions_end_tag name: (tag_name) @tag)
(primefaces_extensions_empty_element name: (tag_name) @tag)

(jstl_start_tag name: (tag_name) @keyword)
(jstl_end_tag name: (tag_name) @keyword)
(jstl_empty_element name: (tag_name) @keyword)

(qualified_start_tag name: (tag_name) @tag)
(qualified_end_tag name: (tag_name) @tag)
(qualified_empty_element name: (tag_name) @tag)
(xml_start_tag name: (tag_name) @tag)
(xml_end_tag name: (tag_name) @tag)
(xml_empty_element name: (tag_name) @tag)

;; Attributes and XML values

(namespace_declaration name: (attribute_name) @keyword)
(faces_attribute name: (attribute_name) @property)
(passthrough_attribute name: (attribute_name) @property)
(qualified_attribute name: (attribute_name) @property)
(plain_attribute name: (attribute_name) @property)

(double_quoted_attribute_text) @string
(single_quoted_attribute_text) @string
(PseudoAttValue) @string
(EntityRef) @constant
(CharRef) @constant

;; Expression Language

["#{" "${" "}"] @punctuation.special
(el_identifier) @variable
(el_function_name) @function.call
(el_property_suffix property: (el_identifier) @property)
(el_boolean) @boolean
(el_null) @constant.builtin
(el_integer) @number
(el_floating_point) @number.float
(el_string) @string
(el_not_operator) @operator
(el_empty_operator) @operator

["!" "?" "=" ";" "," "+" "-" "*" "%"] @operator

["(" ")" "[" "]" "{" "}"] @punctuation.bracket
["<?" "?>" "<!" "]]>" "<" ">" "</" "/>"] @punctuation.delimiter

(CharData) @markup
(CData) @markup.raw
(ERROR) @error
