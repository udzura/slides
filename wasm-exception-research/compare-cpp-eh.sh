#!/bin/sh
set -eu
cd "$(dirname "$0")"
mkdir -p build results
EMXX=/opt/homebrew/opt/emscripten/bin/em++
"$EMXX" --version > results/catch-eh-compiler.txt
"$EMXX" -O1 -fwasm-exceptions -sWASM_LEGACY_EXCEPTIONS=1 \
  -c src/catch-only.cpp -o build/catch-legacy.o
"$EMXX" -O1 -fwasm-exceptions -sWASM_LEGACY_EXCEPTIONS=0 \
  -c src/catch-only.cpp -o build/catch-standard.o
wasm-objdump -d build/catch-legacy.o > results/catch-legacy-disassembly.txt
wasm-objdump -d build/catch-standard.o > results/catch-standard-disassembly.txt
