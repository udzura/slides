## Introduction
Today, I'd like to talk about a product called Uzumibi. I'm Kondo, a product engineer at SmartHR—Japan's largest HR SaaS startup and a Platinum Sponsor of RubyKaigi 2026. I traveled here from Fukuoka, Kyushu. It's my first time in Hokkaido, and I'm thrilled to speak in this beautiful city.

Today's theme is an open-source framework called **Uzumibi**. It's a framework for developing applications on edge and serverless platforms using Ruby. "Uzumibi" means "buried fire" or embers under ashes, named out of admiration for a certain famous framework.

The key features of Uzumibi are: 
* It has a generator and supports multiple platforms.
* It uses an easy-to-remember, Sinatra-like DSL.
* It supports platform integration features—like Durable Objects and Queues—on Cloudflare.
* And above all, it is **extremely lightweight**.

Let's see it in action. You can install Uzumibi using the `cargo` command, then generate a Cloudflare template via `uzumibi new`. The important file generated is `app.rb`. If you open it, any Rubyist can guess what it does. I'll modify it slightly to access a Key-Value Store (KVS). Just like that, this code can be deployed immediately.

Please look at the file size. The artifact generated contains a WebAssembly file that is 1.5MB before compression, and **only about 500KB after compression**. This easily fits well within the free plan limits of Cloudflare Workers. And this isn't just a mockup; if you actually access it, you can see it connects to the KVS exactly as written in Ruby.

Uzumibi proves you can comfortably develop edge applications in Ruby. While this example uses Cloudflare Workers, you can write similar code and run it exactly the same way on serverless environments like Google Cloud Run. Isn't this incredibly convenient?

---

## The Magic Behind It: mrubyEdge
You might find this strange. `ruby.wasm` allows you to write applications in Ruby, but it usually generates much larger artifacts—around 10MB if it includes production code. So how is this magic possible? It's because Uzumibi is based on an entirely different mruby runtime I created, called **mrubyEdge**.

Before you can understand Uzumibi's power, I need to explain mrubyEdge. It's a custom mruby runtime I've been developing since 2014, written entirely in Rust and designed from the ground up to be compiled into WebAssembly. Because it generates highly portable Wasm, it runs everywhere, including the edge.

My motivation was simple: generating small artifacts was too difficult with the CRuby-based `ruby.wasm`. Compiling CRuby to Wasm right now generates a binary of about 10MB before compression. Even gzipped, it's around 5MB.

In contrast, lightweight implementations like `mruby` and `mruby/c` inherently follow a philosophy of excluding unnecessary code. Basing my work on mruby seemed like a great approach to automatically build only the necessary features. 

However, Yukihiro Matsumoto's original mruby relies on C functions like `setjmp` and `longjmp` for code jumps. Since WebAssembly's core instructions lack a `goto` equivalent, compiling these to Wasm requires hacks. Other implementations like PicoRuby rely on Emscripten for this, meaning the Wasm binary must include Emscripten's bulky runtime, which also forcefully imports and exports several functions behind the scenes.

Given this, I decided I couldn't simply rely on existing Ruby or mruby implementations, and chose to rewrite it from scratch in Rust. Rust offers distinct advantages: productivity and safety via its advanced type system, a powerful Wasm ecosystem, and memory safety. Plus, I personally wanted to implement a VM myself.

---

## Implementation Journey and Struggles
By 2024, a prototype of mrubyEdge was complete. Two years ago, I gave a presentation on it at RubyKaigi in Okinawa. However, it was strictly a Proof of Concept, only capable of running a Fibonacci function for a demo.

At the beginning of 2025, I resumed development. I deeply studied implementations like `mruby/c` and redesigned the VM. Once the VM was running, I relentlessly implemented instructions: find a Ruby sample code, confirm it with existing `mruby`, compile it to bytecode, make it run on mrubyEdge, and add it as an E2E test. Through this tedious repetition, mrubyEdge gradually matured.

Let me share a few implementation struggles from this period.

### Register Machine vs. Stack Machine
Here is an mruby instruction to calculate `1 + 2`. As you can see, it looks different from CRuby's instructions. CRuby uses a **stack machine**, pushing operands onto a stack and consuming them with an `add` instruction. mruby, however, is a **register machine**. Operands are stored in registers like R1 and R2, and the `add` instruction specifies those registers and returns the result to one of them.

A register machine requires specific data structures: a container for registers, a reference to the instruction sequence (`IREP`), a program counter, and a call stack (`callinfo`). 

For memory efficiency and access speed, registers are not hash maps; they are internally implemented as **slices**. The implementation shifts the start point of the slice every time a function's stack is pushed. Conceptually, when a function is called, the register offset moves forward, and when it returns, it shifts back.

### Leveraging Rust Traits
We also reused Rust's convenient traits wherever possible. For example, a struct implementing the `Hash` trait can be used as a hash key, and `PartialEq` allows comparisons.

We map Ruby-level Hashes directly to Rust's standard `HashMap`. For the key in the Rust `HashMap`, we insert an enum called `ValueHasher`, which implements the `Hash` trait. The actual Ruby objects—`key` and `value`—are stored as a tuple on the value side. Because `ValueHasher` simply wraps booleans or integers that natively implement the `Hash` trait in Rust, it acts as a perfect hash key. As a result, internal functions like `HashSet` become incredibly clean and simple.

### Closures and Deferred Capture
Next: closures and upvalues. To capture the surrounding environment, we created an `Env` struct in mrubyEdge, which has an `Option` type to hold the parent `Env` and a vector for captured variables.

Interestingly, the array meant to capture the environment **doesn't actually copy anything at the moment the lambda is created**. Why? Because a closure's lifetime is usually shorter than the outer method's. As long as the outer method's environment is alive, the internal lambda is fine, so no capture is needed. But if you return a lambda as a value and use it elsewhere, the method's environment is destroyed, causing a problem.

To solve this, mrubyEdge delays the process: it copies the register contents into the capture at the exact moment the frame ends. This avoids unnecessary copies but secures the data when needed. Since each `Env` holds a reference to its parent, getting an upvalue is just tracing through them.

### Singleton Classes and the Inheritance Tree
Let's look at the inheritance tree. The `RClass` struct holds a method table by attaching an un-inlineable module inside it. In Ruby, singleton classes (eigenclasses) are highly important. 

If class `Bar` inherits from `Foo`, what happens when you create an instance of `Bar`? Since `Bar` itself is a class instance, its inheritance tree is slightly unique: `Bar`'s singleton class, then `Foo`'s singleton, `Object`'s singleton, `BasicObject`'s singleton, and finally the `Class` class. To accurately reproduce this complex chain in Rust, we modified the initialization logic specifically for class instances to recursively call the singleton class generation method on the parent class.

### Exceptions and Break
Finally, exceptions. When compiled into mruby bytecode, an exception is raised specifically at the `send` instruction. Execution then jumps to `rescue`. The VM extracts the active exception into a register, checks for a match, and either executes the rescue clause or re-raises the error, eventually hitting the `ensure` block.

When an exception occurs, the VM's state updates to indicate "an exception is active." While in this state, the VM skips regular instructions and traverses upwards through the blocks until the exception is handled.

The implementation of `break` is quite similar. In mrubyEdge, `break` is implemented as a type of exception because it behaves identically, unwinding the call stack and tracing blocks upwards until it finds the invocation point. 

---

## The Breakthrough: AI and the Edge
By mid-November 2025, basic instructions were supported. About 84% of mruby 3.4's instructions were implemented, along with foundational mechanisms to define classes and methods.

For the finishing touch, I needed a standard library. Since the foundation was solid, I had AI write all the basic standard libraries. This experiment was highly successful. Your favorites like `String`, `Array`, `Hash`, and `Enumerable` were now working. 

By early February, my custom Ruby was running properly, and I wanted to build a real application. I originally named the project "mrubyEdge" because I intended to run it on WasmEdge. I honestly didn't expect it to run on serverless edge platforms. But since it was running everywhere, I decided to test it on Cloudflare Workers. Since Cloudflare Workers runs JavaScript, it can naturally execute Wasm.

I implemented the necessary functions, built a bridge for the Wasm interface, and aligned the Ruby code. After just a few days of trial and error in December, I had mruby running on Cloudflare Workers. 

Furthermore, when compiled, this mruby code fit into **just about 400KB**. Even anticipating a size increase after fully implementing the standard library, I knew it would effortlessly stay under 1MB.

---

## Uzumibi: Building the Framework
Convinced it was viable, I began developing in earnest. I wrote spike code and added support for Fastly and other frameworks. Interestingly, it can even run on Web Workers or Service Workers—meaning you can implement an API completely self-contained within the browser.

I also integrated Cloudflare's rich services, like Durable Objects and Queues. These are introduced as an abstraction layer supporting Cloudflare Workers and Google Cloud Run. For Cloud Run, similar functions are achieved using Firestore and Cloud Pub/Sub. I'd love to continue adding support for other services, and contributions are highly welcome.

I intended to talk mainly about Uzumibi today, but I spent most of the time on my struggles with mrubyEdge. The truth is, because the mrubyEdge foundation was built so solidly, Uzumibi just worked without much fuss. I built what I wanted, and inadvertently created a framework highly useful for everyone.

A key takeaway is that my original approach was right: I wanted a portable Wasm binary with complete control over Wasm-specific features, and I wanted to keep the footprint as small as possible. By achieving this, I believe we are opening up a new horizon on the Edge. 

Uzumibi is still a newborn framework, but it has the power to transform your development workflows. Please give it a try.

---

## Future Challenges: The Async Hurdle
I have a little time left, so let's discuss future challenges: **asynchronous programming**. 

Wasm must work seamlessly with JavaScript, where I/O operations—like `fetch`, or Cloudflare Workers' Durable Objects and Queues—are fundamentally asynchronous. 

However, **Wasm cannot accept asynchronous functions as imports**. As a workaround, a tool called `Asyncify` emerged, allowing you to pseudo-pass async functions to a Wasm instance. Uzumibi uses `Asyncify` internally for Cloudflare Workers support.

But a massive downside is binary bloat—it increases size by about 1.5 times. I started this project to fix bloated binaries, so relying on `Asyncify` is unacceptable.

Furthermore, integrating with Rust's standard server libraries like Hyper and Tokio requires treating async as a first-class citizen. Currently, mrubyEdge compromises on Cloud Run by performing I/O operations on a single thread. While we can mitigate this bottleneck in Cloud Run by spinning up many single-threaded containers—a design strictly dedicated to serverless—it's not truly general-purpose. Therefore, I want to make mrubyEdge inherently async-compatible.

Looking at the current VM, it runs a simple synchronous instruction loop. But since the VM is just a state machine, it shouldn't have a bad affinity with async. A VM tailored for async programming could yield and resume at arbitrary times. I am currently exploring this implementation, and I suppose a fully async VM is my homework for next year.

---

## Conclusion
Today I introduced mrubyEdge and the Uzumibi framework. While hurdles remain, it already has quality sufficient for practical use. 

From an exclusively Ruby-centric world, it's often hard to step into serverless and edge computing. But with mrubyEdge, you can develop with high compatibility using the language you love. Please give it a try—I look forward to your feedback. Thank you very much.