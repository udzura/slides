#!/usr/bin/env python3
"""Compare std variants in a Rust staticlib linked into a C application."""
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / 'build'
RESULTS = ROOT / 'results'
BUILD.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)
EMCC = os.environ.get('EMCC', '/opt/homebrew/opt/emscripten/bin/emcc')
OBJDUMP = os.environ.get('LLVM_OBJDUMP', '/opt/homebrew/opt/emscripten/libexec/llvm/bin/llvm-objdump')
TARGET = 'wasm32-unknown-emscripten'
OPS = r'try_table|try|catch_all|catch|rethrow|throw_ref|throw|delegate'


def run(name, args, env=None, check=True):
    args = list(map(str, args))
    result = subprocess.run(args, cwd=ROOT, env=env, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            timeout=300)
    (RESULTS / f'c-main-{name}.txt').write_text(
        '$ ' + shlex.join(args) + '\n' + result.stdout
        + f'\nexit={result.returncode}\n')
    print(f'{name}: exit={result.returncode}', flush=True)
    if check:
        result.check_returncode()
    return result


run('rustc-version', ['rustc', '+nightly', '-vV'])
run('emcc-version', [EMCC, '--version'])
run('node-version', ['node', '--version'])
c_flags = ['-sSUPPORT_LONGJMP=wasm', '-sWASM_LEGACY_EXCEPTIONS=0']
run('compile-c', [EMCC, 'src/sjlj.c', '-DLIBRARY_ONLY', '-O1', '-g2',
                  *c_flags, '-c', '-o', BUILD / 'c-main-sjlj.o'])
rustflags = ' '.join(['-C panic=unwind', '-C target-feature=+exception-handling',
                      '-C llvm-args=-wasm-use-legacy-eh=0'])
(RESULTS / 'c-main-rustflags.txt').write_text('RUSTFLAGS=' + rustflags + '\n')
summary = {}
for mode, extra in [('prebuilt', []), ('rebuilt', ['-Zbuild-std'])]:
    env = os.environ.copy()
    env['RUSTFLAGS'] = rustflags
    env['CARGO_TARGET_DIR'] = str(BUILD / ('cargo-rust-library-' + mode))
    run(mode + '-build', ['cargo', '+nightly', *extra, 'build', '--offline',
                          '--manifest-path', 'rust-library/Cargo.toml',
                          '--target', TARGET], env)
    archive = Path(env['CARGO_TARGET_DIR']) / TARGET / 'debug/librust_eh_library.a'
    output = BUILD / ('c-main-' + mode + '.js')
    run(mode + '-link', [EMCC, 'src/c_main.c', BUILD / 'c-main-sjlj.o', archive,
                         '-fwasm-exceptions', *c_flags, '-o', output])
    result = run(mode + '-run', ['node', output], check=False)
    if mode == 'prebuilt':
        if result.returncode == 0 or 'mix of legacy and new exception' not in result.stdout:
            raise RuntimeError('Expected prebuilt-std mixed-EH loading failure')
        # This is a Rust-only archive: no C objects are bundled in it.
        shutil.copyfile(archive, BUILD / 'librust_eh_prebuilt.a')
        dump = subprocess.run([OBJDUMP, '-d', '--triple=wasm32-unknown-unknown', archive],
                              text=True, capture_output=True, check=True).stdout
        (BUILD / 'c-main-archive-disassembly.txt').write_text(dump)
        examples = {}
        for line in dump.splitlines():
            match = re.match(r'^\s*[0-9a-f]+:\s+(?:[0-9a-f]{2}\s+)+(' + OPS + r')\b', line)
            if match:
                examples.setdefault(match.group(1), line)
        (RESULTS / 'c-main-archive-examples.txt').write_text(
            '\n'.join(examples[op] for op in ['try_table', 'try', 'catch_all', 'rethrow']) + '\n')
    else:
        result.check_returncode()
        if 'C main: longjmp=42; Rust library: panic caught' not in result.stdout:
            raise RuntimeError('Expected C main and Rust library recovery')
    dump = subprocess.run(['wasm-objdump', '-d', output.with_suffix('.wasm')],
                          text=True, capture_output=True, check=True).stdout
    instructions = re.findall(r'\|\s+(' + OPS + r')\b', dump)
    counts = {op: instructions.count(op) for op in sorted(set(instructions))}
    (RESULTS / f'c-main-{mode}-instructions.json').write_text(json.dumps(counts, indent=2) + '\n')
    if mode == 'rebuilt' and any(counts.get(op, 0) for op in ('try', 'catch', 'catch_all', 'rethrow', 'delegate')):
        raise RuntimeError('Legacy instructions remain after rebuilding std')
    summary[mode] = {'link_exit': 0, 'run_exit': result.returncode, 'instructions': counts}
(RESULTS / 'c-main-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
