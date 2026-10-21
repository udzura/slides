#!/bin/sh
set -eu
cd "$(dirname "$0")"
mkdir -p build results
EMCC=/opt/homebrew/opt/emscripten/bin/emcc
"$EMCC" --version > results/goto-compiler.txt
for level in 0 1; do
  "$EMCC" -O"$level" -fwasm-exceptions \
    -sSUPPORT_LONGJMP=wasm -sWASM_LEGACY_EXCEPTIONS=0 \
    -c src/goto.c -o "build/goto-O$level.o"
  wasm-objdump -d "build/goto-O$level.o" > "results/goto-O$level-disassembly.txt"
done
python3 - <<'PY'
from pathlib import Path
import json
import re

summary = {}
branches = ('block', 'loop', 'br', 'br_if', 'br_table')
exceptions = ('try', 'catch', 'catch_all', 'rethrow', 'delegate',
              'try_table', 'throw', 'throw_ref')
for level in (0, 1):
    dump = Path(f'results/goto-O{level}-disassembly.txt').read_text()
    ops = re.findall(r'\|\s+([a-z_]+)\b', dump)
    counts = {op: ops.count(op) for op in branches + exceptions}
    assert not any(counts[op] for op in exceptions), counts
    summary[f'O{level}'] = counts
    print(f'O{level}: {counts}')
Path('results/goto-instructions.json').write_text(json.dumps(summary, indent=2) + '\n')
PY
