#!/bin/sh
set -eu
cd "$(dirname "$0")"
mkdir -p build
CLANG=/opt/homebrew/opt/emscripten/libexec/llvm/bin/clang
EMXX=/opt/homebrew/opt/emscripten/bin/em++
"$CLANG" --target=wasm32-unknown-emscripten -O1 -fwasm-exceptions \
  -mllvm -wasm-use-legacy-eh=false -c src/catch-only.cpp -o build/catch-clang.o
"$EMXX" -O1 -fwasm-exceptions -sWASM_LEGACY_EXCEPTIONS=0 \
  -c src/catch-only.cpp -o build/catch-emcc.o
wasm-objdump -d build/catch-clang.o > results/catch-clang-disassembly.txt
wasm-objdump -d build/catch-emcc.o > results/catch-emcc-disassembly.txt
wc -c build/catch-clang.o build/catch-emcc.o > results/catch-object-sizes.txt
