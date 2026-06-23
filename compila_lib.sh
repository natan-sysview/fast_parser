#!/bin/bash
# Builds TSMP as a small memory-only shared library for FFI bindings.
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

BUILD_DIR="$DIR/build"

if [ "$1" = "clean" ]; then
    cmake --build "$BUILD_DIR" --target clean 2>/dev/null || true
    rm -f "$DIR/bin/libfastparse.dylib" "$DIR/bin/libfastparse.so" "$DIR/bin/fastparse.dll"
    rm -f "$DIR/bin/libtsmp.dylib" "$DIR/bin/libtsmp.so" "$DIR/bin/tsmp.dll"
    rm -f "$DIR/bin/libts_multi_parser.dylib" "$DIR/bin/libts_multi_parser.so"
    rm -f "$DIR/bin/libfastparse_language_"*.dylib "$DIR/bin/libfastparse_language_"*.so "$DIR/bin/fastparse_language_"*.dll
    exit 0
fi

if ! command -v cmake >/dev/null 2>&1; then
    echo "ERROR: cmake no esta instalado o no esta en PATH."
    exit 1
fi

cmake -S "$DIR" -B "$BUILD_DIR" -DCMAKE_BUILD_TYPE=Release
cmake --build "$BUILD_DIR" --config Release

echo "Shared library built in: $DIR/bin"
