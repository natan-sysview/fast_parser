# JavaSwing Nodes

This document is generated from `src/node-types.json` and is safe for public release.
It lists named `javaswing_*` nodes, their public field names, and direct child node types.

Generated node count: `213`.

## Summary

| Category | Count |
| --- | ---: |
| `arguments` | 24 |
| `class` | 29 |
| `constant` | 10 |
| `creation` | 27 |
| `field` | 18 |
| `interaction` | 17 |
| `local_declaration` | 17 |
| `selector` | 13 |
| `structure` | 42 |
| `type` | 16 |

## Nodes

| Node | Fields | Direct child types |
| --- | --- | --- |
| `javaswing_action_class` | - | - |
| `javaswing_action_command` | `arguments`, `component`, `event`, `name` | `getActionCommand`, `javaswing_action_command_arguments`, `javaswing_empty_argument_list`, `primary_expression`, `setActionCommand`, `super` |
| `javaswing_action_command_arguments` | `command` | `expression` |
| `javaswing_action_metadata` | `action`, `arguments`, `name` | `javaswing_action_put_value_arguments`, `primary_expression`, `putValue`, `super` |
| `javaswing_action_put_value_arguments` | `key`, `value` | `expression` |
| `javaswing_action_structure` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_action_class`, `marker_annotation` |
| `javaswing_border_arguments` | `border` | `expression`, `javaswing_border_creation`, `javaswing_border_factory_creation` |
| `javaswing_border_assignment` | `arguments`, `component`, `name`, `scroll_pane` | `javaswing_border_arguments`, `javaswing_border_factory_creation`, `primary_expression`, `setBorder`, `setViewportBorder`, `super` |
| `javaswing_border_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_border_type`, `marker_annotation` |
| `javaswing_border_factory_creation` | `arguments`, `factory`, `name` | `BorderFactory`, `argument_list`, `createBevelBorder`, `createCompoundBorder`, `createDashedBorder`, `createEmptyBorder`, `createEtchedBorder`, `createLineBorder`, `createLoweredBevelBorder`, `createLoweredSoftBevelBorder`, `createMatteBorder`, `createRaisedBevelBorder`, `createRaisedSoftBevelBorder`, `createSoftBevelBorder`, `createStrokeBorder`, `createTitledBorder` |
| `javaswing_border_layout_constraint` | - | - |
| `javaswing_border_type` | - | - |
| `javaswing_bounds_geometry` | `arguments`, `component`, `name` | `argument_list`, `primary_expression`, `setBounds`, `setLocation`, `setSize`, `super` |
| `javaswing_box_class` | - | - |
| `javaswing_box_factory` | `arguments`, `box`, `name` | `argument_list`, `createGlue`, `createHorizontalBox`, `createHorizontalGlue`, `createHorizontalStrut`, `createRigidArea`, `createVerticalBox`, `createVerticalGlue`, `createVerticalStrut`, `javaswing_box_class` |
| `javaswing_button_group_class` | - | - |
| `javaswing_button_group_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_button_group_class`, `marker_annotation` |
| `javaswing_button_group_field` | `declarator`, `type` | `javaswing_button_group_class`, `modifiers`, `variable_declarator` |
| `javaswing_button_group_local_declaration` | `declarator`, `type` | `javaswing_button_group_class`, `modifiers`, `variable_declarator` |
| `javaswing_cell_renderer_editor_class` | - | - |
| `javaswing_cell_renderer_editor_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_cell_renderer_editor_class`, `marker_annotation` |
| `javaswing_cell_renderer_editor_field` | `declarator`, `type` | `javaswing_cell_renderer_editor_class`, `modifiers`, `variable_declarator` |
| `javaswing_cell_renderer_editor_interaction` | `arguments`, `name`, `renderer_editor` | `argument_list`, `getCellEditor`, `getCellRenderer`, `getDefaultEditor`, `getDefaultRenderer`, `getHeaderRenderer`, `getListCellRendererComponent`, `getTableCellEditorComponent`, `getTableCellRendererComponent`, `primary_expression`, `setCellEditor`, `setCellRenderer`, `setDefaultEditor`, `setDefaultRenderer`, `setHeaderRenderer`, `super` |
| `javaswing_cell_renderer_editor_local_declaration` | `declarator`, `type` | `javaswing_cell_renderer_editor_class`, `modifiers`, `variable_declarator` |
| `javaswing_combo_box_array_type` | `dimensions`, `element` | `dimensions`, `javaswing_combo_box_class`, `javaswing_combo_box_generic_type` |
| `javaswing_combo_box_class` | - | - |
| `javaswing_combo_box_creation` | `arguments`, `type`, `type_arguments` | `annotation`, `argument_list`, `class_body`, `javaswing_combo_box_creation_type`, `marker_annotation`, `type_arguments` |
| `javaswing_combo_box_creation_type` | - | `javaswing_combo_box_class`, `javaswing_combo_box_generic_type` |
| `javaswing_combo_box_field` | `declarator`, `type` | `javaswing_combo_box_reference_type`, `modifiers`, `variable_declarator` |
| `javaswing_combo_box_generic_type` | `type` | `javaswing_combo_box_class`, `type_arguments` |
| `javaswing_combo_box_interaction` | `arguments`, `combo_box`, `name` | `argument_list`, `configureEditor`, `getEditor`, `getKeySelectionManager`, `getMaximumRowCount`, `getPrototypeDisplayValue`, `getRenderer`, `getSelectedItem`, `hidePopup`, `isPopupVisible`, `primary_expression`, `setEditor`, `setKeySelectionManager`, `setMaximumRowCount`, `setPrototypeDisplayValue`, `setRenderer`, `setSelectedItem`, `showPopup`, `super` |
| `javaswing_combo_box_local_declaration` | `declarator`, `type` | `javaswing_combo_box_reference_type`, `modifiers`, `variable_declarator` |
| `javaswing_combo_box_reference_type` | - | `javaswing_combo_box_array_type`, `javaswing_combo_box_class`, `javaswing_combo_box_generic_type` |
| `javaswing_component_array_type` | `dimensions`, `element` | `dimensions`, `javaswing_component_generic_type`, `javaswing_component_type` |
| `javaswing_component_creation` | `arguments`, `type`, `type_arguments` | `annotation`, `argument_list`, `class_body`, `javaswing_component_creation_type`, `marker_annotation`, `type_arguments` |
| `javaswing_component_creation_type` | - | `javaswing_component_generic_type`, `javaswing_component_type` |
| `javaswing_component_field` | `declarator`, `type` | `javaswing_component_reference_type`, `modifiers`, `variable_declarator` |
| `javaswing_component_generic_type` | `type` | `javaswing_component_type`, `type_arguments` |
| `javaswing_component_popup_menu_arguments` | `popup_menu` | `expression` |
| `javaswing_component_reference_type` | - | `javaswing_component_array_type`, `javaswing_component_generic_type`, `javaswing_component_type` |
| `javaswing_component_type` | - | - |
| `javaswing_container_add` | `arguments`, `container`, `name` | `add`, `javaswing_container_add_arguments`, `javaswing_container_add_border_layout_arguments`, `javaswing_container_add_component_creation_arguments`, `javaswing_content_pane_access`, `primary_expression`, `super` |
| `javaswing_container_add_arguments` | `component`, `constraints`, `index` | `expression` |
| `javaswing_container_add_border_layout_arguments` | `component`, `constraints`, `index` | `expression`, `javaswing_border_layout_constraint` |
| `javaswing_container_add_component_creation_arguments` | `component`, `constraints`, `index` | `expression`, `javaswing_component_creation` |
| `javaswing_content_pane_access` | `arguments`, `name`, `object` | `argument_list`, `getContentPane`, `this` |
| `javaswing_dialog_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_dialog_creation_type`, `marker_annotation` |
| `javaswing_dialog_creation_type` | - | `javaswing_dialog_type` |
| `javaswing_dialog_interaction` | `arguments`, `dialog`, `name` | `argument_list`, `javaswing_option_pane_context_access`, `javaswing_option_pane_dialog`, `primary_expression`, `setModal`, `setModalityType`, `super` |
| `javaswing_dialog_type` | - | - |
| `javaswing_dimension_class` | - | - |
| `javaswing_dimension_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_dimension_class`, `marker_annotation` |
| `javaswing_document_class` | - | - |
| `javaswing_document_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_document_class`, `marker_annotation` |
| `javaswing_document_model` | `arguments`, `selector` | `javaswing_document_model_arguments`, `javaswing_document_model_selector`, `javaswing_get_document_arguments`, `javaswing_get_document_selector` |
| `javaswing_document_model_arguments` | `context`, `document` | `expression` |
| `javaswing_document_model_selector` | - | - |
| `javaswing_empty_argument_list` | - | - |
| `javaswing_event_handler` | `body`, `name`, `parameters`, `type` | `block`, `javaswing_event_handler_name`, `javaswing_event_handler_parameters`, `modifiers`, `throws`, `void_type` |
| `javaswing_event_handler_name` | - | - |
| `javaswing_event_handler_parameters` | `event` | `javaswing_event_parameter` |
| `javaswing_event_listener` | `arguments`, `component`, `name` | `addActionListener`, `addAncestorListener`, `addCaretListener`, `addChangeListener`, `addComponentListener`, `addContainerListener`, `addDocumentListener`, `addFocusListener`, `addHierarchyBoundsListener`, `addHierarchyListener`, `addInputMethodListener`, `addInternalFrameListener`, `addItemListener`, `addKeyListener`, `addListDataListener`, `addListSelectionListener`, `addMenuDragMouseListener`, `addMenuKeyListener`, `addMenuListener`, `addMouseListener`, `addMouseMotionListener`, `addMouseWheelListener`, `addPopupMenuListener`, `addPropertyChangeListener`, `addRowSorterListener`, `addTableColumnModelListener`, `addTableModelListener`, `addTreeExpansionListener`, `addTreeModelListener`, `addTreeSelectionListener`, `addTreeWillExpandListener`, `addUndoableEditListener`, `addVetoableChangeListener`, `addWindowFocusListener`, `addWindowListener`, `addWindowStateListener`, `argument_list`, `primary_expression`, `super` |
| `javaswing_event_parameter` | `dimensions`, `name`, `type` | `dimensions`, `identifier`, `javaswing_event_type`, `modifiers`, `underscore_pattern` |
| `javaswing_event_type` | - | - |
| `javaswing_file_chooser_class` | - | - |
| `javaswing_file_chooser_constant` | `class`, `constant` | `APPROVE_OPTION`, `APPROVE_SELECTION`, `CANCEL_OPTION`, `CANCEL_SELECTION`, `CUSTOM_DIALOG`, `DIRECTORIES_ONLY`, `ERROR_OPTION`, `FILES_AND_DIRECTORIES`, `FILES_ONLY`, `OPEN_DIALOG`, `SAVE_DIALOG`, `javaswing_file_chooser_class` |
| `javaswing_file_chooser_interaction` | `arguments`, `chooser`, `name` | `addChoosableFileFilter`, `approveSelection`, `argument_list`, `cancelSelection`, `changeToParentDirectory`, `getSelectedFile`, `getSelectedFiles`, `isMultiSelectionEnabled`, `primary_expression`, `removeChoosableFileFilter`, `rescanCurrentDirectory`, `resetChoosableFileFilters`, `setAcceptAllFileFilterUsed`, `setApproveButtonMnemonic`, `setApproveButtonText`, `setApproveButtonToolTipText`, `setControlButtonsAreShown`, `setCurrentDirectory`, `setDialogTitle`, `setDialogType`, `setFileFilter`, `setFileSelectionMode`, `setMultiSelectionEnabled`, `setSelectedFile`, `setSelectedFiles`, `showDialog`, `showOpenDialog`, `showSaveDialog`, `super` |
| `javaswing_focus_interaction` | `arguments`, `component`, `name` | `argument_list`, `getInputVerifier`, `primary_expression`, `requestFocusInWindow`, `setFocusTraversalKeysEnabled`, `setInputVerifier`, `super` |
| `javaswing_formatted_text_field_class` | - | - |
| `javaswing_formatted_text_field_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_formatted_text_field_class`, `marker_annotation` |
| `javaswing_formatted_text_field_field` | `declarator`, `type` | `javaswing_formatted_text_field_class`, `modifiers`, `variable_declarator` |
| `javaswing_formatted_text_field_focus_lost_arguments` | `behavior` | `expression` |
| `javaswing_formatted_text_field_focus_lost_constant` | `class`, `constant` | `COMMIT`, `COMMIT_OR_REVERT`, `PERSIST`, `REVERT`, `javaswing_formatted_text_field_class` |
| `javaswing_formatted_text_field_interaction` | `arguments`, `formatted_text_field`, `name` | `getFocusLostBehavior`, `javaswing_formatted_text_field_focus_lost_arguments`, `primary_expression`, `setFocusLostBehavior`, `super` |
| `javaswing_formatted_text_field_local_declaration` | `declarator`, `type` | `javaswing_formatted_text_field_class`, `modifiers`, `variable_declarator` |
| `javaswing_get_document_arguments` | - | - |
| `javaswing_get_document_selector` | - | - |
| `javaswing_grid_bag_constraints_class` | - | - |
| `javaswing_grid_bag_constraints_constant` | `constant` | `BOTH`, `CENTER`, `EAST`, `FIRST_LINE_END`, `FIRST_LINE_START`, `HORIZONTAL`, `LAST_LINE_END`, `LAST_LINE_START`, `LINE_END`, `LINE_START`, `NONE`, `NORTH`, `NORTHEAST`, `NORTHWEST`, `PAGE_END`, `PAGE_START`, `RELATIVE`, `REMAINDER`, `SOUTH`, `SOUTHEAST`, `SOUTHWEST`, `VERTICAL`, `WEST` |
| `javaswing_grid_bag_constraints_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_grid_bag_constraints_class`, `marker_annotation` |
| `javaswing_grid_bag_constraints_field` | `declarator`, `type` | `javaswing_grid_bag_constraints_class`, `modifiers`, `variable_declarator` |
| `javaswing_grid_bag_constraints_local_declaration` | `declarator`, `type` | `javaswing_grid_bag_constraints_class`, `modifiers`, `variable_declarator` |
| `javaswing_grid_bag_layout_model` | `selector`, `value` | `expression`, `javaswing_grid_bag_layout_model_selector` |
| `javaswing_grid_bag_layout_model_selector` | - | - |
| `javaswing_init_components` | `body`, `name`, `parameters`, `type` | `(`, `)`, `block`, `javaswing_init_components_name`, `modifiers`, `throws`, `void_type` |
| `javaswing_init_components_call` | `arguments`, `name` | `javaswing_empty_argument_list`, `javaswing_init_components_name` |
| `javaswing_init_components_name` | - | - |
| `javaswing_insets_class` | - | - |
| `javaswing_insets_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_insets_class`, `marker_annotation` |
| `javaswing_item_model_class` | - | - |
| `javaswing_item_model_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_item_model_class`, `marker_annotation` |
| `javaswing_item_model_field` | `declarator`, `type` | `javaswing_item_model_class`, `modifiers`, `variable_declarator` |
| `javaswing_item_model_interaction` | `arguments`, `model`, `name` | `addElement`, `addItem`, `argument_list`, `getElementAt`, `getIndexOf`, `getItemAt`, `getItemCount`, `insertElementAt`, `insertItemAt`, `primary_expression`, `removeAllItems`, `removeElement`, `removeElementAt`, `removeItem`, `removeItemAt`, `super` |
| `javaswing_item_model_local_declaration` | `declarator`, `type` | `javaswing_item_model_class`, `modifiers`, `variable_declarator` |
| `javaswing_key_stroke_selector` | - | - |
| `javaswing_keyboard_bindings` | `arguments`, `component`, `name`, `selector` | `argument_list`, `getActionMap`, `getInputMap`, `javaswing_key_stroke_selector`, `primary_expression`, `super` |
| `javaswing_layout_assignment` | `arguments`, `container`, `name` | `javaswing_layout_assignment_arguments`, `primary_expression`, `setLayout`, `super` |
| `javaswing_layout_assignment_arguments` | `layout` | `javaswing_layout_creation` |
| `javaswing_layout_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_layout_type`, `marker_annotation` |
| `javaswing_layout_type` | - | - |
| `javaswing_list_class` | - | - |
| `javaswing_list_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_list_class`, `marker_annotation` |
| `javaswing_list_field` | `declarator`, `type` | `javaswing_list_class`, `modifiers`, `variable_declarator` |
| `javaswing_list_local_declaration` | `declarator`, `type` | `javaswing_list_class`, `modifiers`, `variable_declarator` |
| `javaswing_list_selection_interaction` | `arguments`, `selector` | `argument_list`, `javaswing_list_selection_selector` |
| `javaswing_list_selection_selector` | - | - |
| `javaswing_menu_bar_arguments` | `menu_bar` | `expression` |
| `javaswing_menu_structure` | `arguments`, `component`, `name`, `window` | `javaswing_component_popup_menu_arguments`, `javaswing_menu_bar_arguments`, `primary_expression`, `setComponentPopupMenu`, `setJMenuBar`, `super` |
| `javaswing_option_pane_class` | - | - |
| `javaswing_option_pane_constant` | `class`, `constant` | `CANCEL_OPTION`, `CLOSED_OPTION`, `DEFAULT_OPTION`, `ERROR_MESSAGE`, `ICON_PROPERTY`, `INFORMATION_MESSAGE`, `INITIAL_SELECTION_VALUE_PROPERTY`, `INITIAL_VALUE_PROPERTY`, `INPUT_VALUE_PROPERTY`, `MESSAGE_PROPERTY`, `MESSAGE_TYPE_PROPERTY`, `NO_OPTION`, `OK_CANCEL_OPTION`, `OK_OPTION`, `OPTIONS_PROPERTY`, `OPTION_TYPE_PROPERTY`, `PLAIN_MESSAGE`, `QUESTION_MESSAGE`, `SELECTION_VALUES_PROPERTY`, `UNINITIALIZED_VALUE`, `VALUE_PROPERTY`, `WANTS_INPUT_PROPERTY`, `WARNING_MESSAGE`, `YES_NO_CANCEL_OPTION`, `YES_NO_OPTION`, `YES_OPTION`, `javaswing_option_pane_class` |
| `javaswing_option_pane_context_access` | `arguments`, `class`, `name` | `argument_list`, `getDesktopPaneForComponent`, `getFrameForComponent`, `getRootFrame`, `javaswing_option_pane_class`, `setDefaultLocale`, `setRootFrame` |
| `javaswing_option_pane_dialog` | `arguments`, `class`, `name` | `argument_list`, `javaswing_option_pane_class`, `showConfirmDialog`, `showInputDialog`, `showInternalConfirmDialog`, `showInternalInputDialog`, `showInternalMessageDialog`, `showInternalOptionDialog`, `showMessageDialog`, `showOptionDialog` |
| `javaswing_password_field_class` | - | - |
| `javaswing_password_field_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_password_field_class`, `marker_annotation` |
| `javaswing_password_field_field` | `declarator`, `type` | `javaswing_password_field_class`, `modifiers`, `variable_declarator` |
| `javaswing_password_field_local_declaration` | `declarator`, `type` | `javaswing_password_field_class`, `modifiers`, `variable_declarator` |
| `javaswing_popup_menu_interaction` | `arguments`, `name`, `popup_menu` | `javaswing_popup_menu_show_arguments`, `primary_expression`, `show`, `super` |
| `javaswing_popup_menu_show_arguments` | `invoker`, `x`, `y` | `expression` |
| `javaswing_progress_bar_class` | - | - |
| `javaswing_progress_bar_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_progress_bar_class`, `marker_annotation` |
| `javaswing_progress_bar_field` | `declarator`, `type` | `javaswing_progress_bar_class`, `modifiers`, `variable_declarator` |
| `javaswing_progress_bar_interaction` | `arguments`, `selector` | `argument_list`, `javaswing_progress_bar_selector` |
| `javaswing_progress_bar_local_declaration` | `declarator`, `type` | `javaswing_progress_bar_class`, `modifiers`, `variable_declarator` |
| `javaswing_progress_bar_selector` | - | - |
| `javaswing_property_setter` | `arguments`, `component`, `name` | `argument_list`, `primary_expression`, `setAction`, `setAlignmentX`, `setAlignmentY`, `setAlwaysOnTop`, `setBackground`, `setCellEditor`, `setCellRenderer`, `setCursor`, `setDisabledIcon`, `setEchoChar`, `setEditable`, `setEnabled`, `setFocusable`, `setFont`, `setForeground`, `setGridColor`, `setHorizontalAlignment`, `setHorizontalTextPosition`, `setIcon`, `setIntercellSpacing`, `setLabel`, `setListData`, `setLocationRelativeTo`, `setMaximumSize`, `setMinimumSize`, `setMnemonic`, `setModel`, `setOpaque`, `setPreferredScrollableViewportSize`, `setPreferredSize`, `setPressedIcon`, `setRequestFocusEnabled`, `setResizable`, `setRolloverEnabled`, `setRolloverIcon`, `setRowHeight`, `setRowSorter`, `setSelectedIcon`, `setSelectedIndex`, `setShowGrid`, `setShowHorizontalLines`, `setShowVerticalLines`, `setText`, `setTitle`, `setToolTipText`, `setUndecorated`, `setVerticalAlignment`, `setVerticalTextPosition`, `super` |
| `javaswing_root_pane_extended` | `arguments`, `container`, `name` | `argument_list`, `getGlassPane`, `getLayeredPane`, `primary_expression`, `setDefaultButton`, `setGlassPane`, `setLayeredPane`, `super` |
| `javaswing_root_pane_structure` | `arguments`, `container`, `name` | `argument_list`, `getRootPane`, `primary_expression`, `setContentPane`, `super` |
| `javaswing_screen` | `body`, `interfaces`, `name`, `permits`, `superclass`, `type_parameters` | `class_body`, `identifier`, `javaswing_screen_superclass`, `modifiers`, `permits`, `super_interfaces`, `type_parameters` |
| `javaswing_screen_superclass` | `type` | `javaswing_screen_type` |
| `javaswing_screen_type` | - | - |
| `javaswing_scroll_bar_access` | `arguments`, `selector` | `javaswing_empty_argument_list`, `javaswing_scroll_bar_access_selector` |
| `javaswing_scroll_bar_access_selector` | - | - |
| `javaswing_scroll_bar_class` | - | - |
| `javaswing_scroll_bar_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_scroll_bar_class`, `marker_annotation` |
| `javaswing_scroll_bar_field` | `declarator`, `type` | `javaswing_scroll_bar_class`, `modifiers`, `variable_declarator` |
| `javaswing_scroll_bar_increment_interaction` | `arguments`, `selector` | `argument_list`, `javaswing_scroll_bar_increment_selector` |
| `javaswing_scroll_bar_increment_selector` | - | - |
| `javaswing_scroll_bar_local_declaration` | `declarator`, `type` | `javaswing_scroll_bar_class`, `modifiers`, `variable_declarator` |
| `javaswing_scroll_bar_policy_arguments` | `policy` | `expression`, `javaswing_scroll_bar_policy_constant` |
| `javaswing_scroll_bar_policy_constant` | - | - |
| `javaswing_scroll_viewport` | `arguments`, `name`, `scroll_pane` | `javaswing_scroll_bar_policy_arguments`, `javaswing_viewport_view_arguments`, `primary_expression`, `setHorizontalScrollBarPolicy`, `setVerticalScrollBarPolicy`, `setViewportView`, `super` |
| `javaswing_selectable_button_arguments` | - | `expression` |
| `javaswing_selectable_button_class` | - | - |
| `javaswing_selectable_button_class_declaration` | `body`, `interfaces`, `name`, `permits`, `superclass`, `type_parameters` | `class_body`, `identifier`, `javaswing_selectable_button_superclass`, `modifiers`, `permits`, `super_interfaces`, `type_parameters` |
| `javaswing_selectable_button_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_selectable_button_class`, `marker_annotation` |
| `javaswing_selectable_button_field` | `declarator`, `type` | `javaswing_selectable_button_class`, `modifiers`, `variable_declarator` |
| `javaswing_selectable_button_interaction` | `arguments`, `selector` | `javaswing_selectable_button_arguments`, `javaswing_selectable_button_selector` |
| `javaswing_selectable_button_local_declaration` | `declarator`, `type` | `javaswing_selectable_button_class`, `modifiers`, `variable_declarator` |
| `javaswing_selectable_button_selector` | - | - |
| `javaswing_selectable_button_superclass` | `type` | `javaswing_selectable_button_class` |
| `javaswing_selection_flag_arguments` | `enabled` | `expression` |
| `javaswing_selection_mode_arguments` | `mode` | `expression`, `javaswing_selection_mode_constant` |
| `javaswing_selection_mode_constant` | - | - |
| `javaswing_selection_model` | `arguments`, `component`, `name` | `argument_list`, `getSelectionModel`, `javaswing_selection_flag_arguments`, `javaswing_selection_mode_arguments`, `javaswing_selection_model_access`, `javaswing_selection_model_arguments`, `primary_expression`, `setCellSelectionEnabled`, `setColumnSelectionAllowed`, `setRowSelectionAllowed`, `setSelectionMode`, `setSelectionModel`, `super` |
| `javaswing_selection_model_access` | `arguments`, `selector` | `argument_list`, `javaswing_selection_model_access_selector` |
| `javaswing_selection_model_access_selector` | - | - |
| `javaswing_selection_model_arguments` | `model` | `expression` |
| `javaswing_separator_class` | - | - |
| `javaswing_separator_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_separator_class`, `marker_annotation` |
| `javaswing_separator_field` | `declarator`, `type` | `javaswing_separator_class`, `modifiers`, `variable_declarator` |
| `javaswing_separator_local_declaration` | `declarator`, `type` | `javaswing_separator_class`, `modifiers`, `variable_declarator` |
| `javaswing_spinner_class` | - | - |
| `javaswing_spinner_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_spinner_class`, `marker_annotation` |
| `javaswing_spinner_field` | `declarator`, `type` | `javaswing_spinner_class`, `modifiers`, `variable_declarator` |
| `javaswing_spinner_local_declaration` | `declarator`, `type` | `javaswing_spinner_class`, `modifiers`, `variable_declarator` |
| `javaswing_spinner_model_class` | - | - |
| `javaswing_spinner_model_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_spinner_model_class`, `marker_annotation` |
| `javaswing_spinner_model_field` | `declarator`, `type` | `javaswing_spinner_model_class`, `modifiers`, `variable_declarator` |
| `javaswing_spinner_model_local_declaration` | `declarator`, `type` | `javaswing_spinner_model_class`, `modifiers`, `variable_declarator` |
| `javaswing_split_pane_class` | - | - |
| `javaswing_split_pane_constant` | `class`, `constant` | `BOTTOM`, `HORIZONTAL_SPLIT`, `LEFT`, `RIGHT`, `TOP`, `VERTICAL_SPLIT`, `javaswing_split_pane_class` |
| `javaswing_split_pane_interaction` | `arguments`, `name`, `split_pane` | `argument_list`, `getBottomComponent`, `getDividerLocation`, `getLeftComponent`, `getOrientation`, `getResizeWeight`, `getRightComponent`, `getTopComponent`, `isOneTouchExpandable`, `primary_expression`, `resetToPreferredSizes`, `setBottomComponent`, `setDividerLocation`, `setLeftComponent`, `setOneTouchExpandable`, `setOrientation`, `setResizeWeight`, `setRightComponent`, `setTopComponent`, `super` |
| `javaswing_swing_worker_callback` | `body`, `name`, `parameters`, `type` | `_unannotated_type`, `block`, `doInBackground`, `done`, `formal_parameters`, `modifiers`, `throws` |
| `javaswing_swing_worker_class` | - | - |
| `javaswing_swing_worker_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_swing_worker_class`, `javaswing_swing_worker_generic_type`, `marker_annotation` |
| `javaswing_swing_worker_generic_type` | - | `type_arguments`, `type_identifier` |
| `javaswing_tabbed_pane_class` | - | - |
| `javaswing_tabbed_pane_constant` | `class`, `constant` | `BOTTOM`, `LEFT`, `RIGHT`, `SCROLL_TAB_LAYOUT`, `TOP`, `WRAP_TAB_LAYOUT`, `javaswing_tabbed_pane_class` |
| `javaswing_tabbed_pane_interaction` | `arguments`, `name`, `tabbed_pane` | `addTab`, `argument_list`, `getBackgroundAt`, `getComponentAt`, `getDisabledIconAt`, `getForegroundAt`, `getIconAt`, `getMnemonicAt`, `getSelectedComponent`, `getTabComponentAt`, `getTabLayoutPolicy`, `getTabPlacement`, `getTitleAt`, `getToolTipTextAt`, `indexOfComponent`, `indexOfTab`, `indexOfTabComponent`, `insertTab`, `isEnabledAt`, `primary_expression`, `setBackgroundAt`, `setComponentAt`, `setDisabledIconAt`, `setDisplayedMnemonicIndexAt`, `setEnabledAt`, `setForegroundAt`, `setIconAt`, `setMnemonicAt`, `setSelectedComponent`, `setTabComponentAt`, `setTabLayoutPolicy`, `setTabPlacement`, `setTitleAt`, `setToolTipTextAt`, `super` |
| `javaswing_table_auto_resize_arguments` | `mode` | `expression`, `javaswing_table_auto_resize_constant` |
| `javaswing_table_auto_resize_constant` | - | - |
| `javaswing_table_column_model` | `arguments`, `column`, `column_model`, `header`, `name`, `table` | `argument_list`, `getColumnIndex`, `getColumnIndexAtX`, `getColumnMargin`, `getDefaultRenderer`, `getTotalColumnWidth`, `javaswing_table_auto_resize_arguments`, `javaswing_table_column_model_arguments`, `javaswing_table_header_arguments`, `moveColumn`, `primary_expression`, `setAutoResizeMode`, `setColumnMargin`, `setColumnModel`, `setDefaultRenderer`, `setHeaderRenderer`, `setHeaderValue`, `setIdentifier`, `setMaxWidth`, `setMinWidth`, `setModelIndex`, `setPreferredWidth`, `setReorderingAllowed`, `setResizingAllowed`, `setTableHeader`, `super` |
| `javaswing_table_column_model_arguments` | `column_model` | `expression` |
| `javaswing_table_header_arguments` | `header` | `expression` |
| `javaswing_table_model_mutation` | `arguments`, `name`, `table_model` | `addColumn`, `addRow`, `argument_list`, `fireTableCellUpdated`, `fireTableDataChanged`, `fireTableRowsDeleted`, `fireTableRowsInserted`, `fireTableRowsUpdated`, `fireTableStructureChanged`, `insertRow`, `moveRow`, `newRowsAdded`, `primary_expression`, `removeRow`, `rowsRemoved`, `setColumnCount`, `setColumnIdentifiers`, `setDataVector`, `setRowCount`, `setValueAt`, `super` |
| `javaswing_text_editor_class` | - | - |
| `javaswing_text_editor_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_text_editor_class`, `marker_annotation` |
| `javaswing_text_editor_field` | `declarator`, `type` | `javaswing_text_editor_class`, `modifiers`, `variable_declarator` |
| `javaswing_text_editor_interaction` | `arguments`, `name`, `selector` | `addStyle`, `argument_list`, `getContentType`, `getEditorKit`, `getStyledDocument`, `insertComponent`, `insertIcon`, `javaswing_text_editor_selector`, `javaswing_text_editor_set_page_arguments`, `javaswing_text_editor_set_page_selector`, `setCharacterAttributes`, `setContentType`, `setEditorKit`, `setPage`, `setParagraphAttributes`, `setStyledDocument` |
| `javaswing_text_editor_local_declaration` | `declarator`, `type` | `javaswing_text_editor_class`, `modifiers`, `variable_declarator` |
| `javaswing_text_editor_selector` | - | - |
| `javaswing_text_editor_set_page_arguments` | - | `expression` |
| `javaswing_text_editor_set_page_selector` | - | - |
| `javaswing_text_input_alignment_constant` | `class`, `constant` | `CENTER`, `LEADING`, `LEFT`, `RIGHT`, `TRAILING`, `javaswing_text_input_class` |
| `javaswing_text_input_class` | - | - |
| `javaswing_text_input_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_text_input_class`, `marker_annotation` |
| `javaswing_text_input_field` | `declarator`, `type` | `javaswing_text_input_class`, `modifiers`, `variable_declarator` |
| `javaswing_text_input_interaction` | `arguments`, `name`, `text_input` | `argument_list`, `primary_expression`, `setColumns`, `setLineWrap`, `setRows`, `setWrapStyleWord`, `super` |
| `javaswing_text_input_local_declaration` | `declarator`, `type` | `javaswing_text_input_class`, `modifiers`, `variable_declarator` |
| `javaswing_threading_arguments` | - | `expression` |
| `javaswing_threading_invocation` | `arguments`, `selector` | `javaswing_threading_arguments`, `javaswing_threading_selector` |
| `javaswing_threading_selector` | - | - |
| `javaswing_timer_class` | - | - |
| `javaswing_timer_structure` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_timer_class`, `marker_annotation` |
| `javaswing_toolbar_class` | - | - |
| `javaswing_toolbar_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_toolbar_class`, `marker_annotation` |
| `javaswing_toolbar_field` | `declarator`, `type` | `javaswing_toolbar_class`, `modifiers`, `variable_declarator` |
| `javaswing_toolbar_local_declaration` | `declarator`, `type` | `javaswing_toolbar_class`, `modifiers`, `variable_declarator` |
| `javaswing_transfer_handler_class` | - | - |
| `javaswing_transfer_handler_creation` | `arguments`, `type` | `annotation`, `argument_list`, `class_body`, `javaswing_transfer_handler_class`, `marker_annotation` |
| `javaswing_transfer_handler_interaction` | `arguments`, `component`, `name` | `argument_list`, `getTransferHandler`, `primary_expression`, `setDragEnabled`, `setTransferHandler`, `super` |
| `javaswing_viewport_view_arguments` | `view` | `expression` |
| `javaswing_window_lifecycle` | `arguments`, `name`, `window` | `argument_list`, `dispose`, `pack`, `primary_expression`, `setDefaultCloseOperation`, `setVisible`, `super` |
