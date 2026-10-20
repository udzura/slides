#!/usr/bin/env python3
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
records = []
def run(name, args, env=None):
    p = subprocess.run(args, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
    (ROOT / 'results' / (name + '.txt')).write_text('$ ' + shlex.join(args) + '\n' + p.stdout + '\nexit=' + str(p.returncode) + '\n')
    print(name, p.returncode, flush=True)
    records.append({'name': name, 'exit': p.returncode})
    return p.returncode == 0

# Preserve original failure artifacts. Generated JS loads the correspondingly named Wasm.
shutil.copyfile('build/rust-standard.js', 'build/rust-translated.js')
p = ROOT / 'build/rust-translated.js'
p.write_text(p.read_text().replace('rust-standard.wasm', 'rust-translated.wasm'))
if run('rust-translate', ['wasm-opt', 'build/rust-standard.wasm', '--translate-to-exnref', '-g', '-o', 'build/rust-translated.wasm']):
    run('rust-translated-run', ['node', 'build/rust-translated.js'])
    run('rust-translated-validate', ['wasm-tools', 'validate', '--features', 'all', 'build/rust-translated.wasm'])

emcc = os.environ.get('EMCC', '/opt/homebrew/opt/emscripten/bin/emcc')
env = os.environ.copy()
env['CARGO_TARGET_DIR'] = str(ROOT / 'build/cargo-standard')
env['RUSTFLAGS'] = ' '.join([
    '-C linker=' + emcc, '-C panic=unwind', '-C target-feature=+exception-handling',
    '-C llvm-args=-wasm-use-legacy-eh=0', '-C link-arg=-fwasm-exceptions',
    '-C link-arg=-sWASM_LEGACY_EXCEPTIONS=0',
    '-C link-arg=' + str(ROOT / 'build/standard-lib.o')])
(ROOT / 'results/rebuild-std-env.txt').write_text('\n'.join(k + '=' + env[k] for k in ['RUSTFLAGS', 'CARGO_TARGET_DIR']) + '\n')
# The external C object is a link argument, not a Cargo dependency. Force relink.
run('rust-clean-app', ['cargo', 'clean', '--manifest-path', 'rust-demo/Cargo.toml', '--target', 'wasm32-unknown-emscripten', '-p', 'wasm-eh-probe'], env)
if run('rust-rebuild-std', ['cargo', '-Zbuild-std', 'build', '--offline', '--manifest-path', 'rust-demo/Cargo.toml', '--target', 'wasm32-unknown-emscripten'], env):
    run('rust-rebuilt-run', ['node', 'build/cargo-standard/wasm32-unknown-emscripten/debug/wasm-eh-probe.js'])
    wasm = Path('build/cargo-standard/wasm32-unknown-emscripten/debug/wasm_eh_probe.wasm')
    run('rust-rebuilt-validate', ['wasm-tools', 'validate', '--features', 'all', str(wasm)])


# Compare the actual final instruction sets, including prebuilt std.
import re
for name, path in [('rust-standard', Path('build/rust-standard.wasm')),
                   ('rust-translated', Path('build/rust-translated.wasm')),
                   ('rust-rebuilt', Path('build/cargo-standard/wasm32-unknown-emscripten/debug/wasm_eh_probe.wasm'))]:
    p = subprocess.run(['wasm-objdump', '-d', str(path)], text=True, capture_output=True, check=True)
    instructions = re.findall(r'\|\s+(try_table|try|catch_all|catch|rethrow|throw_ref|throw)\b', p.stdout)
    counts = {op: instructions.count(op) for op in sorted(set(instructions))}
    (ROOT / 'results' / (name + '-instructions.json')).write_text(json.dumps(counts, indent=2) + '\n')

for name in ['legacy', 'standard', 'rethrow', 'mixed-same-function']:
    if run('wat-' + name + '-assemble', ['wasm-tools', 'parse', 'src/' + name + '.wat', '-o', 'build/wat-' + name + '.wasm']):
        run('wat-' + name + '-run', ['node', 'src/check-wat.cjs', 'build/wat-' + name + '.wasm'])

(ROOT / 'results/recovery-summary.json').write_text(json.dumps(records, indent=2) + '\n')
