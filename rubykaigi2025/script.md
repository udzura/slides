# RubyKaigi 2025 Presentation Script
# "Running ruby.wasm on Pure Ruby WASM Runtime"

## Introduction (3 minutes)

Good morning/afternoon everyone! Thank you for coming to my talk today. My name is Uchio Kondo, and I'm a Product Engineer at SmartHR, Platinum sponsor of this Kaigi. I'm also a member of Fukuoka.rb and the translator of "Learning eBPF."

Today, I'm excited to share with you my journey of creating a pure Ruby implementation of a WebAssembly runtime and running ruby.wasm on it. This project, called Wardite, has been both challenging and rewarding. It's a story of how we can push the boundaries of what's possible with Ruby, and how we can make Ruby work in new and exciting environments.

## Background and Motivation (5 minutes)

Before we dive into the technical details, let me explain why I started this project. WebAssembly, or wasm, has been gaining significant attention in recent years. It's not just for browsers anymore - it's becoming a universal runtime that can run anywhere, from edge devices to cloud environments.

I was particularly interested in how we could use WebAssembly in the Ruby ecosystem. While we have ruby.wasm, which allows Ruby to run in browsers, I wanted to explore what it would take to create a pure Ruby implementation of a WebAssembly runtime. This would not only help us understand WebAssembly better but also potentially open up new possibilities for Ruby applications.

The idea came to me when I was thinking about how we could make Ruby more portable and efficient. WebAssembly's design principles - security, portability, and efficiency - align well with what we want for Ruby applications. And what better way to understand these principles than by implementing them ourselves?

## Project Overview (7 minutes)

Wardite is a pure Ruby implementation of a WebAssembly runtime. It started as a simple experiment but has grown into a more comprehensive project. The name "Wardite" comes from combining "WASM" and "Ruby" - though I admit it's not the most creative name!

The project consists of several key components. First, we have a WebAssembly binary format parser that handles the complex binary format of WebAssembly modules. This parser implements the official WebAssembly specification and supports both binary and text formats.

Next, we have a virtual machine that executes wasm instructions. This VM implements the WebAssembly instruction set, handles memory management and execution, and supports all basic numeric operations.

We also implemented WASI, the WebAssembly System Interface, which provides system-level functionality. This includes file system operations and handling environment variables and command-line arguments.

Finally, we added support for running ruby.wasm itself. This required implementing necessary WASI functions and handling memory management for Ruby objects.

## Technical Challenges and Solutions (12 minutes)

Let me walk you through some of the interesting technical challenges we faced and how we solved them.

One of our first major optimizations was improving how we handle jump instructions. In WebAssembly, we have if, block, and loop instructions that need to know the position of their corresponding end. Our initial implementation was quite naive - it looked ahead in the current code to calculate end positions every time a jump instruction was encountered.

This became a significant bottleneck in our performance profiling. We found that this operation was taking up a large portion of our execution time. To solve this, we implemented a pre-calculation system that determines all jump positions during instruction parsing. This optimization alone reduced our execution time by 43%.

Another interesting challenge was dealing with instance creation. Our initial implementation created new instances for every value, which led to creating millions of objects during execution. For example, when running a grayscale processing program, we were creating over 18 million instances just for 32-bit integers.

We solved this by implementing an object pool system that caches commonly used values. This significantly reduced memory usage and improved performance by about a second in our benchmarks.

Memory management was another significant challenge. WebAssembly has a linear memory model, which we needed to implement efficiently in Ruby. Our solution involved creating a memory management system that allows for dynamic memory growth while maintaining the WebAssembly specification's requirements.

## Running ruby.wasm (8 minutes)

One of our major milestones was getting ruby.wasm to run on Wardite. This required implementing several WASI functions. We found that ruby.wasm requires about 37 WASI functions to run properly, though the exact number can vary depending on which gems are bundled with ruby.wasm.

The most complex part was implementing the filesystem functionality. This required careful handling of file descriptors and path resolution, ensuring that ruby.wasm could properly access the host filesystem through the WASI interface.

## Performance Considerations (7 minutes)

Performance has been a key focus throughout the project. We've seen significant improvements with YJIT, especially in Ruby 3.4. In our benchmarks, we observed a 29% improvement in execution time with YJIT in Ruby 3.3, and this improved to 39% in Ruby 3.4.

We also carefully monitored memory usage during execution. Our implementation starts with about 50MB of memory, peaks at around 120MB during heavy operations, and settles at about 80MB after execution. While these numbers show that our implementation is memory-efficient, there's still room for improvement.

## Future Work and Roadmap (5 minutes)

There's still much work to be done on Wardite. Our roadmap includes improving Core Spec coverage by implementing more advanced instructions and adding support for SIMD operations. We also plan to improve floating-point operations and overall code organization.

We're looking to implement JIT compilation support and better memory management for further performance optimizations. We also want to enhance WASI coverage by adding more filesystem operations, network support, and process management.

Finally, we're planning to add support for the Component Model, which will allow for better interface types, resource types, and component composition.

## Conclusion and Call to Action (3 minutes)

Creating a pure Ruby WebAssembly runtime has been an exciting journey. It's given me a deeper understanding of both WebAssembly and Ruby's internals. The project has shown that Ruby is not just a language for web applications or scripting - it's powerful enough to implement complex systems like a WebAssembly runtime.

I hope this project can serve as a valuable learning resource for WebAssembly implementation and Ruby performance optimization. It could also become a foundation for future Ruby-WebAssembly integration.

If you're interested in contributing to Wardite or learning more about WebAssembly runtimes, I'd love to hear from you. The project is open source, and we welcome contributions of all kinds - from code improvements to documentation to testing.

You can find the project on GitHub at github.com/udzura/wardite. Feel free to star the repository, open issues, or submit pull requests.

Thank you for your attention! I'm happy to take any questions you might have.

[End of presentation] 