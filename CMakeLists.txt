cmake_minimum_required(VERSION 3.20)

project(fastparse
    VERSION 0.3.0
    DESCRIPTION "Small memory-only Tree-sitter parser library"
    LANGUAGES C)

include(CTest)

option(TSMP_BUILD_SHARED "Build TSMP as a shared library" ON)
option(TSMP_USE_VENDORED_TREE_SITTER "Compile the vendored Tree-sitter runtime" ON)

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
    add_executable(tsmp_c_smoke
        "${CMAKE_CURRENT_SOURCE_DIR}/tests/c_smoke.c")
    target_link_libraries(tsmp_c_smoke PRIVATE tsmp)
    set_target_properties(tsmp_c_smoke PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/tests"
        BUILD_RPATH "$<TARGET_FILE_DIR:tsmp>")
    add_test(NAME tsmp_c_smoke COMMAND tsmp_c_smoke)
endif()
