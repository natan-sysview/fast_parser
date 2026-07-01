/**
 * @file Java Swing grammar for tree-sitter
 * @author Ayman Nadeem <aymannadeem@github.com>
 * @author Max Brunsfeld <maxbrunsfeld@gmail.com>
 * @author Amaan Qureshi <amaanq12@gmail.com>
 * @license MIT
 */

/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

const DIGITS = token(choice('0', seq(/[1-9]/, optional(seq(optional('_'), sep1(/[0-9]+/, /_+/))))));
const DECIMAL_DIGITS = token(sep1(/[0-9]+/, '_'));
const HEX_DIGITS = token(sep1(/[A-Fa-f0-9]+/, '_'));

/* eslint-disable no-multi-spaces */

const PREC = {
  // https://introcs.cs.princeton.edu/java/11precedence/
  COMMENT: 0,         // //  /*  */
  ASSIGN: 1,          // =  += -=  *=  /=  %=  &=  ^=  |=  <<=  >>=  >>>=
  DECL: 2,
  ELEMENT_VAL: 2,
  TERNARY: 3,         // ?:
  OR: 4,              // ||
  AND: 5,             // &&
  BIT_OR: 6,          // |
  BIT_XOR: 7,         // ^
  BIT_AND: 8,         // &
  EQUALITY: 9,        // ==  !=
  GENERIC: 10,
  REL: 10,            // <  <=  >  >=  instanceof
  SHIFT: 11,          // <<  >>  >>>
  ADD: 12,            // +  -
  MULT: 13,           // *  /  %
  CAST: 14,           // (Type)
  OBJ_INST: 14,       // new
  UNARY: 15,          // ++a  --a  a++  a--  +  -  !  ~
  ARRAY: 16,          // [Index]
  OBJ_ACCESS: 16,     // .
  PARENS: 16,         // (Expression)
  CLASS_LITERAL: 17,  // .
};

/* eslint-enable no-multi-spaces */

const JAVASWING_SCREEN_SWING_TYPES = [
  'JFrame',
  'JDialog',
  'JWindow',
  'JInternalFrame',
  'JApplet',
  'JPanel',
  'JComponent',
  'JDesktopPane',
  'JLayeredPane',
  'JRootPane',
  'JScrollPane',
  'JSplitPane',
  'JTabbedPane',
  'JViewport',
  'Box',
  'JToolBar',
];

const JAVASWING_SCREEN_AWT_TYPES = [
  'Window',
  'Frame',
  'Dialog',
  'FileDialog',
  'Panel',
  'Container',
  'ScrollPane',
  'Canvas',
];

const JAVASWING_COMPONENT_SWING_TYPES = [
  'AbstractButton',
  'Box',
  'CellRendererPane',
  'JApplet',
  'JButton',
  'JColorChooser',
  'JComponent',
  'JDesktopPane',
  'JFileChooser',
  'JFrame',
  'JInternalFrame',
  'JLabel',
  'JLayer',
  'JLayeredPane',
  'JMenu',
  'JMenuBar',
  'JMenuItem',
  'JPanel',
  'JPopupMenu',
  'JRootPane',
  'JScrollPane',
  'JSlider',
  'JSplitPane',
  'JTabbedPane',
  'JTable',
  'JToolTip',
  'JTree',
  'JViewport',
  'JWindow',
];

const JAVASWING_LAYOUT_TYPES = [
  'BorderLayout',
  'BoxLayout',
  'CardLayout',
  'FlowLayout',
  'GridBagLayout',
  'GridLayout',
  'GroupLayout',
  'OverlayLayout',
  'ScrollPaneLayout',
  'SpringLayout',
  'ViewportLayout',
];

const JAVASWING_GRID_BAG_CONSTRAINT_CONSTANTS = [
  'CENTER',
  'NORTH',
  'NORTHEAST',
  'EAST',
  'SOUTHEAST',
  'SOUTH',
  'SOUTHWEST',
  'WEST',
  'NORTHWEST',
  'PAGE_START',
  'PAGE_END',
  'LINE_START',
  'LINE_END',
  'FIRST_LINE_START',
  'FIRST_LINE_END',
  'LAST_LINE_START',
  'LAST_LINE_END',
  'NONE',
  'BOTH',
  'HORIZONTAL',
  'VERTICAL',
  'RELATIVE',
  'REMAINDER',
];

const JAVASWING_BOX_FACTORY_METHODS = [
  'createGlue',
  'createHorizontalBox',
  'createHorizontalGlue',
  'createHorizontalStrut',
  'createRigidArea',
  'createVerticalBox',
  'createVerticalGlue',
  'createVerticalStrut',
];

const JAVASWING_BOUNDS_GEOMETRY_METHODS = [
  'setBounds',
  'setLocation',
  'setSize',
];

const JAVASWING_WINDOW_LIFECYCLE_METHODS = [
  'dispose',
  'pack',
  'setDefaultCloseOperation',
  'setVisible',
];

const JAVASWING_ROOT_PANE_STRUCTURE_METHODS = [
  'getRootPane',
  'setContentPane',
];

const JAVASWING_ACTION_METADATA_KEYS = [
  'ACCELERATOR_KEY',
  'ACTION_COMMAND_KEY',
  'DEFAULT',
  'DISPLAYED_MNEMONIC_INDEX_KEY',
  'LARGE_ICON_KEY',
  'LONG_DESCRIPTION',
  'MNEMONIC_KEY',
  'NAME',
  'SELECTED_KEY',
  'SHORT_DESCRIPTION',
  'SMALL_ICON',
];

const JAVASWING_KEYBOARD_BINDING_METHODS = [
  'getActionMap',
  'getInputMap',
];

const JAVASWING_ROOT_PANE_EXTENDED_METHODS = [
  'getGlassPane',
  'getLayeredPane',
  'setDefaultButton',
  'setGlassPane',
  'setLayeredPane',
];

const JAVASWING_PROPERTY_SETTER_METHODS = [
  'setAction',
  'setAlignmentX',
  'setAlignmentY',
  'setAlwaysOnTop',
  'setBackground',
  'setCellEditor',
  'setCellRenderer',
  'setCursor',
  'setDisabledIcon',
  'setEchoChar',
  'setEditable',
  'setEnabled',
  'setFocusable',
  'setFont',
  'setForeground',
  'setGridColor',
  'setHorizontalAlignment',
  'setHorizontalTextPosition',
  'setIcon',
  'setIntercellSpacing',
  'setLabel',
  'setListData',
  'setLocationRelativeTo',
  'setMaximumSize',
  'setMinimumSize',
  'setMnemonic',
  'setModel',
  'setOpaque',
  'setPreferredScrollableViewportSize',
  'setPreferredSize',
  'setPressedIcon',
  'setRequestFocusEnabled',
  'setResizable',
  'setRolloverEnabled',
  'setRolloverIcon',
  'setRowHeight',
  'setRowSorter',
  'setSelectedIcon',
  'setSelectedIndex',
  'setShowGrid',
  'setShowHorizontalLines',
  'setShowVerticalLines',
  'setText',
  'setTitle',
  'setToolTipText',
  'setUndecorated',
  'setVerticalAlignment',
  'setVerticalTextPosition',
];

const JAVASWING_TABLE_MODEL_MUTATION_METHODS = [
  'addColumn',
  'addRow',
  'fireTableCellUpdated',
  'fireTableDataChanged',
  'fireTableRowsDeleted',
  'fireTableRowsInserted',
  'fireTableRowsUpdated',
  'fireTableStructureChanged',
  'insertRow',
  'moveRow',
  'newRowsAdded',
  'removeRow',
  'rowsRemoved',
  'setColumnCount',
  'setColumnIdentifiers',
  'setDataVector',
  'setRowCount',
  'setValueAt',
];

const JAVASWING_TABLE_COLUMN_CONFIGURATION_METHODS = [
  'setHeaderRenderer',
  'setHeaderValue',
  'setIdentifier',
  'setMaxWidth',
  'setMinWidth',
  'setModelIndex',
  'setPreferredWidth',
];

const JAVASWING_TABLE_COLUMN_VARIABLE_CONFIGURATION_METHODS = [
  'setHeaderRenderer',
  'setHeaderValue',
  'setIdentifier',
  'setMaxWidth',
  'setMinWidth',
  'setModelIndex',
  'setPreferredWidth',
];

const JAVASWING_TABLE_COLUMN_MODEL_ACCESS_METHODS = [
  'getColumnIndex',
  'getColumnIndexAtX',
  'getColumnMargin',
  'getTotalColumnWidth',
];

const JAVASWING_TABLE_COLUMN_MODEL_MUTATION_METHODS = [
  'moveColumn',
  'setColumnMargin',
];

const JAVASWING_TABLE_HEADER_CONFIGURATION_METHODS = [
  'getDefaultRenderer',
  'setDefaultRenderer',
  'setReorderingAllowed',
  'setResizingAllowed',
];

const JAVASWING_SCROLL_BAR_POLICY_METHODS = [
  'setHorizontalScrollBarPolicy',
  'setVerticalScrollBarPolicy',
];

const JAVASWING_BORDER_FACTORY_METHODS = [
  'createBevelBorder',
  'createCompoundBorder',
  'createDashedBorder',
  'createEmptyBorder',
  'createEtchedBorder',
  'createLineBorder',
  'createLoweredBevelBorder',
  'createLoweredSoftBevelBorder',
  'createMatteBorder',
  'createRaisedBevelBorder',
  'createRaisedSoftBevelBorder',
  'createSoftBevelBorder',
  'createStrokeBorder',
  'createTitledBorder',
];

const JAVASWING_BORDER_TYPES = [
  'BevelBorder',
  'CompoundBorder',
  'EmptyBorder',
  'EtchedBorder',
  'LineBorder',
  'MatteBorder',
  'SoftBevelBorder',
  'TitledBorder',
];

const JAVASWING_OPTION_PANE_DIALOG_METHODS = [
  'showConfirmDialog',
  'showInputDialog',
  'showInternalConfirmDialog',
  'showInternalInputDialog',
  'showInternalMessageDialog',
  'showInternalOptionDialog',
  'showMessageDialog',
  'showOptionDialog',
];

const JAVASWING_OPTION_PANE_CONTEXT_METHODS = [
  'getDesktopPaneForComponent',
  'getFrameForComponent',
  'getRootFrame',
  'setDefaultLocale',
  'setRootFrame',
];

const JAVASWING_OPTION_PANE_CONSTANTS = [
  'CANCEL_OPTION',
  'CLOSED_OPTION',
  'DEFAULT_OPTION',
  'ERROR_MESSAGE',
  'ICON_PROPERTY',
  'INFORMATION_MESSAGE',
  'INITIAL_SELECTION_VALUE_PROPERTY',
  'INITIAL_VALUE_PROPERTY',
  'INPUT_VALUE_PROPERTY',
  'MESSAGE_PROPERTY',
  'MESSAGE_TYPE_PROPERTY',
  'NO_OPTION',
  'OK_CANCEL_OPTION',
  'OK_OPTION',
  'OPTION_TYPE_PROPERTY',
  'OPTIONS_PROPERTY',
  'PLAIN_MESSAGE',
  'QUESTION_MESSAGE',
  'SELECTION_VALUES_PROPERTY',
  'UNINITIALIZED_VALUE',
  'VALUE_PROPERTY',
  'WARNING_MESSAGE',
  'WANTS_INPUT_PROPERTY',
  'YES_NO_CANCEL_OPTION',
  'YES_NO_OPTION',
  'YES_OPTION',
];

const JAVASWING_DIALOG_MODALITY_METHODS = [
  'setModal',
  'setModalityType',
];

const JAVASWING_FILE_CHOOSER_DIALOG_METHODS = [
  'showDialog',
  'showOpenDialog',
  'showSaveDialog',
];

const JAVASWING_FILE_CHOOSER_SELECTION_METHODS = [
  'getSelectedFile',
  'getSelectedFiles',
  'isMultiSelectionEnabled',
  'setMultiSelectionEnabled',
  'setSelectedFile',
  'setSelectedFiles',
];

const JAVASWING_FILE_CHOOSER_CONFIGURATION_METHODS = [
  'addChoosableFileFilter',
  'approveSelection',
  'cancelSelection',
  'changeToParentDirectory',
  'removeChoosableFileFilter',
  'rescanCurrentDirectory',
  'resetChoosableFileFilters',
  'setAcceptAllFileFilterUsed',
  'setApproveButtonMnemonic',
  'setApproveButtonText',
  'setApproveButtonToolTipText',
  'setControlButtonsAreShown',
  'setCurrentDirectory',
  'setDialogTitle',
  'setDialogType',
  'setFileFilter',
  'setFileSelectionMode',
];

const JAVASWING_FILE_CHOOSER_CONSTANTS = [
  'APPROVE_OPTION',
  'APPROVE_SELECTION',
  'CANCEL_OPTION',
  'CANCEL_SELECTION',
  'CUSTOM_DIALOG',
  'DIRECTORIES_ONLY',
  'ERROR_OPTION',
  'FILES_AND_DIRECTORIES',
  'FILES_ONLY',
  'OPEN_DIALOG',
  'SAVE_DIALOG',
];

const JAVASWING_TABBED_PANE_TAB_METHODS = [
  'addTab',
  'insertTab',
];

const JAVASWING_TABBED_PANE_SELECTION_METHODS = [
  'getSelectedComponent',
  'setSelectedComponent',
];

const JAVASWING_TABBED_PANE_LOOKUP_METHODS = [
  'indexOfComponent',
  'indexOfTab',
  'indexOfTabComponent',
];

const JAVASWING_TABBED_PANE_APPEARANCE_METHODS = [
  'getBackgroundAt',
  'getComponentAt',
  'getDisabledIconAt',
  'getForegroundAt',
  'getIconAt',
  'getMnemonicAt',
  'getTabComponentAt',
  'getTitleAt',
  'getToolTipTextAt',
  'isEnabledAt',
  'setBackgroundAt',
  'setComponentAt',
  'setDisabledIconAt',
  'setDisplayedMnemonicIndexAt',
  'setEnabledAt',
  'setForegroundAt',
  'setIconAt',
  'setMnemonicAt',
  'setTabComponentAt',
  'setTitleAt',
  'setToolTipTextAt',
];

const JAVASWING_TABBED_PANE_LAYOUT_METHODS = [
  'getTabLayoutPolicy',
  'getTabPlacement',
  'setTabLayoutPolicy',
  'setTabPlacement',
];

const JAVASWING_TABBED_PANE_CONSTANTS = [
  'BOTTOM',
  'LEFT',
  'RIGHT',
  'SCROLL_TAB_LAYOUT',
  'TOP',
  'WRAP_TAB_LAYOUT',
];

const JAVASWING_SPLIT_PANE_COMPONENT_METHODS = [
  'getBottomComponent',
  'getLeftComponent',
  'getRightComponent',
  'getTopComponent',
  'setBottomComponent',
  'setLeftComponent',
  'setRightComponent',
  'setTopComponent',
];

const JAVASWING_SPLIT_PANE_DIVIDER_METHODS = [
  'getDividerLocation',
  'getResizeWeight',
  'isOneTouchExpandable',
  'resetToPreferredSizes',
  'setDividerLocation',
  'setOneTouchExpandable',
  'setResizeWeight',
];

const JAVASWING_SPLIT_PANE_ORIENTATION_METHODS = [
  'getOrientation',
  'setOrientation',
];

const JAVASWING_SPLIT_PANE_CONSTANTS = [
  'BOTTOM',
  'HORIZONTAL_SPLIT',
  'LEFT',
  'RIGHT',
  'TOP',
  'VERTICAL_SPLIT',
];

const JAVASWING_BUTTON_GROUP_TYPES = [
  'ButtonGroup',
];

const JAVASWING_COMBO_BOX_TYPES = [
  'JComboBox',
];

const JAVASWING_COMBO_BOX_SELECTION_METHODS = [
  'getSelectedItem',
  'setSelectedItem',
];

const JAVASWING_COMBO_BOX_POPUP_METHODS = [
  'hidePopup',
  'isPopupVisible',
  'showPopup',
];

const JAVASWING_COMBO_BOX_RENDERER_EDITOR_METHODS = [
  'configureEditor',
  'getEditor',
  'getRenderer',
  'setEditor',
  'setRenderer',
];

const JAVASWING_COMBO_BOX_DISPLAY_METHODS = [
  'getKeySelectionManager',
  'getMaximumRowCount',
  'getPrototypeDisplayValue',
  'setKeySelectionManager',
  'setMaximumRowCount',
  'setPrototypeDisplayValue',
];

const JAVASWING_ITEM_MODEL_TYPES = [
  'DefaultComboBoxModel',
  'DefaultListModel',
];

const JAVASWING_COMBO_BOX_ITEM_METHODS = [
  'addItem',
  'getItemAt',
  'getItemCount',
  'insertItemAt',
  'removeAllItems',
  'removeItem',
  'removeItemAt',
];

const JAVASWING_ITEM_MODEL_METHODS = [
  'addElement',
  'getElementAt',
  'getIndexOf',
  'insertElementAt',
  'removeElement',
  'removeElementAt',
];

const JAVASWING_CELL_RENDERER_EDITOR_SWING_TYPES = [
  'DefaultCellEditor',
  'DefaultListCellRenderer',
  'ListCellRenderer',
];

const JAVASWING_CELL_RENDERER_EDITOR_TABLE_TYPES = [
  'DefaultTableCellRenderer',
  'TableCellEditor',
  'TableCellRenderer',
];

const JAVASWING_CELL_RENDERER_EDITOR_METHODS = [
  'getCellEditor',
  'getCellRenderer',
  'getDefaultEditor',
  'getDefaultRenderer',
  'getHeaderRenderer',
  'getListCellRendererComponent',
  'getTableCellEditorComponent',
  'getTableCellRendererComponent',
  'setCellEditor',
  'setCellRenderer',
  'setDefaultEditor',
  'setDefaultRenderer',
  'setHeaderRenderer',
];

const JAVASWING_TOOLBAR_TYPES = [
  'JToolBar',
];

const JAVASWING_TOOLBAR_SEPARATOR_METHODS = [
  'addSeparator',
];

const JAVASWING_TOOLBAR_BEHAVIOR_METHODS = [
  'isFloatable',
  'isRollover',
  'setFloatable',
  'setRollover',
];

const JAVASWING_PROGRESS_BAR_TYPES = [
  'JProgressBar',
];

const JAVASWING_PROGRESS_BAR_METHODS = [
  'isIndeterminate',
  'isStringPainted',
  'setIndeterminate',
  'setStringPainted',
];

const JAVASWING_SEPARATOR_TYPES = [
  'JSeparator',
];

const JAVASWING_LIST_TYPES = [
  'JList',
];

const JAVASWING_LIST_SELECTION_METHODS = [
  'getSelectedValue',
  'getSelectedValuesList',
];

const JAVASWING_SCROLL_BAR_TYPES = [
  'JScrollBar',
];

const JAVASWING_SCROLL_BAR_ACCESS_METHODS = [
  'getHorizontalScrollBar',
  'getVerticalScrollBar',
];

const JAVASWING_SCROLL_BAR_INCREMENT_METHODS = [
  'getBlockIncrement',
  'getUnitIncrement',
  'setBlockIncrement',
  'setUnitIncrement',
];

const JAVASWING_TEXT_EDITOR_TYPES = [
  'JEditorPane',
  'JTextPane',
];

const JAVASWING_TEXT_EDITOR_METHODS = [
  'addStyle',
  'getContentType',
  'getEditorKit',
  'getStyledDocument',
  'insertComponent',
  'insertIcon',
  'setCharacterAttributes',
  'setContentType',
  'setEditorKit',
  'setParagraphAttributes',
  'setStyledDocument',
];

const JAVASWING_PASSWORD_FIELD_TYPES = [
  'JPasswordField',
];

const JAVASWING_FORMATTED_TEXT_FIELD_TYPES = [
  'JFormattedTextField',
];

const JAVASWING_FORMATTED_TEXT_FIELD_FOCUS_LOST_METHODS = [
  'getFocusLostBehavior',
  'setFocusLostBehavior',
];

const JAVASWING_FORMATTED_TEXT_FIELD_FOCUS_LOST_CONSTANTS = [
  'COMMIT',
  'COMMIT_OR_REVERT',
  'PERSIST',
  'REVERT',
];

const JAVASWING_TEXT_INPUT_TYPES = [
  'JTextArea',
  'JTextField',
];

const JAVASWING_TEXT_INPUT_CONFIGURATION_METHODS = [
  'setColumns',
  'setLineWrap',
  'setRows',
  'setWrapStyleWord',
];

const JAVASWING_TEXT_INPUT_ALIGNMENT_CONSTANTS = [
  'CENTER',
  'LEADING',
  'LEFT',
  'RIGHT',
  'TRAILING',
];

const JAVASWING_SELECTABLE_BUTTON_TYPES = [
  'JCheckBox',
  'JCheckBoxMenuItem',
  'JRadioButton',
  'JRadioButtonMenuItem',
  'JToggleButton',
];

const JAVASWING_SELECTABLE_BUTTON_METHODS = [
  'doClick',
  'isSelected',
  'setSelected',
];

const JAVASWING_SPINNER_TYPES = [
  'JSpinner',
];

const JAVASWING_SPINNER_MODEL_TYPES = [
  'SpinnerDateModel',
  'SpinnerListModel',
  'SpinnerModel',
  'SpinnerNumberModel',
];

const JAVASWING_THREADING_METHODS = [
  'invokeAndWait',
  'invokeLater',
];

const JAVASWING_FOCUS_METHODS = [
  'getInputVerifier',
  'requestFocusInWindow',
  'setFocusTraversalKeysEnabled',
  'setInputVerifier',
];

const JAVASWING_TRANSFER_HANDLER_TYPES = [
  'TransferHandler',
];

const JAVASWING_TRANSFER_HANDLER_METHODS = [
  'getTransferHandler',
  'setDragEnabled',
  'setTransferHandler',
];

const JAVASWING_EVENT_LISTENER_METHODS = [
  'addActionListener',
  'addAncestorListener',
  'addCaretListener',
  'addChangeListener',
  'addComponentListener',
  'addContainerListener',
  'addDocumentListener',
  'addFocusListener',
  'addHierarchyBoundsListener',
  'addHierarchyListener',
  'addInputMethodListener',
  'addInternalFrameListener',
  'addItemListener',
  'addKeyListener',
  'addListDataListener',
  'addListSelectionListener',
  'addMenuDragMouseListener',
  'addMenuKeyListener',
  'addMenuListener',
  'addMouseListener',
  'addMouseMotionListener',
  'addMouseWheelListener',
  'addPopupMenuListener',
  'addPropertyChangeListener',
  'addRowSorterListener',
  'addTableColumnModelListener',
  'addTableModelListener',
  'addTreeExpansionListener',
  'addTreeModelListener',
  'addTreeSelectionListener',
  'addTreeWillExpandListener',
  'addUndoableEditListener',
  'addVetoableChangeListener',
  'addWindowFocusListener',
  'addWindowListener',
  'addWindowStateListener',
];

const JAVASWING_EVENT_HANDLER_METHODS = [
  'actionPerformed',
  'ancestorAdded',
  'ancestorMoved',
  'ancestorRemoved',
  'caretUpdate',
  'changedUpdate',
  'columnAdded',
  'columnMarginChanged',
  'columnMoved',
  'columnRemoved',
  'columnSelectionChanged',
  'componentAdded',
  'componentHidden',
  'componentMoved',
  'componentRemoved',
  'componentResized',
  'componentShown',
  'contentsChanged',
  'focusGained',
  'focusLost',
  'insertUpdate',
  'intervalAdded',
  'intervalRemoved',
  'internalFrameActivated',
  'internalFrameClosed',
  'internalFrameClosing',
  'internalFrameDeactivated',
  'internalFrameDeiconified',
  'internalFrameIconified',
  'internalFrameOpened',
  'itemStateChanged',
  'keyPressed',
  'keyReleased',
  'keyTyped',
  'menuCanceled',
  'menuDeselected',
  'menuDragMouseDragged',
  'menuDragMouseEntered',
  'menuDragMouseExited',
  'menuDragMouseReleased',
  'menuKeyPressed',
  'menuKeyReleased',
  'menuKeyTyped',
  'menuSelected',
  'mouseClicked',
  'mouseDragged',
  'mouseEntered',
  'mouseExited',
  'mouseMoved',
  'mousePressed',
  'mouseReleased',
  'mouseWheelMoved',
  'popupMenuCanceled',
  'popupMenuWillBecomeInvisible',
  'popupMenuWillBecomeVisible',
  'propertyChange',
  'removeUpdate',
  'sorterChanged',
  'stateChanged',
  'tableChanged',
  'treeCollapsed',
  'treeExpanded',
  'treeNodesChanged',
  'treeNodesInserted',
  'treeNodesRemoved',
  'treeStructureChanged',
  'treeWillCollapse',
  'treeWillExpand',
  'undoableEditHappened',
  'valueChanged',
  'windowActivated',
  'windowClosed',
  'windowClosing',
  'windowDeactivated',
  'windowDeiconified',
  'windowGainedFocus',
  'windowIconified',
  'windowLostFocus',
  'windowOpened',
  'windowStateChanged',
];

const JAVASWING_INIT_COMPONENT_METHODS = [
  'initComponents',
];

const JAVASWING_AWT_EVENT_TYPES = [
  'ActionEvent',
  'AdjustmentEvent',
  'ComponentEvent',
  'ContainerEvent',
  'FocusEvent',
  'HierarchyEvent',
  'InputMethodEvent',
  'ItemEvent',
  'KeyEvent',
  'MouseEvent',
  'MouseWheelEvent',
  'TextEvent',
  'WindowEvent',
];

const JAVASWING_SWING_EVENT_TYPES = [
  'AncestorEvent',
  'CaretEvent',
  'ChangeEvent',
  'DocumentEvent',
  'HyperlinkEvent',
  'InternalFrameEvent',
  'ListDataEvent',
  'ListSelectionEvent',
  'MenuDragMouseEvent',
  'MenuEvent',
  'MenuKeyEvent',
  'PopupMenuEvent',
  'RowSorterEvent',
  'TableColumnModelEvent',
  'TableModelEvent',
  'TreeExpansionEvent',
  'TreeModelEvent',
  'TreeSelectionEvent',
  'UndoableEditEvent',
];

module.exports = grammar({
  name: 'javaswing',

  extras: $ => [
    $.line_comment,
    $.block_comment,
    /\s/,
  ],

  supertypes: $ => [
    $.expression,
    $.declaration,
    $.statement,
    $.primary_expression,
    $._literal,
    $._type,
    $._simple_type,
    $._unannotated_type,
    $.module_directive,
  ],

  inline: $ => [
    $._name,
    $._method_name,
    $._simple_type,
    $._class_body_declaration,
    $._variable_initializer,
  ],

  conflicts: $ => [
    [$.modifiers, $.annotated_type, $.receiver_parameter],
    [$.modifiers, $.annotated_type, $.module_declaration, $.package_declaration],
    [$._unannotated_type, $.primary_expression, $.inferred_parameters],
    [$._unannotated_type, $.primary_expression],
    [$._unannotated_type, $.primary_expression, $.scoped_type_identifier],
    [$._unannotated_type, $.scoped_type_identifier],
    [$._unannotated_type, $.generic_type],
    [$.generic_type, $.primary_expression],
    [$.expression, $.statement],
    // Only conflicts in switch expressions
    [$.lambda_expression, $.primary_expression],
    [$.inferred_parameters, $.primary_expression],
    [$.argument_list, $.record_pattern_body],
    [$.yield_statement, $._reserved_identifier],
    [$.primary_expression, $.javaswing_content_pane_access],
    [$.method_invocation, $.javaswing_content_pane_access],
    [$.javaswing_dialog_type, $.javaswing_screen_type],
    [$.javaswing_file_chooser_class, $.javaswing_component_type],
    [$.javaswing_tabbed_pane_class, $.javaswing_component_type],
    [$.javaswing_tabbed_pane_class, $.javaswing_screen_type],
    [$.javaswing_split_pane_class, $.javaswing_component_type],
    [$.javaswing_split_pane_class, $.javaswing_screen_type],
    [$.javaswing_toolbar_class, $.javaswing_screen_type],
    [$._unqualified_object_creation_expression, $.javaswing_combo_box_creation_type],
    [$._unannotated_type, $.javaswing_combo_box_reference_type],
    [$._unannotated_type, $.javaswing_combo_box_array_type],
    [$._unannotated_type, $.javaswing_item_model_local_declaration],
    [$._unannotated_type, $.javaswing_item_model_field],
    [$._unannotated_type, $.javaswing_cell_renderer_editor_local_declaration],
    [$._unannotated_type, $.javaswing_cell_renderer_editor_field],
    [$._unannotated_type, $.javaswing_toolbar_local_declaration],
    [$._unannotated_type, $.javaswing_toolbar_field],
    [$._unannotated_type, $.javaswing_progress_bar_local_declaration],
    [$._unannotated_type, $.javaswing_progress_bar_field],
    [$._unannotated_type, $.javaswing_separator_local_declaration],
    [$._unannotated_type, $.javaswing_separator_field],
    [$._unannotated_type, $.javaswing_list_local_declaration],
    [$._unannotated_type, $.javaswing_list_field],
    [$._unannotated_type, $.javaswing_scroll_bar_local_declaration],
    [$._unannotated_type, $.javaswing_scroll_bar_field],
    [$._unannotated_type, $.javaswing_text_editor_local_declaration],
    [$._unannotated_type, $.javaswing_text_editor_field],
    [$._unannotated_type, $.javaswing_password_field_local_declaration],
    [$._unannotated_type, $.javaswing_password_field_field],
    [$._unannotated_type, $.javaswing_formatted_text_field_local_declaration],
    [$._unannotated_type, $.javaswing_formatted_text_field_field],
    [$._unannotated_type, $.javaswing_text_input_local_declaration],
    [$._unannotated_type, $.javaswing_text_input_field],
    [$._unannotated_type, $.javaswing_selectable_button_local_declaration],
    [$._unannotated_type, $.javaswing_selectable_button_field],
    [$._unannotated_type, $.javaswing_selectable_button_superclass],
    [$._unannotated_type, $.javaswing_spinner_local_declaration],
    [$._unannotated_type, $.javaswing_spinner_field],
    [$._unannotated_type, $.javaswing_spinner_model_local_declaration],
    [$._unannotated_type, $.javaswing_spinner_model_field],
  ],

  word: $ => $.identifier,

  rules: {
    program: $ => repeat($._toplevel_statement),

    _toplevel_statement: $ => choice(
      $.statement,
      $.javaswing_event_handler,
      $.javaswing_init_components,
      $.method_declaration,
    ),

    // Literals

    _literal: $ => choice(
      $.decimal_integer_literal,
      $.hex_integer_literal,
      $.octal_integer_literal,
      $.binary_integer_literal,
      $.decimal_floating_point_literal,
      $.hex_floating_point_literal,
      $.true,
      $.false,
      $.character_literal,
      $.string_literal,
      $.null_literal,
    ),

    decimal_integer_literal: _ => token(seq(
      DIGITS,
      optional(choice('l', 'L')),
    )),

    hex_integer_literal: _ => token(seq(
      choice('0x', '0X'),
      HEX_DIGITS,
      optional(choice('l', 'L')),
    )),

    octal_integer_literal: _ => token(seq(
      choice('0o', '0O', '0'),
      sep1(/[0-7]+/, '_'),
      optional(choice('l', 'L')),
    )),

    binary_integer_literal: _ => token(seq(
      choice('0b', '0B'),
      sep1(/[01]+/, '_'),
      optional(choice('l', 'L')),
    )),

    decimal_floating_point_literal: _ => token(choice(
      seq(DECIMAL_DIGITS, '.', optional(DECIMAL_DIGITS), optional(seq((/[eE]/), optional(choice('-', '+')), DECIMAL_DIGITS)), optional(/[fFdD]/)),
      seq('.', DECIMAL_DIGITS, optional(seq((/[eE]/), optional(choice('-', '+')), DECIMAL_DIGITS)), optional(/[fFdD]/)),
      seq(DIGITS, /[eE]/, optional(choice('-', '+')), DECIMAL_DIGITS, optional(/[fFdD]/)),
      seq(DIGITS, optional(seq((/[eE]/), optional(choice('-', '+')), DECIMAL_DIGITS)), (/[fFdD]/)),
    )),

    hex_floating_point_literal: _ => token(seq(
      choice('0x', '0X'),
      choice(
        seq(HEX_DIGITS, optional('.')),
        seq(optional(HEX_DIGITS), '.', HEX_DIGITS),
      ),
      optional(seq(
        /[pP]/,
        optional(choice('-', '+')),
        DIGITS,
        optional(/[fFdD]/),
      )),
    )),

    true: _ => 'true',

    false: _ => 'false',

    character_literal: _ => token(seq(
      '\'',
      repeat1(choice(
        /[^\\'\n]/,
        /\\./,
        /\\\n/,
      )),
      '\'',
    )),

    string_literal: $ => choice($._string_literal, $._multiline_string_literal),
    _string_literal: $ => seq(
      '"',
      repeat(choice(
        $.string_fragment,
        $.escape_sequence,
        $.string_interpolation,
      )),
      '"',
    ),
    _multiline_string_literal: $ => seq(
      '"""',
      repeat(choice(
        alias($._multiline_string_fragment, $.multiline_string_fragment),
        $._escape_sequence,
        $.string_interpolation,
      )),
      '"""',
    ),
    // Workaround to https://github.com/tree-sitter/tree-sitter/issues/1156
    // We give names to the token() constructs containing a regexp
    // so as to obtain a node in the CST.

    string_fragment: _ => token.immediate(prec(1, /[^"\\]+/)),
    _multiline_string_fragment: _ => choice(
      /[^"\\]+/,
      /"([^"\\]|\\")*/,
    ),

    string_interpolation: $ => seq(
      '\\{',
      $.expression,
      '}',
    ),

    _escape_sequence: $ => choice(
      prec(2, token.immediate(seq('\\', /[^bfnrts'\"\\]/))),
      prec(1, $.escape_sequence),
    ),
    escape_sequence: _ => token.immediate(seq(
      '\\',
      choice(
        /[^xu0-7]/,
        /[0-7]{1,3}/,
        /x[0-9a-fA-F]{2}/,
        /u[0-9a-fA-F]{4}/,
        /u\{[0-9a-fA-F]+\}/,
      ))),

    null_literal: _ => 'null',

    // Expressions

    expression: $ => choice(
      $.javaswing_grid_bag_layout_model,
      $.assignment_expression,
      $.binary_expression,
      $.instanceof_expression,
      $.lambda_expression,
      $.ternary_expression,
      $.update_expression,
      $.primary_expression,
      $.unary_expression,
      $.cast_expression,
      $.switch_expression,
    ),

    cast_expression: $ => prec(PREC.CAST, choice(
      seq(
        '(',
        field('type', $._type),
        ')',
        field('value', $.expression),
      ),
      seq(
        '(',
        sep1(field('type', $._type), '&'),
        ')',
        field('value', choice($.primary_expression, $.lambda_expression)),
      ),
    )),

    assignment_expression: $ => prec.right(PREC.ASSIGN, seq(
      field('left', choice(
        $.identifier,
        $._reserved_identifier,
        $.field_access,
        $.array_access,
      )),
      field('operator', choice('=', '+=', '-=', '*=', '/=', '&=', '|=', '^=', '%=', '<<=', '>>=', '>>>=')),
      field('right', $.expression),
    )),

    binary_expression: $ => choice(
      ...[
        ['>', PREC.REL],
        ['<', PREC.REL],
        ['>=', PREC.REL],
        ['<=', PREC.REL],
        ['==', PREC.EQUALITY],
        ['!=', PREC.EQUALITY],
        ['&&', PREC.AND],
        ['||', PREC.OR],
        ['+', PREC.ADD],
        ['-', PREC.ADD],
        ['*', PREC.MULT],
        ['/', PREC.MULT],
        ['&', PREC.BIT_AND],
        ['|', PREC.BIT_OR],
        ['^', PREC.BIT_XOR],
        ['%', PREC.MULT],
        ['<<', PREC.SHIFT],
        ['>>', PREC.SHIFT],
        ['>>>', PREC.SHIFT],
      ].map(([operator, precedence]) =>
        prec.left(precedence, seq(
          field('left', $.expression),
          // @ts-ignore
          field('operator', operator),
          field('right', $.expression),
        )),
      )),

    instanceof_expression: $ => prec(PREC.REL, seq(
      field('left', $.expression),
      'instanceof',
      optional('final'),
      choice(
        seq(
          field('right', $._type),
          optional(field('name', choice($.identifier, $._reserved_identifier))),
        ),
        field('pattern', $.record_pattern),
      ),
    )),

    lambda_expression: $ => seq(
      field('parameters', choice(
        $.identifier, $.formal_parameters, $.inferred_parameters, $._reserved_identifier,
      )),
      '->',
      field('body', choice($.expression, $.block)),
    ),

    inferred_parameters: $ => seq(
      '(',
      commaSep1(choice($.identifier, $._reserved_identifier)),
      ')',
    ),

    ternary_expression: $ => prec.right(PREC.TERNARY, seq(
      field('condition', $.expression),
      '?',
      field('consequence', $.expression),
      ':',
      field('alternative', $.expression),
    )),

    unary_expression: $ => choice(...[
      ['+', PREC.UNARY],
      ['-', PREC.UNARY],
      ['!', PREC.UNARY],
      ['~', PREC.UNARY],
    ].map(([operator, precedence]) =>
      prec.left(precedence, seq(
        // @ts-ignore
        field('operator', operator),
        field('operand', $.expression),
      )),
    )),

    update_expression: $ => prec.left(PREC.UNARY, choice(
      // Post (in|de)crement is evaluated before pre (in|de)crement
      seq($.expression, '++'),
      seq($.expression, '--'),
      seq('++', $.expression),
      seq('--', $.expression),
    )),

    primary_expression: $ => choice(
      $._literal,
      $.class_literal,
      $.this,
      $.javaswing_option_pane_class,
      $.javaswing_option_pane_constant,
      $.javaswing_file_chooser_constant,
      $.javaswing_tabbed_pane_constant,
      $.javaswing_split_pane_constant,
      $.javaswing_formatted_text_field_focus_lost_constant,
      $.javaswing_text_input_alignment_constant,
      $.javaswing_grid_bag_constraints_constant,
      $.javaswing_dialog_type,
      $.identifier,
      $._reserved_identifier,
      $.parenthesized_expression,
      $.object_creation_expression,
      $.field_access,
      $.array_access,
      $.method_invocation,
      $.method_reference,
      $.array_creation_expression,
      $.template_expression,
    ),

    array_creation_expression: $ => prec.right(seq(
      'new',
      repeat($._annotation),
      field('type', choice($._simple_type, $.javaswing_component_creation_type)),
      choice(
        seq(
          field('dimensions', repeat1($.dimensions_expr)),
          field('dimensions', optional($.dimensions)),
        ),
        seq(
          field('dimensions', $.dimensions),
          field('value', $.array_initializer),
        ),
      ),
    )),

    dimensions_expr: $ => seq(repeat($._annotation), '[', $.expression, ']'),

    parenthesized_expression: $ => seq('(', $.expression, ')'),

    class_literal: $ => prec.dynamic(PREC.CLASS_LITERAL, seq($._unannotated_type, '.', 'class')),

    object_creation_expression: $ => choice(
      $.javaswing_dialog_creation,
      $.javaswing_button_group_creation,
      $.javaswing_combo_box_creation,
      $.javaswing_item_model_creation,
      $.javaswing_cell_renderer_editor_creation,
      $.javaswing_toolbar_creation,
      $.javaswing_progress_bar_creation,
      $.javaswing_separator_creation,
      $.javaswing_list_creation,
      $.javaswing_scroll_bar_creation,
      $.javaswing_text_editor_creation,
      $.javaswing_password_field_creation,
      $.javaswing_formatted_text_field_creation,
      $.javaswing_text_input_creation,
      $.javaswing_selectable_button_creation,
      $.javaswing_spinner_creation,
      $.javaswing_spinner_model_creation,
      $.javaswing_grid_bag_constraints_creation,
      $.javaswing_insets_creation,
      $.javaswing_dimension_creation,
      $.javaswing_action_structure,
      $.javaswing_timer_structure,
      $.javaswing_swing_worker_creation,
      $.javaswing_document_creation,
      $.javaswing_transfer_handler_creation,
      $.javaswing_component_creation,
      $.javaswing_border_creation,
      $._unqualified_object_creation_expression,
      seq($.primary_expression, '.', $._unqualified_object_creation_expression),
    ),

    javaswing_component_creation: $ => prec.right(seq(
      'new',
      choice(
        seq(
          repeat($._annotation),
          field('type_arguments', $.type_arguments),
          repeat($._annotation),
        ),
        repeat($._annotation),
      ),
      field('type', $.javaswing_component_creation_type),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_component_creation_type: $ => choice(
      $.javaswing_component_type,
      $.javaswing_component_generic_type,
    ),

    _unqualified_object_creation_expression: $ => prec.right(seq(
      'new',
      choice(
        seq(
          repeat($._annotation),
          field('type_arguments', $.type_arguments),
          repeat($._annotation),
        ),
        repeat($._annotation),
      ),
      field('type', $._simple_type),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    field_access: $ => seq(
      field('object', choice($.primary_expression, $.super)),
      optional(seq(
        '.',
        $.super,
      )),
      '.',
      field('field', choice($.identifier, $._reserved_identifier, $.this)),
    ),

    template_expression: $ => seq(
      field('template_processor', $.primary_expression),
      '.',
      field('template_argument', $.string_literal),
    ),

    array_access: $ => seq(
      field('array', $.primary_expression),
      '[',
      field('index', $.expression),
      ']',
    ),

    method_invocation: $ => choice(
      $.javaswing_action_command,
      $.javaswing_menu_structure,
      $.javaswing_event_listener,
      $.javaswing_init_components_call,
      $.javaswing_cell_renderer_editor_interaction,
      $.javaswing_progress_bar_interaction,
      $.javaswing_list_selection_interaction,
      $.javaswing_scroll_bar_increment_interaction,
      $.javaswing_scroll_bar_access,
      $.javaswing_text_editor_interaction,
      $.javaswing_formatted_text_field_interaction,
      $.javaswing_text_input_interaction,
      $.javaswing_selectable_button_interaction,
      $.javaswing_combo_box_interaction,
      $.javaswing_table_column_model,
      $.javaswing_scroll_viewport,
      $.javaswing_border_assignment,
      $.javaswing_dialog_interaction,
      $.javaswing_file_chooser_interaction,
      $.javaswing_tabbed_pane_interaction,
      $.javaswing_popup_menu_interaction,
      $.javaswing_split_pane_interaction,
      $.javaswing_item_model_interaction,
      $.javaswing_selection_model_access,
      $._javaswing_generic_show_invocation,
      $.javaswing_table_model_mutation,
      $.javaswing_selection_model,
      $.javaswing_box_factory,
      $.javaswing_bounds_geometry,
      $.javaswing_window_lifecycle,
      $.javaswing_root_pane_structure,
      $.javaswing_keyboard_bindings,
      $.javaswing_action_metadata,
      $.javaswing_document_model,
      $.javaswing_root_pane_extended,
      $.javaswing_threading_invocation,
      $.javaswing_focus_interaction,
      $.javaswing_transfer_handler_interaction,
      $.javaswing_property_setter,
      $.javaswing_layout_assignment,
      $.javaswing_container_add,
      seq(
        choice(
          field('name', $._method_name),
          seq(
            field('object', choice($.primary_expression, $.super)),
            '.',
            optional(seq(
              $.super,
              '.',
            )),
            field('type_arguments', optional($.type_arguments)),
            field('name', $._method_name),
          ),
        ),
        field('arguments', $.argument_list),
      ),
    ),

    javaswing_table_column_model: $ => prec.right(PREC.OBJ_ACCESS + 2, choice(
      seq(
        field('table', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_set_auto_resize_mode_method),
        field('arguments', $.javaswing_table_auto_resize_arguments),
      ),
      seq(
        field('table', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_set_column_model_method),
        field('arguments', $.javaswing_table_column_model_arguments),
      ),
      seq(
        field('table', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_set_table_header_method),
        field('arguments', $.javaswing_table_header_arguments),
      ),
      seq(
        field('column', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_table_column_configuration_method),
        field('arguments', $.argument_list),
      ),
      seq(
        field('column_model', choice($.primary_expression, $.super)),
        '.',
        field('name', choice(
          $._javaswing_table_column_model_access_method,
          $._javaswing_table_column_model_mutation_method,
        )),
        field('arguments', $.argument_list),
      ),
      seq(
        field('header', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_table_header_configuration_method),
        field('arguments', $.argument_list),
      ),
    )),

    javaswing_table_column_access_arguments: $ => prec(PREC.OBJ_ACCESS + 4, seq(
      '(',
      field('column', $.expression),
      ')',
    )),

    javaswing_table_auto_resize_arguments: $ => prec(PREC.OBJ_ACCESS + 3, seq(
      '(',
      field('mode', choice($.javaswing_table_auto_resize_constant, $.expression)),
      ')',
    )),

    javaswing_table_column_model_arguments: $ => prec(PREC.OBJ_ACCESS + 3, seq(
      '(',
      field('column_model', $.expression),
      ')',
    )),

    javaswing_table_header_arguments: $ => prec(PREC.OBJ_ACCESS + 3, seq(
      '(',
      field('header', $.expression),
      ')',
    )),

    javaswing_table_auto_resize_constant: _ => choice(
      seq('JTable', '.', choice(
        'AUTO_RESIZE_OFF',
        'AUTO_RESIZE_NEXT_COLUMN',
        'AUTO_RESIZE_SUBSEQUENT_COLUMNS',
        'AUTO_RESIZE_LAST_COLUMN',
        'AUTO_RESIZE_ALL_COLUMNS',
      )),
      seq('javax', '.', 'swing', '.', 'JTable', '.', choice(
        'AUTO_RESIZE_OFF',
        'AUTO_RESIZE_NEXT_COLUMN',
        'AUTO_RESIZE_SUBSEQUENT_COLUMNS',
        'AUTO_RESIZE_LAST_COLUMN',
        'AUTO_RESIZE_ALL_COLUMNS',
      )),
    ),

    javaswing_scroll_viewport: $ => prec(PREC.OBJ_ACCESS + 2, choice(
      seq(
        field('name', $._javaswing_set_viewport_view_method),
        field('arguments', $.javaswing_viewport_view_arguments),
      ),
      seq(
        field('scroll_pane', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_set_viewport_view_method),
        field('arguments', $.javaswing_viewport_view_arguments),
      ),
      seq(
        field('name', $._javaswing_scroll_bar_policy_method),
        field('arguments', $.javaswing_scroll_bar_policy_arguments),
      ),
      seq(
        field('scroll_pane', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_scroll_bar_policy_method),
        field('arguments', $.javaswing_scroll_bar_policy_arguments),
      ),
    )),

    javaswing_viewport_view_arguments: $ => prec(PREC.OBJ_ACCESS + 3, seq(
      '(',
      field('view', $.expression),
      ')',
    )),

    javaswing_scroll_bar_policy_arguments: $ => prec(PREC.OBJ_ACCESS + 3, seq(
      '(',
      field('policy', choice($.javaswing_scroll_bar_policy_constant, $.expression)),
      ')',
    )),

    javaswing_scroll_bar_policy_constant: _ => choice(
      seq(choice('JScrollPane', 'ScrollPaneConstants'), '.', choice(
        'HORIZONTAL_SCROLLBAR_AS_NEEDED',
        'HORIZONTAL_SCROLLBAR_NEVER',
        'HORIZONTAL_SCROLLBAR_ALWAYS',
        'VERTICAL_SCROLLBAR_AS_NEEDED',
        'VERTICAL_SCROLLBAR_NEVER',
        'VERTICAL_SCROLLBAR_ALWAYS',
      )),
      seq('javax', '.', 'swing', '.', choice('JScrollPane', 'ScrollPaneConstants'), '.', choice(
        'HORIZONTAL_SCROLLBAR_AS_NEEDED',
        'HORIZONTAL_SCROLLBAR_NEVER',
        'HORIZONTAL_SCROLLBAR_ALWAYS',
        'VERTICAL_SCROLLBAR_AS_NEEDED',
        'VERTICAL_SCROLLBAR_NEVER',
        'VERTICAL_SCROLLBAR_ALWAYS',
      )),
    ),

    javaswing_border_assignment: $ => prec(PREC.OBJ_ACCESS + 2, choice(
      seq(
        field('name', $._javaswing_set_border_method),
        field('arguments', $.javaswing_border_arguments),
      ),
      seq(
        field('component', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_set_border_method),
        field('arguments', $.javaswing_border_arguments),
      ),
      seq(
        field('name', $._javaswing_set_viewport_border_method),
        field('arguments', $.javaswing_border_arguments),
      ),
      seq(
        field('scroll_pane', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_set_viewport_border_method),
        field('arguments', $.javaswing_border_arguments),
      ),
      $.javaswing_border_factory_creation,
    )),

    javaswing_border_arguments: $ => prec(PREC.OBJ_ACCESS + 3, seq(
      '(',
      field('border', choice(
        $.javaswing_border_factory_creation,
        $.javaswing_border_creation,
        $.expression,
      )),
      ')',
    )),

    javaswing_border_factory_creation: $ => prec(PREC.OBJ_ACCESS + 3, seq(
      field('factory', choice(
        'BorderFactory',
        token(seq('javax', '.', 'swing', '.', 'BorderFactory')),
      )),
      '.',
      field('name', $._javaswing_border_factory_method),
      field('arguments', $.argument_list),
    )),

    javaswing_border_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_border_type),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_border_type: _ => choice(
      ...JAVASWING_BORDER_TYPES.map(type => type),
    ),

    javaswing_dialog_interaction: $ => prec(PREC.OBJ_ACCESS + 2, choice(
      $.javaswing_option_pane_dialog,
      $.javaswing_option_pane_context_access,
      seq(
        field('name', $._javaswing_dialog_modality_method),
        field('arguments', $.argument_list),
      ),
      seq(
        field('dialog', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_dialog_modality_method),
        field('arguments', $.argument_list),
      ),
    )),

    javaswing_option_pane_dialog: $ => prec(PREC.OBJ_ACCESS + 3, seq(
      field('class', $.javaswing_option_pane_class),
      '.',
      field('name', $._javaswing_option_pane_dialog_method),
      field('arguments', $.argument_list),
    )),

    javaswing_option_pane_context_access: $ => prec(PREC.OBJ_ACCESS + 3, seq(
      field('class', $.javaswing_option_pane_class),
      '.',
      field('name', $._javaswing_option_pane_context_method),
      field('arguments', $.argument_list),
    )),

    javaswing_option_pane_constant: $ => prec(PREC.OBJ_ACCESS + 4, seq(
      field('class', $.javaswing_option_pane_class),
      '.',
      field('constant', $._javaswing_option_pane_constant_name),
    )),

    javaswing_option_pane_class: _ => prec(PREC.OBJ_ACCESS + 5, choice(
      'JOptionPane',
      token(seq('javax', '.', 'swing', '.', 'JOptionPane')),
    )),

    javaswing_dialog_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_dialog_creation_type),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_dialog_creation_type: $ => prec(PREC.OBJ_INST + 2, $.javaswing_dialog_type),

    javaswing_dialog_type: _ => choice(
      'JDialog',
      'JOptionPane',
      token(seq('javax', '.', 'swing', '.', 'JDialog')),
      token(seq('javax', '.', 'swing', '.', 'JOptionPane')),
    ),

    javaswing_file_chooser_interaction: $ => prec(PREC.OBJ_ACCESS + 2, seq(
      field('chooser', choice($.primary_expression, $.super)),
      '.',
      field('name', choice(
        $._javaswing_file_chooser_dialog_method,
        $._javaswing_file_chooser_selection_method,
        $._javaswing_file_chooser_configuration_method,
      )),
      field('arguments', $.argument_list),
    )),

    javaswing_file_chooser_constant: $ => prec(PREC.OBJ_ACCESS + 4, seq(
      field('class', $.javaswing_file_chooser_class),
      '.',
      field('constant', $._javaswing_file_chooser_constant_name),
    )),

    javaswing_file_chooser_class: _ => choice(
      'JFileChooser',
      token(seq('javax', '.', 'swing', '.', 'JFileChooser')),
    ),

    javaswing_tabbed_pane_interaction: $ => prec(PREC.OBJ_ACCESS + 2, seq(
      field('tabbed_pane', choice($.primary_expression, $.super)),
      '.',
      field('name', choice(
        $._javaswing_tabbed_pane_tab_method,
        $._javaswing_tabbed_pane_selection_method,
        $._javaswing_tabbed_pane_lookup_method,
        $._javaswing_tabbed_pane_appearance_method,
        $._javaswing_tabbed_pane_layout_method,
      )),
      field('arguments', $.argument_list),
    )),

    javaswing_tabbed_pane_constant: $ => prec(PREC.OBJ_ACCESS + 4, seq(
      field('class', $.javaswing_tabbed_pane_class),
      '.',
      field('constant', $._javaswing_tabbed_pane_constant_name),
    )),

    javaswing_tabbed_pane_class: _ => choice(
      'JTabbedPane',
      token(seq('javax', '.', 'swing', '.', 'JTabbedPane')),
    ),

    javaswing_split_pane_interaction: $ => prec(PREC.OBJ_ACCESS + 2, seq(
      field('split_pane', choice($.primary_expression, $.super)),
      '.',
      field('name', choice(
        $._javaswing_split_pane_component_method,
        $._javaswing_split_pane_divider_method,
        $._javaswing_split_pane_orientation_method,
      )),
      field('arguments', $.argument_list),
    )),

    javaswing_split_pane_constant: $ => prec(PREC.OBJ_ACCESS + 4, seq(
      field('class', $.javaswing_split_pane_class),
      '.',
      field('constant', $._javaswing_split_pane_constant_name),
    )),

    javaswing_split_pane_class: _ => choice(
      'JSplitPane',
      token(seq('javax', '.', 'swing', '.', 'JSplitPane')),
    ),

    javaswing_button_group_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_button_group_class),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_button_group_class: _ => choice(
      ...JAVASWING_BUTTON_GROUP_TYPES.map(type => type),
      token(seq('javax', '.', 'swing', '.', 'ButtonGroup')),
    ),

    javaswing_combo_box_interaction: $ => prec(PREC.OBJ_ACCESS + 2, seq(
      field('combo_box', choice($.primary_expression, $.super)),
      '.',
      field('name', choice(
        $._javaswing_combo_box_selection_method,
        $._javaswing_combo_box_popup_method,
        $._javaswing_combo_box_renderer_editor_method,
        $._javaswing_combo_box_display_method,
      )),
      field('arguments', $.argument_list),
    )),

    javaswing_combo_box_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      choice(
        seq(
          repeat($._annotation),
          field('type_arguments', $.type_arguments),
          repeat($._annotation),
        ),
        repeat($._annotation),
      ),
      field('type', $.javaswing_combo_box_creation_type),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_combo_box_creation_type: $ => choice(
      $.javaswing_combo_box_class,
      $.javaswing_combo_box_generic_type,
    ),

    javaswing_combo_box_reference_type: $ => choice(
      $.javaswing_combo_box_class,
      $.javaswing_combo_box_generic_type,
      $.javaswing_combo_box_array_type,
    ),

    javaswing_combo_box_generic_type: $ => prec.dynamic(PREC.GENERIC + 1, seq(
      field('type', $.javaswing_combo_box_class),
      $.type_arguments,
    )),

    javaswing_combo_box_array_type: $ => seq(
      field('element', choice(
        $.javaswing_combo_box_class,
        $.javaswing_combo_box_generic_type,
      )),
      field('dimensions', $.dimensions),
    ),

    javaswing_combo_box_class: _ => choice(
      ...JAVASWING_COMBO_BOX_TYPES.map(type => type),
      token(seq('javax', '.', 'swing', '.', 'JComboBox')),
    ),

    javaswing_item_model_interaction: $ => prec(PREC.OBJ_ACCESS + 2, seq(
      field('model', choice($.primary_expression, $.super)),
      '.',
      field('name', choice(
        $._javaswing_combo_box_item_method,
        $._javaswing_item_model_method,
      )),
      field('arguments', $.argument_list),
    )),

    javaswing_item_model_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_item_model_class),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_item_model_class: _ => choice(
      ...JAVASWING_ITEM_MODEL_TYPES.map(type => type),
      token(seq('javax', '.', 'swing', '.', choice(...JAVASWING_ITEM_MODEL_TYPES))),
    ),

    javaswing_cell_renderer_editor_interaction: $ => prec(PREC.OBJ_ACCESS + 3, seq(
      field('renderer_editor', choice($.primary_expression, $.super)),
      '.',
      field('name', $._javaswing_cell_renderer_editor_method),
      field('arguments', $.argument_list),
    )),

    javaswing_cell_renderer_editor_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_cell_renderer_editor_class),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_cell_renderer_editor_class: _ => choice(
      ...JAVASWING_CELL_RENDERER_EDITOR_SWING_TYPES.map(type => type),
      ...JAVASWING_CELL_RENDERER_EDITOR_TABLE_TYPES.map(type => type),
      token(seq(
        'javax',
        '.',
        'swing',
        '.',
        choice(...JAVASWING_CELL_RENDERER_EDITOR_SWING_TYPES),
      )),
      token(seq(
        'javax',
        '.',
        'swing',
        '.',
        'table',
        '.',
        choice(...JAVASWING_CELL_RENDERER_EDITOR_TABLE_TYPES),
      )),
    ),

    javaswing_toolbar_interaction: $ => prec(PREC.OBJ_ACCESS + 2, choice(
      seq(
        field('toolbar', $._javaswing_toolbar_receiver),
        '.',
        field('name', $._javaswing_toolbar_separator_method),
        field('arguments', $.javaswing_toolbar_separator_arguments),
      ),
      seq(
        field('toolbar', $._javaswing_toolbar_receiver),
        '.',
        field('name', $._javaswing_toolbar_behavior_method),
        field('arguments', $.argument_list),
      ),
    )),

    _javaswing_toolbar_receiver: $ => prec(PREC.OBJ_ACCESS + 2, choice(
      $.field_access,
      $.array_access,
      $.parenthesized_expression,
    )),

    javaswing_toolbar_separator_arguments: $ => prec(PREC.OBJ_ACCESS + 4, choice(
      seq('(', ')'),
      seq(
        '(',
        field('size', $._javaswing_toolbar_separator_size),
        ')',
      ),
    )),

    _javaswing_toolbar_separator_size: $ => choice(
      $.identifier,
      $.field_access,
      $.object_creation_expression,
      $.parenthesized_expression,
      $.cast_expression,
    ),

    javaswing_toolbar_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_toolbar_class),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_toolbar_class: _ => choice(
      ...JAVASWING_TOOLBAR_TYPES.map(type => type),
      token(seq('javax', '.', 'swing', '.', 'JToolBar')),
    ),

    javaswing_progress_bar_interaction: $ => prec(PREC.OBJ_ACCESS + 2, seq(
      field('selector', $.javaswing_progress_bar_selector),
      field('arguments', $.argument_list),
    )),

    javaswing_progress_bar_selector: _ => token(prec(1, seq(
      /[A-Za-z_$][A-Za-z0-9_$]*/,
      repeat(seq('.', /[A-Za-z_$][A-Za-z0-9_$]*/)),
      '.',
      choice(...JAVASWING_PROGRESS_BAR_METHODS),
    ))),


    javaswing_progress_bar_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_progress_bar_class),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_progress_bar_class: _ => choice(
      ...JAVASWING_PROGRESS_BAR_TYPES.map(type => type),
      token(seq('javax', '.', 'swing', '.', 'JProgressBar')),
    ),

    javaswing_separator_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_separator_class),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_separator_class: _ => choice(
      ...JAVASWING_SEPARATOR_TYPES.map(type => type),
      token(seq('javax', '.', 'swing', '.', 'JSeparator')),
    ),

    javaswing_list_selection_interaction: $ => prec(PREC.OBJ_ACCESS + 2, seq(
      field('selector', $.javaswing_list_selection_selector),
      field('arguments', $.argument_list),
    )),

    javaswing_list_selection_selector: _ => token(prec(1, seq(
      /[A-Za-z_$][A-Za-z0-9_$]*/,
      repeat(seq('.', /[A-Za-z_$][A-Za-z0-9_$]*/)),
      '.',
      choice(...JAVASWING_LIST_SELECTION_METHODS),
    ))),

    javaswing_list_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_list_class),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_list_class: _ => choice(
      ...JAVASWING_LIST_TYPES.map(type => type),
      token(seq('javax', '.', 'swing', '.', 'JList')),
    ),

    javaswing_scroll_bar_access: $ => prec(PREC.OBJ_ACCESS + 3, seq(
      field('selector', $.javaswing_scroll_bar_access_selector),
      field('arguments', $.javaswing_empty_argument_list),
    )),

    javaswing_scroll_bar_access_selector: _ => token(prec(1, seq(
      /[A-Za-z_$][A-Za-z0-9_$]*/,
      repeat(choice(
        seq('.', /[A-Za-z_$][A-Za-z0-9_$]*/),
        seq('.', /[A-Za-z_$][A-Za-z0-9_$]*/, '(', ')'),
      )),
      '.',
      choice(...JAVASWING_SCROLL_BAR_ACCESS_METHODS),
    ))),

    javaswing_scroll_bar_increment_interaction: $ => prec(PREC.OBJ_ACCESS + 2, seq(
      field('selector', $.javaswing_scroll_bar_increment_selector),
      field('arguments', $.argument_list),
    )),

    javaswing_scroll_bar_increment_selector: _ => token(prec(1, seq(
      /[A-Za-z_$][A-Za-z0-9_$]*/,
      repeat(choice(
        seq('.', /[A-Za-z_$][A-Za-z0-9_$]*/),
        seq('.', /[A-Za-z_$][A-Za-z0-9_$]*/, '(', ')'),
      )),
      '.',
      choice(...JAVASWING_SCROLL_BAR_INCREMENT_METHODS),
    ))),

    javaswing_scroll_bar_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_scroll_bar_class),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_scroll_bar_class: _ => choice(
      ...JAVASWING_SCROLL_BAR_TYPES.map(type => type),
      token(seq('javax', '.', 'swing', '.', 'JScrollBar')),
    ),

    javaswing_text_editor_interaction: $ => prec(PREC.OBJ_ACCESS + 2, choice(
      seq(
        field('selector', $.javaswing_text_editor_selector),
        field('arguments', $.argument_list),
      ),
      seq(
        field('selector', $.javaswing_text_editor_set_page_selector),
        field('arguments', $.javaswing_text_editor_set_page_arguments),
      ),
      seq(
        field('name', $._javaswing_text_editor_method),
        field('arguments', $.argument_list),
      ),
      seq(
        field('name', $._javaswing_set_page_method),
        field('arguments', $.argument_list),
      ),
    )),

    javaswing_text_editor_selector: _ => token(prec(1, seq(
      /[A-Za-z_$][A-Za-z0-9_$]*/,
      repeat(seq('.', /[A-Za-z_$][A-Za-z0-9_$]*/)),
      '.',
      choice(...JAVASWING_TEXT_EDITOR_METHODS),
    ))),

    javaswing_text_editor_set_page_selector: _ => token(prec(1, seq(
      /[A-Za-z_$][A-Za-z0-9_$]*/,
      repeat(seq('.', /[A-Za-z_$][A-Za-z0-9_$]*/)),
      '.',
      'setPage',
      /\s*\(/,
    ))),

    javaswing_text_editor_set_page_arguments: $ => seq(
      commaSep($.expression),
      ')',
    ),

    javaswing_text_editor_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_text_editor_class),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_text_editor_class: _ => choice(
      ...JAVASWING_TEXT_EDITOR_TYPES.map(type => type),
      token(seq('javax', '.', 'swing', '.', choice('JEditorPane', 'JTextPane'))),
    ),

    javaswing_password_field_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_password_field_class),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_password_field_class: _ => choice(
      ...JAVASWING_PASSWORD_FIELD_TYPES.map(type => type),
      token(seq('javax', '.', 'swing', '.', 'JPasswordField')),
    ),

    javaswing_formatted_text_field_interaction: $ => prec(PREC.OBJ_ACCESS + 2, seq(
      field('formatted_text_field', choice($.primary_expression, $.super)),
      '.',
      field('name', $._javaswing_formatted_text_field_focus_lost_method),
      field('arguments', $.javaswing_formatted_text_field_focus_lost_arguments),
    )),

    javaswing_formatted_text_field_focus_lost_arguments: $ => seq(
      '(',
      optional(field('behavior', $.expression)),
      ')',
    ),

    javaswing_formatted_text_field_focus_lost_constant: $ => prec(PREC.OBJ_ACCESS + 4, seq(
      field('class', $.javaswing_formatted_text_field_class),
      '.',
      field('constant', $._javaswing_formatted_text_field_focus_lost_constant_name),
    )),

    javaswing_formatted_text_field_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_formatted_text_field_class),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_formatted_text_field_class: _ => choice(
      ...JAVASWING_FORMATTED_TEXT_FIELD_TYPES.map(type => type),
      token(seq('javax', '.', 'swing', '.', 'JFormattedTextField')),
    ),

    javaswing_text_input_interaction: $ => prec(PREC.OBJ_ACCESS + 2, seq(
      field('text_input', choice($.primary_expression, $.super)),
      '.',
      field('name', $._javaswing_text_input_configuration_method),
      field('arguments', $.argument_list),
    )),

    javaswing_text_input_alignment_constant: $ => prec(PREC.OBJ_ACCESS + 4, seq(
      field('class', $.javaswing_text_input_class),
      '.',
      field('constant', $._javaswing_text_input_alignment_constant_name),
    )),

    javaswing_text_input_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_text_input_class),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_text_input_class: _ => choice(
      ...JAVASWING_TEXT_INPUT_TYPES.map(type => type),
      token(seq('javax', '.', 'swing', '.', choice(...JAVASWING_TEXT_INPUT_TYPES))),
    ),

    javaswing_selectable_button_interaction: $ => prec(PREC.OBJ_ACCESS + 2, seq(
      field('selector', $.javaswing_selectable_button_selector),
      field('arguments', $.javaswing_selectable_button_arguments),
    )),

    javaswing_selectable_button_selector: _ => token(prec(1, seq(
      /[A-Za-z_$][A-Za-z0-9_$]*/,
      repeat(choice(
        seq('.', /[A-Za-z_$][A-Za-z0-9_$]*/),
        seq('.', /[A-Za-z_$][A-Za-z0-9_$]*/, '(', ')'),
      )),
      '.',
      choice(...JAVASWING_SELECTABLE_BUTTON_METHODS),
      /\s*/,
      '(',
    ))),

    javaswing_selectable_button_arguments: $ => seq(
      optional(commaSep1($.expression)),
      ')',
    ),

    javaswing_selectable_button_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_selectable_button_class),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_selectable_button_class: _ => choice(
      ...JAVASWING_SELECTABLE_BUTTON_TYPES.map(type => type),
      token(seq('javax', '.', 'swing', '.', choice(...JAVASWING_SELECTABLE_BUTTON_TYPES))),
    ),

    javaswing_spinner_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_spinner_class),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_spinner_model_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_spinner_model_class),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_spinner_class: _ => choice(
      ...JAVASWING_SPINNER_TYPES.map(type => type),
      token(seq('javax', '.', 'swing', '.', 'JSpinner')),
    ),

    javaswing_spinner_model_class: _ => choice(
      ...JAVASWING_SPINNER_MODEL_TYPES.map(type => type),
      token(seq('javax', '.', 'swing', '.', choice(...JAVASWING_SPINNER_MODEL_TYPES))),
    ),

    javaswing_popup_menu_interaction: $ => prec(PREC.OBJ_ACCESS + 2, seq(
      field('popup_menu', choice($.primary_expression, $.super)),
      '.',
      field('name', $._javaswing_popup_menu_display_method),
      field('arguments', $.javaswing_popup_menu_show_arguments),
    )),

    _javaswing_generic_show_invocation: $ => prec(PREC.OBJ_ACCESS + 1, seq(
      field('object', choice($.primary_expression, $.super)),
      '.',
      field('name', $._javaswing_popup_menu_display_method),
      field('arguments', $.argument_list),
    )),

    javaswing_popup_menu_show_arguments: $ => prec(PREC.OBJ_ACCESS + 3, seq(
      '(',
      field('invoker', $.expression),
      ',',
      field('x', $.expression),
      ',',
      field('y', $.expression),
      ')',
    )),

    javaswing_menu_structure: $ => prec(PREC.OBJ_ACCESS + 2, choice(
      seq(
        field('name', $._javaswing_set_menu_bar_method),
        field('arguments', $.javaswing_menu_bar_arguments),
      ),
      seq(
        field('window', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_set_menu_bar_method),
        field('arguments', $.javaswing_menu_bar_arguments),
      ),
      seq(
        field('name', $._javaswing_set_component_popup_menu_method),
        field('arguments', $.javaswing_component_popup_menu_arguments),
      ),
      seq(
        field('component', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_set_component_popup_menu_method),
        field('arguments', $.javaswing_component_popup_menu_arguments),
      ),
    )),

    javaswing_menu_bar_arguments: $ => prec(PREC.OBJ_ACCESS + 3, seq(
      '(',
      field('menu_bar', $.expression),
      ')',
    )),

    javaswing_component_popup_menu_arguments: $ => prec(PREC.OBJ_ACCESS + 3, seq(
      '(',
      field('popup_menu', $.expression),
      ')',
    )),

    javaswing_action_command: $ => prec(PREC.OBJ_ACCESS + 2, choice(
      seq(
        field('name', $._javaswing_action_command_setter_method),
        field('arguments', $.javaswing_action_command_arguments),
      ),
      seq(
        field('component', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_action_command_setter_method),
        field('arguments', $.javaswing_action_command_arguments),
      ),
      seq(
        field('name', $._javaswing_action_command_getter_method),
        field('arguments', $.javaswing_empty_argument_list),
      ),
      seq(
        field('event', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_action_command_getter_method),
        field('arguments', $.javaswing_empty_argument_list),
      ),
    )),

    javaswing_action_command_arguments: $ => prec(PREC.OBJ_ACCESS + 3, seq(
      '(',
      field('command', $.expression),
      ')',
    )),

    javaswing_empty_argument_list: _ => prec(PREC.OBJ_ACCESS + 3, seq('(', ')')),

    javaswing_selection_model: $ => prec(PREC.OBJ_ACCESS + 2, choice(
      seq(
        field('name', $._javaswing_selection_flag_method),
        field('arguments', $.javaswing_selection_flag_arguments),
      ),
      seq(
        field('component', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_selection_flag_method),
        field('arguments', $.javaswing_selection_flag_arguments),
      ),
      seq(
        field('name', $._javaswing_set_selection_mode_method),
        field('arguments', $.javaswing_selection_mode_arguments),
      ),
      seq(
        field('component', $.javaswing_selection_model_access),
        '.',
        field('name', $._javaswing_set_selection_mode_method),
        field('arguments', $.javaswing_selection_mode_arguments),
      ),
      seq(
        field('component', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_set_selection_mode_method),
        field('arguments', $.javaswing_selection_mode_arguments),
      ),
      seq(
        field('name', $._javaswing_set_selection_model_method),
        field('arguments', $.javaswing_selection_model_arguments),
      ),
      seq(
        field('component', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_set_selection_model_method),
        field('arguments', $.javaswing_selection_model_arguments),
      ),
      seq(
        field('name', $._javaswing_get_selection_model_method),
        field('arguments', $.argument_list),
      ),
      seq(
        field('component', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_get_selection_model_method),
        field('arguments', $.argument_list),
      ),
    )),

    javaswing_selection_model_access: $ => prec(PREC.OBJ_ACCESS + 3, seq(
      field('selector', $.javaswing_selection_model_access_selector),
      field('arguments', $.argument_list),
    )),

    javaswing_selection_model_access_selector: _ => token(prec(1, seq(
      /[A-Za-z_$][A-Za-z0-9_$]*/,
      repeat(seq('.', /[A-Za-z_$][A-Za-z0-9_$]*/)),
      '.',
      'getSelectionModel',
    ))),

    javaswing_selection_flag_arguments: $ => prec(PREC.OBJ_ACCESS + 3, seq(
      '(',
      field('enabled', $.expression),
      ')',
    )),

    javaswing_selection_mode_arguments: $ => prec(PREC.OBJ_ACCESS + 3, seq(
      '(',
      field('mode', choice($.javaswing_selection_mode_constant, $.expression)),
      ')',
    )),

    javaswing_selection_model_arguments: $ => prec(PREC.OBJ_ACCESS + 3, seq(
      '(',
      field('model', $.expression),
      ')',
    )),

    javaswing_selection_mode_constant: _ => choice(
      seq('ListSelectionModel', '.', choice(
        'SINGLE_SELECTION',
        'SINGLE_INTERVAL_SELECTION',
        'MULTIPLE_INTERVAL_SELECTION',
      )),
      seq('javax', '.', 'swing', '.', 'ListSelectionModel', '.', choice(
        'SINGLE_SELECTION',
        'SINGLE_INTERVAL_SELECTION',
        'MULTIPLE_INTERVAL_SELECTION',
      )),
      seq('TreeSelectionModel', '.', choice(
        'SINGLE_TREE_SELECTION',
        'CONTIGUOUS_TREE_SELECTION',
        'DISCONTIGUOUS_TREE_SELECTION',
      )),
      seq('javax', '.', 'swing', '.', 'tree', '.', 'TreeSelectionModel', '.', choice(
        'SINGLE_TREE_SELECTION',
        'CONTIGUOUS_TREE_SELECTION',
        'DISCONTIGUOUS_TREE_SELECTION',
      )),
    ),

    javaswing_event_listener: $ => prec(PREC.OBJ_ACCESS + 1, choice(
      seq(
        field('name', $._javaswing_event_listener_method),
        field('arguments', $.argument_list),
      ),
      seq(
        field('component', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_event_listener_method),
        field('arguments', $.argument_list),
      ),
    )),

    javaswing_table_model_mutation: $ => prec(PREC.OBJ_ACCESS + 1, choice(
      seq(
        field('name', $._javaswing_table_model_mutation_method),
        field('arguments', $.argument_list),
      ),
      seq(
        field('table_model', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_table_model_mutation_method),
        field('arguments', $.argument_list),
      ),
    )),

    javaswing_property_setter: $ => prec(PREC.OBJ_ACCESS + 1, choice(
      seq(
        field('name', $._javaswing_property_setter_method),
        field('arguments', $.argument_list),
      ),
      seq(
        field('component', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_property_setter_method),
        field('arguments', $.argument_list),
      ),
    )),

    javaswing_layout_assignment: $ => prec(PREC.OBJ_ACCESS + 1, choice(
      seq(
        field('name', $._javaswing_set_layout_method),
        field('arguments', $.javaswing_layout_assignment_arguments),
      ),
      seq(
        field('container', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_set_layout_method),
        field('arguments', $.javaswing_layout_assignment_arguments),
      ),
    )),

    javaswing_layout_assignment_arguments: $ => seq(
      '(',
      field('layout', $.javaswing_layout_creation),
      ')',
    ),

    javaswing_layout_creation: $ => prec.right(seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_layout_type),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_layout_type: _ => choice(
      ...JAVASWING_LAYOUT_TYPES.map(type => type),
    ),

    javaswing_container_add: $ => choice(
      seq(
        field('container', $.javaswing_content_pane_access),
        '.',
        field('name', $._javaswing_container_add_method),
        field('arguments', $.javaswing_container_add_arguments),
      ),
      seq(
        field('container', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_container_add_method),
        field('arguments', $.javaswing_container_add_component_creation_arguments),
      ),
      seq(
        field('container', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_container_add_method),
        field('arguments', $.javaswing_container_add_border_layout_arguments),
      ),
    ),

    javaswing_content_pane_access: $ => choice(
      seq(
        field('name', $._javaswing_get_content_pane_method),
        field('arguments', $.argument_list),
      ),
      seq(
        field('object', $.this),
        '.',
        field('name', $._javaswing_get_content_pane_method),
        field('arguments', $.argument_list),
      ),
    ),

    javaswing_container_add_arguments: $ => seq(
      '(',
      field('component', $.expression),
      optional(seq(
        ',',
        field('constraints', $.expression),
        optional(seq(
          ',',
          field('index', $.expression),
        )),
      )),
      ')',
    ),

    javaswing_container_add_component_creation_arguments: $ => prec(PREC.OBJ_INST + 1, seq(
      '(',
      field('component', $.javaswing_component_creation),
      optional(seq(
        ',',
        field('constraints', $.expression),
        optional(seq(
          ',',
          field('index', $.expression),
        )),
      )),
      ')',
    )),

    javaswing_container_add_border_layout_arguments: $ => seq(
      '(',
      field('component', $.expression),
      ',',
      field('constraints', $.javaswing_border_layout_constraint),
      optional(seq(
        ',',
        field('index', $.expression),
      )),
      ')',
    ),

    javaswing_border_layout_constraint: $ => seq(
      'BorderLayout',
      '.',
      choice(
        'NORTH',
        'SOUTH',
        'EAST',
        'WEST',
        'CENTER',
        'BEFORE_FIRST_LINE',
        'AFTER_LAST_LINE',
        'BEFORE_LINE_BEGINS',
        'AFTER_LINE_ENDS',
        'PAGE_START',
        'PAGE_END',
        'LINE_START',
        'LINE_END',
      ),
    ),

    _javaswing_container_add_method: _ => 'add',

    _javaswing_get_content_pane_method: _ => 'getContentPane',

    _javaswing_set_layout_method: _ => 'setLayout',

    javaswing_grid_bag_constraints_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_grid_bag_constraints_class),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_grid_bag_constraints_constant: $ => seq(
      'GridBagConstraints',
      '.',
      field('constant', choice(
        ...JAVASWING_GRID_BAG_CONSTRAINT_CONSTANTS.map(name => name),
      )),
    ),

    javaswing_grid_bag_constraints_class: _ => choice(
      'GridBagConstraints',
      token(seq('java', '.', 'awt', '.', 'GridBagConstraints')),
    ),

    javaswing_box_factory: $ => prec(PREC.OBJ_ACCESS + 3, seq(
      field('box', $.javaswing_box_class),
      '.',
      field('name', $._javaswing_box_factory_method),
      field('arguments', $.argument_list),
    )),

    javaswing_box_class: _ => choice(
      prec(1, 'Box'),
      token(seq('javax', '.', 'swing', '.', 'Box')),
    ),

    javaswing_bounds_geometry: $ => prec(PREC.OBJ_ACCESS + 2, choice(
      seq(
        field('name', $._javaswing_bounds_geometry_method),
        field('arguments', $.argument_list),
      ),
      seq(
        field('component', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_bounds_geometry_method),
        field('arguments', $.argument_list),
      ),
    )),

    javaswing_grid_bag_layout_model: $ => prec.right(PREC.ASSIGN + 1, seq(
      field('selector', $.javaswing_grid_bag_layout_model_selector),
      '=',
      field('value', $.expression),
    )),

    javaswing_grid_bag_layout_model_selector: _ => token(prec(1, /\(\s*\(\s*(?:java\s*\.\s*awt\s*\.\s*)?GridBagLayout\s*\)\s*[A-Za-z_$][A-Za-z0-9_$]*(?:\s*\.\s*[A-Za-z_$][A-Za-z0-9_$]*(?:\s*\([^()]*\))?)*\s*\)\s*\.\s*(?:columnWidths|columnWeights|rowHeights|rowWeights)/)),

    javaswing_window_lifecycle: $ => prec(PREC.OBJ_ACCESS + 2, choice(
      seq(
        field('name', $._javaswing_window_lifecycle_method),
        field('arguments', $.argument_list),
      ),
      seq(
        field('window', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_window_lifecycle_method),
        field('arguments', $.argument_list),
      ),
    )),

    javaswing_root_pane_structure: $ => prec(PREC.OBJ_ACCESS + 2, choice(
      seq(
        field('name', $._javaswing_root_pane_structure_method),
        field('arguments', $.argument_list),
      ),
      seq(
        field('container', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_root_pane_structure_method),
        field('arguments', $.argument_list),
      ),
    )),

    javaswing_insets_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_insets_class),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_insets_class: _ => choice(
      'Insets',
      token(seq('java', '.', 'awt', '.', 'Insets')),
    ),

    javaswing_dimension_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_dimension_class),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_dimension_class: _ => choice(
      'Dimension',
      token(seq('java', '.', 'awt', '.', 'Dimension')),
    ),

    javaswing_action_structure: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_action_class),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_action_class: _ => choice(
      'AbstractAction',
      token(seq('javax', '.', 'swing', '.', 'AbstractAction')),
    ),

    javaswing_action_metadata: $ => prec(PREC.OBJ_ACCESS + 2, choice(
      seq(
        field('action', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_action_put_value_method),
        field('arguments', $.javaswing_action_put_value_arguments),
      ),
    )),

    javaswing_action_put_value_arguments: $ => seq(
      '(',
      field('key', $.expression),
      ',',
      field('value', $.expression),
      ')',
    ),

    javaswing_action_key_constant: _ => choice(
      seq('Action', '.', choice(...JAVASWING_ACTION_METADATA_KEYS)),
      token(seq('javax', '.', 'swing', '.', 'Action', '.', choice(...JAVASWING_ACTION_METADATA_KEYS))),
    ),

    javaswing_keyboard_bindings: $ => prec(PREC.OBJ_ACCESS + 2, choice(
      seq(
        field('component', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_keyboard_binding_method),
        field('arguments', $.argument_list),
      ),
      seq(
        field('selector', $.javaswing_key_stroke_selector),
        field('arguments', $.argument_list),
      ),
    )),

    javaswing_key_stroke_selector: _ => token(prec(1, seq(
      choice('KeyStroke', seq('javax', '.', 'swing', '.', 'KeyStroke')),
      '.',
      'getKeyStroke',
    ))),

    javaswing_timer_structure: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_timer_class),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_timer_class: _ => choice(
      'Timer',
      token(seq('javax', '.', 'swing', '.', 'Timer')),
    ),

    javaswing_swing_worker_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', choice($.javaswing_swing_worker_class, $.javaswing_swing_worker_generic_type)),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_swing_worker_class: _ => choice(
      'SwingWorker',
      token(seq('javax', '.', 'swing', '.', 'SwingWorker')),
    ),

    javaswing_swing_worker_generic_type: $ => prec.dynamic(PREC.GENERIC + 1, seq(
      choice(
        alias('SwingWorker', $.type_identifier),
        token(seq('javax', '.', 'swing', '.', 'SwingWorker')),
      ),
      $.type_arguments,
    )),

    javaswing_swing_worker_callback: $ => prec(PREC.DECL + 1, seq(
      optional($.modifiers),
      field('type', $._unannotated_type),
      field('name', $._javaswing_swing_worker_callback_method),
      field('parameters', $.formal_parameters),
      optional($.throws),
      choice(field('body', $.block), ';'),
    )),

    _javaswing_swing_worker_callback_method: _ => choice(
      'doInBackground',
      'done',
    ),

    javaswing_document_model: $ => prec(PREC.OBJ_ACCESS + 2, choice(
      seq(
        field('selector', $.javaswing_document_model_selector),
        field('arguments', $.javaswing_document_model_arguments),
      ),
      seq(
        field('selector', $.javaswing_get_document_selector),
        field('arguments', $.javaswing_get_document_arguments),
      ),
    )),

    javaswing_document_model_selector: _ => token(prec(1, seq(
      /[A-Za-z_$][A-Za-z0-9_$]*/,
      repeat(seq('.', /[A-Za-z_$][A-Za-z0-9_$]*/)),
      '.',
      'setDocument',
      /\s*\(/,
    ))),

    javaswing_get_document_selector: _ => token(prec(1, seq(
      /[A-Za-z_$][A-Za-z0-9_$]*/,
      repeat(seq('.', /[A-Za-z_$][A-Za-z0-9_$]*/)),
      '.',
      'getDocument',
      /\s*\(/,
    ))),

    javaswing_document_model_arguments: $ => seq(
      field('document', $.expression),
      optional(seq(',', field('context', $.expression))),
      ')',
    ),

    javaswing_get_document_arguments: _ => ')',

    javaswing_document_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_document_class),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_document_class: _ => choice(
      'PlainDocument',
      'StyledDocument',
      token(seq('javax', '.', 'swing', '.', 'text', '.', choice('Document', 'PlainDocument', 'StyledDocument'))),
    ),

    javaswing_threading_invocation: $ => prec(PREC.OBJ_ACCESS + 2, seq(
      field('selector', $.javaswing_threading_selector),
      field('arguments', $.javaswing_threading_arguments),
    )),

    javaswing_threading_selector: _ => token(prec(1, seq(
      choice(
        'SwingUtilities',
        seq('javax', '.', 'swing', '.', 'SwingUtilities'),
        'EventQueue',
        seq('java', '.', 'awt', '.', 'EventQueue'),
      ),
      '.',
      choice(...JAVASWING_THREADING_METHODS),
      /\s*\(/,
    ))),

    javaswing_threading_arguments: $ => seq(
      commaSep($.expression),
      ')',
    ),

    javaswing_focus_interaction: $ => prec(PREC.OBJ_ACCESS + 2, seq(
      field('component', choice($.primary_expression, $.super)),
      '.',
      field('name', $._javaswing_focus_method),
      field('arguments', $.argument_list),
    )),

    javaswing_transfer_handler_creation: $ => prec.right(PREC.OBJ_INST + 1, seq(
      'new',
      repeat($._annotation),
      field('type', $.javaswing_transfer_handler_class),
      field('arguments', $.argument_list),
      optional($.class_body),
    )),

    javaswing_transfer_handler_class: _ => choice(
      ...JAVASWING_TRANSFER_HANDLER_TYPES.map(type => type),
      token(seq('javax', '.', 'swing', '.', 'TransferHandler')),
    ),

    javaswing_transfer_handler_interaction: $ => prec(PREC.OBJ_ACCESS + 2, seq(
      field('component', choice($.primary_expression, $.super)),
      '.',
      field('name', $._javaswing_transfer_handler_method),
      field('arguments', $.argument_list),
    )),

    javaswing_root_pane_extended: $ => prec(PREC.OBJ_ACCESS + 2, choice(
      seq(
        field('name', $._javaswing_root_pane_extended_method),
        field('arguments', $.argument_list),
      ),
      seq(
        field('container', choice($.primary_expression, $.super)),
        '.',
        field('name', $._javaswing_root_pane_extended_method),
        field('arguments', $.argument_list),
      ),
    )),

    _javaswing_box_factory_method: _ => choice(
      ...JAVASWING_BOX_FACTORY_METHODS.map(method => method),
    ),

    _javaswing_bounds_geometry_method: _ => choice(
      ...JAVASWING_BOUNDS_GEOMETRY_METHODS.map(method => method),
    ),

    _javaswing_window_lifecycle_method: _ => choice(
      ...JAVASWING_WINDOW_LIFECYCLE_METHODS.map(method => method),
    ),

    _javaswing_root_pane_structure_method: _ => choice(
      ...JAVASWING_ROOT_PANE_STRUCTURE_METHODS.map(method => method),
    ),

    _javaswing_keyboard_binding_method: _ => choice(
      ...JAVASWING_KEYBOARD_BINDING_METHODS.map(method => method),
    ),

    _javaswing_root_pane_extended_method: _ => choice(
      ...JAVASWING_ROOT_PANE_EXTENDED_METHODS.map(method => method),
    ),

    _javaswing_property_setter_method: _ => choice(
      ...JAVASWING_PROPERTY_SETTER_METHODS.map(method => method),
    ),

    _javaswing_table_model_mutation_method: _ => choice(
      ...JAVASWING_TABLE_MODEL_MUTATION_METHODS.map(method => method),
    ),

    _javaswing_event_listener_method: _ => choice(
      ...JAVASWING_EVENT_LISTENER_METHODS.map(method => method),
    ),

    _javaswing_set_auto_resize_mode_method: _ => 'setAutoResizeMode',

    _javaswing_get_column_model_method: _ => 'getColumnModel',

    _javaswing_set_column_model_method: _ => 'setColumnModel',

    _javaswing_get_table_header_method: _ => 'getTableHeader',

    _javaswing_set_table_header_method: _ => 'setTableHeader',

    _javaswing_get_column_method: _ => 'getColumn',

    _javaswing_table_column_configuration_method: _ => choice(
      ...JAVASWING_TABLE_COLUMN_CONFIGURATION_METHODS.map(method => method),
    ),

    _javaswing_table_column_variable_configuration_method: _ => choice(
      ...JAVASWING_TABLE_COLUMN_VARIABLE_CONFIGURATION_METHODS.map(method => method),
    ),

    _javaswing_table_column_model_access_method: _ => choice(
      ...JAVASWING_TABLE_COLUMN_MODEL_ACCESS_METHODS.map(method => method),
    ),

    _javaswing_table_column_model_mutation_method: _ => choice(
      ...JAVASWING_TABLE_COLUMN_MODEL_MUTATION_METHODS.map(method => method),
    ),

    _javaswing_table_header_configuration_method: _ => choice(
      ...JAVASWING_TABLE_HEADER_CONFIGURATION_METHODS.map(method => method),
    ),

    _javaswing_set_viewport_view_method: _ => 'setViewportView',

    _javaswing_scroll_bar_policy_method: _ => choice(
      ...JAVASWING_SCROLL_BAR_POLICY_METHODS.map(method => method),
    ),

    _javaswing_scroll_bar_access_method: _ => choice(
      ...JAVASWING_SCROLL_BAR_ACCESS_METHODS.map(method => method),
    ),

    _javaswing_scroll_bar_increment_method: _ => choice(
      ...JAVASWING_SCROLL_BAR_INCREMENT_METHODS.map(method => method),
    ),

    _javaswing_text_editor_method: _ => choice(
      ...JAVASWING_TEXT_EDITOR_METHODS.map(method => method),
    ),

    _javaswing_set_page_method: _ => 'setPage',

    _javaswing_action_put_value_method: _ => 'putValue',

    _javaswing_focus_method: _ => choice(
      ...JAVASWING_FOCUS_METHODS.map(method => method),
    ),

    _javaswing_transfer_handler_method: _ => choice(
      ...JAVASWING_TRANSFER_HANDLER_METHODS.map(method => method),
    ),

    _javaswing_formatted_text_field_focus_lost_method: _ => choice(
      ...JAVASWING_FORMATTED_TEXT_FIELD_FOCUS_LOST_METHODS.map(method => method),
    ),

    _javaswing_formatted_text_field_focus_lost_constant_name: _ => choice(
      ...JAVASWING_FORMATTED_TEXT_FIELD_FOCUS_LOST_CONSTANTS.map(name => name),
    ),

    _javaswing_text_input_configuration_method: _ => choice(
      ...JAVASWING_TEXT_INPUT_CONFIGURATION_METHODS.map(method => method),
    ),

    _javaswing_text_input_alignment_constant_name: _ => choice(
      ...JAVASWING_TEXT_INPUT_ALIGNMENT_CONSTANTS.map(name => name),
    ),

    _javaswing_set_border_method: _ => 'setBorder',

    _javaswing_set_viewport_border_method: _ => 'setViewportBorder',

    _javaswing_border_factory_method: _ => choice(
      ...JAVASWING_BORDER_FACTORY_METHODS.map(method => method),
    ),

    _javaswing_option_pane_dialog_method: _ => choice(
      ...JAVASWING_OPTION_PANE_DIALOG_METHODS.map(method => method),
    ),

    _javaswing_option_pane_context_method: _ => choice(
      ...JAVASWING_OPTION_PANE_CONTEXT_METHODS.map(method => method),
    ),

    _javaswing_option_pane_constant_name: _ => choice(
      ...JAVASWING_OPTION_PANE_CONSTANTS.map(name => name),
    ),

    _javaswing_dialog_modality_method: _ => choice(
      ...JAVASWING_DIALOG_MODALITY_METHODS.map(method => method),
    ),

    _javaswing_file_chooser_dialog_method: _ => choice(
      ...JAVASWING_FILE_CHOOSER_DIALOG_METHODS.map(method => method),
    ),

    _javaswing_file_chooser_selection_method: _ => choice(
      ...JAVASWING_FILE_CHOOSER_SELECTION_METHODS.map(method => method),
    ),

    _javaswing_file_chooser_configuration_method: _ => choice(
      ...JAVASWING_FILE_CHOOSER_CONFIGURATION_METHODS.map(method => method),
    ),

    _javaswing_file_chooser_constant_name: _ => choice(
      ...JAVASWING_FILE_CHOOSER_CONSTANTS.map(name => name),
    ),

    _javaswing_tabbed_pane_tab_method: _ => choice(
      ...JAVASWING_TABBED_PANE_TAB_METHODS.map(method => method),
    ),

    _javaswing_tabbed_pane_selection_method: _ => choice(
      ...JAVASWING_TABBED_PANE_SELECTION_METHODS.map(method => method),
    ),

    _javaswing_tabbed_pane_lookup_method: _ => choice(
      ...JAVASWING_TABBED_PANE_LOOKUP_METHODS.map(method => method),
    ),

    _javaswing_tabbed_pane_appearance_method: _ => choice(
      ...JAVASWING_TABBED_PANE_APPEARANCE_METHODS.map(method => method),
    ),

    _javaswing_tabbed_pane_layout_method: _ => choice(
      ...JAVASWING_TABBED_PANE_LAYOUT_METHODS.map(method => method),
    ),

    _javaswing_tabbed_pane_constant_name: _ => choice(
      ...JAVASWING_TABBED_PANE_CONSTANTS.map(name => name),
    ),

    _javaswing_split_pane_component_method: _ => choice(
      ...JAVASWING_SPLIT_PANE_COMPONENT_METHODS.map(method => method),
    ),

    _javaswing_split_pane_divider_method: _ => choice(
      ...JAVASWING_SPLIT_PANE_DIVIDER_METHODS.map(method => method),
    ),

    _javaswing_split_pane_orientation_method: _ => choice(
      ...JAVASWING_SPLIT_PANE_ORIENTATION_METHODS.map(method => method),
    ),

    _javaswing_split_pane_constant_name: _ => choice(
      ...JAVASWING_SPLIT_PANE_CONSTANTS.map(name => name),
    ),

    _javaswing_popup_menu_display_method: _ => prec(1, 'show'),

    _javaswing_combo_box_selection_method: _ => choice(
      ...JAVASWING_COMBO_BOX_SELECTION_METHODS.map(method => method),
    ),

    _javaswing_combo_box_popup_method: _ => choice(
      ...JAVASWING_COMBO_BOX_POPUP_METHODS.map(method => method),
    ),

    _javaswing_combo_box_renderer_editor_method: _ => choice(
      ...JAVASWING_COMBO_BOX_RENDERER_EDITOR_METHODS.map(method => method),
    ),

    _javaswing_combo_box_display_method: _ => choice(
      ...JAVASWING_COMBO_BOX_DISPLAY_METHODS.map(method => method),
    ),

    _javaswing_combo_box_item_method: _ => choice(
      ...JAVASWING_COMBO_BOX_ITEM_METHODS.map(method => method),
    ),

    _javaswing_item_model_method: _ => choice(
      ...JAVASWING_ITEM_MODEL_METHODS.map(method => method),
    ),

    _javaswing_cell_renderer_editor_method: _ => choice(
      ...JAVASWING_CELL_RENDERER_EDITOR_METHODS.map(method => prec(2, method)),
    ),

    _javaswing_toolbar_separator_method: _ => choice(
      ...JAVASWING_TOOLBAR_SEPARATOR_METHODS.map(method => prec(2, method)),
    ),

    _javaswing_toolbar_behavior_method: _ => choice(
      ...JAVASWING_TOOLBAR_BEHAVIOR_METHODS.map(method => prec(2, method)),
    ),

    _javaswing_selection_flag_method: _ => choice(
      'setCellSelectionEnabled',
      'setColumnSelectionAllowed',
      'setRowSelectionAllowed',
    ),

    _javaswing_set_selection_mode_method: _ => 'setSelectionMode',

    _javaswing_set_selection_model_method: _ => 'setSelectionModel',

    _javaswing_get_selection_model_method: _ => 'getSelectionModel',

    _javaswing_action_command_setter_method: _ => 'setActionCommand',

    _javaswing_action_command_getter_method: _ => 'getActionCommand',

    _javaswing_set_menu_bar_method: _ => 'setJMenuBar',

    _javaswing_set_component_popup_menu_method: _ => 'setComponentPopupMenu',

    _method_name: $ => choice(
      $.identifier,
      $._reserved_identifier,
      $._javaswing_container_add_method,
      $._javaswing_get_content_pane_method,
      $._javaswing_set_layout_method,
      $._javaswing_property_setter_method,
      $._javaswing_table_model_mutation_method,
      $._javaswing_event_listener_method,
      $._javaswing_action_command_setter_method,
      $._javaswing_action_command_getter_method,
      $._javaswing_set_border_method,
      $._javaswing_set_viewport_border_method,
      $._javaswing_border_factory_method,
      $._javaswing_box_factory_method,
      $._javaswing_bounds_geometry_method,
      $._javaswing_window_lifecycle_method,
      $._javaswing_root_pane_structure_method,
      $._javaswing_option_pane_dialog_method,
      $._javaswing_option_pane_context_method,
      $._javaswing_dialog_modality_method,
      $._javaswing_file_chooser_dialog_method,
      $._javaswing_file_chooser_selection_method,
      $._javaswing_file_chooser_configuration_method,
      $._javaswing_tabbed_pane_tab_method,
      $._javaswing_tabbed_pane_selection_method,
      $._javaswing_tabbed_pane_lookup_method,
      $._javaswing_tabbed_pane_appearance_method,
      $._javaswing_tabbed_pane_layout_method,
      $._javaswing_split_pane_component_method,
      $._javaswing_split_pane_divider_method,
      $._javaswing_split_pane_orientation_method,
      $._javaswing_scroll_bar_access_method,
      $._javaswing_scroll_bar_increment_method,
      $._javaswing_text_editor_method,
      $._javaswing_combo_box_selection_method,
      $._javaswing_combo_box_popup_method,
      $._javaswing_combo_box_renderer_editor_method,
      $._javaswing_combo_box_display_method,
      $._javaswing_combo_box_item_method,
      $._javaswing_item_model_method,
      $._javaswing_cell_renderer_editor_method,
    ),
    

    argument_list: $ => seq('(', commaSep($.expression), ')'),

    method_reference: $ => seq(
      choice($._type, $.primary_expression, $.super),
      '::',
      optional($.type_arguments),
      choice('new', $.identifier),
    ),

    type_arguments: $ => seq(
      '<',
      commaSep(choice($._type, $.wildcard)),
      '>',
    ),

    wildcard: $ => seq(
      repeat($._annotation),
      '?',
      optional($._wildcard_bounds),
    ),

    _wildcard_bounds: $ => choice(
      seq('extends', $._type),
      seq($.super, $._type),
    ),

    dimensions: $ => prec.right(repeat1(
      seq(repeat($._annotation), '[', ']'),
    )),

    switch_expression: $ => seq(
      'switch',
      field('condition', $.parenthesized_expression),
      field('body', $.switch_block),
    ),

    switch_block: $ => seq(
      '{',
      choice(
        repeat($.switch_block_statement_group),
        repeat($.switch_rule),
      ),
      '}',
    ),

    switch_block_statement_group: $ => prec.left(seq(
      repeat1(seq($.switch_label, ':')),
      repeat($.statement),
    )),

    switch_rule: $ => seq(
      $.switch_label,
      '->',
      choice($.expression_statement, $.throw_statement, $.block),
    ),

    switch_label: $ => choice(
      seq('case',
        choice(
          $.pattern,
          commaSep1($.expression),
        ),
        optional($.guard),
      ),
      'default',
    ),

    pattern: $ => choice(
      $.type_pattern,
      $.record_pattern,
    ),
    type_pattern: $ => seq($._unannotated_type, choice($.identifier, $._reserved_identifier)),
    record_pattern: $ => seq(choice($.identifier, $._reserved_identifier, $.generic_type), $.record_pattern_body),
    record_pattern_body: $ => seq('(', commaSep(choice($.record_pattern_component, $.record_pattern)), ')'),
    record_pattern_component: $ => choice(
      $.underscore_pattern,
      seq(
        $._unannotated_type,
        choice($.identifier, $._reserved_identifier),
      ),
    ),

    underscore_pattern: _ => '_',

    guard: $ => seq('when', $.expression),

    // Statements

    statement: $ => choice(
      $.declaration,
      $.expression_statement,
      $.labeled_statement,
      $.if_statement,
      $.while_statement,
      $.for_statement,
      $.enhanced_for_statement,
      $.block,
      ';',
      $.assert_statement,
      $.do_statement,
      $.break_statement,
      $.continue_statement,
      $.return_statement,
      $.yield_statement,
      $.switch_expression, // switch statements and expressions are identical
      $.synchronized_statement,
      $.javaswing_button_group_local_declaration,
      $.javaswing_combo_box_local_declaration,
      $.javaswing_item_model_local_declaration,
      $.javaswing_cell_renderer_editor_local_declaration,
      $.javaswing_toolbar_local_declaration,
      $.javaswing_progress_bar_local_declaration,
      $.javaswing_separator_local_declaration,
      $.javaswing_list_local_declaration,
      $.javaswing_scroll_bar_local_declaration,
      $.javaswing_text_editor_local_declaration,
      $.javaswing_password_field_local_declaration,
      $.javaswing_formatted_text_field_local_declaration,
      $.javaswing_text_input_local_declaration,
      $.javaswing_selectable_button_local_declaration,
      $.javaswing_spinner_local_declaration,
      $.javaswing_spinner_model_local_declaration,
      $.javaswing_grid_bag_constraints_local_declaration,
      $.local_variable_declaration,
      $.throw_statement,
      $.try_statement,
      $.try_with_resources_statement,
    ),

    block: $ => seq(
      '{', repeat($.statement), '}',
    ),

    expression_statement: $ => seq(
      $.expression,
      ';',
    ),

    labeled_statement: $ => seq(
      $.identifier, ':', $.statement,
    ),

    assert_statement: $ => choice(
      seq('assert', $.expression, ';'),
      seq('assert', $.expression, ':', $.expression, ';'),
    ),

    do_statement: $ => seq(
      'do',
      field('body', $.statement),
      'while',
      field('condition', $.parenthesized_expression),
      ';',
    ),

    break_statement: $ => seq('break', optional($.identifier), ';'),

    continue_statement: $ => seq('continue', optional($.identifier), ';'),

    return_statement: $ => seq(
      'return',
      optional($.expression),
      ';',
    ),

    yield_statement: $ => seq(
      'yield',
      $.expression,
      ';',
    ),

    synchronized_statement: $ => seq(
      'synchronized',
      $.parenthesized_expression,
      field('body', $.block),
    ),

    throw_statement: $ => seq('throw', $.expression, ';'),

    try_statement: $ => seq(
      'try',
      field('body', $.block),
      choice(
        repeat1($.catch_clause),
        seq(repeat($.catch_clause), $.finally_clause),
      ),
    ),

    catch_clause: $ => seq(
      'catch',
      '(',
      $.catch_formal_parameter,
      ')',
      field('body', $.block),
    ),

    catch_formal_parameter: $ => seq(
      optional($.modifiers),
      $.catch_type,
      $._variable_declarator_id,
    ),

    catch_type: $ => sep1($._unannotated_type, '|'),

    finally_clause: $ => seq('finally', $.block),

    try_with_resources_statement: $ => seq(
      'try',
      field('resources', $.resource_specification),
      field('body', $.block),
      repeat($.catch_clause),
      optional($.finally_clause),
    ),

    resource_specification: $ => seq(
      '(', sep1($.resource, ';'), optional(';'), ')',
    ),

    resource: $ => choice(
      seq(
        optional($.modifiers),
        field('type', $._unannotated_type),
        $._variable_declarator_id,
        '=',
        field('value', $.expression),
      ),
      $.identifier,
      $.field_access,
    ),

    if_statement: $ => prec.right(seq(
      'if',
      field('condition', $.parenthesized_expression),
      field('consequence', $.statement),
      optional(seq('else', field('alternative', $.statement))),
    )),

    while_statement: $ => seq(
      'while',
      field('condition', $.parenthesized_expression),
      field('body', $.statement),
    ),

    for_statement: $ => seq(
      'for', '(',
      choice(
        field('init', $.local_variable_declaration),
        seq(
          commaSep(field('init', $.expression)),
          ';',
        ),
      ),
      field('condition', optional($.expression)), ';',
      commaSep(field('update', $.expression)), ')',
      field('body', $.statement),
    ),

    enhanced_for_statement: $ => seq(
      'for',
      '(',
      optional($.modifiers),
      field('type', $._unannotated_type),
      $._variable_declarator_id,
      ':',
      field('value', $.expression),
      ')',
      field('body', $.statement),
    ),

    // Annotations

    _annotation: $ => choice(
      $.marker_annotation,
      $.annotation,
    ),

    marker_annotation: $ => seq(
      '@',
      field('name', $._name),
    ),

    annotation: $ => seq(
      '@',
      field('name', $._name),
      field('arguments', $.annotation_argument_list),
    ),

    annotation_argument_list: $ => seq(
      '(',
      choice(
        $._element_value,
        commaSep($.element_value_pair),
      ),
      ')',
    ),

    element_value_pair: $ => seq(
      field('key', choice($.identifier, $._reserved_identifier)),
      '=',
      field('value', $._element_value),
    ),

    _element_value: $ => prec(PREC.ELEMENT_VAL, choice(
      $.expression,
      $.element_value_array_initializer,
      $._annotation,
    )),

    element_value_array_initializer: $ => seq(
      '{',
      commaSep($._element_value),
      optional(','),
      '}',
    ),

    // Declarations

    declaration: $ => prec(PREC.DECL, choice(
      $.module_declaration,
      $.package_declaration,
      $.import_declaration,
      $.javaswing_screen,
      $.javaswing_selectable_button_class_declaration,
      $.class_declaration,
      $.record_declaration,
      $.interface_declaration,
      $.annotation_type_declaration,
      $.enum_declaration,
    )),

    module_declaration: $ => seq(
      repeat($._annotation),
      optional('open'),
      'module',
      field('name', $._name),
      field('body', $.module_body),
    ),

    module_body: $ => seq(
      '{',
      repeat($.module_directive),
      '}',
    ),

    module_directive: $ => choice(
      $.requires_module_directive,
      $.exports_module_directive,
      $.opens_module_directive,
      $.uses_module_directive,
      $.provides_module_directive,
    ),

    requires_module_directive: $ => seq(
      'requires',
      repeat(field('modifiers', $.requires_modifier)),
      field('module', $._name),
      ';',
    ),

    requires_modifier: _ => choice(
      'transitive',
      'static',
    ),

    exports_module_directive: $ => seq(
      'exports',
      field('package', $._name),
      optional(seq(
        'to',
        field('modules', $._name),
        repeat(seq(',', field('modules', $._name))),
      )),
      ';',
    ),

    opens_module_directive: $ => seq(
      'opens',
      field('package', $._name),
      optional(seq(
        'to',
        field('modules', $._name),
        repeat(seq(',', field('modules', $._name))),
      )),
      ';',
    ),

    uses_module_directive: $ => seq(
      'uses',
      field('type', $._name),
      ';',
    ),

    provides_module_directive: $ => seq(
      'provides',
      field('provided', $._name),
      'with',
      $._name,
      repeat(seq(',', (field('provider', $._name)))),
      ';',
    ),

    package_declaration: $ => seq(
      repeat($._annotation),
      'package',
      $._name,
      ';',
    ),

    import_declaration: $ => seq(
      'import',
      optional('static'),
      $._name,
      optional(seq('.', $.asterisk)),
      ';',
    ),

    asterisk: _ => '*',

    enum_declaration: $ => seq(
      optional($.modifiers),
      'enum',
      field('name', $.identifier),
      field('interfaces', optional($.super_interfaces)),
      field('body', $.enum_body),
    ),

    enum_body: $ => seq(
      '{',
      commaSep($.enum_constant),
      optional(','),
      optional($.enum_body_declarations),
      '}',
    ),

    enum_body_declarations: $ => seq(
      ';',
      repeat($._class_body_declaration),
    ),

    enum_constant: $ => (seq(
      optional($.modifiers),
      field('name', $.identifier),
      field('arguments', optional($.argument_list)),
      field('body', optional($.class_body)),
    )),

    class_declaration: $ => seq(
      optional($.modifiers),
      'class',
      field('name', $.identifier),
      optional(field('type_parameters', $.type_parameters)),
      optional(field('superclass', $.superclass)),
      optional(field('interfaces', $.super_interfaces)),
      optional(field('permits', $.permits)),
      field('body', $.class_body),
    ),

    javaswing_screen: $ => prec(PREC.DECL + 1, seq(
      optional($.modifiers),
      'class',
      field('name', $.identifier),
      optional(field('type_parameters', $.type_parameters)),
      field('superclass', $.javaswing_screen_superclass),
      optional(field('interfaces', $.super_interfaces)),
      optional(field('permits', $.permits)),
      field('body', $.class_body),
    )),

    javaswing_screen_superclass: $ => seq(
      'extends',
      field('type', $.javaswing_screen_type),
    ),

    javaswing_screen_type: $ => choice(
      choice(...JAVASWING_SCREEN_SWING_TYPES),
      choice(...JAVASWING_SCREEN_AWT_TYPES),
      token(seq('javax', '.', 'swing', '.', choice(...JAVASWING_SCREEN_SWING_TYPES))),
      token(seq('java', '.', 'awt', '.', choice(...JAVASWING_SCREEN_AWT_TYPES))),
    ),

    javaswing_selectable_button_class_declaration: $ => prec(PREC.DECL + 1, seq(
      optional($.modifiers),
      'class',
      field('name', $.identifier),
      optional(field('type_parameters', $.type_parameters)),
      field('superclass', $.javaswing_selectable_button_superclass),
      optional(field('interfaces', $.super_interfaces)),
      optional(field('permits', $.permits)),
      field('body', $.class_body),
    )),

    javaswing_selectable_button_superclass: $ => seq(
      'extends',
      field('type', $.javaswing_selectable_button_class),
    ),

    modifiers: $ => repeat1(choice(
      $._annotation,
      'public',
      'protected',
      'private',
      'abstract',
      'static',
      'final',
      'strictfp',
      'default',
      'synchronized',
      'native',
      'transient',
      'volatile',
      'sealed',
      'non-sealed',
    )),

    type_parameters: $ => seq(
      '<', commaSep1($.type_parameter), '>',
    ),

    type_parameter: $ => seq(
      repeat($._annotation),
      alias($.identifier, $.type_identifier),
      optional($.type_bound),
    ),

    type_bound: $ => seq('extends', $._type, repeat(seq('&', $._type))),

    superclass: $ => seq(
      'extends',
      $._type,
    ),

    super_interfaces: $ => seq(
      'implements',
      $.type_list,
    ),

    type_list: $ => seq(
      $._type,
      repeat(seq(',', $._type)),
    ),

    permits: $ => seq(
      'permits',
      $.type_list,
    ),

    class_body: $ => seq(
      '{',
      repeat($._class_body_declaration),
      '}',
    ),

    _class_body_declaration: $ => choice(
      $.javaswing_event_handler,
      $.javaswing_init_components,
      $.javaswing_swing_worker_callback,
      $.method_declaration,
      $.javaswing_button_group_field,
      $.javaswing_combo_box_field,
      $.javaswing_item_model_field,
      $.javaswing_cell_renderer_editor_field,
      $.javaswing_toolbar_field,
      $.javaswing_progress_bar_field,
      $.javaswing_separator_field,
      $.javaswing_list_field,
      $.javaswing_scroll_bar_field,
      $.javaswing_text_editor_field,
      $.javaswing_password_field_field,
      $.javaswing_formatted_text_field_field,
      $.javaswing_text_input_field,
      $.javaswing_selectable_button_field,
      $.javaswing_spinner_field,
      $.javaswing_spinner_model_field,
      $.javaswing_grid_bag_constraints_field,
      $.javaswing_component_field,
      $.field_declaration,
      $.record_declaration,
      $.compact_constructor_declaration, // For records.
      $.javaswing_screen,
      $.javaswing_selectable_button_class_declaration,
      $.class_declaration,
      $.interface_declaration,
      $.annotation_type_declaration,
      $.enum_declaration,
      $.block,
      $.static_initializer,
      $.constructor_declaration,
      ';',
    ),

    static_initializer: $ => seq(
      'static',
      $.block,
    ),

    constructor_declaration: $ => seq(
      optional($.modifiers),
      $._constructor_declarator,
      optional($.throws),
      field('body', $.constructor_body),
    ),

    _constructor_declarator: $ => seq(
      field('type_parameters', optional($.type_parameters)),
      field('name', $.identifier),
      field('parameters', $.formal_parameters),
    ),

    constructor_body: $ => seq(
      '{',
      optional($.explicit_constructor_invocation),
      repeat($.statement),
      '}',
    ),

    explicit_constructor_invocation: $ => seq(
      choice(
        seq(
          field('type_arguments', optional($.type_arguments)),
          field('constructor', choice($.this, $.super)),
        ),
        seq(
          field('object', choice($.primary_expression)),
          '.',
          field('type_arguments', optional($.type_arguments)),
          field('constructor', $.super),
        ),
      ),
      field('arguments', $.argument_list),
      ';',
    ),

    _name: $ => choice(
      $.identifier,
      $._reserved_identifier,
      $.scoped_identifier,
    ),

    scoped_identifier: $ => seq(
      field('scope', $._name),
      '.',
      field('name', $.identifier),
    ),

    field_declaration: $ => seq(
      optional($.modifiers),
      field('type', $._unannotated_type),
      $._variable_declarator_list,
      ';',
    ),

    javaswing_component_field: $ => seq(
      optional($.modifiers),
      field('type', $.javaswing_component_reference_type),
      $._variable_declarator_list,
      ';',
    ),

    javaswing_button_group_field: $ => prec(PREC.DECL + 1, seq(
      optional($.modifiers),
      field('type', $.javaswing_button_group_class),
      $._variable_declarator_list,
      ';',
    )),

    javaswing_combo_box_field: $ => prec.dynamic(1, seq(
      optional($.modifiers),
      field('type', $.javaswing_combo_box_reference_type),
      $._variable_declarator_list,
      ';',
    )),

    javaswing_item_model_field: $ => seq(
      optional($.modifiers),
      field('type', $.javaswing_item_model_class),
      $._variable_declarator_list,
      ';',
    ),

    javaswing_cell_renderer_editor_field: $ => seq(
      optional($.modifiers),
      field('type', $.javaswing_cell_renderer_editor_class),
      $._variable_declarator_list,
      ';',
    ),

    javaswing_toolbar_field: $ => seq(
      optional($.modifiers),
      field('type', $.javaswing_toolbar_class),
      $._variable_declarator_list,
      ';',
    ),

    javaswing_progress_bar_field: $ => prec.dynamic(1, seq(
      optional($.modifiers),
      field('type', $.javaswing_progress_bar_class),
      $._variable_declarator_list,
      ';',
    )),

    javaswing_separator_field: $ => prec.dynamic(1, seq(
      optional($.modifiers),
      field('type', $.javaswing_separator_class),
      $._variable_declarator_list,
      ';',
    )),

    javaswing_list_field: $ => prec.dynamic(1, seq(
      optional($.modifiers),
      field('type', $.javaswing_list_class),
      $._variable_declarator_list,
      ';',
    )),

    javaswing_scroll_bar_field: $ => prec.dynamic(1, seq(
      optional($.modifiers),
      field('type', $.javaswing_scroll_bar_class),
      $._variable_declarator_list,
      ';',
    )),

    javaswing_text_editor_field: $ => prec.dynamic(1, seq(
      optional($.modifiers),
      field('type', $.javaswing_text_editor_class),
      $._variable_declarator_list,
      ';',
    )),

    javaswing_password_field_field: $ => prec.dynamic(1, seq(
      optional($.modifiers),
      field('type', $.javaswing_password_field_class),
      $._variable_declarator_list,
      ';',
    )),

    javaswing_formatted_text_field_field: $ => prec.dynamic(1, seq(
      optional($.modifiers),
      field('type', $.javaswing_formatted_text_field_class),
      $._variable_declarator_list,
      ';',
    )),

    javaswing_text_input_field: $ => prec.dynamic(1, seq(
      optional($.modifiers),
      field('type', $.javaswing_text_input_class),
      $._variable_declarator_list,
      ';',
    )),

    javaswing_selectable_button_field: $ => prec.dynamic(1, seq(
      optional($.modifiers),
      field('type', $.javaswing_selectable_button_class),
      $._variable_declarator_list,
      ';',
    )),

    javaswing_spinner_field: $ => prec.dynamic(1, seq(
      optional($.modifiers),
      field('type', $.javaswing_spinner_class),
      $._variable_declarator_list,
      ';',
    )),

    javaswing_spinner_model_field: $ => prec.dynamic(1, seq(
      optional($.modifiers),
      field('type', $.javaswing_spinner_model_class),
      $._variable_declarator_list,
      ';',
    )),

    javaswing_grid_bag_constraints_field: $ => seq(
      optional($.modifiers),
      field('type', $.javaswing_grid_bag_constraints_class),
      $._variable_declarator_list,
      ';',
    ),

    javaswing_component_reference_type: $ => choice(
      $.javaswing_component_type,
      $.javaswing_component_generic_type,
      $.javaswing_component_array_type,
    ),

    javaswing_component_generic_type: $ => prec.dynamic(PREC.GENERIC + 1, seq(
      field('type', $.javaswing_component_type),
      $.type_arguments,
    )),

    javaswing_component_array_type: $ => seq(
      field('element', choice(
        $.javaswing_component_type,
        $.javaswing_component_generic_type,
      )),
      field('dimensions', $.dimensions),
    ),

    javaswing_component_type: $ => choice(
      choice(...JAVASWING_COMPONENT_SWING_TYPES),
    ),

    record_declaration: $ => seq(
      optional($.modifiers),
      'record',
      field('name', $.identifier),
      optional(field('type_parameters', $.type_parameters)),
      field('parameters', $.formal_parameters),
      optional(field('interfaces', $.super_interfaces)),
      field('body', $.class_body),
    ),

    annotation_type_declaration: $ => seq(
      optional($.modifiers),
      '@interface',
      field('name', $.identifier),
      field('body', $.annotation_type_body),
    ),

    annotation_type_body: $ => seq(
      '{',
      repeat(choice(
        $.annotation_type_element_declaration,
        $.constant_declaration,
        $.class_declaration,
        $.interface_declaration,
        $.enum_declaration,
        $.annotation_type_declaration,
        ';',
      )),
      '}',
    ),

    annotation_type_element_declaration: $ => seq(
      optional($.modifiers),
      field('type', $._unannotated_type),
      field('name', choice($.identifier, $._reserved_identifier)),
      '(', ')',
      field('dimensions', optional($.dimensions)),
      optional($._default_value),
      ';',
    ),

    _default_value: $ => seq(
      'default',
      field('value', $._element_value),
    ),

    interface_declaration: $ => seq(
      optional($.modifiers),
      'interface',
      field('name', $.identifier),
      field('type_parameters', optional($.type_parameters)),
      optional($.extends_interfaces),
      optional(field('permits', $.permits)),
      field('body', $.interface_body),
    ),

    extends_interfaces: $ => seq(
      'extends',
      $.type_list,
    ),

    interface_body: $ => seq(
      '{',
      repeat(choice(
        $.constant_declaration,
        $.enum_declaration,
        $.method_declaration,
        $.class_declaration,
        $.interface_declaration,
        $.record_declaration,
        $.annotation_type_declaration,
        ';',
      )),
      '}',
    ),

    constant_declaration: $ => seq(
      optional($.modifiers),
      field('type', $._unannotated_type),
      $._variable_declarator_list,
      ';',
    ),

    _variable_declarator_list: $ => commaSep1(
      field('declarator', $.variable_declarator),
    ),

    variable_declarator: $ => seq(
      $._variable_declarator_id,
      optional(seq('=', field('value', $._variable_initializer))),
    ),

    _variable_declarator_id: $ => seq(
      field('name', choice($.identifier, $._reserved_identifier, $.underscore_pattern)),
      field('dimensions', optional($.dimensions)),
    ),

    _variable_initializer: $ => choice(
      $.expression,
      $.array_initializer,
    ),

    array_initializer: $ => seq(
      '{',
      commaSep($._variable_initializer),
      optional(','),
      '}',
    ),

    // Types

    _type: $ => choice(
      $._unannotated_type,
      $.annotated_type,
    ),

    _unannotated_type: $ => choice(
      $._simple_type,
      $.array_type,
    ),

    _simple_type: $ => choice(
      $.void_type,
      $.integral_type,
      $.floating_point_type,
      $.boolean_type,
      $.javaswing_dialog_type,
      $.javaswing_file_chooser_class,
      $.javaswing_tabbed_pane_class,
      $.javaswing_split_pane_class,
      $.javaswing_button_group_class,
      $.javaswing_combo_box_class,
      $.javaswing_item_model_class,
      $.javaswing_cell_renderer_editor_class,
      $.javaswing_toolbar_class,
      $.javaswing_progress_bar_class,
      $.javaswing_separator_class,
      $.javaswing_list_class,
      $.javaswing_scroll_bar_class,
      $.javaswing_text_editor_class,
      $.javaswing_password_field_class,
      $.javaswing_formatted_text_field_class,
      $.javaswing_text_input_class,
      $.javaswing_selectable_button_class,
      $.javaswing_spinner_class,
      $.javaswing_spinner_model_class,
      $.javaswing_box_class,
      $.javaswing_timer_class,
      $.javaswing_document_class,
      $.javaswing_transfer_handler_class,
      $.javaswing_insets_class,
      $.javaswing_dimension_class,
      alias($.identifier, $.type_identifier),
      $.scoped_type_identifier,
      $.generic_type,
    ),

    annotated_type: $ => seq(
      repeat1($._annotation),
      $._unannotated_type,
    ),

    scoped_type_identifier: $ => seq(
      choice(
        alias($.identifier, $.type_identifier),
        $.scoped_type_identifier,
        $.generic_type,
      ),
      '.',
      repeat($._annotation),
      alias($.identifier, $.type_identifier),
    ),

    generic_type: $ => prec.dynamic(PREC.GENERIC, seq(
      choice(
        alias($.identifier, $.type_identifier),
        $.scoped_type_identifier,
      ),
      $.type_arguments,
    )),

    array_type: $ => seq(
      field('element', $._unannotated_type),
      field('dimensions', $.dimensions),
    ),

    integral_type: _ => choice(
      'byte',
      'short',
      'int',
      'long',
      'char',
    ),

    floating_point_type: _ => choice(
      'float',
      'double',
    ),

    boolean_type: _ => 'boolean',

    void_type: _ => 'void',

    _method_header: $ => seq(
      optional(seq(
        field('type_parameters', $.type_parameters),
        repeat($._annotation),
      )),
      field('type', choice($._unannotated_type, $.javaswing_component_reference_type)),
      $._method_declarator,
      optional($.throws),
    ),

    _method_declarator: $ => seq(
      field('name', choice($.identifier, $._reserved_identifier, $.javaswing_event_handler_name)),
      field('parameters', $.formal_parameters),
      field('dimensions', optional($.dimensions)),
    ),

    formal_parameters: $ => seq(
      '(',
      choice(
        $.receiver_parameter,
        seq(
          optional(seq($.receiver_parameter, ',')),
          commaSep(choice($.formal_parameter, $.spread_parameter)),
        ),
      ),
      ')',
    ),

    formal_parameter: $ => seq(
      optional($.modifiers),
      field('type', $._unannotated_type),
      $._variable_declarator_id,
    ),

    receiver_parameter: $ => seq(
      repeat($._annotation),
      $._unannotated_type,
      repeat(seq($.identifier, '.')),
      $.this,
    ),

    spread_parameter: $ => seq(
      optional($.modifiers),
      $._unannotated_type,
      '...',
      repeat($._annotation),
      $.variable_declarator,
    ),

    throws: $ => seq(
      'throws', commaSep1($._type),
    ),

    local_variable_declaration: $ => seq(
      optional($.modifiers),
      field('type', $._unannotated_type),
      $._variable_declarator_list,
      ';',
    ),

    javaswing_combo_box_local_declaration: $ => prec.dynamic(1, seq(
      optional($.modifiers),
      field('type', $.javaswing_combo_box_reference_type),
      $._variable_declarator_list,
      ';',
    )),

    javaswing_item_model_local_declaration: $ => seq(
      optional($.modifiers),
      field('type', $.javaswing_item_model_class),
      $._variable_declarator_list,
      ';',
    ),

    javaswing_cell_renderer_editor_local_declaration: $ => seq(
      optional($.modifiers),
      field('type', $.javaswing_cell_renderer_editor_class),
      $._variable_declarator_list,
      ';',
    ),

    javaswing_toolbar_local_declaration: $ => seq(
      optional($.modifiers),
      field('type', $.javaswing_toolbar_class),
      $._variable_declarator_list,
      ';',
    ),

    javaswing_progress_bar_local_declaration: $ => seq(
      optional($.modifiers),
      field('type', $.javaswing_progress_bar_class),
      $._variable_declarator_list,
      ';',
    ),

    javaswing_separator_local_declaration: $ => seq(
      optional($.modifiers),
      field('type', $.javaswing_separator_class),
      $._variable_declarator_list,
      ';',
    ),

    javaswing_list_local_declaration: $ => seq(
      optional($.modifiers),
      field('type', $.javaswing_list_class),
      $._variable_declarator_list,
      ';',
    ),

    javaswing_scroll_bar_local_declaration: $ => prec.dynamic(1, seq(
      optional($.modifiers),
      field('type', $.javaswing_scroll_bar_class),
      $._variable_declarator_list,
      ';',
    )),

    javaswing_text_editor_local_declaration: $ => prec.dynamic(1, seq(
      optional($.modifiers),
      field('type', $.javaswing_text_editor_class),
      $._variable_declarator_list,
      ';',
    )),

    javaswing_password_field_local_declaration: $ => prec.dynamic(1, seq(
      optional($.modifiers),
      field('type', $.javaswing_password_field_class),
      $._variable_declarator_list,
      ';',
    )),

    javaswing_formatted_text_field_local_declaration: $ => prec.dynamic(1, seq(
      optional($.modifiers),
      field('type', $.javaswing_formatted_text_field_class),
      $._variable_declarator_list,
      ';',
    )),

    javaswing_text_input_local_declaration: $ => prec.dynamic(1, seq(
      optional($.modifiers),
      field('type', $.javaswing_text_input_class),
      $._variable_declarator_list,
      ';',
    )),

    javaswing_selectable_button_local_declaration: $ => prec.dynamic(1, seq(
      optional($.modifiers),
      field('type', $.javaswing_selectable_button_class),
      $._variable_declarator_list,
      ';',
    )),

    javaswing_spinner_local_declaration: $ => seq(
      optional($.modifiers),
      field('type', $.javaswing_spinner_class),
      $._variable_declarator_list,
      ';',
    ),

    javaswing_spinner_model_local_declaration: $ => seq(
      optional($.modifiers),
      field('type', $.javaswing_spinner_model_class),
      $._variable_declarator_list,
      ';',
    ),

    javaswing_grid_bag_constraints_local_declaration: $ => seq(
      optional($.modifiers),
      field('type', $.javaswing_grid_bag_constraints_class),
      $._variable_declarator_list,
      ';',
    ),

    javaswing_button_group_local_declaration: $ => prec(PREC.DECL + 1, seq(
      optional($.modifiers),
      field('type', $.javaswing_button_group_class),
      $._variable_declarator_list,
      ';',
    )),

    method_declaration: $ => seq(
      optional($.modifiers),
      $._method_header,
      choice(field('body', $.block), ';'),
    ),

    javaswing_event_handler: $ => prec(PREC.DECL + 1, seq(
      optional($.modifiers),
      field('type', $.void_type),
      field('name', $.javaswing_event_handler_name),
      field('parameters', $.javaswing_event_handler_parameters),
      optional($.throws),
      choice(field('body', $.block), ';'),
    )),

    javaswing_init_components: $ => prec(PREC.DECL + 1, seq(
      optional($.modifiers),
      field('type', $.void_type),
      field('name', $.javaswing_init_components_name),
      field('parameters', $._javaswing_empty_formal_parameters),
      optional($.throws),
      choice(field('body', $.block), ';'),
    )),

    javaswing_init_components_call: $ => prec(PREC.OBJ_ACCESS + 1, seq(
      field('name', $.javaswing_init_components_name),
      field('arguments', $.javaswing_empty_argument_list),
    )),

    _javaswing_empty_formal_parameters: _ => seq('(', ')'),

    javaswing_init_components_name: _ => JAVASWING_INIT_COMPONENT_METHODS[0],

    javaswing_event_handler_parameters: $ => seq(
      '(',
      field('event', $.javaswing_event_parameter),
      ')',
    ),

    javaswing_event_parameter: $ => seq(
      optional($.modifiers),
      field('type', $.javaswing_event_type),
      $._variable_declarator_id,
    ),

    javaswing_event_handler_name: _ => choice(
      ...JAVASWING_EVENT_HANDLER_METHODS.map(method => method),
    ),

    javaswing_event_type: _ => choice(
      choice(...JAVASWING_AWT_EVENT_TYPES),
      'PropertyChangeEvent',
      choice(...JAVASWING_SWING_EVENT_TYPES),
      seq('java', '.', 'awt', '.', 'event', '.', choice(...JAVASWING_AWT_EVENT_TYPES)),
      seq('java', '.', 'beans', '.', 'PropertyChangeEvent'),
      seq('javax', '.', 'swing', '.', 'event', '.', choice(...JAVASWING_SWING_EVENT_TYPES)),
    ),

    compact_constructor_declaration: $ => seq(
      optional($.modifiers),
      field('name', $.identifier),
      field('body', $.block),
    ),

    _reserved_identifier: $ => choice(
      prec(-3, alias(
        choice(
          'open',
          'module',
          'record',
          'with',
          'sealed',
          'show',
        ),
        $.identifier,
      )),
      alias('yield', $.identifier),
    ),

    this: _ => 'this',

    super: _ => 'super',

    // https://docs.oracle.com/javase/specs/jls/se8/html/jls-3.html#jls-IdentifierChars
    identifier: _ => /[\p{XID_Start}_$][\p{XID_Continue}\u00A2_$]*/,

    line_comment: _ => token(prec(PREC.COMMENT, seq('//', /[^\r\n]*/))),

    // http://stackoverflow.com/questions/13014947/regex-to-match-a-c-style-multiline-comment/36328890#36328890
    block_comment: _ => token(prec(PREC.COMMENT,
      seq(
        '/*',
        /[^*]*\*+([^/*][^*]*\*+)*/,
        '/',
      ),
    )),
  },
});

/**
 * Creates a rule to match one or more of the rules separated by `separator`
 *
 * @param {RuleOrLiteral} rule
 *
 * @param {RuleOrLiteral} separator
 *
 * @returns {SeqRule}
 */
function sep1(rule, separator) {
  return seq(rule, repeat(seq(separator, rule)));
}

/**
 * Creates a rule to match one or more of the rules separated by a comma
 *
 * @param {RuleOrLiteral} rule
 *
 * @returns {SeqRule}
 */
function commaSep1(rule) {
  return seq(rule, repeat(seq(',', rule)));
}

/**
 * Creates a rule to optionally match one or more of the rules separated by a comma
 *
 * @param {RuleOrLiteral} rule
 *
 * @returns {ChoiceRule}
 */
function commaSep(rule) {
  return optional(commaSep1(rule));
}
