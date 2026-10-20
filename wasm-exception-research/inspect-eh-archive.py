#!/usr/bin/env python3
"""Build a Rust+C staticlib with prebuilt std and inspect its EH instructions."""
import json
import os
from pathlib import Path
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / 'build'
RESULTS = ROOT / 'results'
BUILD.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)
EMCC = os.environ.get('EMCC', '/opt/homebrew/opt/emscripten/bin/emcc')
EMAR = str(Path(EMCC).with_name('emar'))
OBJDUMP = os.environ.get('LLVM_OBJDUMP', '/opt/homebrew/opt/emscripten/libexec/llvm/bin/llvm-objdump')
OPS = 'try_table|throw_ref|try|catch|catch_all|rethrow|delegate'
PATTERN = '[[:space:]](' + OPS + ')([[:space:]]|$)'


def run(name, args):
    args = list(map(str, args))
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=120)
    (RESULTS / f'archive-eh-{name}.txt').write_text(
        '$ ' + shlex.join(args) + '\n' + result.stdout + result.stderr
        + f'\nexit={result.returncode}\n')
    result.check_returncode()
    return result.stdout


run('objdump-version', [OBJDUMP, '--version'])
run('compile-c', [EMCC, 'src/sjlj.c', '-DLIBRARY_ONLY', '-O1', '-g2',
                  '-sSUPPORT_LONGJMP=wasm', '-sWASM_LEGACY_EXCEPTIONS=0',
                  '-c', '-o', BUILD / 'c-library-standard.o'])
run('archive-c', [EMAR, 'rcs', BUILD / 'libsjlj-standard.a', BUILD / 'c-library-standard.o'])
run('compile-rust', ['rustc', '+nightly', 'src/rust_static.rs', '--edition=2024',
                     '--crate-type=staticlib', '--target=wasm32-unknown-emscripten',
                     '-C', 'opt-level=1', '-C', 'panic=unwind',
                     '-C', 'target-feature=+exception-handling',
                     '-C', 'llvm-args=-wasm-use-legacy-eh=0',
                     '-L', 'native=' + str(BUILD), '-o', BUILD / 'librust_c_mixed.a'])
args = [OBJDUMP, '-d', '--triple=wasm32-unknown-unknown', 'build/librust_c_mixed.a']
result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=True)
# Keep the full disassembly in ignored build/, with filtered evidence in results/.
(BUILD / 'archive-eh-disassembly.txt').write_text(result.stdout)
matches = subprocess.run(['grep', '-E', PATTERN], input=result.stdout,
                          text=True, capture_output=True, check=True).stdout
(RESULTS / 'archive-eh-matches.txt').write_text(matches)
(RESULTS / 'archive-eh-command.txt').write_text(
    shlex.join(args) + ' | grep -E ' + shlex.quote(PATTERN) + '\n'
    + result.stderr)
counts = {op: 0 for op in OPS.split('|')}
examples = {}
member = function = ''
for line in result.stdout.splitlines():
    if ':\tfile format wasm' in line:
        member = line.split(':\tfile format wasm')[0]
    elif re.match(r'^[0-9a-f]+ <.*>:$', line):
        function = line
    match = re.match(r'^\s*[0-9a-f]+:\s+(?:[0-9a-f]{2}\s+)+(' + OPS + r')\b', line)
    if match:
        op = match.group(1)
        counts[op] += 1
        examples.setdefault(op, {'member': member, 'function': function, 'line': line})
if not counts['try_table'] or not counts['try']:
    raise RuntimeError('Expected both standard and legacy EH in the static archive')
summary = {'instructions': counts, 'first_examples': examples}
(RESULTS / 'archive-eh-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
for op in ['try_table', 'throw_ref', 'try', 'catch_all', 'rethrow']:
    if op in examples:
        print(examples[op]['member'])
        print(examples[op]['line'])
print(json.dumps(counts))
