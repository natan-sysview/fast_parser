; Swing-oriented query layer for tree-sitter-javaswing.

; Public grammar nodes

(javaswing_screen) @swing.screen
(javaswing_component_field) @swing.component.field
(javaswing_component_creation) @swing.component.creation
(javaswing_container_add) @swing.container.add
(javaswing_init_components) @swing.init_components
(javaswing_event_listener) @swing.event.listener
(javaswing_event_handler) @swing.event.handler
(javaswing_layout_assignment) @swing.layout.assignment
(javaswing_bounds_geometry) @swing.geometry.bounds
(javaswing_border_assignment) @swing.border.assignment
(javaswing_menu_structure) @swing.menu.structure
(javaswing_toolbar_creation) @swing.toolbar.creation
(javaswing_toolbar_field) @swing.toolbar.field
(javaswing_dialog_interaction) @swing.dialog.interaction
(javaswing_file_chooser_interaction) @swing.file_chooser.interaction
(javaswing_table_model_mutation) @swing.table.model_mutation
(javaswing_table_column_model) @swing.table.column_model
(javaswing_list_selection_interaction) @swing.list.selection
(javaswing_combo_box_interaction) @swing.combo_box.interaction
(javaswing_spinner_model_creation) @swing.spinner.model
(javaswing_text_input_interaction) @swing.text_input.interaction
(javaswing_text_editor_interaction) @swing.text_editor.interaction
(javaswing_root_pane_structure) @swing.root_pane.structure
(javaswing_tabbed_pane_interaction) @swing.tabbed_pane.interaction
(javaswing_split_pane_interaction) @swing.split_pane.interaction
(javaswing_scroll_viewport) @swing.scroll.viewport
(javaswing_action_structure) @swing.action.structure
(javaswing_action_metadata) @swing.action.metadata
(javaswing_timer_structure) @swing.timer.structure
(javaswing_swing_worker_creation) @swing.worker.creation
(javaswing_threading_invocation) @swing.threading.invocation
(javaswing_focus_interaction) @swing.focus.interaction
(javaswing_transfer_handler_interaction) @swing.transfer_handler.interaction

((import_declaration
  (scoped_identifier
    scope: (scoped_identifier
      scope: (identifier) @swing.import.root
      name: (identifier) @swing.import.package)
    name: (identifier) @swing.import.type))
  (#eq? @swing.import.root "javax")
  (#eq? @swing.import.package "swing"))

((import_declaration
  (scoped_identifier
    scope: (identifier) @swing.import.root
    name: (identifier) @swing.import.package)
  (asterisk) @swing.import.wildcard)
  (#eq? @swing.import.root "javax")
  (#eq? @swing.import.package "swing"))

((class_declaration
  name: (identifier) @swing.class.name
  superclass: (superclass
    (type_identifier) @swing.class.superclass))
  (#match? @swing.class.superclass "^(JPanel|JFrame|JDialog|JWindow|JApplet)$"))

((method_declaration
  name: (identifier) @swing.init.method)
  (#eq? @swing.init.method "initComponents"))

((field_declaration
  type: (type_identifier) @swing.field.type
  declarator: (variable_declarator
    name: (identifier) @swing.field.name))
  (#match? @swing.field.type "^(J[A-Z][A-Za-z0-9_]*|AbstractButton|ButtonGroup|TableModel|ListModel|ComboBoxModel)$"))

((assignment_expression
  left: (identifier) @swing.component.name
  right: (object_creation_expression
    type: (type_identifier) @swing.component.type))
  (#match? @swing.component.type "^(J[A-Z][A-Za-z0-9_]*|GroupLayout|GridBagLayout|BorderLayout|FlowLayout)$"))

((method_invocation
  name: (identifier) @swing.listener.method)
  (#match? @swing.listener.method "^add.*Listener$"))

((method_invocation
  name: (identifier) @swing.layout.method)
  (#match? @swing.layout.method "^(setLayout|setBounds|setPreferredSize|add)$"))
