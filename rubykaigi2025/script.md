Okay, I'd like to begin my presentation.

My name is Kondo.
I'm from Fukuoka, Japan and a Product Engineer at SmartHR, which is Ruby Kaigi plutinum sponsor.

Today's topic is Wardite, a WebAssembly runtime written entirely in pure Ruby.
Wardite is named after the real mineral Wardite, which starts with letters "W" and "A".

Wardite allows you to execute WebAssembly (or Wasm) binaries directly within your Ruby applications.
Because it's a standard Ruby Gem, you can simply run `gem install Wardite` and start using it.
You can also load and interact with existing Wasm modules directly from your Ruby code, using Wardite as a library.

Now, for a quick description: WebAssembly is a binary instruction format.
Think of it as a portable compilation target of compilers, such as rustc or clang.

Originally for browsers, Wasm is now designed to run anywhere – servers, edge devices, embedded systems, and yes, inside other applications.

Here's a simple WebAssembly example. This C code, as you can see, just performs addition. If we compile this code into a Wasm binary, and then write JavaScript like this in the browser...
...we can verify that the addition function, originally written in C, is now running successfully within the browser.

To execute Wasm binaries, you need a Wasm runtime.
Browsers have built-in runtimes, and there are standalone ones like Wasmtime or WasmEdge.

Here's the flow of how wasm program works:
First, prepare source code such as C, C++, Rust...
Then compile it into wasm binary,
and finally, executing wasm binary via WebAssembly runtime

Now, let's return to the topic of Wardite. It's a Wasm runtime for the Ruby ecosystem, built in Ruby.
Since it's written in Ruby, you can run WebAssembly within Ruby.

A key design principle is its purity and portability:
Wardite depends only on Ruby's standard libraries. No external C dependencies or gems.
This means if you have Ruby, you can run Wardite. Maybe even on mruby, JRuby or else... in the future.

Currently, Wardite has a near-complete implementation of the WebAssembly Core Specification.
WebAssembly Core Spec covers the fundamental instruction set, types, and memory model needed to execute compliant Wasm files.

Crucially, Wardite also implements WASI – the WebAssembly System Interface, specifically the common Preview 1 version.
The Core Wasm spec doesn't define how to interact with the outside world, like filesystems or clocks.

WASI provides that standard interface.
It allows Wardite to run more complex applications compiled to Wasm, including, excitingly, Ruby itself compiled to Wasm.

So, why I built this? There are several reasons:

First: Expand Ruby + Wasm Integration. The primary goal is to unlock the potential of WebAssembly's power within Ruby applications.

Then: High Portability. We wanted a runtime that works wherever standard Ruby works, potentially even extending to environments like mruby in the future.

And third one is: Leverage Wasm's Strengths into Ruby ecosystem. Fundamentally, WebAssembly offers compelling advantages.

But, the true reason is that I wanted to play a complicated problem with Ruby, just for fun.

In my opinion, WebAssembly holds significant potential due to several key strengths. such as:

Language-Agnostic: It serves as a compilation target for many languages like Rust, Go, and C++.
And crucially, C support potentially allows C-based languages (like Ruby or Python) to run via Wasm as well.

Also it's Embeddable & Portable: Its relatively simple core specification leads to small, efficient runtimes.
This makes Wasm easy to embed securely within diverse applications
it's helpful to view the browser itself as just one prominent example of an environment embedding a Wasm runtime.

And finally, it Enables Polyglot Systems in the future: Combining language agnosticism with embeddability allows developers
to build applications by components written in different languages,
choosing the best tool for each specific job.

The figure on WasmCloud's website does a really good job of showing this concept.

In essence, Wasm's value extends well beyond just the browser, enabling flexible and powerful new ways to construct software across many environments.

----

Now that you understand the Wardite's background, Let's dive deeper.

Let's look back at the development process of Wardite.

There were several milestones during Wardite's development. I'm going to describe them in order.

The first milestone was porting a work called GorillaBook and getting "Hello World" to run in Wardite.
GorillaBook is a web book originally written for learning the basic implementation of WebAssembly using Rust.
It is called "Gorilla Book" after the author's penname
Since I happened to have an opportunity to study it, I tried writing it out, aiming to port it into Ruby, and that's how it started.

In my impression it's an excellent book, but understanding the overall design philosophy of the VM was quite challenging.
However, the book itself includes Rust reference implementations, which was extremely helpful.

Let me briefly explain the internals of Wasm.
First, you must parse the Wasm binary format.
However, the binary format is quite simple. Here's a diagram illustrating it.

It starts with a header, which contains the type and size, followed by the content of various sections. It's a simple combination of sections.

Once the binary is parsed, the next step is just running the VM. The VM implementation is also fundamentally a loop:
fetch the current frame and an instruction, execute it, then fetch the next one.
Repeating this loop is the basic VM implementation.
This snippet is almost a real Wardite code.

Conversely, while the VM is simple, interacting with the outside world, like handling output, is a bit more difficult.
To produce output, you must implement at least the WASI function `FD_write`. So, I implemented this as well, having the book made it manageable.

Afrer all of the coding, "Hello World" worked!
"Hello World" is always a great thing, isn't it?

Next, I decided to cover the basic instructions of the Wasm Core Spec.
At this point, I had a slight desire to run Ruby Wasm.

The Wasm instruction set has a basic range and extension sets.
The Core Spec defines which instructions belong to which range. There are special extension sets for things like GC, SIMD instructions, concurrency, and others.
This time, I focused only on the basic parts.

You can refer to the Opcode Table website to see which instructions are included in the basic set.

The challenging part was the sheer number of instructions. Naturally.
Even focusing on the basic part, I had to implement 192 instructions.
However, each VM instruction is relatively small, so it felt like doing many small tasks diligently.

By the way Wasm has four numeric types: integer32, integer64, float32, float64.
Often, similar instructions exist for each of these types, like Add or Sub.
For these common instructions, I created a generator to produce them collectively.
Surprisingly, there were apparently about 167 such generated instructions.

I created a very simple template like this.
And here's the generated code.

Okay. With the basic instructions covered, I thought about running a more practical program. Named grayscale journey.
I tried running a Rust program for grayscale conversion
that I had created for another project.

And... it didn't work.

Thus began the days of debugging.

Briefly, the grayscale program takes Base64 encoded data, like a data URL, decodes it, treats the result as a PNG image, converts the pixels to grayscale, re-encodes it as a PNG, and finally encodes it back to Base64 text.

The first issue I encountered was that
the memory allocation process wasn't working correctly.
The fix was just one line, but it took some hard efforts.

Memory issues were fixed, but it still didn't work.
The problem was that Rust panics are translated into the Wasm `Unreachable` instruction.
`Unreachable` simply means "make error if reached," which wasn't very helpful for debugging.
So, instead of letting it panic, I modified it to return the error string directly.
This revealed the error message: "Corrupted deflate stream."
Now I had an error ID. I looked at the Rust code.

"I see... I'm not sure."

This part was clearly decompressing a Deflate stream, based on the function names.
I wondered if I had to study the Deflate algorithm from scratch, which felt a bit daunting.

However, looking at the code, I could see that
bitshift operations were heavily used.
So, I decided to first verify if the bitshift and other numeric instructions were correct.

The correctness of numeric instructions like i32 operations can be verified using the official Wasm test suite.

The official WebAssembly test suite is provided in a format called Wast.
Using a command called `wast2json`, you can generate JSON files describing the test cases,
along with the corresponding Wasm binaries needed for testing, directly from these Wast files.
Each test case specification in the JSON includes input values
and either the expected output value or the expected error that should occur.
Testing then simply involves executing the Wasm binaries according to these JSON specifications.

I found examples where this process was automated using Python. For us, doing this with Ruby is straightforward.

When I first ran the test cases related to i32 operations, several tests failed,
including bitshift instructions, as somewhat expected.
After fixing all of those failures, I was able to get the grayscale example program to run successfully to completion.

It's working correctly, right? Looks like the examples.

This raised the momentum to run something even more practical:
Ruby dot Wasm.

Running Ruby dot Wasm requires proper WASI support in addition to the instructions.

Building Ruby dot Wasm in default options requires 37 WASI functions.

I started to implement these 37 functions,
grouping them into a single class for easy importing.

As an example, implementing `ClockTime.get` essentially just wraps Ruby's `Time.now`.
It might look a bit odd, since it's just bridging the Wasm world and the OS world using Ruby, but it is a essential process.

Thus, the task became diligently implementing these WASI functions one by one.
My strategy was simple:
- Repeatedly try to launch Ruby Wasm.
- When it failed saying "function X is missing,"
- I implemented that function. and again.

The functions implemented were truly basic system interactions: getting arguments, current time, random numbers, environment variables, file descriptor operations etc.

After some of functionalities are implemented, the Ruby Wasm version started working. Booyah!

At this stage, Ruby's embedded core libraries worked, so things like `Integer#times` ran somehow.

However, even it can handle basic standerd i/o, the file system wasn't recognized yet.
This meant `require` didn't work correctly, and loading warnings appeared.

So, the next step was to make `require` work correctly.

To do this, Wardite needed to recognize the file system collectively.

So, I tried implementing the file system handling functions.
Initially, I crudely tried to make `Path_open` work, assuming it would be called.
But that function wasn't even being called.
Why?

Because I needed to correctly implement the Preopens mechanism first.

First, I'm trying to describe overview of preopens in English:
- By default, a Wasm runtime, even with WASI enabled, cannot access the host environment's file system at all,
for security reasons.
- When launching the Wasm runtime, information about the host file systems to be shared
must be passed via pre-registerd file descriptors.
This mechanism is often referred to as Preopens.

Looking at the WASI SDK's Lib C implementation, you can see a specific process.

Inside the WASI SDK, before a program attempts to open a file, a function named `__wasilibc_populate_preopens` is called.
Within that function, it iterates through file descriptors starting from number 3,
attempting to retrieve information about pre-registered host filesystem entries.
If it successfully retrieves information for a file descriptor,
it registers the mapping between the guest path and the corresponding host path within the current process's state.
It continues this process for the next file descriptor until it encounters error.

Actually, functions like `path_open` are implemented such that
if no relevant preopen information has been registered, they won't even attempt to call
the underlying internal WASI function.
This appears to be a design choice focused on safety.
For reference, see the function used internally by `path_open`
to resolve full paths based on these preopens:

So, I implemented the necessary functions related to Preopens.
After all, standard Ruby started
without any loading warnings, right?

So, all's well that ends well. However...
In my environment, initializing all of RubyGems takes 68 seconds.
This leads into the final topic: performance.

Now that we see ruby.wasm is working, let's talk about performance measurement.
This is still ongoing work, but I hope it's informative.
Here are the benchmark topics:

Additionally, the measurement premise is primarily based on the grayscale processing benchmark,
so it's heavily skewed towards numerical calculations.
Unless otherwise noted, I'm using grayscale benchmark. The software versions are as listed. I'm using an M3 Mac.

Let's start with improvements to block jumps. WebAssembly's jump instructions (like If, Block, Loop) are a bit unusual. Instead of instructions holding fixed offsets, the target 'End' position is calculated dynamically when the instruction is encountered.
This was done in a method called `fetch_ops_while_end`.
This method was dynamically calculating the corresponding 'End' position
every time an If, Block, or Loop instruction was encounteredby peeking ahead at subsequent instructions.

When I profiled the very first implementation with RubyProf,  `fetch_ops_while_end` was consuming a lot of time.
Because the calculation happened inside functions called repeatedly, it would naturally be slow.

So, assuming that the instructions aren't dynamically rewritten, I pre-calculated the 'End' positions.
After parsing the instructions once, I iterate through them again, calculate the 'End' positions, and cache them.
And this is the code.

This change reduced execution time by 43% for the grayscale benchmark. This is Wardite's first speed improvement.

Next is instance creation, which is something I'm currently struggling with.

Profiling Wardite using perf identified bottlenecks in C functions
like `rb_vm_set_ivar_id` and `rb_class_new_instance_pass_kw`.
Here's an excerpt from the perf results.

The problem is that it's creating way too many object instances, which is slow.
Wardite's internal representation for types like integer32 or integeer64 uses a simple class,
but creating these repeatedly is slow.

How many? Using tracepoints on the grayscale benchmark,

I found it creates about 18.8 million integer32 objects.
Even if creating each object took only a tiny fraction of time, this adds up significantly.

I tried a simple experiment: memoizing frequently used integer instances. I memoized values from 0 to 64 and -1 for hypothesis.

This did result in a speedup of about 1 second in the measurement.
Note that this result includes commit that eliminates some Object#tap calls.

So, I've kept this optimization. However, ideally, immediate values should be used for integers or floats. But this requires significant design changes, so it's marked as a ToDo.

There are some more TODOs:

for example, Breaking Ruby Wasm startup time:
Parsing the binary file accounts for over half of the startup time.
There might be room for optimization in the binary parsing phase, perhaps by using something like StringScanner to speed it up.

On the other hand, the impact of interactions with WASI functions appears to be relatively minimal.

Last topic: Does YJIT help?

Yes, it's extremely effective. All the benchmarks previously shown were run with YJIT enabled.
How effective? On my Arm environment, compared to no YJIT: Ruby 3.3 showed this much improvement, 3.4 showed even more. 3.4 bench resulted in roughly a 57% reduction in execution time.
YJIT provides a significant boost. Thank you always (to the YJIT team)!

To conclude the talk, I would like to present a startup demonstration.
Note I run it with `disable-gems`, then it should start up in about 10 seconds.

(Waiting for startup)

Okay, thank you.

Now I've covered a lot, and I think I've said most of what I wanted to say.
To conclude again, while summarizing, let me mention one more thing. There's a next-generation Wasm format called the Component Model.
I would like to support it eventually. That's just my intention for now, but I'm aware of it, want to do it.
Because I believe the Component Model will further enhance Wasm's language-agnostic nature, which I initially discussed in today's talk.

And I would likely accept contributions if pull requests come in.
Otherwise, I plan to continue making steady improvements, especially focusing on compatibility and performance.

Running a Wasm runtime purely in Ruby still feels quite like "bold" adventure in some ways.
I'm going bold.
But even just playing around with it might spark ideas for various interesting use cases, so please give Wardite a try.

Thank you very much for listening.

And final digression: this is a haiku about Sakura and a hangover.
It's by the founder of modern haiku-style poem, Masaoka Shiki, who was from Matsuyama. See you in drinkup!