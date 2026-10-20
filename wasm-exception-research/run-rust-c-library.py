#!/usr/bin/env python3
"""Compare prebuilt and rebuilt Rust std with the same standard-EH C archive."""
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
TARGET = 'wasm32-unknown-emscripten'


def run(name, args, env=None, check=True):
    args = list(map(str, args))
    result = subprocess.run(args, cwd=ROOT, env=env, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            timeout=300)
    (RESULTS / f'c-library-{name}.txt').write_text(
        '$ ' + shlex.join(args) + '\n' + result.stdout
        + f'\nexit={result.returncode}\n')
    print(f'{name}: exit={result.returncode}', flush=True)
    if check:
        result.check_returncode()
    return result


run('rustc-version', ['rustc', '+nightly', '-vV'])
run('emcc-version', [EMCC, '--version'])
run('node-version', ['node', '--version'])
run('compile', [EMCC, 'src/sjlj.c', '-DLIBRARY_ONLY', '-O1', '-g2',
                '-sSUPPORT_LONGJMP=wasm', '-sWASM_LEGACY_EXCEPTIONS=0',
                '-c', '-o', BUILD / 'c-library-standard.o'])
archive = BUILD / 'libsjlj-standard.a'
run('archive', [EMAR, 'rcs', archive, BUILD / 'c-library-standard.o'])
rustflags = ' '.join([
    '-C linker=' + EMCC, '-C panic=unwind',
    '-C target-feature=+exception-handling',
    '-C llvm-args=-wasm-use-legacy-eh=0',
    '-C link-arg=-fwasm-exceptions',
    '-C link-arg=-sSUPPORT_LONGJMP=wasm',
    '-C link-arg=-sWASM_LEGACY_EXCEPTIONS=0',
    '-C link-arg=' + str(archive),
])
(RESULTS / 'c-library-rustflags.txt').write_text('RUSTFLAGS=' + rustflags + '\n')
summary = {}
for mode, extra in [('prebuilt', []), ('rebuilt', ['-Zbuild-std'])]:
    env = os.environ.copy()
    env['RUSTFLAGS'] = rustflags
    env['CARGO_TARGET_DIR'] = str(BUILD / ('cargo-c-library-' + mode))
    base = ['--manifest-path', 'rust-demo/Cargo.toml', '--target', TARGET]
    # Cargo does not track changes to an archive passed directly as a link arg.
    run(mode + '-clean', ['cargo', '+nightly', 'clean', *base, '-p', 'wasm-eh-probe'], env)
    run(mode + '-build', ['cargo', '+nightly', *extra, 'build', '--offline', *base], env)
    artifacts = Path(env['CARGO_TARGET_DIR']) / TARGET / 'debug'
    result = run(mode + '-run', ['node', artifacts / 'wasm-eh-probe.js'], check=False)
    if mode == 'prebuilt':
        if result.returncode == 0 or 'mix of legacy and new exception' not in result.stdout:
            raise RuntimeError('Expected the prebuilt-std mixed-EH loading failure')
    else:
        result.check_returncode()
        if 'C longjmp=42; Rust panic caught' not in result.stdout:
            raise RuntimeError('Expected C longjmp and Rust panic recovery')
    dump = subprocess.run(['wasm-objdump', '-d', artifacts / 'wasm_eh_probe.wasm'],
                          text=True, capture_output=True, check=True).stdout
    instructions = re.findall(r'\|\s+(try_table|try|catch_all|catch|rethrow|throw_ref|throw)\b', dump)
    counts = {op: instructions.count(op) for op in sorted(set(instructions))}
    (RESULTS / f'c-library-{mode}-instructions.json').write_text(json.dumps(counts, indent=2) + '\n')
    if mode == 'rebuilt' and any(counts.get(op, 0) for op in ('try', 'catch', 'catch_all', 'rethrow')):
        raise RuntimeError('Legacy instructions remain after rebuilding std')
    summary[mode] = {'build_exit': 0, 'run_exit': result.returncode, 'instructions': counts}
(RESULTS / 'c-library-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
