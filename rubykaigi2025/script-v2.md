Okay, I'd like to begin my presentation.
My name is Kondo.
I'm a Product Engineer at SmartHR.

Today's topic is Wardite, a Wasm Gem written in pure Ruby.

Wardite is a Pure Ruby WebAssembly runtime.
You can easily run Wardite with `gem install Wardite`, and it allows you to execute existing Wasm binaries.
Also, since it's a Gem, you can use it as a library, making it possible to load and run Wasm files within your Ruby code.
So, Wardite is a Pure Ruby WebAssembly runtime.

Now, let's revisit what WebAssembly is and what a WebAssembly runtime is.

WebAssembly (Wasm) is a type of instruction set architecture in binary format.
Originally, it was intended to run in web browsers, but in recent years, it has become usable in various environments.
For example, if you compile C code like this into a Wasm format binary, you can run it in a browser.

You might think WebAssembly only runs in browsers, but it's now considered capable of running anywhere.
It's possible to run Wasm binaries using client-side command-line tools.
Furthermore, you can even embed a Wasm execution environment within your application.

The execution flow for WebAssembly generally starts with source code, which is then compiled by a Wasm-specific compiler to produce a Wasm binary.
Running this Wasm binary within a runtime is what finally allows the program to execute. That's the general process.

Therefore, a WebAssembly runtime can be described as an environment for executing pre-compiled Wasm binaries.
In this sense, even a browser can be considered a runtime. Additionally, there are dedicated implementations for running WebAssembly, such as Wasmtime and WasmEdge.
Furthermore, implementations exist that are embedded within programming languages themselves, and often, these implementations are written purely in that language. Examples include Go's WasmZero and Swift's SwiftWasm.

Wardite is written in Pure Ruby.
Because it's written in Ruby, it's an excellent tool for running WebAssembly within Ruby.
While a separate command-line tool is also provided, you can also run it directly within Ruby.

Wardite's design policy is to depend only on Ruby's standard libraries.
It also fully utilizes RBS, ensuring strong typing throughout the code.

Currently, Wardite's implementation of the WebAssembly Core Spec is mostly complete. It also implements the specification known as WASI, which makes it capable of running Ruby Wasm, at least to some extent.

Now, what is the WebAssembly Core Spec? It can be described as the set of fundamental specifications for WebAssembly.
It defines various models, including binary and text formats, instruction sets, type systems, and memory. A runtime only needs to correctly implement these specifications to be able to execute compliant Wasm binaries.
Specifications like WASI and the so-called Component Model are built on top of this Core Spec.

Next, let's talk about WASI. This stands for WebAssembly System Interface.
The WebAssembly Core Spec itself doesn't actually define interactions with the operating system.
Therefore, the API for interacting with the OS or other external systems is defined separately in the form of WASI.
There are versions P1 and P2, but since P1 is still commonly used, Wardite implements P1.

Having explained the current state of Wardite, let me talk about why I created it.
There are several reasons: First, I wanted to expand the use cases for embedding Wasm within Ruby applications.
Alternatively, I wanted a highly portable implementation. For instance, something that runs wherever Ruby runs, or even an implementation that works properly with mruby.
Additionally, as part of testing Ruby's own performance, I thought having such complex software would be beneficial.
However, honestly, it was also "Just for Fun."

There was a preceding implementation by someone named Techno Hippy (?), but it hadn't been updated in quite some time, and its support had ended, so I decided to take a fresh shot at it.

Fundamentally, I see great potential in WebAssembly, and I thought it would be great to be able to interact with that world through Ruby.
WebAssembly has several potential advantages.
One is its language-agnostic nature, which I find very interesting.
Many compiled languages like Rust, Go, and C++ support Wasm as a compilation target.
Furthermore, since C can be compiled to Wasm, languages written in C like Ruby, Python, Lua, and Perl also potentially have the possibility of running on Wasm.

Additionally, the WebAssembly Core Spec itself, while simple, seems to maintain a logical structure, which I find very intriguing.
Related to its simplicity, WebAssembly can be embedded and executed within various applications.
Since the runtime itself is relatively small, it seems feasible to implement and integrate it into different environments yourself.

For example, Go has a Wasm implementation called WasmZero written in Go itself. At the same time, Go itself can be compiled to Wasm.
Therefore, by running a Go-compiled Wasm binary within the Go-based Wasm implementation, Go achieves dynamic loading.
Since the Go language generally has difficulty using C language assets, there is demand for such safe dynamic loading mechanisms.

And as I've mentioned several times, it's correct to reconsider the browser as an environment with an embedded Wasm runtime.
So, exploring these aspects suggests a future where languages can be skillfully combined. Wasm's strong language-agnostic nature allows embedding it into various applications, and the code running on that Wasm runtime can be written in any language.

The conceptual diagram for WasmCloud, an OSS project, might illustrate this idea well.
A future where applications can be built by combining blocks like this might be possible.

(Skipping the details about Wasm here.)

While sometimes compared to the JVM, I believe the design philosophies are different.
Its value isn't just that it runs in the browser; I think it enables more interesting possibilities.

Now that I've discussed the potential of WebAssembly, let's look back at the development process of Wardite.

There were several milestones during Wardite's development.
The first milestone was porting a work called GorillaBook and getting "Hello World" to run in Wardite.
GorillaBook is a web book originally written for learning the basic implementation of WebAssembly using Rust. Since I happened to have an opportunity to study it, I tried writing it out, and that's how it started.
Since the original implementation was in Rust, I thought I could write a similar version in Ruby using RBS extensively.

My impression was that it's an excellent book, but understanding the overall design philosophy of the VM was quite challenging.
However, the book itself includes Rust reference implementations, which was extremely helpful.

The following description is quite similar to GorillaBook, but let me briefly explain the internals of Wasm.
First, you must parse the Wasm binary format.
However, the binary format is quite simple. It starts with a header, which contains the size, followed by the content of various sections. It's a simple combination of sections.
Here's a diagram illustrating it.

Once the binary is parsed, the next step is just writing the VM. The VM implementation is also fundamentally a loop: fetch an instruction, execute it, then fetch the next one. Repeating this loop is the basic VM implementation.

Conversely, while the VM is simple, interacting with the outside world, like handling output, is surprisingly difficult.
To produce output, you must implement at least the WASI function `FD_write`. So, I implemented this as well. Again, having the book made it manageable.

And so, "Hello World" worked!
"Hello World" is always a great thing, isn't it?

Next, I decided to cover the basic instructions of the Wasm Core Spec.
At this point, I had a slight desire to run Ruby Wasm.

The Wasm instruction set has a basic range and extension sets.
The Core Spec defines which instructions belong to which range. There are special extension sets for things like GC, SIMD instructions, concurrency, and others.
This time, I focused only on the basic parts.
You can refer to the Opcode Table website to see which instructions are included in the basic set.

The challenging part was the sheer number of instructions. Naturally. Even focusing on the basic part, I had to implement 192 instructions.
However, each VM instruction is small, so it felt like doing many small tasks diligently.

Wasm has four numeric types: i32, i64, f32, f64 (integers and floats).
Often, similar instructions exist for each of these types, like Add or Sub.
For these common instructions, I created a generator to produce them collectively.
Surprisingly, including conversion instructions, there were apparently about 167 such generated instructions.
I created a very simple template and used `Rake generate`.

Okay. With the basic instructions covered, I thought about running a more practical program.
I tried running a Rust program for grayscale conversion that I had created for another project.
And it didn't work.

Thus began the days of debugging.

Briefly, the grayscale program takes Base64 encoded data (like a data URL), decodes it, treats the result as a PNG image, converts the pixels to grayscale, re-encodes it as a PNG, and finally encodes it back to Base64 text.

The first issue I encountered was that the memory allocation process wasn't working correctly. The fix was just one line, but getting there involved comparing execution in the browser (running the Wasm grayscale program with breakpoints) with Wardite's execution to find discrepancies. I did some complicated things, but I don't remember the details clearly.

Memory issues were fixed, but it still didn't work.
The problem was that Rust panics are translated into the Wasm `Unreachable` instruction. `Unreachable` simply means "error if reached," which wasn't very helpful for debugging.
So, instead of letting it panic, I modified it to return the error string directly.
This revealed the error message: "Corrupted deflate stream."
Now I had an error ID. I looked at the Rust code.
"I see... but I don't understand." This part was clearly decompressing a Deflate stream, based on the function names. I wondered if I had to study the Deflate algorithm from scratch, which felt a bit daunting.
However, looking at the code, I could see that bitshift operations were heavily used. So, I decided to first verify if the bitshift and other numeric instructions were correct.

The correctness of numeric instructions like i32 operations can be verified using the official Wasm test suite.
Specifically (you can find details in the article I linked), a tool called `Wast2json` can be used to generate test cases in JSON format. You can then use Ruby to iterate through these tests, run the Wasm code in Wardite, and check if the results match the expectations.
It's quite simple, right?

I adapted this process to fit the `Test::Unit` format and ran the tests iteratively. Indeed, many issues were found, particularly around bitshift instructions, especially where overflow handling was inadequate.
After fixing these issues, all the standard test cases passed.
As a result, the grayscale program also worked correctly.
It's working correctly, right? Looks like it. Yes, I think it worked properly.

This raised the momentum to run something even more practical: Ruby Wasm.
Running Ruby Wasm requires proper WASI support in addition to the instructions.
Building Ruby Wasm without specific options requires 37 WASI functions.
I implemented these 37 functions, grouping them into a single class for easy importing.
As an example, implementing `ClockTime.get` essentially just wraps Ruby's `Time.now`. It might look a bit odd, but since it's just bridging the Wasm world and the OS world using Ruby, a lot of straightforward, almost naive code emerges.

So, the task became diligently implementing these WASI functions one by one.
My strategy was simple: repeatedly try to launch Ruby Wasm in a `loop do`. When it failed saying "function X is missing," I implemented that function.
The functions implemented were truly basic system interactions: getting ARGV, current time, random numbers, environment variables, etc.
After implementing the minimum required functions, I hit a final snag: an incorrect implementation of an `if` block. Debugging this involved using Wasm Tools to convert Wasm to Wat (text format) and staring at it until I found the issue.
It took quite a few commits to resolve this.

Finally, the Ruby Wasm version started working. Hooray!

At this stage, Ruby's core libraries (implemented in C) worked, so things like `times` ran somehow.
However, as mentioned, the file system wasn't recognized yet. This meant `require` didn't work correctly, and loading warnings appeared.
So, the next step was to make `require` work correctly. To do this, Wardite needed to recognize the file system collectively.

So, I tried implementing the file system.
Initially, I crudely tried to make `Pathname.open` work, assuming it would be called.
But that function wasn't even being called.
Why? Because I needed to correctly implement the Preopens mechanism first.

Looking at the WASI SDK's Lib C implementation, you can see (in C code, which I'll skip showing) a specific process.
To explain it in Japanese (or English now): By default, a Wasm runtime, even with WASI enabled, cannot access the host environment's file system at all for security reasons.
When launching the Wasm runtime, information about the host file systems to be shared must be passed via file descriptors (starting from FD 3) in a specific format. This mechanism is often referred to as Preopens.

In the WASI SDK, a function like `PopulatePreopens` is called early on (at startup or before the first file open). It iterates through file descriptors starting from 3, inspects them, and registers the shared file system information.
Therefore, functions like `Pathname.open` are simply not called if the relevant Preopen environment information hasn't been registered beforehand; they would return an error like EBadF.

Indeed, looking at the WASI SDK's Lib C code confirms that it iterates through Preopens.
So, I implemented the necessary functions related to Preopens. It required implementing several functions, and `ReadDir` was particularly tough, but eventually, I managed it.
About a week ago, standard Ruby started without any loading warnings.
No warnings appeared, and `Defined Gem` correctly resolved to a constant.

So, all's well that ends well. However,
In my environment, initializing all of RubyGems takes 68 seconds. This leads into the final topic: performance considerations.

First, a quick demo of the startup.
If I run it with `disable_gems`, it should start up in about 10 seconds.

(Waiting for startup)

Okay, thank you.

Finally, let's talk about performance measurement. This is still ongoing work, but I hope it's informative.
The measurement premise is primarily based on the grayscale processing benchmark, so it's heavily skewed towards numerical calculations.
Unless otherwise noted, I'm using that benchmark. The software versions are as listed. I'm using an M1 (or M3) Mac.

Let's start with improvements to block jumps. WebAssembly's jump instructions (like If, Block, Loop) are a bit unusual. Instead of instructions holding fixed offsets, the target 'End' position is calculated dynamically when the instruction is encountered.
When I profiled the very first implementation with RubyProf, a method called `FetchOpsWhileEnd` was consuming a lot of time. This method was dynamically calculating the corresponding 'End' position every time an If, Block, or Loop instruction was encountered by peeking ahead at subsequent instructions.
If this calculation happened inside functions called repeatedly, it would naturally be slow.
So, assuming (for now, without considering JIT) that the instructions aren't dynamically rewritten, I pre-calculated the 'End' positions. After parsing the instructions once, I iterate through them again, calculate the 'End' positions, and cache them.
This reduced execution time by 43% for the grayscale benchmark. This level of optimization felt necessary.

Next is instance creation, which is something I'm currently struggling with.
Profiling Wardite identified bottlenecks in methods like `RubyVM#setivar` and `Class#new_instance_pass`.
The problem is that it's creating way too many object instances, which is slow.
Wardite's internal representation for types like i32 and i64 uses a simple object structure.
Creating these repeatedly is slow.
How many? Using tracepoints on the grayscale benchmark, I found it creates about 18.8 million i32 objects.
Even if creating each object took only a tiny fraction of time (e.g., 1 microsecond), this adds up significantly.

I tried a simple experiment: memoizing frequently used integer instances. I memoized values from 0 to 64 and -1. This did result in a speedup of about 1 second in the measurement.
So, I've kept this optimization. However, ideally, immediate values (like tagged integers in Ruby) should be used for integers like i32. But this requires significant design changes, so it's marked as a ToDo.

Regarding Ruby Wasm startup time: First, parsing the binary itself is also slow, taking up this much relative time. Comparing startup with and without `disable_gems` shows a large difference. Why? Mainly because the WASI function calls invoked during RubyGems initialization are slow. If we extract just the time spent in WASI calls, it looks like this (please note there's measurement overhead here; it's just the rough time inside the WASI implementations).

Does YJIT help? Yes, it's extremely effective. All the benchmarks shown were run with YJIT enabled.
How effective? On my Arm environment, compared to no YJIT: Ruby 3.3 showed this much improvement, 3.4 showed even more, and 3.5 was like this. YJIT provides a significant boost. Thank you always (to the YJIT team)!

So, YJIT can be used effectively.

Okay, I've covered a lot, and I think I've said most of what I wanted to say.
To conclude, while summarizing, let me mention one more thing. There's a next-generation Wasm format called the Component Model.
I would like to support it eventually. That's just my intention for now, but I'm aware of it, want to do it, and would likely accept contributions if pull requests come in.
Otherwise, I plan to continue making steady improvements, focusing on performance.

Running a Wasm runtime purely in Ruby still feels quite like "out there" adventure in some ways.
But even just playing around with it might spark ideas for various interesting uses, so please give Wardite a try.

Thank you very much for listening.