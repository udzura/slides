----
marp: true
theme: rubykaigi2025
paginate: true
backgroundImage: url(./rubykaigi2025_bg.004.jpeg)
title: Running ruby.wasm on Pure Ruby WASM Runtime
description: On RubyKaigi 2025 Matzyama / Running ruby.wasm on Pure Ruby WASM Runtime
# header: "Running ruby.wasm on Pure Ruby WASM Runtime"
image: https://udzura.jp/slides/2025/rubykaigi/ogp.png
size: 16:9
----

<!--
_class: title
_backgroundImage: url(./rubykaigi2025_bg.002.jpeg)
-->

# Running ruby.wasm<br>On Pure Ruby WASM Runtime

## Presentation by Uchio Kondo

----

<!--
_class: hero0
_backgroundImage: url(./rubykaigi2025_bg.005.jpeg)
-->

# Hello from Matz-yama!

----
<!--
_class: profile
-->

<img class="me" width="300" src="./rk2024-me-2.png" />

# self.introduce!

- Uchio Kondo
  - from Fukuoka.rb
- Member of <img class="shr" alt="SmartHR, Inc." width="250" src="./image-25.png" />
  - Product Engineer
- Translator of "Learning eBPF"

----

<!--
_class: hero0
_backgroundImage: url(./rubykaigi2025_bg.005.jpeg)
-->

# Today's Theme: Wardite

----

<!--
_class: hero
_backgroundImage: url(./rubykaigi2025_bg.003.jpeg)
-->

# What's Wardite?

----

# Wardite?

<ul>
<li style="margin-left: -2.2em !important;">A Pure Ruby WebAssembly Runtime</li>
</ul>

----

# Wardite?

- Wardite is named<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;after the real mineral<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**WA**rdite.

![bg right](./image-wardite.png)

<address>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
photo: https://en.wikipedia.org/wiki/Wardite#/media/File:Wardite.jpg 
</address>


----

# Running Wardite

```
$ gem install wardite
$ wardite ./helloworld.wasm
Hello, world
```

----

# Using Wardite as a Gem

```ruby
require 'wardite'

instance = Wardite.new(path: './helloworld.wasm', enable_wasi: true)
ret = instance._start
#=> Output: Hello, world
p ret
#=> I32(0)
```

----

<!--
_class: hero
_backgroundImage: url(./rubykaigi2025_bg.003.jpeg)
-->

# What is WebAssembly?

----

# What is WebAssembly?

- WebAssembly is:
  - A binary instruction format
  - Originally designed for execution in web browsers
  - Nowadays used in various environments including server-side

----

# WebAssembly Runs in Browsers

- You can compile C code like this into wasm and run it

<br>
<br>
<br>
<br>
<br>

```c
int add(int a, int b) {
    return a + b;
}
```

```javascript
WebAssembly.instantiateStreaming(fetch("./out.wasm"), {}).then(
    (obj) => {
        let answer = obj.instance.exports.add(100, 200);
        console.log("debug: 100 + 200 = ", answer);
    },
);
```

----

# Result

![bg right:70% w:800](image-19.png)

----

# WebAssembly Execution Flow

- First, prepare source code (in C, C++, Rust...)
- Then compile it into wasm binary
- Finally, executing wasm binary via WebAssembly runtime

----

# WebAssembly Execution Flow

![w:1000](image-9.png)

----

<!--
_class: hero
_backgroundImage: url(./rubykaigi2025_bg.003.jpeg)
-->

# So, What is Wardite?

----

# So, What is Wardite?

- A WebAssembly Runtime written in Pure Ruby
- We can run WebAssembly within Ruby

----

# Wardite's Design Principles

- Purity:
  - Depend only on Ruby's standard and bundled libraries
  - No external C dependencies or gems
- Portability:
  - Can be run on any Ruby environment
  - Even on mruby (...future work!)

----

# Wardite's Implementation Status

- Support basic WebAssembly Core specifications
- WASI preview1 (p1)

----

# WebAssembly Core Spec is...

- A set of basic WebAssembly specifications
  - Defines WebAssembly's...
    - binary and text formats
    - instruction set
    - type system
    - memory model, etc.

----

# And what is WASI?

- = WebAssembly System Interface
- The Core Spec itself doesn't define OS interactions
  - e.g. I/O, filesystem, clock, etc.

----

# WASI picture

- WASI defines APIs to interact with the OS

<br>
<br>
<br>
<br>
<br>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;![w:800](image-10.png)

----

<!--
_class: hero
_backgroundImage: url(./rubykaigi2025_bg.003.jpeg)
-->

# Why Wardite?

----

# Wardite's Goals

- #1
  - Expand use cases for wasm language embedding in Ruby

----

# Wardite's Goals

- #2
  - Desire to make very portable implementation
  - (works where Ruby works, or works with mruby)

----

# Wardite's Goals

- #3
  - Helps with Ruby's performance testing
    - or complicated program usecase
  - Like optcarrot?

----

<!--
_class: hero
_backgroundImage: url(./rubykaigi2025_bg.003.jpeg)
-->

# But the real reason is...

----

<!--
_class: hero0
_backgroundImage: url(./rubykaigi2025_bg.005.jpeg)
-->

# Just for Fun.

----

<!--
_class: hero
_backgroundImage: url(./rubykaigi2025_bg.003.jpeg)
-->

# Bet WebAssembly's Potential!

----

# Language-Agnostic Aspects

- Many compiled languages support wasm targets
  - Rust, Go, C/C++, Swift, Scala...
  - LLVM supporting wasm
  - And Some languages are written in C.
    - Ruby, Python, Lua, Perl...

----

# Possibilities for Application Embedding

- The WebAssembly Core Spec seems to maintain simplicity
- Suitability for embedded execution in applications

----

# Browser as an Embedded Environment

- Browser execution can be better understood...
  - As "a wasm runtime embedded in the browser"

<br>
<br>
<br>
<br>
<br>
<br>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ![w:600](image-11.png)

----

# Polyglot Systems

- Language agnosticism + Embeddability
  - Write (wasm) component in any language
  - Combine them into an application in another language!

<!-- TBA: 図？ -->

----

# Conceptual Figure

<br>
<br>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ![h:300](image-4.png)

<ul class="underpre">
<li><a href="https://wasmcloud.com/">From wasmCloud official website</a></li>
</ul>

----

<!--
_class: hero
_backgroundImage: url(./rubykaigi2025_bg.003.jpeg)-->

# Wasm is Going Beyond the Browser

----

<!--
_class: hero0
_backgroundImage: url(./rubykaigi2025_bg.005.jpeg)-->

# How to Develop Wardite

----

<!--
_class: hero
_backgroundImage: url(./rubykaigi2025_bg.003.jpeg)
-->

# Past Development Milestones

----

# Wardite's Development Milestones

- Porting the Gorilla Book (Hello, World)
- Covering basic Core Spec instructions
- Running the grayscale sample program
- Starting ruby.wasm
- Making require work in ruby.wasm

----

# Port the "Implementing Wasm Runtime" Book

- Goal: Make "Hello, World" work
- Required implementation...
  - Basic VM structure and instructions
    - Local variables, global variables (+ control structures)
    - Memory allocation and deallocation
    - Function import/export sections
    - Only supporting WASI's fd_write()

----

# What is "Implementing Wasm Runtime in Rust"?

- 『[RustでWasm Runtimeを実装する](https://zenn.dev/skanehira/books/writing-wasm-runtime-in-rust)』
  -  "Gorilla Book" after the author's penname
- A book for learning basic Wasm implementation in Rust
- Got a chance to use paid leave...
- Thought "So let's write it in Ruby"
  - Rust -> Ruby with full RBS seemed like a great challenge

----

# Book Impressions

- Although wasm is relatively simple, understanding the overall VM design philosophy is quite challenging
- However, it's understandable with careful reading of the book and spec documentation
- Having a Rust reference implementation was very helpful!

----

# Binary Format

- Implemented straightforwardly following the Gorilla Book
  - Section format
    - Header and content size at the beginning
    - Simple structure with section-specific content following

----

# Binary Format Overview

<br>
<br>

![w:1000](image-12.png)

----

# Basic VM Code

```ruby
def execute!
  loop do
    cur_frame = self.call_stack.last #: Frame
    break unless cur_frame
    cur_frame.pc += 1
    insn = cur_frame.body[cur_frame.pc] #: Op
    break unless insn
    eval_insn(cur_frame, insn)
  end
end
```

<ul class="underpre">
<li>This is almost a real Wardite code!</li>
</ul>

----

# Actually, "Output" is Difficult

- A common issue for programming language creator?
- "Output" requires using OS functionality
- Had to implement WASI's `fd_write()` just for "output"
  - Following the book was sufficient. Thank goodness

----

# "Hello World" Worked

> @ 2024-10-28
> Allowing `fib()` to work, I just completed "Gorilla Book" basic course for now!
> All that's left is to thoroughly master Wasm...

![bg right w:500](image-13.png)

----

# Covering Basic Core Spec Instructions

- After Hello World worked, wanted to implement more
- Goals
  - Cover basic Core Spec instructions
  - At this point, had the desire to "make ruby.wasm work", so investigated which instructions were used

----

# wasm Instruction Set

- There are basic and extended sets
- Basic range is written in the Core Spec
- About extended sets
  - GC, atomic, reference types, simd, exception handling...
  - Extentions are... future work!

----

![bg right:49% h:550](image-14.png)

# [WebAssembly Opcodes](https://pengowray.github.io/wasm-ops/)

----

# Challenges

- Wow, there are so many... (or maybe not that many?)
- Implemented 192 instructions in total
  - Doesn't seem that many...
- Just kept working diligently

----

# Implement Numeric Operations Declaratively

- Numeric ops (a.k.a ALU) are handled through file generation
- Since there are 4 types, there're common ones
  - i32, i64, f32, f64
- Created a generator with Rake task
- Apparently, there are 167 insns automatically generated

----

# Automatic Generation Templates

<br>
<br>

```ruby
  DEFS = { #: Hash[Symbol, String]
    # ...
  
    add: <<~RUBY,
      when :${PREFIX}_add
        right, left = runtime.stack.pop, runtime.stack.pop
        if !right.is_a?(${CLASS}) || !left.is_a?(${CLASS})
          raise EvalError, "maybe empty or invalid stack"
        end
        runtime.stack.push(${CLASS}(left.value + right.value))
    RUBY
    # ...
```

----

# Generated Codes

<br>
<br>

```ruby
module Wardite
  module Evaluator
    # @rbs ...
    def self.i32_eval_insn(runtime, frame, insn)
      case insn.code
      # ...
      when :i32_add
        right, left = runtime.stack.pop, runtime.stack.pop
        if !right.is_a?(I32) || !left.is_a?(I32)
          raise EvalError, "maybe empty or invalid stack"
        end
        runtime.stack.push(I32(left.value + right.value))

      when :i32_sub
      # ...
```

----

# Running Sample Programs

- With instructions implemented, moved to practical testing
- Tried running a grayscale processing program made in Rust from another project

----

# It Didn't Work...

![alt text](image-17.png)

----

<!--
_class: hero
_backgroundImage: url(./rubykaigi2025_bg.003.jpeg)
-->

# Let's start debugging

----

# Overview of the Grayscale Program

<br>

![w:950](image-15.png)

----

# Fixing Memory Allocation (memory.grow)

- Found memory allocation wasn't working correctly
- The fix was [just one line](https://github.com/udzura/wardite/commit/ecd64f25856c99c12a644efac4becb2573021e45), but took quite some effort
  - note: tracing wasm binary in browser debugger was efficient

----

# Fix Commit

![alt text](image-18.png)

----

# But It Still Didn't Work

- Rust's panic was converted to `unreachable`...
  - `unreachable` = a wasm instruction meaning "this point should never be reached, error if reached"
- Modified it to return error strings instead of panicking

----

# Error String

- Content:
  > `Format error decoding Png: Corrupt deflate stream. DistanceTooFarBack`
- [Looking at the Rust implementation](https://github.com/image-rs/fdeflate/blob/4610c916ae1000c9b5839059340598a7c55130e8/src/decompress.rs#L42)
- Hmm, not sure what's going on

----

![alt text](image-6.png)

----

# What It's Doing

- On decoding PNG
- Decompressing deflate compression
- Getting an error in this process

----

# Correctly Handling Deflate...?

- Looking at the inflate/deflate processing
  - it's clear that **bit shift operations** are heavily used
- Maybe one of the related insns isn't working correctly?

----

# Verifying i32 Instruction Correctness

- Let's run core spec tests
- How to run:
  - [Official wasm core spec test cases](https://github.com/WebAssembly/spec/tree/main/test/core) are available
  - Generate wasm binaries and execution scenarios from them
  - Run them with Wardite

----

# TBA:

- スクリプトに合わせて書き直すこと

----

```ruby
testcase = JSON.load_file("spec/i32.json", symbolize_names: true)
testcase[:commands].each do |command|
  case command[:type]
  when "module"
    command => {filename:}
    current = filename
  when "assert_return"
    command => {line:, action:, expected:}
    action => {type:, field:, args:}
    args_ = args.map{|v| parse_value(v) } 
    expected_ = expected.map{|v| parse_result(v) }
    ret = Wardite::new(path: "spec/" + current).runtime.call(field, args_)
    if ret != expected_[0]
      warn "test failed! expect: #{expected_} got: #{ret}"
    end
  end
end
```

----

# Then Fix One by One

- Indeed, bit shift instructions were failing, so fixed those
- Normal cases now pass (omitted some exeption tests)

<br>
<br>
<br>
<br>
<br>

```
$ bundle exec ruby spec/runner.rb
...
Finished in 0.272498 seconds.
-------------------------------------------------------------------------------------------
442 tests, 368 assertions, 0 failures, 0 errors, 0 pendings, 83 omissions, 0 notifications
100% passed
-------------------------------------------------------------------------------------------
1622.03 tests/s, 1350.47 assertions/s
```

----

# Grayscale Worked!

&nbsp;
&nbsp;

![w:500](image-1.png)

<ul class="underpre">
<li>Grayscale execution result looks OK</li>
</ul>

----

# Want to Run Something More (?) Practical

- Finally, the challenge of running ruby.wasm

----

<!--
_class: hero
_backgroundImage: url(./rubykaigi2025_bg.003.jpeg)
-->

# Running ruby.wasm

----

# Running ruby.wasm

- Make it work by passing ruby.wasm to `wardite` command
- Besides instruction coverage, what else is needed?
  - WASI support is needed for ruby.wasm to work

----

# What WASI Functions Does ruby.wasm Need?

- Can be checked with this command:

```
$ wasm-objdump -x -j Import ./ruby-wasm32-wasi/usr/local/bin/ruby
```

<ul class="underpre2">
<li>This time, 37 functions are needed. </li>
<li>※ Depending on bundled gems or build env</li>
</ul>

----

```
Import[37]:
 - func[0] sig=1 <__imported_wasi_snapshot_preview1_args_get> <- wasi_snapshot_preview1.args_get
 - func[1] sig=1 <__imported_wasi_snapshot_preview1_args_sizes_get> <- wasi_snapshot_preview1.args_sizes_get
 - func[2] sig=1 <__imported_wasi_snapshot_preview1_environ_get> <- wasi_snapshot_preview1.environ_get
 - func[3] sig=1 <__imported_wasi_snapshot_preview1_environ_sizes_get> <- wasi_snapshot_preview1.environ_sizes_get
 - func[4] sig=1 <__imported_wasi_snapshot_preview1_clock_res_get> <- wasi_snapshot_preview1.clock_res_get
 - func[5] sig=37 <__imported_wasi_snapshot_preview1_clock_time_get> <- wasi_snapshot_preview1.clock_time_get
 - func[6] sig=38 <__imported_wasi_snapshot_preview1_fd_advise> <- wasi_snapshot_preview1.fd_advise
 - func[7] sig=2 <__imported_wasi_snapshot_preview1_fd_close> <- wasi_snapshot_preview1.fd_close
 - func[8] sig=2 <__imported_wasi_snapshot_preview1_fd_datasync> <- wasi_snapshot_preview1.fd_datasync
 - func[9] sig=1 <__imported_wasi_snapshot_preview1_fd_fdstat_get> <- wasi_snapshot_preview1.fd_fdstat_get
 - func[10] sig=1 <__imported_wasi_snapshot_preview1_fd_fdstat_set_flags> <- wasi_snapshot_preview1.fd_fdstat_set_flags
 - func[11] sig=1 <__imported_wasi_snapshot_preview1_fd_filestat_get> <- wasi_snapshot_preview1.fd_filestat_get
 - func[12] sig=26 <__imported_wasi_snapshot_preview1_fd_filestat_set_size> <- wasi_snapshot_preview1.fd_filestat_set_size
 - func[13] sig=27 <__imported_wasi_snapshot_preview1_fd_pread> <- wasi_snapshot_preview1.fd_pread
 - func[14] sig=1 <__imported_wasi_snapshot_preview1_fd_prestat_get> <- wasi_snapshot_preview1.fd_prestat_get
 - func[15] sig=0 <__imported_wasi_snapshot_preview1_fd_prestat_dir_name> <- wasi_snapshot_preview1.fd_prestat_dir_name
 - func[16] sig=27 <__imported_wasi_snapshot_preview1_fd_pwrite> <- wasi_snapshot_preview1.fd_pwrite
 - func[17] sig=3 <__imported_wasi_snapshot_preview1_fd_read> <- wasi_snapshot_preview1.fd_read
 - func[18] sig=27 <__imported_wasi_snapshot_preview1_fd_readdir> <- wasi_snapshot_preview1.fd_readdir
 - func[19] sig=1 <__imported_wasi_snapshot_preview1_fd_renumber> <- wasi_snapshot_preview1.fd_renumber
 - func[20] sig=45 <__imported_wasi_snapshot_preview1_fd_seek> <- wasi_snapshot_preview1.fd_seek
 - func[21] sig=2 <__imported_wasi_snapshot_preview1_fd_sync> <- wasi_snapshot_preview1.fd_sync
 - func[22] sig=1 <__imported_wasi_snapshot_preview1_fd_tell> <- wasi_snapshot_preview1.fd_tell
 - func[23] sig=3 <__imported_wasi_snapshot_preview1_fd_write> <- wasi_snapshot_preview1.fd_write
 - func[24] sig=0 <__imported_wasi_snapshot_preview1_path_create_directory> <- wasi_snapshot_preview1.path_create_directory
 - func[25] sig=5 <__imported_wasi_snapshot_preview1_path_filestat_get> <- wasi_snapshot_preview1.path_filestat_get
 - func[26] sig=64 <__imported_wasi_snapshot_preview1_path_filestat_set_times> <- wasi_snapshot_preview1.path_filestat_set_times
 - func[27] sig=13 <__imported_wasi_snapshot_preview1_path_link> <- wasi_snapshot_preview1.path_link
 - func[28] sig=65 <__imported_wasi_snapshot_preview1_path_open> <- wasi_snapshot_preview1.path_open
 - func[29] sig=9 <__imported_wasi_snapshot_preview1_path_readlink> <- wasi_snapshot_preview1.path_readlink
 - func[30] sig=0 <__imported_wasi_snapshot_preview1_path_remove_directory> <- wasi_snapshot_preview1.path_remove_directory
 - func[31] sig=9 <__imported_wasi_snapshot_preview1_path_rename> <- wasi_snapshot_preview1.path_rename
 - func[32] sig=5 <__imported_wasi_snapshot_preview1_path_symlink> <- wasi_snapshot_preview1.path_symlink
 - func[33] sig=0 <__imported_wasi_snapshot_preview1_path_unlink_file> <- wasi_snapshot_preview1.path_unlink_file
 - func[34] sig=3 <__imported_wasi_snapshot_preview1_poll_oneoff> <- wasi_snapshot_preview1.poll_oneoff
 - func[35] sig=4 <__imported_wasi_snapshot_preview1_proc_exit> <- wasi_snapshot_preview1.proc_exit
 - func[36] sig=1 <__imported_wasi_snapshot_preview1_random_get> <- wasi_snapshot_preview1.random_get
```

----

# Wardite's WASI Implementation Strategy

- Implement everything in a class called
  - `Wardite::WasiSnapshotPreview1`
- This class is treated specially during import

----

```ruby
module Wardite
  class WasiSnapshotPreview1
    # @rbs store: Store
    # @rbs args: Array[wasmValue]
    # @rbs return: Object
    def clock_time_get(store, args)
      clock_id = args[0].value
      _precision = args[1].value
      timebuf64 = args[2].value
      if clock_id != 0 # - CLOCKID_REALTIME
        return Wasi::EINVAL
      end
      now = Time.now.to_i * 1_000_000
      memory = store.memories[0]
      now_packed = [now].pack("Q!")
      memory.data[timebuf64...(timebuf64+8)] = now_packed
      0
    end
  end
end
```

----

# Basic Strategy

- `loop do`
  - Try to start ruby.wasm
  - Get "`**** function not found!`" error
  - Implement that function
- `end`

----

# Examples of Functions Implemented

- Getting argv, environment variables
- Getting current time
- Getting random numbers
- prestat functions
  - As mentioned later, this was implemented incorrectly.
- read/write, other functions to get various info from `fd`

----

# ruby.wasm's `--version` Now Works!

```
$ bundle exec wardite ./ruby -- --version        
ruby 3.4.2 (2025-02-15 revision d2930f8e7a) +PRISM [wasm32-wasi]
```

----

# Release information

- Released this version as Wardite 0.6.0
- [Code at that point](https://github.com/udzura/wardite/blob/7ef48389415df9e44784d515f3e0e96aa00f2ad2/lib/wardite/wasi.rb)
- Worked with 12 WASI functions

----

# Behavior at This Point

<br>

```
$ bundle exec wardite ./ruby -- -e '5.times { p "hello: #{_1}" }'
`RubyGems' were not loaded.
`error_highlight' was not loaded.
`did_you_mean' was not loaded.
`syntax_suggest' was not loaded.
"hello: 0"
"hello: 1"
"hello: 2"
"hello: 3"
"hello: 4"
```

<ul class="underpre">
<li>Ruby's C implementation core library works</li>
</ul>

----

# Behavior at This Point

<br>

```
$ bundle exec wardite ./ruby -- -e 'puts "Hello"'        
`RubyGems' were not loaded.
`error_highlight' were not loaded.
`did_you_mean' were not loaded.
`syntax_suggest' were not loaded.
Hello
```

<ul class="underpre">
<li>Cannot recognize file system</li>
<li>Cannot require, of course - load warnings at startup</li>
</ul>

----

# Want to Make `Kernel#require` Work

- For that...
  - Need to make Wardite properly recognize the file system

----

# Initial File System Implementation

- Start with opening files
  - Tried implementing `path_open` function roughly, but
  - Doesn't work properly...
  - Not even being called?
- Why?

----

# WASI Has a Mechanism Called preopens

- Refer to wasi-sdk's libc
- [See codes in `libc-bottom-half/sources/preopens.c`](https://github.com/WebAssembly/wasi-libc/blob/e9524a0980b9bb6bb92e87a41ed1055bdda5bb86/libc-bottom-half/sources/preopens.c#L246-L276)

----

```c
    for (__wasi_fd_t fd = 3; fd != 0; ++fd) {
        __wasi_prestat_t prestat;
        __wasi_errno_t ret = __wasi_fd_prestat_get(fd, &prestat);
        if (ret == __WASI_ERRNO_BADF)
            break;
        if (ret != __WASI_ERRNO_SUCCESS)
            goto oserr;
        switch (prestat.tag) {
        case __WASI_PREOPENTYPE_DIR: {
            char *prefix = malloc(prestat.u.dir.pr_name_len + 1);
            if (prefix == NULL)
                goto software;

            ret = __wasi_fd_prestat_dir_name(fd, (uint8_t *)prefix,
                                             prestat.u.dir.pr_name_len);
            if (ret != __WASI_ERRNO_SUCCESS)
                goto oserr;
            prefix[prestat.u.dir.pr_name_len] = '\0';

            if (internal_register_preopened_fd_unlocked(fd, prefix) != 0)
                goto software;
            free(prefix);

            break;
        }
        default:
            break;
        }
    }
```

----

# File System Handling in WASI p1

- In WASI p1 compatible WASM runtimes, by default, they **cannot** access the parent environment's file system at startup.
- When starting a WASM runtime, you need to pass information about the file system you want to share with the parent environment at `fd = 3` and beyond
  - This is called "preopens"

----

# File System Sharing Initialization Process

- (Based on wasi-sdk's assumptions)
- File system registration is done 
  - in the `__wasilibc_populate_preopens(void)` function
  - Checks preopens sequentially using `fd_prestat_get()`
  - Gets names with `fd_prestat_dir_name()` and register
  - Returns `EBADF` and exits when there's no more preopens

----

# Why Couldn't We Access Files?

- Functions like `path_open()` aren't even called
  - if the preopen environment isn't registered
- See `__wasilibc_find_abspath()`:
  - [`libc-bottom-half/sources/preopens.c#L190-L213`](https://github.com/WebAssembly/wasi-libc/blob/e9524a0980b9bb6bb92e87a41ed1055bdda5bb86/libc-bottom-half/sources/preopens.c#L190-L213)

----

```c
    // by udzura: Process to find matching path from preopens
    for (size_t i = num_preopens; i > 0; --i) {
        const preopen *pre = &preopens[i - 1];
        const char *prefix = pre->prefix;
        size_t len = strlen(prefix);

        // If we haven't had a match yet, or the candidate path is longer than
        // our current best match's path, and the candidate path is a prefix of
        // the requested path, take that as the new best path.
        if ((fd == -1 || len > match_len) &&
            prefix_matches(prefix, len, path))
        {
            fd = pre->fd;
            match_len = len;
            *abs_prefix = prefix;
        }
    }
```

----

# So Fixed the prestat Functions

- Mostly correctly fixed
  - `fd_prestat_get()` and `fd_prestat_dir_name()`

----

# Normal Ruby Started Without load Warnings

- All's well that ends well

![alt text](image.png)

----

![w:500](image-7.png)

----

# ...It's Taking Quite Some Time...

- Let's talk about performance at the end

----

# Let's Demo the Startup Here

- Please let me use `--disable-gems` for speed

```
$ bundle exec wardite \
    --mapdir ./ruby-wasm32-wasi/:/ ./ruby -- \
    --disable-gems -e '5.times { p "hello: #{_1}" }'
```

----

<!--
_class: hero
_backgroundImage: url(./rubykaigi2025_bg.003.jpeg)
-->

# Dealing with Performance Measurement

----

# Dealing with Performance Measurement

- Still halfway there!
  - Haven't been doing nothing
- Let me talk about some implemented improvements
  - Block jump improvements
  - Instance creation issues
  - YJIT effects

----

# Measurement Assumptions

- Software versions etc.
  - macOS 14.0 / Apple M3 Pro
  - ruby 3.4.2 (2025-02-15 revision d2930f8e7a) +YJIT +PRISM [arm64-darwin24]
  - Wardite 0.6.1

----

<!--
_class: hero
_backgroundImage: url(./rubykaigi2025_bg.003.jpeg)
-->

# Block Jump Improvements

----

# Background: About Jump Instructions

- WebAssembly's jump instructions
  - There are if, block, and loop
  - These instructions need to know the position of their corresponding end
    - Unlike common jump instructions, they don't hold offsets

----

# When measuring the first version with ruby-prof

- Clearly, the `fetch_ops_while_end` method was at the top...

<br>
<br>

```
-------------------------------------------------------------------------------------------------------------------------------------
                     54.539      9.845      0.000     44.69413069318/13069318     Kernel#loop
  73.63%  13.29%     54.539      9.845      0.000     44.694         13069318     Wardite::Runtime#eval_insn     /.../lib/wardite.rb:420
                     19.493      0.024      0.000     19.469      95886/95886     Wardite::Runtime#fetch_ops_while_end
                     15.638      6.483      0.000      9.156  5225913/5225913     <Module::Wardite::Evaluator>#i32_eval_insn
                      3.330      1.238      0.000      2.093  1155055/1155055     Wardite::Runtime#do_branch
                      0.773      0.773      0.000      0.00013069318/13069318     Wardite::Op#namespace
                      0.757      0.757      0.000      0.00012631671/73174992     Array#[]
                      0.749      0.749      0.000      0.00015275900/53340046     BasicObject#!
                      0.542      0.542      0.000      0.00010109073/23362733     Wardite::Runtime#stack
```

----

# Initial Naive Implementation

- Every time an if/block/loop instruction was encountered:
  - Looked ahead in the current code to calculate the position of the corresponding end
- Therefore, when looping many times or calling functions containing if statements repeatedly, it had to fetch and calculate each time...

----

![alt text](image-16.png)

----

# Cache the End Position in Advance

- Decided to **cache end positions** in instruction metadata and reuse that
- Once instructions are parsed, revisit the instruction sequence, calc end positon, then cache it on-memory

----

# Reduce Time by 43%

![bg right:45% h:500](image-23.png)

- PR: [Cache end position #1](https://github.com/udzura/wardite/pull/1)
- Used grayscale program

----

<!--
_class: hero
_backgroundImage: url(./rubykaigi2025_bg.003.jpeg)
-->

# Instance Creation Issues

----

# Instance Creation Issues

- Next, measured Wardite's bottlenecks with perf...

----

```
# Children      Self  Command  Shared Object          Symbol 
# ........  ........  .......  .....................  ....................................................
#
   100.00%     0.00%  ruby     ruby                   [.] _start
            |
            ---_start
               __libc_start_main
               0xffffbd7173fc
               main
               ruby_run_node
               rb_ec_exec_node
               rb_vm_exec
               |          
               |--98.93%--vm_exec_core
               |          |          
               |          |--9.67%--0xffffbe152a58
               |          |          |          
               |          |          |--7.26%--rb_vm_set_ivar_id
               |          |          |          |          
               |          |          |          |--2.86%--rb_shape_get_iv_index
               |          |          |          |          | ....
               |          |          
               |          |--7.32%--0xffffbe1525cc
               |          |          |          
               |          |           --6.62%--rb_class_new_instance_pass_kw
               |          |                     |          
               |          |                     |--2.52%--vm_call0_cc
               |          |                     |          |          
               |          |                     |          | ....
               |          |                     |          
               |          |                     |--2.22%--rb_class_allocate_instance
               |          |                     |          |          
               |          |                     |           --2.15%--newobj_alloc
               |          |                     |                     | ....
               |          |          
               |          |--5.78%--0xffffbe14a65c
....
```

----

# Examine Perf Results

- Common occurrences were:
  - `rb_vm_set_ivar_id`
  - `rb_class_new_instance_pass_kw`
- These appear at the top even with YJIT enabled

----

# In Other Words

- Creating too many instances is slow
- Wardite's internal Value implementation looks like this

<br>
<br>
<br>
<br>
<br>

```ruby
class I32
  def initialize(value)
    @value = value
  end
end
```

----

# How Many Are Actually Being Created?

- Measured Wardite's internal Value-making functions:

<br>
<br>
<br>
<br>

```ruby
$COUNTER = {}
TracePoint.trace(:call) do |tp|
  if %i(I32 I64 F32 F64).include?(tp.method_id)
    $COUNTER[tp.method_id] ||= 0
    $COUNTER[tp.method_id] += 1
  end
end

END {
  pp $COUNTER
}
```

----

# For Example, Grayscale Processing

<br>
<br>
<br>

```
{:I32=>18845604, :I64=>1710552, :F32=>247500}
```

- In case of I32, 18.8 million instances are being created
  - w/ grayscale processing

----

# Thoughts

- Even though they're I32
  - there might be many instances of specific values?
  - For example, `-1, 0, 1, 2, 3, 4, 8, 16` ... ?
- Let's try memoization

----

```ruby
class I32
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

----

# There Was Some Effect

- Changed by about 1 second. [Commit `e5b8f3a`](https://github.com/udzura/wardite/commit/e5b8f3ada850791d2170823d8a33c73362b62ec2)
  - Also, quit to use tap on initialize... [Commit `16ef6b5`](https://github.com/udzura/wardite/commit/16ef6b5a7929f65abf961901b5af9cc591540f6e)
- Note: this result is from Ruby 3.3 with YJIT

----

# Results

![bg right:45% h:500](image-22.png)

- Good to some extent
- TODO: Try eliminating whole instance creation in value assignment...



----

<!--
_class: hero
_backgroundImage: url(./rubykaigi2025_bg.003.jpeg)
-->

# Further Tuning?

----

# Inspection: Breakdown of ruby.wasm bootstrap

- Time taken for binary parsing
- Time taken for WASI function calls

----

# Execution Overview

- Over half is laoding
- Sample:

<br>
<br>
<br>

```
$ ruby.wasm --version
```

![bg right h:500](image-24.png)

----

# BTW: WASI function calls

- Sample: `ruby.wasm -e 'puts "Hello, World"'`
- Seems to be less controlling

<br>
<br>
<br>
<br>

```
total process done: 69.89s
load_from_buffer: 6.05s
external call count: 1049
external call elapsed: 0.0611s (0.087% ... )
```

----

# YJIT Effects

- YJIT has a significant effect on Wardite's execution speed
- Just putting the results here for reference
  - All environments are aarch64
- Sample: `ruby.wasm --version`

----

# Results

![bg right:60% w:700](image-21.png)

- 15.22s -> 6.57s<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(Ruby 3.4)

<!--
# Ruby version, YJIT Off, YJIT On
# 3.3,14.98,7.09
# 3.4,15.22,6.57
# 3.5-dev,14.51,6.6
-->

----

<!--
_class: hero
_backgroundImage: url(./rubykaigi2025_bg.003.jpeg)
-->

# Conclusion

----

# Wardite's Future

- Still need more implementation
  - Improve Core Spec coverage
  - Overall refactoring
  - Performance improvements
  - Improve WASI coverage
  - Component model support ...

----

# Looking for People Interested in Wasm Runtime

- First, please try using it, even just for fun
- Thank you for your attention!

----

<!--
_class: hero1
_backgroundImage: url(./rubykaigi2025_bg.005.jpeg)
-->

# Thanks!


<!--
- 人を見ん桜は酒の肴なり
- 一枝の花おもさうや酒の酔
- 花に酔ふた頭重たし春の雨
  - の、方が情景としてはいいが、雨は降ってほしくないので
-->

<blockquote>
花に酔ふた頭重たし春の風<br />
&nbsp;<small><small>... A Haiku from Masaoka Shiki</small></small>
</blockquote>

----

![bg](./rubykaigi2025_bg.001.jpeg)
