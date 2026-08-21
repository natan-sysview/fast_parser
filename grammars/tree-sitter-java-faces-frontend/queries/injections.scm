;; Embedded JavaScript in ordinary XHTML script elements.

(xml_element
  open: (xml_start_tag
    name: (tag_name) @_script)
  body: (content
    (CharData) @injection.content)
  (#eq? @_script "script")
  (#set! injection.language "javascript"))

(xml_element
  open: (xml_start_tag
    name: (tag_name) @_script)
  body: (content
    (CDSect (CData) @injection.content))
  (#eq? @_script "script")
  (#set! injection.language "javascript"))

;; Embedded CSS in ordinary XHTML style elements.

(xml_element
  open: (xml_start_tag
    name: (tag_name) @_style)
  body: (content
    (CharData) @injection.content)
  (#eq? @_style "style")
  (#set! injection.language "css"))

(xml_element
  open: (xml_start_tag
    name: (tag_name) @_style)
  body: (content
    (CDSect (CData) @injection.content))
  (#eq? @_style "style")
  (#set! injection.language "css"))
