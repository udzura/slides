----
marp: true
theme: rubykaigi2026
paginate: false
backgroundImage: url(./bg-2026.002.png)
title: "Uzumibi: Reinventing mruby for the Edges"
description: "On RubyKaigi 2026 Hakodate / Uzumibi: Reinventing mruby for the Edges"
# header: "Uzumibi: Reinventing mruby for the Edges"
image: https://udzura.jp/slides/2026/rubykaigi/ogp.png
size: 16:9
----

<!--
_class: title
_backgroundImage: url(./bg-2026.001.png)
-->

# <big>Uzumibi:</big><br>Reinventing mruby for the Edges

## Presentation by Uchio Kondo

----

<!--
_class: hero0
_backgroundImage: url(./bg-2026.003.png)
-->

# Hello, Hakodate!

<!--
It's my first time in Hokkaido, and I'm thrilled to speak in this beautiful city.
-->

----
<!--
_class: profile
-->

<img class="me" width="300" src="./me.jpg" />

# self.introduce!

- Uchio Kondo
  - from Fukuoka.rb (Kyushu)
- Member of &nbsp;<img class="shr" alt="SmartHR, Inc." width="250" src="./image-25.png" />
  - Product Engineer
- SmartHR is a **Platinum Sponsor** of RubyKaigi 2026

----

<!--
_class: hero
-->

# What is Uzumibi?

----

# Uzumibi

- An open-source framework for developing apps on **edge** and **serverless** platforms using Ruby
- "Uzumibi" = "buried fire" (embers under ashes)
  - Named out of admiration for a certain famous framework

----

# Key Features

- Generator with **multi-platform** support
- Easy-to-remember, **Sinatra-like DSL**
- Platform integration features
  - Durable Objects, Queues on Cloudflare
- **Extremely lightweight** artifacts

----

<!--
_class: pre-top20
-->

# Let's See It in Action

```bash
$ cargo install uzumibi
$ uzumibi new --platform cloudflare my_app
```

<!--
You can install Uzumibi using cargo, then generate a Cloudflare template.
-->

----

<!--
_class: pre-top20
-->

# The Generated `app.rb`

```ruby
app = Uzumibi::App.new

app.get "/" do |req, res|
  kv = Uzumibi::KV.new("MY_KV")
  count = (kv.get("count") || 0).to_i + 1
  kv.put("count", count.to_s)
  res.text "Hello! Count: #{count}"
end
```

- Any Rubyist can guess what this does

----

# Artifact Size

- WebAssembly file: **1.5MB** before compression
- After gzip: **~500KB**
- Easily fits within **Cloudflare Workers free plan**
- This is NOT a mockup — it actually connects to KVS as written in Ruby

----

# Multi-Platform

- Cloudflare Workers
- Google Cloud Run
- Write similar code, runs the same way
- Isn't this incredibly convenient?

----

<!--
_class: hero
-->

# The Magic Behind It: mrubyEdge

----

# Why Not `ruby.wasm`?

- `ruby.wasm` (CRuby-based) generates **~10MB** binaries
  - Even gzipped: **~5MB**
- Uzumibi is based on an entirely different runtime: **mrubyEdge**

----

# What is mrubyEdge?

- A custom mruby runtime, developed since **2014**
- Written entirely in **Rust**
- Designed from the ground up for **WebAssembly**
- Highly portable Wasm → runs everywhere, including the edge

----

# Why Not Original mruby?

- `mruby` uses `setjmp` / `longjmp` for code jumps
- Wasm core instructions have **no `goto` equivalent**
- Compiling requires Emscripten hacks
  - Emscripten runtime adds bulk
  - Forcefully imports/exports several functions
- PicoRuby has the same Emscripten dependency

----

# Why Rust?

- Advanced type system → productivity & safety
- Powerful Wasm ecosystem
- **Memory safety** guarantees
- ... and I personally wanted to implement a VM myself

----

<!--
_class: hero
-->

# Implementation Journey and Struggles

----

# History: Prototype (2024)

- Gave a presentation at **RubyKaigi 2024 in Okinawa**
- Strictly a **Proof of Concept**
  - Only capable of running a Fibonacci function for a demo

----

# Resumed Development (2025)

- Deeply studied `mruby/c` and redesigned the VM
- Relentless instruction implementation cycle:
  1. Find a Ruby sample code
  2. Compile to bytecode with existing `mruby`
  3. Make it run on mrubyEdge
  4. Add as E2E test
- Gradually matured through **tedious repetition**

----

<!--
_class: hero
-->

# Struggle 1: Register Machine

----

<!--
_class: two-samples
-->

# Register Machine vs. Stack Machine

| CRuby (Stack Machine) | mruby (Register Machine) |
|---|---|
| `push 1` | `LOADI R1, 1` |
| `push 2` | `LOADI R2, 2` |
| `add` | `ADD R1, R2` |

- CRuby: push operands onto a stack, consume with `add`
- mruby: operands stored in registers, `add` specifies registers

----

# Register Machine Data Structures

- **Register container** (not a hash map — a **slice**)
- **IREP**: reference to instruction sequence
- **Program counter**
- **Callinfo stack**: call context information

----

<!--
_class: pre-top20
-->

# Register as Slices

```
[R0][R1][R2][R3][R4][R5][R6][R7][R8][R9]...
 ^                   ^
 frame 0 start       frame 1 start (after call)
```

- Offset shifts forward on function call
- Shifts back on return
- Efficient memory access, no hash map overhead

----

<!--
_class: hero
-->

# Struggle 2: Leveraging Rust Traits

----

<!--
_class: pre-top20
-->

# Ruby Hash → Rust HashMap

```rust
// ValueHasher implements Hash trait — acts as the key
// Ruby key-value pair stored as tuple on the value side
type InnerHash = HashMap<ValueHasher, (RValue, RValue)>;

enum ValueHasher {
    Bool(bool),     // natively implements Hash
    Integer(i64),   // natively implements Hash
    // ...
}
```

- Result: `HashSet` internals become incredibly clean and simple

----

<!--
_class: hero
-->

# Struggle 3: Closures and Upvalues

----

<!--
_class: pre-top20
-->

# The `Env` Struct

```rust
struct Env {
    parent: Option<Box<Env>>,   // parent environment
    captures: Vec<RValue>,      // captured variables
}
```

- Created when a lambda/block is generated
- **Captures nothing at creation time**

----

# Deferred Capture

- A closure's lifetime is usually **shorter** than the outer method's
  - No copy needed while the outer env is alive
- Problem: returning a lambda as a value
  - The method's environment is destroyed
- Solution: **copy register contents into capture at the moment the frame ends**
  - Avoids unnecessary copies
  - Secures data when needed

----

<!--
_class: hero
-->

# Struggle 4: Singleton Classes

----

# Inheritance Tree with Singleton Classes

- Class `Bar` inherits from `Foo`
- `Bar` itself is a class instance → has a singleton class
- Inheritance tree of `Bar` (as class instance):
  1. `Bar`'s singleton class
  2. `Foo`'s singleton class
  3. `Object`'s singleton class
  4. `BasicObject`'s singleton class
  5. `Class`

----

# Implementing the Chain

- Modified initialization logic **specifically for class instances**
- Recursively calls singleton class generation on the parent class
- Accurately reproduces Ruby's complex inheritance chain in Rust

----

<!--
_class: hero
-->

# Struggle 5: Exceptions and Break

----

# Exceptions in mrubyEdge

- Exception raised at the `send` instruction
- Execution jumps to `rescue`
- VM extracts exception into a register
- Checks for match → execute rescue or re-raise
- Eventually hits `ensure` block

----

# Exception State & Break

- When exception occurs: VM updates to **"exception active"** state
- While in this state: **skips regular instructions**
- Traverses upward through blocks until handled
- `break` is implemented as **a type of exception**
  - Same behavior: unwinds call stack upward

----

<!--
_class: hero
-->

# The Breakthrough

----

# November 2025: Milestone

- **84%** of mruby 3.4's instructions implemented
- Foundational mechanisms to define classes and methods working
- For the finishing touch: **standard library**

----

# AI-Assisted Standard Library

- Foundation was solid → had **AI write all basic standard libraries**
- This experiment was **highly successful**
- Now working:
  - `String`, `Array`, `Hash`, `Enumerable`
  - ... and more

----

# Running on Cloudflare Workers

- Originally named "mrubyEdge" for WasmEdge
  - Didn't actually expect it to run on serverless edge platforms!
- Cloudflare Workers runs JavaScript → naturally executes Wasm
- After just **a few days of trial and error** (December 2025):
  - mruby running on Cloudflare Workers

----

# The Size: Just ~400KB

- Compiled mruby code: **~400KB**
- Even with full standard library: **well under 1MB**
- Effortlessly within free plan limits
- This is when I knew: **it's viable**

----

<!--
_class: hero
-->

# Uzumibi: Building the Framework

----

# Platform Support

- Cloudflare Workers
- Fastly
- Google Cloud Run
- **Web Workers / Service Workers**
  - API completely self-contained within the browser!

----

# Cloudflare Service Integration

- **KV** (Key-Value Store)
- **Durable Objects**
- **Queues**
- Introduced as an **abstraction layer**
  - Cloudflare Workers: native APIs
  - Cloud Run: Firestore, Cloud Pub/Sub
- Contributions for other services are welcome!

----

# The Framework Just Worked

- mrubyEdge foundation was built so solidly
- Uzumibi just worked **without much fuss**
- Built what I wanted → inadvertently created a **framework useful for everyone**

----

# Key Takeaway

- The original approach was right:
  - **Portable** Wasm binary
  - Complete control over Wasm-specific features
  - **Smallest possible footprint**
- By achieving this: **opening up a new horizon on the Edge**
- Uzumibi is still a newborn, but it has the power to **transform your development workflows**

----

<!--
_class: hero
-->

# Future Challenges: The Async Hurdle

----

# Wasm and Async

- Wasm must work with JavaScript
- In JS, I/O operations are **fundamentally asynchronous**
  - `fetch`, Durable Objects, Queues...
- But: **Wasm cannot accept async functions as imports**

----

# Asyncify: A Workaround

- `Asyncify` allows pseudo-passing async functions to Wasm
- Uzumibi uses it internally for Cloudflare Workers
- Massive downside: **binary bloat (~1.5x)**
- I started this project to fix bloated binaries
  - Relying on Asyncify is **unacceptable**

----

# Cloud Run Compromise

- Rust server libraries (Hyper, Tokio) require async as first-class
- Current compromise: I/O on a **single thread**
- Mitigated by spinning up many single-threaded containers
  - Design strictly dedicated to **serverless**
  - Not truly general-purpose

----

# Toward an Async VM

- VM is just a **state machine**
  - Should have good affinity with async
- A VM tailored for async:
  - **Yield** and **resume** at arbitrary times
- Currently exploring this implementation
- Homework for **next year**

----

<!--
_class: hero
-->

# Conclusion

----

# Conclusion

- Introduced **mrubyEdge** and the **Uzumibi** framework
- Hurdles remain, but already has **practical quality**
- From an exclusively Ruby-centric world:
  - Hard to step into serverless and edge computing
  - With mrubyEdge: develop with **the language you love**
- Please give it a try!

----

<!--
_class: hero0
_backgroundImage: url(./bg-2026.003.png)
-->

# Thank you!
