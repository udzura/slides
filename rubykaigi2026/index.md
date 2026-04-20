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

<!--
Today, I'd like to talk about a product called Uzumibi.
-->

----

<!--
_class: hero0
_backgroundImage: url(./bg-2026.003.png)
-->

# Hello, Hakodate!

<!--
I traveled here from Fukuoka, Kyushu—about 1,700 km away, almost the full length of Japan. It's my first time in Hokkaido, and I'm thrilled to speak in this beautiful city.
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

<!--
I'm Kondo, a product engineer at SmartHR—Japan's largest HR SaaS startup and a Platinum Sponsor of RubyKaigi 2026.
-->

----

<!--
_class: hero
-->

# What is Uzumibi?

<!--
Today's theme is an open-source framework called Uzumibi.
-->

----

# Uzumibi

- An open-source framework for developing apps on **edge** and **serverless** platforms using Ruby
- "Uzumibi" = "buried fire" (embers under ashes)
  - Named out of admiration for a certain famous framework

<!--
It's a framework for developing applications on edge and serverless platforms using Ruby. "Uzumibi" means "buried fire" or embers under ashes, named out of admiration for a certain famous framework.
-->

----

# Key Features

- Generator with **multi-platform** support
- Easy-to-remember, **Sinatra-like DSL**
- Platform integration features
  - Durable Objects, Queues on Cloudflare

<!--
The key features of Uzumibi are: it has a generator and supports multiple platforms; it uses an easy-to-remember, Sinatra-like DSL; it supports platform integration features like Durable Objects and Queues on Cloudflare; 
-->

----

# Special Key Feature

- **Extremely lightweight** artifacts

<!--
and above all, it is extremely lightweight.
-->

----

<!--
_class: pre-top20
-->

# Let's See It in Action

```bash
$ cargo install uzumibi
$ uzumibi new --template cloudflare my-app
```

<!--
Let's see it in action. You can install Uzumibi using the cargo command, 
-->

----

```
my-app/
├── Cargo.toml
├── lib
│   └── app.rb
├── package.json
├── src
│   └── index.js
├── vitest.config.js
├── wasm-app
│   ├── build.rs
│   ├── Cargo.toml
│   └── src
│       └── lib.rs
└── wrangler.jsonc

5 directories, 9 files
```

<!--
then generate a Cloudflare template via uzumibi new.
-->

----

<!--
-->

# The Generated `app.rb`

<br />
<br />

```ruby
# Any Rubyist can guess what this does...
class App < Uzumibi::Router
  get "/" do |req, res|
    res.status_code = 200
    res.headers = {
      "content-type" => "text/plain",
      "x-powered-by" => "#{RUBY_ENGINE} #{RUBY_VERSION}"
    }
    res.body = "It works!\n"
    res
  end
end

$APP = App.new
```

<!--
The important file generated is app.rb. If you open it, any Rubyist can guess what it does. I'll modify it slightly to access a Key-Value Store. Just like that, this code can be deployed immediately.
-->

----

# Artifact Size

- WebAssembly file: **1.2MiB** before compression
- After gzip: **~370KiB**
- Easily fits within **Cloudflare Workers free plan**

<!--
Please look at the file size. The artifact generated contains a WebAssembly file that is 1.5MB before compression, and only about 500KB after compression. This easily fits well within the free plan limits of Cloudflare Workers.
-->

----

```
Total Upload: 1224.92 KiB / gzip: 369.05 KiB
Your Worker has access to the following bindings:
Binding                                    Resource            
env.UZUMIBI_KV_DATA (UzumibiKVObject)      Durable Object      
env.ASSETS                                 Assets              

Uploaded sample-app-xxx (7.59 sec)
Deployed sample-app-xxx triggers (1.53 sec)
  https://sample-app-xxx.udzura.workers.dev
Current Version ID: 2bfc85d2-7582-436a-98fd-xxxxxxxx

```

----

# This is NOT a mockup!!!

- It actually connects to real Cloudflare functions, e.g. KVS, Queue...

<!--
And this isn't just a mockup; if you actually access it, you can see it connects to the KVS exactly as written in Ruby.
-->

----

# Multi-Platform

- Cloudflare Workers or Google Cloud Run
- Write similar code, runs the same way

<!--
Uzumibi proves you can comfortably develop edge applications in Ruby. While this example uses Cloudflare Workers, you can write similar code and run it exactly the same way on serverless environments like Google Cloud Run. Isn't this incredibly convenient?
-->

----

<!--
_class: hero
-->

# The Magic Behind It: mruby/edge

<!--
You might find this strange. ruby.wasm allows you to write applications in Ruby, but it usually generates much larger artifacts—around 10MB. So how is this magic possible? It's because Uzumibi is based on an entirely different mruby runtime I created, called mruby/edge.
-->

----

# Why Not `ruby.wasm`?

- `ruby.wasm` (CRuby-based) generates **30 ~ 60 MB** binaries
  - Even gzipped: **~8.6MB** [ref](https://qiita.com/hiroeorz@github/items/a2aad2f3e9939a9c257b)
- Uzumibi is based on an entirely different runtime: **mruby/edge**

<!--
My motivation was simple: generating small artifacts was too difficult with the CRuby-based ruby.wasm. Compiling CRuby to Wasm right now generates a binary of about some tens of MB before compression. Even gzipped, it's around 8.6MB.
-->

----

# What is mruby/edge?

- A custom mruby runtime, developed since **2014**
- Written entirely in **Rust**
- Designed from the ground up for **WebAssembly**
- Highly portable Wasm → runs everywhere, including the edge

<!--
Before you can understand Uzumibi's power, I need to explain mruby/edge. It's a custom mruby runtime I've been developing since 2014, written entirely in Rust and designed from the ground up to be compiled into WebAssembly. Because it generates highly portable Wasm, it runs everywhere, including the edge.
-->

----

# Why Not Original mruby?

- `mruby` uses `setjmp` / `longjmp` for code jumps
- Wasm core instructions have **no `goto` equivalent**
- Compiling requires some hacks
  - PicoRuby has the same Emscripten dependency
    - Emscripten runtime adds bulk codes
    - Forcefully imports/exports several functions

<!--
Lightweight implementations like mruby and mruby/c inherently follow a philosophy of excluding unnecessary code. However, Yukihiro Matsumoto's original mruby relies on C functions like setjmp and longjmp for code jumps. Since WebAssembly's core instructions lack a goto equivalent, compiling these to Wasm requires hacks. Other implementations like PicoRuby rely on Emscripten for this, meaning the Wasm binary must include Emscripten's bulky runtime, which also forcefully imports and exports several functions behind the scenes.
-->

----

# Why Rust?

- Advanced type system → productivity & safety
- Powerful Wasm ecosystem
- **Memory safety** guarantees
- ... and I personally wanted to implement a VM myself

<!--
Given this, I decided I couldn't simply rely on existing Ruby or mruby implementations, and chose to rewrite it from scratch in Rust. Rust offers distinct advantages: productivity and safety via its advanced type system, a powerful Wasm ecosystem, and memory safety. Plus, I personally wanted to implement a VM myself.
-->

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

<!--
By 2024, a prototype of mruby/edge was complete. Two years ago, I gave a presentation on it at RubyKaigi in Okinawa. However, it was strictly a Proof of Concept, only capable of running a Fibonacci function for a demo.
-->

----

![bg w:70%](./slide-2024.png)

----

# Resumed Development (2025)

- Deeply studied `mruby/c` and redesigned the VM
- Relentless instruction implementation cycle:
  - Find a Ruby sample code
  - Compile to bytecode with existing `mruby`
  - Make it run on mruby/edge
  - Add as E2E test

<!--
At the beginning of 2025, I resumed development. I deeply studied implementations like mruby/c and redesigned the VM. Once the VM was running, I relentlessly implemented instructions: find a Ruby sample code, confirm it with existing mruby, compile it to bytecode, make it run on mruby/edge, and add it as an E2E test. Through this tedious repetition, mruby/edge gradually matured.
-->

----

<!--
_class: hero
-->

# Struggle 1: Register Machine

<!--
Let me share a few implementation struggles from this period. Here is an mruby instruction to calculate 1 + 2. As you can see, it looks different from CRuby's instructions.
-->

----

<!--
_class: two-samples
-->

# Register Machine vs. Stack Machine

| CRuby (Stack Machine) | mruby (Register Machine) |
|---|---|
| `putobject 1` | `LOADI R1, 1` |
| `putobject 2` | `LOADI R2, 2` |
| `opt_plus` | `ADD R1, R2` |

- CRuby: put operands onto a stack, consume with `opt_plus`
- mruby: operands loaded in registers, `ADD` specifies registers

<!--
CRuby uses a stack machine, pushing operands onto a stack and consuming them with an add instruction. mruby, however, is a register machine. Operands are stored in registers like R1 and R2, and the add instruction specifies those registers and returns the result to one of them.
-->

----

# Register Machine Data Structures

- **Register container** (not a hash map — a **slice**)
- **IREP**: reference to instruction sequence
- **Program counter**
- **Callinfo stack**: call context information

<!--
A register machine requires specific data structures: a container for registers, a reference to the instruction sequence called IREP, a program counter, and a call stack called callinfo.
-->

----

# VM Struct

<br />

```rust
pub struct VM {
    pub id: usize,
    pub irep: Rc<IREP>,
    pub pc: Cell<usize>,
    pub regs: [Option<Rc<RObject>>; MAX_REGS_SIZE],
    pub current_regs_offset: usize,
    pub current_callinfo: Option<Rc<CALLINFO>>,
    pub globals: RHashMap<String, Rc<RObject>>,
    pub consts: RHashMap<String, Rc<RObject>>,
    //...
}
```

----

## IREP & CALLINFO

```rust
pub struct IREP {
    pub nlocals: usize,
    pub nregs: usize,
    pub code: Vec<Op>,
    pub syms: Vec<RSym>,
    pub pool: Vec<RPool>,
    pub catch_target_pos: Vec<usize>,
    // ...
}

pub struct CALLINFO {
    pub prev: Option<Rc<CALLINFO>>,
    pub pc_irep: Rc<IREP>,
    pub current_regs_offset: usize,
    pub target_class: TargetContext,
    pub n_args: usize,
    // ...
}
```

----

<!--
_class: pre-top20
-->

# Register as Slices

- Offset shifts forward on function call
- Shifts back on return
- Efficient memory access, no hash map overhead

<!--
For memory efficiency and access speed, registers are not hash maps; they are internally implemented as slices. The implementation shifts the start point of the slice every time a function's stack is pushed. Conceptually, when a function is called, the register offset moves forward, and when it returns, it shifts back.
-->

----

```
[R0][R1][R2][R3][R4][R5][R6][R7][R8][R9]...
 ^                   ^
 frame 0 start       frame 1 start (after call)
```

----

```rust
pub struct VM {
    // Only one array in the VM struct
    regs: [Option<Rc<RObject>>; 256]
    // Points to the "start of the current frame"
    current_regs_offset: usize         
}

// Method call = shift the offset
// Behavior model:

vm.current_regs_offset += a as usize;  // Call → shift forward
// ... method execution ...
vm.current_regs_offset -= a as usize;  // Return → shift back
```

----

<!--
_class: hero
-->

# Struggle 2: Leveraging Rust Traits

<!--
We also reused Rust's convenient traits wherever possible. For example, a struct implementing the Hash trait can be used as a hash key, and PartialEq allows comparisons.
-->

----

# Ruby Hash → Rust HashMap

<br />
<br />

```rust
pub type RHash = HashMap<ValueHasher, (Rc<RObject>, Rc<RObject>)>;
#[derive(Debug, Hash, Eq, /*...snip*/)]
pub enum ValueHasher {
    Bool(bool),
    Integer(i64),
    Float(Vec<u8>),
    Symbol(String),
    String(Vec<u8>),
    Class(String),
}

// Each variant's content, such as bool, i64, String, Vec<u8>,
// etc., all natively implement Hash + Eq in Rust,
// so derive(Hash) automatically generates the implementation.
```

<!--
We map Ruby-level Hashes directly to Rust's standard HashMap. For the key in the Rust HashMap, we insert an enum called ValueHasher, which implements the Hash trait. The actual Ruby objects—key and value—are stored as a tuple on the value side. Because ValueHasher simply wraps booleans or integers that natively implement the Hash trait in Rust, it acts as a perfect hash key. As a result, internal functions like `mrb_hash_set_index` become incredibly clean and simple.
-->

----

# `mrb_hash_set_index` — Clean & Simple

<br />
<br />

```rust
pub fn mrb_hash_set_index(
    this: Rc<RObject>,
    key: Rc<RObject>,
    value: Rc<RObject>,
) -> Result<Rc<RObject>, Error> {
    let hash: &RefCell<_> = match &this.value {
        RValue::Hash(a) => a,
        _ => return Err(Error::RuntimeError(
            "Hash#[] must called on a hash".to_string(),
        )),
    };
    let mut hash = hash.borrow_mut();
    let hashed: ValueHasher = key.as_hash_key()?;
    hash.insert(hashed, (key.clone(), value.clone()));
    Ok(value.clone())
}
```

----

<!--
_class: hero
-->

# Struggle 3: Closures and Upvalues

<!--
Next: closures and upvalues. To capture the surrounding environment, we created an Env struct in mruby/edge.
-->

----

<!--
_class: pre-top20
-->

# The `Env` Struct

```rust
pub struct ENV {
     pub upper: Option<Rc<ENV>>,
     pub current_regs_offset: usize,
     pub captured: RefCell<Option<Vec<Option<Rc<RObject>>>>>,
     pub is_expired: Cell<bool>,
 }
```

- Created when a lambda/block is generated
- **Captures nothing at creation time**

<!--
The Env struct has an Option type to hold the parent Env and a vector for captured variables. Interestingly, the array meant to capture the environment doesn't actually copy anything at the moment the lambda is created.
-->

----

# Deferred Capture

- A closure's lifetime is usually **shorter** than the outer method's
  - No copy needed while the outer env is alive

----

<!--
_class: pre-top20
-->

# Safe Pattern: Block Doesn't Outlive Method

```ruby
def greet(name)
  3.times do |i|
    puts "#{i}: Hello, #{name}!"
    # `name` lives as long as `greet` → no capture needed
  end
end
```

- The block's lifetime ≤ the method's lifetime
- Outer env is alive → **no copy needed**

----

# 　How's this going?: Lambda Escapes

<br />

```ruby
def make_counter
  count = 0
  -> { count += 1; count }
end

c = make_counter
# method `make_counter` returns a lambda,
# but method's env is destroyed
p c.call  #=> ?
```

----

# "Orphaned" Lambdas

- Problem: returning a lambda as a value
  - The method's environment is destroyed
- Solution: **copy register contents into capture at the moment the frame ends**
  - Avoids unnecessary copies
  - Secures data when needed

<!--
Why? Because a closure's lifetime is usually shorter than the outer method's. As long as the outer method's environment is alive, the internal lambda is fine, so no capture is needed. But if you return a lambda as a value and use it elsewhere, the method's environment is destroyed, causing a problem. To solve this, mruby/edge delays the process: it copies the register contents into the capture at the exact moment the frame ends. This avoids unnecessary copies but secures the data when needed. Since each Env holds a reference to its parent, getting an upvalue is just tracing through them.
-->

----

<!--
_class: hero
-->

# Struggle 4: Singleton Classes

<!--
Let's look at the inheritance tree. The RClass struct holds a method table. In Ruby, singleton classes (eigenclasses) are highly important.
-->

----
<!--
_class: pre-top20
-->

# Inheritance Tree with Singleton Classes

- Class `Bar` inherits from `Foo`
- `Bar` has its own singleton class (eigenclass)

```ruby
class Foo; end
class Bar < Foo; end
```

----

# Singleton Class of `Bar`

```ruby
Bar.new.singleton_class.ancestors
#=> [
#    #<Class:#<Bar:0x...>>,
#    Bar,
#    Foo,
#    Object, Kernel, BasicObject
#   ]
```

----

# Class's Singleton Class

- `Bar` itself is a class instance → has a singleton class
- Inheritance tree of `Bar` (as class instance):
  - `Bar`'s singleton class
  - `Foo`'s singleton class
  - `Object/BasicObject`'s singleton class
  - `Class`, ...

<!--
If class Bar inherits from Foo, what happens when you create an instance of Bar? Since Bar itself is a class instance, its inheritance tree is slightly unique: Bar's singleton class, then Foo's singleton, Object's singleton, BasicObject's singleton, and finally the Class class.
-->

----

# #\<Class:Bar\>'s Ancestors

```ruby
Bar.singleton_class.ancestors
#=> [
#    #<Class:Bar>,
#    #<Class:Foo>,
#    #<Class:Object>,
#    #<Class:BasicObject>,
#    Class, Module, Object, Kernel, BasicObject
#   ]
```

----

# Implementing the Chain

- Modified initialization logic **specifically for class instances**
- Recursively calls singleton class generation on the parent class
- Accurately reproduces Ruby's complex inheritance chain in Rust

<!--
To accurately reproduce this complex chain in Rust, we modified the initialization logic specifically for class instances to recursively call the singleton class generation method on the parent class.
-->

----

# Impl of Singleton Class for Class Instances

<br />
<br />

```rust
fn initialize_or_get_singleton_class_for_class(
    self, vm
) -> Rc<RClass> {
    let super_class = match &class.super_class {
        Some(parent) => {
            let parent_obj = RObject::class(parent.clone(), vm);
            // Recursively generate parent's singleton class!
            parent_obj
                .initialize_or_get_singleton_class_for_class(vm)
        }
        None => vm.get_class_by_name("Class"),
    };
    RClass::new_singleton(&class_name, Some(super_class), ...)
}
```

----

<!--
_class: hero
-->

# Struggle 5: Exceptions and Break

<!--
Finally, exceptions. When compiled into mruby bytecode, an exception is raised specifically at the send instruction.
-->

----

<!--
_class: pre-top20
-->

# Exception: Ruby Code

```ruby
begin
  raise RuntimeError, "foobar"
rescue ArgumentError => e
  p e
ensure
  p "done"
end
```

----

<!--
_class: pre-top5
-->

# Compiled Bytecode

<br />

```
  SSEND    R2  :raise  n=2
  JMP      043
  EXCEPT   R2                  
  GETCONST R3  ArgumentError
  RESCUE   R2  R3             
  JMPIF    R3  028             
  JMP      041                 
  MOVE     R1  R2              
  SSEND    R2  :p  n=1         
  JMP      043                 
  RAISEIF  R2                  
  EXCEPT   R4                  
  STRING   R6  "done"
  SSEND    R5  :p  n=1         
  RAISEIF  R4                  
  RETURN   R2
```

----

<!--
_class: pre-top5
-->

# Compiled Bytecode

<br />

```
  SSEND    R2  :raise  n=2     ← exception raised!
  JMP      043
  EXCEPT   R2                  ← extract exception to R2
  GETCONST R3  ArgumentError
  RESCUE   R2  R3              ← R2.is_a?(R3)?
  JMPIF    R3  028             ← match → goto rescue body
  JMP      041                 ← no match → skip
  MOVE     R1  R2              ← e = exception
  SSEND    R2  :p  n=1         ← p(e)
  JMP      043                 ← goto ensure
  RAISEIF  R2                  ← unhandled → re-raise
  EXCEPT   R4                  ← ensure: extract remaining exc
  STRING   R6  "done"
  SSEND    R5  :p  n=1         ← p("done")
  RAISEIF  R4                  ← if exc remains, re-raise
  RETURN   R2
```

<!--
Execution then jumps to rescue. The VM extracts the active exception into a register, checks for a match, and either executes the rescue clause or re-raises the error, eventually hitting the ensure block.
-->

----

# Exception State & Break

- When exception occurs: VM updates to **"exception active"** state
- While in this state: **skips regular instructions**
- Traverses upward through blocks until handled

----

# Exception State in VM

```rust
// vm.rs — when an instruction raises an error:
match consume_expr(self, op.code, ...) {
    Err(e) => {
        self.exception = Some(
            Rc::new(RException::from_error(self, &e))
        );
        continue; // jump to loop head
        // → finds nearest catch target after current PC
    }
}
```

<!--
When an exception occurs, the VM's state updates to indicate "an exception is active." While in this state, the VM skips regular instructions and traverses upwards through the blocks until the exception is handled. The implementation of break is quite similar. In mruby/edge, break is implemented as a type of exception because it behaves identically, unwinding the call stack and tracing blocks upwards until it finds the invocation point.
-->

----

# cf. `break` in mruby/edge

- `break` is implemented as **a type of exception**
  - Same behavior: unwinds call stack upward

----

<!--
_class: pre-top5
-->

# Error Enum Type in Rust

<br />

```rust
pub enum Error {
    General,
    Internal(String),
    InvalidOpCode,
    RuntimeError(String),
    ArgumentError(String),
    RangeError(String),
    TypeMismatch,
    NoMethodError(String),
    NameError(String),
    ZeroDivisionError, //...

    Break(Rc<RObject>),              // ← break as exception!
    BlockReturn(usize, Rc<RObject>), // and more...
}
```

----

<!--
_class: hero
-->

# After the Struggles

----

# November 2025: Milestone Cleared

- **84%** of mruby 3.4's instructions implemented
- Foundational mechanisms to define classes and methods working
- For the finishing touch: **standard library**

<!--
By mid-November 2025, basic instructions were supported. About 84% of mruby 3.4's instructions were implemented, along with foundational mechanisms to define classes and methods.
-->

----

![alt text](./mruby-table.png)

[https://mrubyedge.github.io/mrubyedge/table.html](https://mrubyedge.github.io/mrubyedge/table.html)

----

# AI-Assisted Standard Library

- Foundation was solid → had **AI write all basic standard libraries**
- This experiment was **highly successful**
- Now working:
  - `String`, `Array`, `Hash`, `Enumerable`
  - ... and more

<!--
For the finishing touch, I needed a standard library. Since the foundation was solid, I had AI write all the basic standard libraries. This experiment was highly successful. Your favorites like String, Array, Hash, and Enumerable were now working.
-->

----

<!--
_class: hero
-->

# Voyage for the True Edge

----

# Running on Cloudflare Workers

- Originally named "mruby/edge" for WasmEdge
  - Didn't actually expect it to run on serverless edge platforms!
- Cloudflare Workers runs JavaScript → naturally executes Wasm
- After just **a few days of trial and error** (December 2025):
  - mruby running on Cloudflare Workers

<!--
By early February, my custom Ruby was running properly. I originally named the project "mruby/edge" because I intended to run it on WasmEdge. I honestly didn't expect it to run on serverless edge platforms. But since it was running everywhere, I decided to test it on Cloudflare Workers. Since Cloudflare Workers runs JavaScript, it can naturally execute Wasm. I implemented the necessary functions, built a bridge for the Wasm interface, and aligned the Ruby code. After just a few days of trial and error in December, I had mruby running on Cloudflare Workers.
-->

----

![bg h:80%](./first-pr-uzumibi.png)

<br />
<br />
<br />
<br />
<br />
<br />
<br />
<br />
<br />
<br />
<br />
<br />
<br />

[https://github.com/mrubyedge/uzumibi/pull/1](https://github.com/mrubyedge/uzumibi/pull/1)

----

# First Deployment

```
 ⛅️ wrangler 4.54.0 (update available 4.83.0)
─────────────────────────────────────────────
Total Upload: 303.82 KiB / gzip: 97.16 KiB
```

----

# The Size: Just 300KiB

- Compiled mruby code: **300KiB**
    - Compressed to under **100KiB**
- Effortlessly within free plan limits
- This is when I knew: **it's viable**

<!--
Furthermore, when compiled, this mruby code fit into just about 400KB. Even anticipating a size increase after fully implementing the standard library, I knew it would effortlessly stay under 1MB.
-->

----

<!--
_class: hero
-->

# Igniting Uzumibi

<!--
Convinced it was viable, I began developing in earnest. I wrote spike code and added support for Fastly and other frameworks.
-->

----

# Platform Support

- Cloudflare Workers
- Fastly
- Google Cloud Run
- **Web Workers / Service Workers**
  - API completely self-contained within the browser!

<!--
Interestingly, it can even run on Web Workers or Service Workers—meaning you can implement an API completely self-contained within the browser.
-->

----

| Platform | Template Name | Status |
|----------|--------------|--------|
| Cloudflare Workers | `cloudflare` | Beta |
| Fastly Compute@Edge | `fastly` | Experimental |
| Spin (Fermyon Cloud) | `spin` | Experimental |
| Google Cloud Run | `cloudrun` | Alpha |
| Service Worker | `serviceworker` | Experimental |
| Web Worker | `webworker` | Experimental |

----

# Cloudflare Service Integration

- **KV** (Key-Value Store)
- **Durable Objects**
- **Queues**

----

# External Service Abstraction

- Introduced as an **abstraction layer**
  - Cloudflare Workers: native APIs
  - Cloud Run: Firestore, Cloud Pub/Sub
- Contributions for other services are welcome!

<!--
I also integrated Cloudflare's rich services, like Durable Objects and Queues. These are introduced as an abstraction layer supporting Cloudflare Workers and Google Cloud Run. For Cloud Run, similar functions are achieved using Firestore and Cloud Pub/Sub. I'd love to continue adding support for other services, and contributions are highly welcome.
-->

----

| Feature | Cloudflare Workers | Cloud Run |
|---|---|---|
| KV | Durable Objects | Firestore |
| Queue | Queues | Cloud Pub/Sub |
| Access | Access (JWT) | IAP (JWT) |
| HTTP | `fetch()` | library (reqwest-based) |

----

<!--
_class: hero
-->

# Retrospective: The Journey So Far

----

# The Framework Just Worked

- mruby/edge foundation was built so solidly
- Uzumibi just worked **without much fuss**
- Built what I wanted → inadvertently created a **framework useful for everyone**

<!--
I intended to talk mainly about Uzumibi today, but I spent most of the time on my struggles with mruby/edge. The truth is, because the mruby/edge foundation was built so solidly, Uzumibi just worked without much fuss. I built what I wanted, and inadvertently created a framework highly useful for everyone.
-->

----

# Key Takeaway

- The original approach was right:
  - **Portable** Wasm binary
  - Complete control over Wasm-specific features
  - **Smallest possible footprint**
- By achieving this: **opening up a new horizon on the Edge**
- Uzumibi is still a newborn, but it has the power to **transform your development workflows**

<!--
A key takeaway is that my original approach was right: I wanted a portable Wasm binary with complete control over Wasm-specific features, and I wanted to keep the footprint as small as possible. By achieving this, I believe we are opening up a new horizon on the Edge. Uzumibi is still a newborn framework, but it has the power to transform your development workflows. Please give it a try.
-->

----

<!--
_class: hero
-->

# Future Challenges: The Async Hurdle

<!--
I have a little time left, so let's discuss future challenges: asynchronous programming.
-->

----

# Wasm and Async

- Wasm must work with JavaScript
- In JS, I/O operations are **fundamentally asynchronous**
  - `fetch`, Durable Objects, Queues...
- But: **Wasm cannot accept async functions as imports**

<!--
Wasm must work seamlessly with JavaScript, where I/O operations—like fetch, or Cloudflare Workers' Durable Objects and Queues—are fundamentally asynchronous. However, Wasm cannot accept asynchronous functions as imports.
-->

----

# Asyncify: A Workaround

- `Asyncify` allows pseudo-passing async functions to Wasm
- Uzumibi uses it internally for Cloudflare Workers
- Massive downside: **binary bloat (~1.5x)**
- I started this project to fix bloated binaries
  - Relying on Asyncify is **unacceptable**

<!--
As a workaround, a tool called Asyncify emerged, allowing you to pseudo-pass async functions to a Wasm instance. Uzumibi uses Asyncify internally for Cloudflare Workers support. But a massive downside is binary bloat—it increases size by about 1.5 times. I started this project to fix bloated binaries, so relying on Asyncify is unacceptable.
-->

----

# Cloud Run Compromise

- Rust server libraries (Hyper, Tokio) require async as first-class
- Current compromise: I/O on a **single thread**
- Mitigated by spinning up many single-threaded containers
  - Design strictly dedicated to **serverless**
  - Not truly general-purpose

<!--
You might think single-threaded I/O would be a bottleneck. But on Cloud Run, you can spin up many single-threaded containers instead of using multi-core within a single process. It works, but it's a serverless-specific workaround—not truly general-purpose. So I want to make mruby/edge itself async-compatible.
-->

----

# Blocking I/O on a Thread

```rust
let mut uzumibi_request = uzumibi::build_uzumibi_request(&request);

let result = tokio::task::spawn_blocking(move || {
    uzumibi::uzumibi_handle_request(uzumibi_request)
        .map_err(|e| e.to_string())
})
.await;
```

----

# Current VM: A Simple Loop

- The VM runs a **synchronous instruction loop**
  - Unchanged since 2024
- But the VM is just a **state machine**
  - Naturally suited for async: **pause** and **resume** at any point

<!--
Looking at the current VM, it runs a straightforward synchronous instruction loop—unchanged since 2024. But notice that the VM is essentially a state machine. If we design it to pause and resume at arbitrary points, it should integrate well with async programming.
-->

----

# Currently

<br />

```rust
loop {
    let op = self.irep.code[self.pc.get()];
    self.pc.set(self.pc.get() + 1);
    match consume_expr(self, op.code, ...) {
        Err(e) => {
            self.exception = Some(
                Rc::new(RException::from_error(self, &e))
            );
            continue;
        }
        Ok(_) => {}
    }
    // ...
}
```

----

# Maybe like this?

<br />
<br />

```rust
impl<'a> Future for VmFuture<'a> {
    type Output = Value;

    fn poll(self: Pin<&mut Self>, c: &mut Context<'_>) -> Poll<Value> {
        let op = self.irep.code[self.pc.get()];
        let inst = this.iseq.instructions[this.pc];
        match consume_expr(self, op.code, ...) {
            Pending => {
                // Pause the VM and return Pending
                Poll::Pending
            }
            Ok(value) => Poll::Ready(value.clone()),
            Err(e) => { /*...*/ },
        }
    }
}
```

----

<!--
_class: hero
-->

# Demo: Async VM in the Browser

<!--
Let me demonstrate an async VM running in the browser. Just like two years ago, we'll execute a Fibonacci function.
-->

---

# Demo movie 1

<br />
<br />

<video controls muted width="680">
  <source src="./00_future-vm-run-all.mp4" type="video/mp4">
</video>

----

# Synchronous Execution

- Compute Fibonacci in one shot
- During computation: **browser UI freezes**
  - No control returned to the event loop

<!--
First, let's compute Fibonacci all at once. In this case, the browser gets no control back during the computation—the UI completely freezes.
-->

---

# Demo movie 2

<br />
<br />

<video controls muted width="680">
  <source src="./01_future-vm-tick.mp4" type="video/mp4">
</video>

----

# Async Execution: Yield per Instruction

- Yield control back to the browser **after each instruction**
- Browser UI remains **responsive** throughout
- The instruction loop lives on the **browser side**
  - Async function calls become feasible via glue code

<!--
Next, let's compute Fibonacci while yielding control back to the browser after each instruction. This time the UI stays responsive. Since the instruction loop runs on the browser side, we can insert async function calls with some glue code.
-->

----

# Caveat: Granularity

- Browser loop throughput: **~250 instructions/sec**
- Yielding every single instruction is too fine-grained
  - Need to find the right **batch size**
- A production-ready async mruby is homework for the future

<!--
Here's one caveat: the browser loop maxes out at around 250 instructions per second, so yielding on every single instruction is too fine-grained. The right batch size needs further investigation. I wish I could show a fully production-ready async mruby here, but that remains homework for the future.
-->

----

<!--
_class: hero
-->

# Conclusion

----

# Conclusion

- Introduced **mruby/edge** and the **Uzumibi** framework
- Hurdles remain, but already has **practical quality**
- From an exclusively Ruby-centric world:
  - Hard to step into serverless and edge computing

<!--
Today I introduced mruby/edge and the Uzumibi framework. While hurdles remain, it already has quality sufficient for practical use. From an exclusively Ruby-centric world, it's often hard to step into serverless and edge computing. But with mruby/edge, you can develop with high compatibility using the language you love. Please give it a try—I look forward to your feedback. Thank you very much.
-->

----
<!--
_class: hero
-->

# With mruby/edge:<br />Develop with the Language You Love

----

<!--
_class: hero
-->

# Please Give it a Try!

----

<!--
_class: hero0
_backgroundImage: url(./bg-2026.003.png)
-->

# Thank You!

<!--
Thank you very much!
-->
