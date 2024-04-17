import { WASI, File, OpenFile, ConsoleStdout, PreopenDirectory } from "@bjorn3/browser_wasi_shim";

let args = ["bin", "arg1", "arg2"];
let env = ["FOO=bar"];
let fds = [
    new OpenFile(new File([])), // stdin
    ConsoleStdout.lineBuffered(msg => console.log(`[WASI stdout] ${msg}`)),
    ConsoleStdout.lineBuffered(msg => console.warn(`[WASI stderr] ${msg}`)),
    new PreopenDirectory(".", [
        ["example.c", new File(new TextEncoder("utf-8").encode(`#include "a"`))],
        ["hello.rs", new File(new TextEncoder("utf-8").encode(`fn main() { println!("Hello World!"); }`))],
    ]),
];
let wasi = new WASI(args, env, fds);

let wasm = await WebAssembly.compileStreaming(fetch("fib.wasm"));
let inst = await WebAssembly.instantiate(wasm, {
    "wasi_snapshot_preview1": wasi.wasiImport,
});
wasi.start(inst);
