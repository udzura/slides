Here is the translated transcript, refined for clear, spoken English at a CEFR B2/C1 level, making it ideal for an oral presentation while preserving all the original information.

***

## Introduction & Welcome

I would like to talk about my product. I'm Kondo, a product engineer at SmartHR. SmartHR is a startup providing Japan's largest HR SaaS, and we are also a Platinum Sponsor of RubyKaigi 2026. I traveled here to Hakodate today from Fukuoka, Kyushu, which is on the almost exact opposite side of Japan. It is my first time landing in Hokkaido. Welcome to Hakodate, everyone. I am truly happy to give a talk in such a beautiful city.

Since I did a little research on the city of Hakodate, I’d like to talk about that first. Hakodate is a city with a very deep history. At the end of the Edo period, the Boshin War took place, which was the last civil war in Japanese history. The final and main stage for this conflict was Goryokaku, right here in Hakodate. Goryokaku Park is beautiful, but it might also be a good place to reflect on peace in Japan.

Hakodate is also a literary city. Today, I'll introduce one writer: Takuboku Ishikawa. He is a famous young poet from the Meiji era who represents Japan; almost everyone living in Japan knows him. He actually lived in Hakodate for a while. Though he moved all over the country throughout his life, it's said that the city he loved the most was Hakodate. There is a bronze statue of him and his grave here. I really like Takuboku Ishikawa, so going a bit off-topic today, I'd like to quote one of his *tanka* poems. It's said this poem was inspired by Omorihama beach in Hakodate.

> *"On the white sand of the beach of a small island in the Eastern Sea, I, bathed in tears, play with a crab."*

I resonate with this poem in two ways. First, this poem is said to depict the agony of creation. It reminds me of how I suffered when I was young, unable to write programs the way I wanted. Second, I am literally crying right now while playing with a crab *(Rust's mascot)*. The product I'm introducing today is written in Rust, you see.

---

## Introducing Uzumibi

Returning to our main topic, let me introduce the theme for today: an open-source framework called **Uzumibi**. 

Uzumibi is a framework for developing applications on edge and serverless platforms using Ruby. "Uzumibi" means "buried fire" or embers, and I named it out of admiration for a certain famous framework.

The key features of Uzumibi are:
* It has a **generator** and supports multiple platforms.
* It has an easy-to-remember, **Sinatra-like DSL**.
* It supports **platform integration features**, such as Durable Objects and Queues, if you are using Cloudflare.
* Above all, it is **extremely lightweight**.

So, let's see it in action. You can easily install it using the `cargo` command. Then, you can create a Cloudflare template via the `uzumibi` command. Typing `uzumibi new` generates some code, but the important one is the `app.rb` file. If you open this file, any Rubyist can probably guess what it means. I'll modify this a bit to access a Key-Value Store (KVS). And this code can be deployed immediately, just like this.

Please look at the capacity. The artifact generated from this code contains a WebAssembly file that is 1.5MB before compression, and **only about 500KB after compression**. This size easily fits within the free plan limits of Cloudflare Workers. And this code isn't just for show; if you actually access it, you can see that it accesses the KVS exactly as written in the Ruby code.

As you can see, Uzumibi proves that you can comfortably develop Edge applications in Ruby. This example uses Cloudflare Workers. But you can write similar code and run it the exact same way on serverless environments like Google Cloud Run. Don't you think this is incredibly convenient?

---

## The Magic Behind It: mrubyEdge

At the same time, you might find this strange. `ruby.wasm` allows you to write applications in Ruby, but it should generate much larger artifacts. Probably over 5MB, and if it includes production code, it is expected to be 8 to 10MB. 

How is this magic possible? It's because Uzumibi is based on an entirely different mruby runtime I created, called **mrubyEdge**.

Before you can understand the power of Uzumibi, I need to talk about the recent progress of mrubyEdge. It is a custom mruby runtime I've been developing since 2014. It is written entirely in Rust and is designed from the ground up to be compiled to WebAssembly. Because it can create highly portable WebAssembly, it runs in many places. Therefore, it can also be used on the Edge.

The motivation for developing mrubyEdge was simple: generating small artifacts was difficult with the CRuby-based `ruby.wasm`. If you compile CRuby to Wasm right now, it generates a binary of about 10MB even before compression. You can gzip it, but it will still be around 5MB.

On the other hand, there are more lightweight implementations like `mruby` and `mruby/c`. These inherently follow a philosophy of not including unnecessary code in the runtime. Therefore, I thought that basing my work on mruby would be a good choice to automatically select and build only the necessary features.

`mruby` was also developed by Yukihiro Matsumoto, but its internal implementation uses C language functions called `setjmp` and `longjmp`. This makes the problem difficult. Actually, WebAssembly's core instructions do not have anything like a `goto` instruction. So, when compiling code that uses `setjmp` or `longjmp` to Wasm, you have to either use hacks with Emscripten or convert them into proposed exception-handling instructions.

By the way, you can also generate Wasm with PicoRuby. However, it still uses `setjmp` and `longjmp` in its compiler part, so I thought it was a bit unsuitable for what I wanted to achieve. If you depend on Emscripten, the Wasm binary will have to include Emscripten's own runtime. Also, Emscripten automatically imports and exports several functions on its own.

Against this background, I decided I couldn't simply rely on existing Ruby or mruby implementations, and chose the path of rewriting it in Rust. Of course, Rust has distinct advantages: productivity and safety due to its advanced type system, a powerful ecosystem surrounding WebAssembly, and above all, memory safety. But honestly, I also had a personal motivation to try implementing a Virtual Machine (VM) myself at least once.

---

## Implementation Journey and Struggles

Let's briefly look back at the history of mrubyEdge. By 2024, a prototype of mrubyEdge was complete. So, two years ago, I actually gave a presentation on mrubyEdge at RubyKaigi in Okinawa—which is very far from Hokkaido. However, it was strictly a Proof of Concept. It was only capable of running the features needed to execute a Fibonacci function for a demo.

At the beginning of 2025, I restarted the development. My previous approach was hitting a wall, so I deeply studied existing implementations like `mruby/c` for reference and redesigned the VM. Once the VM was running, I just kept implementing instructions. 

The process was simple: 
1. Find a Ruby sample code that would trigger a specific instruction.
2. Confirm the bytecode using the existing `mruby`.
3. Compile it and make it run on mrubyEdge.
4. Finally, add the original code as an E2E test case. 

I just repeated this steadily. Through this process, mrubyEdge gradually became more complete. I'll share a few more struggles about the implementation here.

### Register Machine vs. Stack Machine
As a basic premise, let me briefly show you an mruby instruction. This is an mruby instruction to calculate `1 + 2`. In reality, the mruby compiler might optimize this, so please treat it as just an example, but it feels a bit different from the instructions CRuby generates. 

CRuby's instructions are based on a **stack machine**, so operands 1 and 2 are pushed onto the stack in order, and the `add` instruction consumes the stack contents once. On the other hand, mruby is a **register machine**. Operands are stored in registers like R1 and R2, just like variables, and the `add` instruction specifies the registers and returns the result to the same register.

To briefly introduce the data structures needed for a register machine: we need a container to hold registers, a reference to the instruction sequence called `IREP`, a program counter, and a stack for context information of called functions, known as `callinfo`. 

Now, looking at this structure, there's something I need to explain. Registers have numbers like 1, 2, 3, and 4, but you might find it strange that they are not implemented as a hash map. For memory efficiency and access speed, registers are internally implemented as **slices**. We designed it so the start point of the slice moves every time a function stack is pushed. Also, by limiting the maximum value of the entire register array, stack overflows can be automatically detected. The pseudo-code looks like this. The structure has a member pointing to the head of the current frame. The mental image is that when a function is called, the register offset moves forward, and when it returns, it goes back.

### Reusing Rust's Ecosystem
Let me talk about a few more implementation tricks. First, we reused Rust's convenient traits wherever possible. Ruby has hash maps (Hashes) and mechanisms to evaluate equality, and Rust has similar things. For example, a struct that implements the `Hash` trait can be used as a hash key in Rust, and if it implements `PartialEq`, it can be compared.

This is an example of the actual Hash struct implementation in mrubyEdge. We map Ruby's Hash directly to Rust's standard `HashMap`. Here, we insert an enum called `ValueHasher` as the key for the Rust-level HashMap, and implement the `Hash` trait on it. Inside the HashMap, we use this `ValueHasher` as the key, and the actual Ruby object `key` and `value` are held as a tuple in the value side. Since the inside of `ValueHasher` directly stores boolean or integer values—which natively implement the Hash trait in Rust—it can easily be used as a hash key. As a result, the implementation of internal functions like `HashSet` becomes very simple.

### Closures and Upvalues
Next, I'll explain the implementation of closures and upvalues. You probably don't need an explanation of what a closure is, but it's a function that carries its surrounding environment. Since information about the surrounding environment is needed, we created a struct called `Env`. It has an Option type to hold the `Env` of the layer above it, and a vector for captured variables.

What's interesting is that this `Env` is generated from the VM's state exactly when the lambda or block is created. The key point is that the array capturing the environment **doesn't copy anything at this stage**. Why? Because while this kind of Ruby code generates a closure, the lifetime of this closure is shorter than the outer method. Therefore, as long as the outer method's environment is alive, this internal lambda is also alive. In such cases, we can guarantee the upper environment is alive, so there's no need to capture it. 

However, if you create a lambda inside a method, return it as a value, and use it elsewhere, it becomes a problem. The environment from when the method was called should be destroyed when the method ends. It seems some implementations don't support this properly, but in mrubyEdge, we added an implementation that copies the register contents to the capture at the exact moment the frame ends. This avoids unnecessary copies but secures the data when needed. Since an `Env` holds the `Env` above it, getting an upvalue is just a matter of tracing through them.

### The Inheritance Tree and Singleton Classes
Let me explain a little more. Let's talk about the inheritance tree. The `RClass` struct in mrubyEdge roughly looks like this. We hold a method table by creating a module that cannot be inlined inside the module. 

By the way, in Ruby's inheritance, the existence of singleton classes (eigenclasses) is very important. Can you visualize Ruby's inheritance tree, including singleton classes?

For example, if you have a class `Foo` and a class `Bar` that inherits from it, the inheritance tree for this class looks like this. When you create an instance of this `Bar` class, the singleton class's inheritance tree starts with `Bar`'s singleton class. Now, this `Bar` class itself is also a class instance, right? So, this class instance has its own singleton class. What does this inheritance tree look like? 

The answer is: first, `Bar`'s singleton class, then `Foo`'s singleton class, above that is `Object`'s singleton class, above that `BasicObject`'s singleton class, and finally the `Class` class appears. As you can see, the inheritance tree for class instances is slightly unique, so we had to reproduce this. 

Specifically, we implemented a `find` method in Rust. For normal cases, you can just search recursively. The function to initialize the singleton class of a certain object is here. Once a singleton class is created, the class above it is its original class, and you just follow the classes above it in order. We changed the initialization method for singleton classes only for class instances. It recursively calls the generation method of the parent class's singleton class, treating the parent class functioning as the original class as its parent. As a result, we can generate the exact inheritance tree we just saw.

### Exceptions and Break
Finally, regarding exceptions: mrubyEdge's exceptions look like this. When you compile Ruby code that simply raises an exception into mruby bytecode, a few special instructions appear. 

If you follow the bytecode, you can see that an exception is raised by the `send` instruction. If an exception occurs, it jumps to `rescue`. The VM takes the exception it holds into a register, and at `rescue`, if R2 matches R3, it stores `true`. If it's `true`, it moves and executes the rescue clause; if not, it jumps and raises the exception again. Finally, there's an `ensure` block. 

Therefore, when an exception occurs, the VM's state is updated with the information that "an exception occurred." Based on that, by combining actions like simply fetching instructions or raising it again, we can implement Ruby's exceptions. By the way, if the VM is in a state holding an exception, it skips loops and goes back to upper blocks within the VM's instruction loop.

The implementation of `break` is similar. In mrubyEdge, `break` is implemented as a type of exception. This is because when a `break` occurs, it behaves the exact same way, tracing blocks upwards. Once it finds the place where the block was called, it stops there. However, while working on the `break` implementation, I noticed the `ensure` implementation might not be completely accurate yet, so that's a future task.

---

## Standard Library and Cloudflare Workers

Through all this repeated implementation, I was able to support the basic instructions by mid-November 2025. About 80% was implemented, and as the finishing touch, I needed a standard library. Waiting for contributors would have been fine, but since the foundation was ready, I had AI write the entire basic standard library. As a result, I managed to implement about the equivalent of `mruby/c`'s methods as a benchmark. In the future, I'd like to make it pass the `mruby` test cases themselves, but the really basic Ruby functions are working quite well.

It was early February when it worked to a satisfying degree. Since my custom Ruby was working well, I started wanting a real application. The timeline goes back and forth a bit, but I originally named it "Edge" intending to run it on WasmEdge, and I didn't actually think it would run on Serverless Edge platforms. But thinking it might actually work, I started looking into Cloudflare Workers. 

Cloudflare Workers is fundamentally an edge platform for running JavaScript, but of course, you can use Wasm inside JavaScript. So, I implemented the necessary functions, made it possible to exchange data, investigated the Wasm interface, and implemented a bridge that matched the Ruby code with the Cloudflare Workers interface. This was done at the end of December last year, and I was able to run mruby on Cloudflare Workers after just a few days of trial and error. 

Furthermore, when I compiled and deployed this mruby code, it fit into **just about 400KB before compilation**. Of course, it had very few features at this stage, so naturally it was small, but it was well below the free plan limits. I easily imagined that even if I seriously implemented the standard library and the size increased, it would still comfortably stay under 1MB. 

So, first, I enriched the Cloudflare Workers implementation. I also wrote spike code and implemented it for Fastly and other frameworks. The current implementation status looks like this. Interestingly, it can be run on Web Workers or Service Workers, meaning an API entirely self-contained in the browser is also possible. Please try that out if you have the chance. 

And speaking of Cloudflare Workers, there are rich integration services like Durable Objects and Queues. I made all of those available from Uzumibi as well. These services are introduced as an external service abstraction layer in the form of KV, Queue, and Access. Currently, this abstraction layer only supports Cloudflare Workers and Google Cloud Run. For Cloud Run, similar functions are realized using Firestore, Cloud Pub/Sub, and Identity-Aware Proxy. I want to continue supporting other services if there are corresponding ones, but since I've mostly achieved what I personally want to use, I would very much welcome contributions.

---

## Conclusion and Future Challenges

I intended to talk about Uzumibi today, but I ended up talking mostly about my struggles with mrubyEdge. Because the foundation of mrubyEdge was built so solidly, Uzumibi just worked normally. So, I just kept making what I wanted, and as a result, I think I've created a framework that is useful for everyone. 

The important thing is that my original philosophy was quite right. What I wanted to create was a portable Wasm binary where I could fully control Wasm-specific features like import and export. Also, artifacts that are too large aren't very Wasm-like, so I wanted to keep them as small as possible. By achieving these two concepts, I created a Wasm that runs in many places, and I think it is opening up a new horizon called the "Edge." I guess the important thing is to think from scratch and create the right tools.

Uzumibi is still a newborn framework, but I believe it has the power to change your workflows. Please give it a try.

### The Asynchronous Hurdle
I have a little bit of time left, so I'd like to talk about future challenges at the end. That is, we have to face **asynchronous programming**. 

Actually, Wasm and asynchronous programming are inseparable. Naturally, as a primary requirement, Wasm needs to work in tandem with JavaScript, and in JavaScript, functions related to I/O are basically all asynchronous. This is true for browsers, and also for Node.js. Naturally, Cloudflare Workers' APIs are also asynchronous. The integration features like Durable Objects and Queues are all async APIs, and basic functions like `fetch` are of course async.

However, Wasm has one tricky point: to call integration features from inside Wasm, you have to pass them as import functions. But **Wasm cannot pass async functions to imports**. Many people were troubled by this, and as a result, a tool called *Asyncify* appeared. Using this tool, you can pseudo-pass async functions to a Wasm instance. Therefore, Uzumibi's Cloudflare Workers support uses Asyncify internally. 

But a major drawback is that the binary size gets bloated. It's said to increase by about 1.5 times. I started making Uzumibi and mrubyEdge specifically because large binary sizes are a major problem, so ending up with a bloated size due to Asyncify is unacceptable.

Furthermore, the Cloud Run implementation is a native implementation, but it speeds up and simplifies things by integrating with Rust's general-purpose server libraries. However, standard Rust server libraries like Hyper and Tokio have fantastic performance but are frameworks that treat async as a first-class citizen. Therefore, mrubyEdge won't reach its best performance unless it fully supports async natively. 

Currently, there are some compromises. For example, in the current Cloud Run implementation, operations requiring I/O are performed on a single thread. This is a constraint of Tokio's specifications, and currently, the only options are to do this or communicate with a thread in charge of I/O via channels.

Hearing this, you might naturally think that this point becomes a bottleneck, but for Cloud Run, it's possible to handle it by launching many single-threaded containers in a multi-process manner without using multi-core. So, it can be called a design dedicated to serverless, but it's not a general-purpose state. Therefore, I want to make mrubyEdge itself support async.

Looking briefly at the current VM implementation, it has a very simple instruction loop. This hasn't changed since 2024. We run this loop synchronously, but I'm focusing on the fact that the VM itself is just a state machine. Somehow, this doesn't seem to have a bad affinity with async. If I were to create a VM specialized for async programming, I think it would work well if I designed the VM itself to be able to stop and resume at any arbitrary timing, but I'm currently at the stage of considering how to implement it. I really wanted to finish the async VM by now, but I guess that's homework for next year.

**To wrap up:** Today I talked about mrubyEdge and introduced Uzumibi, which utilizes it. There are still challenges, but I think it already has a quality sufficient for practical use at this stage. When you are just touching Ruby, it's hard to step into the world of serverless and edge, but using mrubyEdge allows for highly compatible development. 

Please give it a try, and I look forward to your feedback. Thank you very much.