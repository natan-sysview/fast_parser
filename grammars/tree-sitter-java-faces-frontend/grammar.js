/**
 * @file Tree-sitter grammar for Jakarta Faces and JavaServer Faces frontends
 * @license MIT
 */

/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

import * as c from './common/common.mjs';

const O = optional;
const elSpace = $ => optional($._el_whitespace);
const elToken = (_, value) => token(choice(
  seq(/[ \t\r\n]+/, value, /[ \t\r\n]+/),
  seq(/[ \t\r\n]+/, value),
  seq(value, /[ \t\r\n]+/),
  value,
));

const elementRule = ($, empty, start, end) => choice(
  empty,
  seq(
    field('open', start),
    optional(field('body', $.content)),
    field('close', end),
  ),
);

const emptyElementRule = ($, name) => seq(
  '<',
  field('name', alias(name, $.tag_name)),
  c.rseq($._S, $.attribute),
  O($._S),
  '/>',
);

const startTagRule = ($, name) => seq(
  '<',
  field('name', alias(name, $.tag_name)),
  c.rseq($._S, $.attribute),
  O($._S),
  '>',
);

const endTagRule = ($, name) => seq(
  '</',
  field('name', alias(name, $.tag_name)),
  O($._S),
  '>',
);

export default grammar({
  name: 'java_faces_frontend',

  externals: $ => [
    $.PITarget,
    $._pi_content,
    $.Comment,
    $.CharData,
    $.CData,
    'xml-model',
    'xml-stylesheet',
    $._generic_start_tag_name,
    $._facelets_start_tag_name,
    $._jsf_html_start_tag_name,
    $._jsf_core_start_tag_name,
    $._composite_start_tag_name,
    $._faces_start_tag_name,
    $._primefaces_start_tag_name,
    $._primefaces_extensions_start_tag_name,
    $._jstl_start_tag_name,
    $._qualified_start_tag_name,
    $._generic_end_tag_name,
    $._facelets_end_tag_name,
    $._jsf_html_end_tag_name,
    $._jsf_core_end_tag_name,
    $._composite_end_tag_name,
    $._faces_end_tag_name,
    $._primefaces_end_tag_name,
    $._primefaces_extensions_end_tag_name,
    $._jstl_end_tag_name,
    $._qualified_end_tag_name,
    $._el_qualified_function_name,
    $._erroneous_end_name,
    '/>',
  ],

  extras: _ => [],

  supertypes: $ => [
    $.element,
    $.attribute,
    $._markupdecl,
    $._AttType,
    $._EnumeratedType,
    $._EntityDecl,
    $._Reference,
    $._el_primary_expression,
  ],

  conflicts: $ => [
    [$.AttlistDecl, $.AttDef],
    [$.el_lambda_parameters, $._el_primary_expression],
  ],

  word: $ => $.el_identifier,

  rules: {
    document: $ => prec(2, seq(
      O($._S),
      O($.prolog),
      field('root', $.element),
      repeat($._Misc),
    )),

    ...c.rules,

    prolog: $ => choice(
      seq($.XMLDecl, repeat($._Misc)),
      seq(O($.XMLDecl), repeat($._Misc), $.doctypedecl, repeat($._Misc)),
      repeat1($._Misc),
    ),

    _Misc: $ => choice(
      $.PI,
      $.StyleSheetPI,
      $.XmlModelPI,
      $.Comment,
      $._S,
    ),

    XMLDecl: $ => seq(
      '<?',
      'xml',
      $._VersionInfo,
      O($._EncodingDecl),
      O($._SDDecl),
      O($._S),
      '?>',
    ),

    _SDDecl: $ => seq(
      $._S,
      'standalone',
      $._Eq,
      c.str(choice('yes', 'no')),
    ),

    doctypedecl: $ => seq(
      '<!',
      'DOCTYPE',
      $._S,
      $.Name,
      O(seq($._S, $.ExternalID)),
      O($._S),
      O(seq('[', O(choice($._intSubset, $._S)), ']', O($._S))),
      '>',
    ),

    _intSubset: $ => c.rseq1(O($._S), $._markupdecl, $._DeclSep),

    element: $ => choice(
      $.facelets_element,
      $.jsf_html_element,
      $.jsf_core_element,
      $.composite_component_element,
      $.faces_element,
      $.primefaces_element,
      $.primefaces_extensions_element,
      $.jstl_element,
      $.qualified_element,
      $.xml_element,
    ),

    facelets_element: $ => elementRule($, $.facelets_empty_element, $.facelets_start_tag, $.facelets_end_tag),
    facelets_empty_element: $ => emptyElementRule($, $._facelets_start_tag_name),
    facelets_start_tag: $ => startTagRule($, $._facelets_start_tag_name),
    facelets_end_tag: $ => endTagRule($, $._facelets_end_tag_name),

    jsf_html_element: $ => elementRule($, $.jsf_html_empty_element, $.jsf_html_start_tag, $.jsf_html_end_tag),
    jsf_html_empty_element: $ => emptyElementRule($, $._jsf_html_start_tag_name),
    jsf_html_start_tag: $ => startTagRule($, $._jsf_html_start_tag_name),
    jsf_html_end_tag: $ => endTagRule($, $._jsf_html_end_tag_name),

    jsf_core_element: $ => elementRule($, $.jsf_core_empty_element, $.jsf_core_start_tag, $.jsf_core_end_tag),
    jsf_core_empty_element: $ => emptyElementRule($, $._jsf_core_start_tag_name),
    jsf_core_start_tag: $ => startTagRule($, $._jsf_core_start_tag_name),
    jsf_core_end_tag: $ => endTagRule($, $._jsf_core_end_tag_name),

    composite_component_element: $ => elementRule(
      $,
      $.composite_component_empty_element,
      $.composite_component_start_tag,
      $.composite_component_end_tag,
    ),
    composite_component_empty_element: $ => emptyElementRule($, $._composite_start_tag_name),
    composite_component_start_tag: $ => startTagRule($, $._composite_start_tag_name),
    composite_component_end_tag: $ => endTagRule($, $._composite_end_tag_name),

    faces_element: $ => elementRule($, $.faces_empty_element, $.faces_start_tag, $.faces_end_tag),
    faces_empty_element: $ => emptyElementRule($, $._faces_start_tag_name),
    faces_start_tag: $ => startTagRule($, $._faces_start_tag_name),
    faces_end_tag: $ => endTagRule($, $._faces_end_tag_name),

    primefaces_element: $ => elementRule(
      $,
      $.primefaces_empty_element,
      $.primefaces_start_tag,
      $.primefaces_end_tag,
    ),
    primefaces_empty_element: $ => emptyElementRule($, $._primefaces_start_tag_name),
    primefaces_start_tag: $ => startTagRule($, $._primefaces_start_tag_name),
    primefaces_end_tag: $ => endTagRule($, $._primefaces_end_tag_name),

    primefaces_extensions_element: $ => elementRule(
      $,
      $.primefaces_extensions_empty_element,
      $.primefaces_extensions_start_tag,
      $.primefaces_extensions_end_tag,
    ),
    primefaces_extensions_empty_element: $ => emptyElementRule($, $._primefaces_extensions_start_tag_name),
    primefaces_extensions_start_tag: $ => startTagRule($, $._primefaces_extensions_start_tag_name),
    primefaces_extensions_end_tag: $ => endTagRule($, $._primefaces_extensions_end_tag_name),

    jstl_element: $ => elementRule($, $.jstl_empty_element, $.jstl_start_tag, $.jstl_end_tag),
    jstl_empty_element: $ => emptyElementRule($, $._jstl_start_tag_name),
    jstl_start_tag: $ => startTagRule($, $._jstl_start_tag_name),
    jstl_end_tag: $ => endTagRule($, $._jstl_end_tag_name),

    qualified_element: $ => elementRule(
      $,
      $.qualified_empty_element,
      $.qualified_start_tag,
      $.qualified_end_tag,
    ),
    qualified_empty_element: $ => emptyElementRule($, $._qualified_start_tag_name),
    qualified_start_tag: $ => startTagRule($, $._qualified_start_tag_name),
    qualified_end_tag: $ => endTagRule($, $._qualified_end_tag_name),

    xml_element: $ => elementRule($, $.xml_empty_element, $.xml_start_tag, $.xml_end_tag),
    xml_empty_element: $ => emptyElementRule($, $._generic_start_tag_name),
    xml_start_tag: $ => startTagRule($, $._generic_start_tag_name),
    xml_end_tag: $ => endTagRule($, $._generic_end_tag_name),

    _ErroneousETag: $ => seq(
      '</',
      alias($._erroneous_end_name, $.ERROR),
      O($._S),
      '>',
    ),

    attribute: $ => choice(
      $.namespace_declaration,
      $.faces_attribute,
      $.passthrough_attribute,
      $.qualified_attribute,
      $.plain_attribute,
    ),

    namespace_declaration: $ => seq(
      field('name', alias($.namespace_declaration_name, $.attribute_name)),
      $._Eq,
      field('uri', $.AttValue),
    ),

    faces_attribute: $ => seq(
      field('name', alias($.faces_attribute_name, $.attribute_name)),
      $._Eq,
      field('value', $.AttValue),
    ),

    passthrough_attribute: $ => seq(
      field('name', alias($.passthrough_attribute_name, $.attribute_name)),
      $._Eq,
      field('value', $.AttValue),
    ),

    qualified_attribute: $ => seq(
      field('name', alias($.qualified_attribute_name, $.attribute_name)),
      $._Eq,
      field('value', $.AttValue),
    ),

    plain_attribute: $ => seq(
      field('name', alias($.plain_attribute_name, $.attribute_name)),
      $._Eq,
      field('value', $.AttValue),
    ),

    namespace_declaration_name: _ => token(prec(5, /xmlns(?::[a-zA-Z_][a-zA-Z0-9_.-]*)?/)),
    faces_attribute_name: _ => token(prec(4, /(?:faces|jsf):[a-zA-Z_][a-zA-Z0-9_.-]*/)),
    passthrough_attribute_name: _ => token(prec(4, /pt:[a-zA-Z_][a-zA-Z0-9_.-]*/)),
    qualified_attribute_name: _ => token(prec(3, /[a-zA-Z_][a-zA-Z0-9_.-]*:[a-zA-Z_][a-zA-Z0-9_.-]*/)),
    plain_attribute_name: _ => token(prec(2, /[a-zA-Z_][a-zA-Z0-9_.-]*/)),

    AttValue: $ => choice(
      $.double_quoted_attribute_value,
      $.single_quoted_attribute_value,
    ),

    double_quoted_attribute_value: $ => seq(
      '"',
      field('content', repeat(choice(
        $.double_quoted_attribute_text,
        $.escaped_expression_marker,
        $._Reference,
        $.expression_language,
        '#',
        '$',
        '\\',
      ))),
      '"',
    ),

    single_quoted_attribute_value: $ => seq(
      "'",
      field('content', repeat(choice(
        $.single_quoted_attribute_text,
        $.escaped_expression_marker,
        $._Reference,
        $.expression_language,
        '#',
        '$',
        '\\',
      ))),
      "'",
    ),

    double_quoted_attribute_text: _ => /[^<&"\\#$]+/,
    single_quoted_attribute_text: _ => /[^<&'\\#$]+/,
    escaped_expression_marker: _ => token(/\\[\\#$]/),

    content: $ => repeat1(choice(
      $.CharData,
      $.element,
      $._Reference,
      $.CDSect,
      $.PI,
      $.Comment,
      $.expression_language,
    )),

    CDSect: $ => prec.left(seq($.CDStart, O($.CData), ']]>')),
    CDStart: _ => seq('<![', 'CDATA', '['),

    StyleSheetPI: $ => seq(
      '<?',
      'xml-stylesheet',
      c.rseq($._S, $.PseudoAtt),
      O($._S),
      '?>',
    ),

    XmlModelPI: $ => seq(
      '<?',
      'xml-model',
      c.rseq($._S, $.PseudoAtt),
      O($._S),
      '?>',
    ),

    PseudoAtt: $ => seq($.Name, $._Eq, $.PseudoAttValue),
    PseudoAttValue: $ => choice(c.att_value($, '"'), c.att_value($, "'")),

    expression_language: $ => choice(
      $.deferred_expression,
      $.immediate_expression,
    ),

    deferred_expression: $ => seq(
      '#{',
      elSpace($),
      field('body', $.el_sequence_expression),
      elSpace($),
      '}',
    ),

    immediate_expression: $ => seq(
      '${',
      elSpace($),
      field('body', $.el_sequence_expression),
      elSpace($),
      '}',
    ),

    el_sequence_expression: $ => prec.left(seq(
      $.el_assignment_expression,
      repeat(seq(elToken($, ';'), $.el_assignment_expression)),
    )),

    el_assignment_expression: $ => choice(
      $.el_lambda_expression,
      prec.right(seq(
        field('left', $.el_conditional_expression),
        elToken($, '='),
        field('right', $.el_assignment_expression),
      )),
      $.el_conditional_expression,
    ),

    el_lambda_expression: $ => prec.right(seq(
      field('parameters', $.el_lambda_parameters),
      elToken($, '->'),
      field('body', choice($.el_lambda_expression, $.el_conditional_expression)),
    )),

    el_lambda_parameters: $ => choice(
      $.el_identifier,
      seq(
        '(',
        elSpace($),
        O(seq(
          $.el_identifier,
          repeat(seq(elToken($, ','), $.el_identifier)),
        )),
        elSpace($),
        ')',
      ),
    ),

    el_conditional_expression: $ => choice(
      prec.right(5, seq(
        $.el_or_expression,
        elToken($, '?'),
        field('consequence', $.el_conditional_expression),
        elToken($, ':'),
        field('alternative', $.el_conditional_expression),
      )),
      $.el_or_expression,
    ),

    el_or_expression: $ => prec.left(seq(
      $.el_and_expression,
      repeat(seq(field('operator', elToken($, choice('||', 'or'))), $.el_and_expression)),
    )),

    el_and_expression: $ => prec.left(seq(
      $.el_equality_expression,
      repeat(seq(
        field('operator', elToken($, choice('&&', '&amp;&amp;', 'and'))),
        $.el_equality_expression,
      )),
    )),

    el_equality_expression: $ => prec.left(seq(
      $.el_relational_expression,
      repeat(seq(
        field('operator', elToken($, choice('==', 'eq', '!=', 'ne'))),
        $.el_relational_expression,
      )),
    )),

    el_relational_expression: $ => prec.left(seq(
      $.el_concatenation_expression,
      repeat(seq(
        field('operator', elToken($, choice(
          '<', '&lt;', 'lt',
          '>', '&gt;', 'gt',
          '<=', '&lt;=', 'le',
          '>=', '&gt;=', 'ge',
          'instanceof',
        ))),
        $.el_concatenation_expression,
      )),
    )),

    el_concatenation_expression: $ => prec.left(seq(
      $.el_additive_expression,
      repeat(seq(elToken($, '+='), $.el_additive_expression)),
    )),

    el_additive_expression: $ => prec.left(seq(
      $.el_multiplicative_expression,
      repeat(seq(
        field('operator', elToken($, choice('+', '-'))),
        $.el_multiplicative_expression,
      )),
    )),

    el_multiplicative_expression: $ => prec.left(seq(
      $.el_unary_expression,
      repeat(seq(
        field('operator', elToken($, choice('*', '/', 'div', '%', 'mod'))),
        $.el_unary_expression,
      )),
    )),

    el_unary_expression: $ => choice(
      prec.right(seq(
        field('operator', choice('-', '!', $.el_not_operator, $.el_empty_operator)),
        elSpace($),
        $.el_unary_expression,
      )),
      $.el_value_expression,
    ),

    el_not_operator: _ => token(prec(3, 'not')),
    el_empty_operator: _ => token(prec(3, 'empty')),

    el_value_expression: $ => seq(
      $._el_primary_expression,
      repeat(choice(
        $.el_property_suffix,
        $.el_bracket_suffix,
        $.el_method_arguments,
      )),
    ),

    _el_primary_expression: $ => choice(
      $.el_boolean,
      $.el_null,
      $.el_floating_point,
      $.el_integer,
      $.el_string,
      $.el_function_call,
      $.el_identifier,
      $.el_parenthesized_expression,
      $.el_map_or_set_literal,
      $.el_list_literal,
    ),

    el_parenthesized_expression: $ => seq(
      '(',
      elSpace($),
      $.el_sequence_expression,
      elSpace($),
      ')',
    ),

    el_function_call: $ => prec(1, choice(
      seq(
        field('name', alias($._el_qualified_function_name, $.el_function_name)),
        repeat1($.el_method_arguments),
      ),
      seq(
        field('name', $.el_identifier),
        repeat1($.el_method_arguments),
      ),
    )),

    el_property_suffix: $ => seq(
      elToken($, '.'),
      field('property', $.el_identifier),
    ),

    el_bracket_suffix: $ => seq(
      elToken($, '['),
      field('property', $.el_sequence_expression),
      elToken($, ']'),
    ),

    el_method_arguments: $ => seq(
      elToken($, '('),
      O(seq(
        $.el_sequence_expression,
        repeat(seq(elToken($, ','), $.el_sequence_expression)),
      )),
      elToken($, ')'),
    ),

    el_map_or_set_literal: $ => seq(
      '{',
      elSpace($),
      O(seq(
        $.el_collection_entry,
        repeat(seq(elToken($, ','), $.el_collection_entry)),
      )),
      elSpace($),
      '}',
    ),

    el_collection_entry: $ => seq(
      field('key', $.el_sequence_expression),
      O(seq(elToken($, ':'), field('value', $.el_sequence_expression))),
    ),

    el_list_literal: $ => seq(
      '[',
      elSpace($),
      O(seq(
        $.el_sequence_expression,
        repeat(seq(elToken($, ','), $.el_sequence_expression)),
      )),
      elSpace($),
      ']',
    ),

    el_boolean: _ => token(prec(3, choice('true', 'false'))),
    el_null: _ => token(prec(3, 'null')),

    el_floating_point: _ => token(prec(2, choice(
      /[0-9]+\.[0-9]*([eE][+-]?[0-9]+)?/,
      /\.[0-9]+([eE][+-]?[0-9]+)?/,
      /[0-9]+[eE][+-]?[0-9]+/,
    ))),

    el_integer: _ => token(prec(1, /[0-9]+/)),

    el_string: $ => choice(
      seq('"', repeat(choice($.el_double_string_text, $.el_escape_sequence, $._Reference)), '"'),
      seq("'", repeat(choice($.el_single_string_text, $.el_escape_sequence, $._Reference)), "'"),
      seq('&quot;', repeat(choice($.el_encoded_double_string_text, $._Reference)), '&quot;'),
      seq('&apos;', repeat(choice($.el_encoded_single_string_text, $._Reference)), '&apos;'),
    ),

    el_double_string_text: _ => /[^"\\&]+/,
    el_single_string_text: _ => /[^'\\&]+/,
    el_encoded_double_string_text: _ => /[^&]+/,
    el_encoded_single_string_text: _ => /[^&]+/,
    el_escape_sequence: _ => token(/\\[\\"']/),

    el_identifier: _ => token(prec(1, /[$A-Z_a-z\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u1fff\u3040-\u318f\u3300-\u337f\u3400-\u3d2d\u4e00-\u9fff\uf900-\ufaff#][$A-Z_a-z0-9\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u1fff\u3040-\u318f\u3300-\u337f\u3400-\u3d2d\u4e00-\u9fff\uf900-\ufaff]*/)),

    _el_whitespace: _ => /[ \t\r\n]+/,
  },
});
