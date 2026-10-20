#!/usr/bin/env python3
"""Run independently logged probes; expected failures do not stop later probes."""
import json
import os
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
BUILD = ROOT / 'build'
RESULTS = ROOT / 'results'
BUILD.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)
EMCC = os.environ.get('EMCC', '/opt/homebrew/opt/emscripten/bin/emcc')
records = []

def run(name, args):
    p = subprocess.run([str(x) for x in args], text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, timeout=180)
    output_dir = BUILD if name.startswith('rust-') and name.endswith('-disassembly') else RESULTS
    (output_dir / (name + '.txt')).write_text('$ ' + shlex.join(map(str, args)) + '\n' + p.stdout + '\nexit=' + str(p.returncode) + '\n')
    records.append({'name': name, 'exit': p.returncode})
    print(name, p.returncode, flush=True)
    return p.returncode == 0

run('emcc-version', [EMCC, '--version'])
for tool in ['node', 'wasm-objdump', 'wasm-tools', 'wasm-opt']:
    run(tool + '-version', [tool, '--version'])
run('rustc-version', ['rustc', '-vV'])
run('node-versions', ['node', '-p', 'JSON.stringify(process.versions)'])

modes = {'js': ['-sSUPPORT_LONGJMP=emscripten'],
         'legacy': ['-sSUPPORT_LONGJMP=wasm', '-sWASM_LEGACY_EXCEPTIONS=1'],
         'standard': ['-sSUPPORT_LONGJMP=wasm', '-sWASM_LEGACY_EXCEPTIONS=0']}
for mode, flags in modes.items():
    obj = f'build/{mode}.o'
    if run(mode + '-compile', [EMCC, 'src/sjlj.c', '-O1', '-g2', *flags, '-c', '-o', obj]):
        run(mode + '-object', ['wasm-objdump', '-dx', obj])
        if run(mode + '-link', [EMCC, obj, '-O1', '-g2', *flags, '-o', f'build/{mode}.js']):
            run(mode + '-run', ['node', f'build/{mode}.js'])
            run(mode + '-disassembly', ['wasm-objdump', '-dx', f'build/{mode}.wasm'])
            run(mode + '-wat', ['wasm-tools', 'print', f'build/{mode}.wasm'])
            run(mode + '-validate', ['wasm-tools', 'validate', '--features', 'all', f'build/{mode}.wasm'])
            records.append({'name': mode + '-bytes', 'wasm': Path(f'build/{mode}.wasm').stat().st_size, 'js': Path(f'build/{mode}.js').stat().st_size})
    run(mode + '-library', [EMCC, 'src/sjlj.c', '-DLIBRARY_ONLY', '-O1', '-g2', *flags, '-c', '-o', f'build/{mode}-lib.o'])
    if mode != 'js':
        run(mode + '-named-library', [EMCC, 'src/sjlj.c', '-DLIBRARY_ONLY', '-DPROBE=' + mode + '_probe', '-O1', '-g2', *flags, '-c', '-o', f'build/{mode}-named.o'])

for mode in ['legacy', 'standard']:
    for opt in ['-O0', '-O1', '-O2']:
        name = 'mixed-' + mode + '-' + opt[1:]
        if run(name + '-link', [EMCC, 'src/mixed.c', 'build/legacy-named.o', 'build/standard-named.o', opt, '-g2', *modes[mode], '-o', f'build/{name}.js']):
            run(name + '-run', ['node', f'build/{name}.js'])
            run(name + '-disassembly', ['wasm-objdump', '-dx', f'build/{name}.wasm'])

# Link-time flags alone do not recompile a non-LTO object.
if run('legacy-object-standard-link', [EMCC, 'build/legacy.o', '-O1', '-g2', *modes['standard'], '-o', 'build/link-only.js']):
    run('link-only-disassembly', ['wasm-objdump', '-dx', 'build/link-only.wasm'])
    run('link-only-run', ['node', 'build/link-only.js'])

# Rust prebuilt std remains as installed; this intentionally tests that constraint.
for mode in ['legacy', 'standard']:
    name = 'rust-' + mode
    args = ['rustc', 'src/rust_main.rs', '--edition=2024', '--target=wasm32-unknown-emscripten',
            '-C', 'linker=' + EMCC, '-C', 'panic=unwind', '-C', 'target-feature=+exception-handling',
            '-C', 'llvm-args=-wasm-use-legacy-eh=' + ('1' if mode == 'legacy' else '0'),
            '-C', 'link-arg=-fwasm-exceptions', '-C', 'link-arg=-sWASM_LEGACY_EXCEPTIONS=' + ('1' if mode == 'legacy' else '0'),
            '-C', 'link-arg=' + f'build/{mode}-lib.o', '-o', f'build/{name}.js']
    if run(name + '-build', args):
        run(name + '-run', ['node', f'build/{name}.js'])
        run(name + '-disassembly', ['wasm-objdump', '-dx', f'build/{name}.wasm'])
(RESULTS / 'summary.json').write_text(json.dumps(records, indent=2) + '\n')
