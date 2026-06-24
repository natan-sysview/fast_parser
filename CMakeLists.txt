cmake_minimum_required(VERSION 3.20)

project(fastparse
    VERSION 0.5.0
    DESCRIPTION "Small memory-only Tree-sitter parser library"
    LANGUAGES C)

include(CTest)

option(TSMP_BUILD_SHARED "Build TSMP as a shared library" ON)
option(TSMP_USE_VENDORED_TREE_SITTER "Compile the vendored Tree-sitter runtime" ON)
set(FASTPARSE_COBOL_GRAMMAR_DIR "" CACHE PATH "Optional tree-sitter-cobol grammar directory for the experimental COBOL language extension")
set(FASTPARSE_PYTHON_GRAMMAR_DIR "" CACHE PATH "Optional tree-sitter-python grammar directory for the experimental Python language extension")

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

set(TSMP_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src")
set(TSMP_GRAMMARS_DIR "${CMAKE_CURRENT_SOURCE_DIR}/grammars")
set(TSMP_VENDOR_TREE_SITTER_DIR "${CMAKE_CURRENT_SOURCE_DIR}/vendor/tree-sitter")

set(TSMP_CORE_SOURCES
    "${TSMP_SOURCE_DIR}/tsmp_api.c"
    "${TSMP_SOURCE_DIR}/tsmp_buffer.c"
    "${TSMP_SOURCE_DIR}/tsmp_languages.c"
    "${TSMP_SOURCE_DIR}/tsmp_render.c"
    "${TSMP_SOURCE_DIR}/tsmp_render_binary.c"
    "${TSMP_SOURCE_DIR}/tsmp_render_csv.c"
    "${TSMP_SOURCE_DIR}/tsmp_render_json.c")

set(TSMP_RUNTIME_SOURCES)
if(TSMP_USE_VENDORED_TREE_SITTER)
    list(APPEND TSMP_RUNTIME_SOURCES
        "${TSMP_VENDOR_TREE_SITTER_DIR}/lib/src/lib.c")
endif()

file(GLOB TSMP_GRAMMAR_PARSERS CONFIGURE_DEPENDS
    "${TSMP_GRAMMARS_DIR}/tree-sitter-*/src/parser.c")
file(GLOB TSMP_GRAMMAR_SCANNERS CONFIGURE_DEPENDS
    "${TSMP_GRAMMARS_DIR}/tree-sitter-*/src/scanner.c")

set(TSMP_GRAMMAR_INCLUDES)
foreach(parser_source IN LISTS TSMP_GRAMMAR_PARSERS)
    get_filename_component(parser_dir "${parser_source}" DIRECTORY)
    list(APPEND TSMP_GRAMMAR_INCLUDES "${parser_dir}")
endforeach()
list(REMOVE_DUPLICATES TSMP_GRAMMAR_INCLUDES)

if(TSMP_BUILD_SHARED)
    add_library(tsmp SHARED
        ${TSMP_CORE_SOURCES}
        ${TSMP_RUNTIME_SOURCES}
        ${TSMP_GRAMMAR_PARSERS}
        ${TSMP_GRAMMAR_SCANNERS})
else()
    add_library(tsmp STATIC
        ${TSMP_CORE_SOURCES}
        ${TSMP_RUNTIME_SOURCES}
        ${TSMP_GRAMMAR_PARSERS}
        ${TSMP_GRAMMAR_SCANNERS})
endif()

target_include_directories(tsmp
    PUBLIC
        "${CMAKE_CURRENT_SOURCE_DIR}/include"
    PRIVATE
        "${TSMP_VENDOR_TREE_SITTER_DIR}/lib/include"
        "${TSMP_VENDOR_TREE_SITTER_DIR}/lib/src"
        ${TSMP_GRAMMAR_INCLUDES})

target_compile_definitions(tsmp
    PRIVATE
        TSMP_BUILD_SHARED
        TREE_SITTER_HIDE_SYMBOLS)

if(UNIX AND NOT APPLE)
    target_compile_definitions(tsmp PRIVATE _DEFAULT_SOURCE _BSD_SOURCE)
endif()

if(MSVC)
    target_compile_options(tsmp PRIVATE /W4)
else()
    target_compile_options(tsmp PRIVATE -Wall -fvisibility=hidden)
endif()

set_target_properties(tsmp PROPERTIES
    OUTPUT_NAME "fastparse"
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/bin"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/bin"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/bin")

foreach(config DEBUG RELEASE RELWITHDEBINFO MINSIZEREL)
    set_target_properties(tsmp PROPERTIES
        ARCHIVE_OUTPUT_DIRECTORY_${config} "${CMAKE_CURRENT_SOURCE_DIR}/bin"
        LIBRARY_OUTPUT_DIRECTORY_${config} "${CMAKE_CURRENT_SOURCE_DIR}/bin"
        RUNTIME_OUTPUT_DIRECTORY_${config} "${CMAKE_CURRENT_SOURCE_DIR}/bin")
endforeach()

function(fastparse_configure_language_extension target_name output_name)
    target_include_directories(${target_name}
        PRIVATE
            "${CMAKE_CURRENT_SOURCE_DIR}/include"
            "${TSMP_VENDOR_TREE_SITTER_DIR}/lib/include"
            "${TSMP_VENDOR_TREE_SITTER_DIR}/lib/src")
    if(MSVC)
        target_compile_options(${target_name} PRIVATE /W4)
    else()
        target_compile_options(${target_name} PRIVATE -Wall -fvisibility=hidden)
    endif()
    set_target_properties(${target_name} PROPERTIES
        OUTPUT_NAME "${output_name}"
        ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/bin"
        LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/bin"
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/bin")
    foreach(config DEBUG RELEASE RELWITHDEBINFO MINSIZEREL)
        set_target_properties(${target_name} PROPERTIES
            ARCHIVE_OUTPUT_DIRECTORY_${config} "${CMAKE_CURRENT_SOURCE_DIR}/bin"
            LIBRARY_OUTPUT_DIRECTORY_${config} "${CMAKE_CURRENT_SOURCE_DIR}/bin"
            RUNTIME_OUTPUT_DIRECTORY_${config} "${CMAKE_CURRENT_SOURCE_DIR}/bin")
    endforeach()
endfunction()

if(FASTPARSE_COBOL_GRAMMAR_DIR)
    if(NOT EXISTS "${FASTPARSE_COBOL_GRAMMAR_DIR}/src/parser.c")
        message(FATAL_ERROR "FASTPARSE_COBOL_GRAMMAR_DIR must point to a tree-sitter-cobol checkout with src/parser.c")
    endif()
    add_library(fastparse_language_cobol SHARED
        "${CMAKE_CURRENT_SOURCE_DIR}/extensions/cobol/fastparse_language_cobol.c"
        "${FASTPARSE_COBOL_GRAMMAR_DIR}/src/parser.c"
        "${FASTPARSE_COBOL_GRAMMAR_DIR}/src/scanner.c")
    target_include_directories(fastparse_language_cobol
        PRIVATE
            "${FASTPARSE_COBOL_GRAMMAR_DIR}/src")
    fastparse_configure_language_extension(fastparse_language_cobol "fastparse_language_cobol")
endif()

if(FASTPARSE_PYTHON_GRAMMAR_DIR)
    if(NOT EXISTS "${FASTPARSE_PYTHON_GRAMMAR_DIR}/src/parser.c")
        message(FATAL_ERROR "FASTPARSE_PYTHON_GRAMMAR_DIR must point to a tree-sitter-python checkout with src/parser.c")
    endif()
    set(FASTPARSE_PYTHON_SOURCES
        "${CMAKE_CURRENT_SOURCE_DIR}/extensions/python/fastparse_language_python.c"
        "${FASTPARSE_PYTHON_GRAMMAR_DIR}/src/parser.c")
    if(EXISTS "${FASTPARSE_PYTHON_GRAMMAR_DIR}/src/scanner.c")
        list(APPEND FASTPARSE_PYTHON_SOURCES "${FASTPARSE_PYTHON_GRAMMAR_DIR}/src/scanner.c")
    endif()
    add_library(fastparse_language_python SHARED
        ${FASTPARSE_PYTHON_SOURCES})
    target_include_directories(fastparse_language_python
        PRIVATE
            "${FASTPARSE_PYTHON_GRAMMAR_DIR}/src")
    fastparse_configure_language_extension(fastparse_language_python "fastparse_language_python")
endif()

if(APPLE AND TSMP_BUILD_SHARED)
    target_link_options(tsmp PRIVATE
        "LINKER:-exported_symbols_list,${CMAKE_CURRENT_SOURCE_DIR}/exports/tsmp_macos.exports")
elseif(UNIX AND NOT APPLE AND TSMP_BUILD_SHARED)
    target_link_options(tsmp PRIVATE
        "LINKER:--version-script=${CMAKE_CURRENT_SOURCE_DIR}/exports/tsmp_linux.map")
endif()

install(TARGETS tsmp
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib)

install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/include/tsmp.h"
    DESTINATION include)

install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/include/fastparse.h"
    DESTINATION include)

if(BUILD_TESTING)
    add_library(tsmp_test_language_extension SHARED
        "${CMAKE_CURRENT_SOURCE_DIR}/tests/fixtures/test_language_extension.c"
        "${TSMP_GRAMMARS_DIR}/tree-sitter-java/src/parser.c")
    target_include_directories(tsmp_test_language_extension
        PRIVATE
            "${TSMP_GRAMMARS_DIR}/tree-sitter-java/src")
    fastparse_configure_language_extension(tsmp_test_language_extension "fastparse_language_test_java")

    add_executable(tsmp_c_smoke
        "${CMAKE_CURRENT_SOURCE_DIR}/tests/c_smoke.c")
    target_link_libraries(tsmp_c_smoke PRIVATE tsmp)
    set_target_properties(tsmp_c_smoke PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/tests"
        BUILD_RPATH "$<TARGET_FILE_DIR:tsmp>")
    if(WIN32 AND TSMP_BUILD_SHARED)
        add_custom_command(TARGET tsmp_c_smoke POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "$<TARGET_FILE:tsmp>"
                "$<TARGET_FILE_DIR:tsmp_c_smoke>")
    endif()
    add_test(NAME tsmp_c_smoke COMMAND tsmp_c_smoke)

    add_executable(tsmp_c_extension_smoke
        "${CMAKE_CURRENT_SOURCE_DIR}/tests/c_extension_smoke.c")
    target_link_libraries(tsmp_c_extension_smoke PRIVATE tsmp)
    set_target_properties(tsmp_c_extension_smoke PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/tests"
        BUILD_RPATH "$<TARGET_FILE_DIR:tsmp>")
    if(WIN32 AND TSMP_BUILD_SHARED)
        add_custom_command(TARGET tsmp_c_extension_smoke POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "$<TARGET_FILE:tsmp>"
                "$<TARGET_FILE_DIR:tsmp_c_extension_smoke>")
    endif()
    add_test(
        NAME tsmp_c_extension_smoke
        COMMAND tsmp_c_extension_smoke "$<TARGET_FILE:tsmp_test_language_extension>")
endif()
