# RubyKaigi 2025 Presentation Script
# "Running ruby.wasm on Pure Ruby WASM Runtime"

## Introduction (3 minutes)

Good morning/afternoon everyone! Thank you for coming to my talk today. My name is Uchio Kondo, and I'm a Product Engineer at SmartHR. I'm also a member of Fukuoka.rb and the translator of "Learning eBPF."

Today, I'm excited to share with you my journey of creating a pure Ruby implementation of a WebAssembly runtime and running ruby.wasm on it. This project, called Wardite, has been both challenging and rewarding. It's a story of how we can push the boundaries of what's possible with Ruby, and how we can make Ruby work in new and exciting environments.

## Background and Motivation (5 minutes)

Before we dive into the technical details, let me explain why I started this project. WebAssembly, or wasm, has been gaining significant attention in recent years. It's not just for browsers anymore - it's becoming a universal runtime that can run anywhere, from edge devices to cloud environments.

I was particularly interested in how we could use WebAssembly in the Ruby ecosystem. While we have ruby.wasm, which allows Ruby to run in browsers, I wanted to explore what it would take to create a pure Ruby implementation of a WebAssembly runtime. This would not only help us understand WebAssembly better but also potentially open up new possibilities for Ruby applications.

The idea came to me when I was thinking about how we could make Ruby more portable and efficient. WebAssembly's design principles - security, portability, and efficiency - align well with what we want for Ruby applications. And what better way to understand these principles than by implementing them ourselves?

## Project Overview (7 minutes)

Wardite is a pure Ruby implementation of a WebAssembly runtime. It started as a simple experiment but has grown into a more comprehensive project. The name "Wardite" comes from combining "WASM" and "Ruby" - though I admit it's not the most creative name!

The project has several key components:

1. A WebAssembly binary format parser
   - Handles the complex binary format of WebAssembly modules
   - Implements the official WebAssembly specification
   - Supports both binary and text formats

2. A virtual machine that executes wasm instructions
   - Implements the WebAssembly instruction set
   - Handles memory management and execution
   - Supports all basic numeric operations

3. WASI (WebAssembly System Interface) implementation
   - Provides system-level functionality
   - Implements file system operations
   - Handles environment variables and command-line arguments

4. Support for running ruby.wasm
   - Implements necessary WASI functions
   - Handles memory management for Ruby objects
   - Supports basic Ruby functionality

## Technical Challenges and Solutions (12 minutes)

Let me walk you through some of the interesting technical challenges we faced and how we solved them:

### 1. Block Jump Implementation

One of our first major optimizations was improving how we handle jump instructions. In WebAssembly, we have if, block, and loop instructions that need to know the position of their corresponding end. Our initial implementation was quite naive:

```ruby
# Initial implementation
def fetch_ops_while_end
  # Looked ahead in the current code to calculate end positions
  # This was called for every jump instruction
end
```

This became a significant bottleneck, as shown by our profiling:
```
73.63%  13.29%     54.539      9.845      0.000     44.694         13069318     Wardite::Runtime#eval_insn
19.493      0.024      0.000     19.469      95886/95886     Wardite::Runtime#fetch_ops_while_end
```

We improved this by pre-calculating end positions during instruction parsing. The new implementation looks like this:

```ruby
def pre_calculate_jumps
  @instructions.each_with_index do |insn, index|
    if %i(if block loop).include?(insn.opcode)
      insn.metadata[:end_position] = find_matching_end(index)
    end
  end
end
```

This optimization reduced execution time by 43% and significantly improved the performance of loops and conditional statements.

### 2. Instance Creation Optimization

Another interesting challenge was dealing with instance creation. Our initial implementation created new instances for every value:

```ruby
class I32
  def initialize(value)
    @value = value
  end
end
```

When running a grayscale processing program, we found we were creating:
```
{:I32=>18845604, :I64=>1710552, :F32=>247500}
```

That's 18.8 million I32 instances! We implemented a simple object pool for common values:

```ruby
class I32
  @@i32_object_pool = {}
  
  (0..64).each do |value|
    @@i32_object_pool[value] = I32.new(value)
  end
  value = -1 & I32::I32_MAX
  @@i32_object_pool[value] = I32.new(value)

  def self.cached_or_initialize(value)
    @@i32_object_pool[value] || I32.new(value)
  end
end
```

This optimization reduced memory usage and improved performance by about 1 second in our benchmarks.

### 3. Memory Management

Memory management was another significant challenge. WebAssembly has a linear memory model, and we needed to implement this efficiently in Ruby. Our solution involved:

```ruby
class Memory
  def initialize(initial_pages, maximum_pages)
    @pages = initial_pages
    @maximum_pages = maximum_pages
    @data = Array.new(initial_pages * PAGE_SIZE, 0)
  end

  def grow(n)
    return -1 if @pages + n > @maximum_pages
    @data.concat(Array.new(n * PAGE_SIZE, 0))
    @pages += n
    @pages - n
  end
end
```

This implementation allows for dynamic memory growth while maintaining the WebAssembly specification's requirements.

## Running ruby.wasm (8 minutes)

One of our major milestones was getting ruby.wasm to run on Wardite. This required implementing several WASI functions. Let's look at some key implementations:

### Basic WASI Functions

```ruby
def clock_time_get(id, precision, result_ptr)
  time = case id
         when 0 then Process.clock_gettime(Process::CLOCK_REALTIME)
         when 1 then Process.clock_gettime(Process::CLOCK_MONOTONIC)
         else raise "Unknown clock ID: #{id}"
         end
  store_i64(result_ptr, (time * 1_000_000_000).to_i)
  0
end
```

We found that ruby.wasm requires about 37 WASI functions to run properly. The exact number can vary depending on which gems are bundled with ruby.wasm. Here's how we check the required functions:

```bash
$ wasm-objdump -x -j Import ./ruby-wasm32-wasi/usr/local/bin/ruby
```

### Filesystem Implementation

One of the most complex parts was implementing the filesystem functionality:

```ruby
def path_open(dirfd, dirflags, path, path_len, oflags, fs_rights_base, fs_rights_inheriting, fdflags, opened_fd)
  path_str = read_string(path, path_len)
  full_path = resolve_path(dirfd, path_str)
  
  if File.exist?(full_path)
    fd = allocate_fd
    @fds[fd] = FileDescriptor.new(full_path, oflags)
    store_i32(opened_fd, fd)
    0
  else
    -1
  end
end
```

This implementation allows ruby.wasm to access the host filesystem through the WASI interface.

## Performance Considerations (7 minutes)

Performance has been a key focus throughout the project. Let's look at some of our findings:

### YJIT Impact

We've seen significant improvements with YJIT, especially in Ruby 3.4. Here's a comparison of execution times:

```
Ruby 3.3:
- Default: 12.3s
- YJIT: 8.7s (29% improvement)

Ruby 3.4:
- Default: 11.8s
- YJIT: 7.2s (39% improvement)
```

The performance gains are even more pronounced in Ruby 3.4, showing how YJIT continues to improve.

### Memory Usage

We also monitored memory usage during execution:

```
Initial memory: ~50MB
Peak memory: ~120MB
Final memory: ~80MB
```

These numbers show that while our implementation is memory-efficient, there's still room for improvement.

## Future Work and Roadmap (5 minutes)

There's still much work to be done on Wardite. Here's our roadmap:

1. Improving Core Spec coverage
   - Implementing more advanced instructions
   - Adding support for SIMD operations
   - Improving floating-point operations

2. Overall refactoring
   - Better code organization
   - Improved error handling
   - More comprehensive testing

3. Further performance optimizations
   - JIT compilation support
   - Better memory management
   - Optimized instruction dispatch

4. Enhancing WASI coverage
   - More filesystem operations
   - Network support
   - Process management

5. Adding support for the Component Model
   - Interface types
   - Resource types
   - Component composition

## Conclusion and Call to Action (3 minutes)

Creating a pure Ruby WebAssembly runtime has been an exciting journey. It's given me a deeper understanding of both WebAssembly and Ruby's internals. The project has shown that Ruby is not just a language for web applications or scripting - it's powerful enough to implement complex systems like a WebAssembly runtime.

I hope this project can serve as:
1. A learning resource for WebAssembly implementation
2. A reference for Ruby performance optimization
3. A foundation for future Ruby-WebAssembly integration

If you're interested in contributing to Wardite or learning more about WebAssembly runtimes, I'd love to hear from you. The project is open source, and we welcome contributions of all kinds - from code improvements to documentation to testing.

You can find the project on GitHub at [github.com/udzura/wardite](https://github.com/udzura/wardite). Feel free to star the repository, open issues, or submit pull requests.

Thank you for your attention! I'm happy to take any questions you might have.

[End of presentation] 