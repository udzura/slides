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

# Wardite: A Pure Ruby Wasm Runtime

-   **Today's Topic:** Wardite - a WebAssembly runtime Gem.
-   **Key Feature:** Written entirely in **Pure Ruby**.
-   *(Name Origin: Named after the mineral Wardite - W + A)*

----

# What Can Wardite Do?

-   Execute WebAssembly (`Wasm`) binaries directly within Ruby applications.
-   **Easy Installation:** Standard Ruby Gem (`gem install Wardite`).
-   **Two Modes:**
    -   Run existing Wasm command-line tools.
    -   Use as a library: Load & interact with Wasm modules from Ruby code.

----

# Quick Refresher: What is WebAssembly (Wasm)?

-   A **binary instruction format**.
-   Think of it as a **portable compilation target** for compilers like `rustc` or `clang`.

----

# Where Does Wasm Run? (Beyond the Browser)

-   Originally designed for browsers.
-   Now designed to run **anywhere**:
    -   Servers
    -   Edge devices
    -   Embedded systems
    -   Inside other applications

----

# The Role of Wasm Runtimes

-   To execute Wasm binaries, you need a **Wasm Runtime**.
-   **Examples:**
    -   Browsers (built-in)
    -   Standalone (`Wasmtime`, `WasmEdge`)
    -   **Embedded** in language ecosystems (`WasmZero` in Go, SwiftWasm, etc.)

----

# Wardite: A Wasm Runtime *for* Ruby, *in* Ruby

-   **Niche:** Specifically designed for the Ruby ecosystem.
-   **Implementation:** Built *in* Ruby itself.

----

# Wardite: Key Features - Purity & Portability

-   **Pure Ruby:** Depends *only* on Ruby's standard libraries.
-   **Zero Dependencies:** No external C libraries or other Gems required.
-   **High Portability:** If you have Ruby, you can run Wardite.

----

# Wardite: Core Spec & WASI Support

-   **Core Spec:** Near-complete implementation of the fundamental Wasm rules (instructions, types, memory).
-   **WASI Support:** **Crucially**, implements `WASI` (WebAssembly System Interface) Preview 1.
    -   WASI defines how Wasm interacts with the outside world (filesystem, clocks, etc.).
    -   *Essential* for running complex applications.
    *   Enables running **Ruby itself compiled to Wasm**!

----

# Why Build Wardite? (Motivation)

-   **1. Expand Ruby + Wasm Integration:** Unlock Wasm's power *within* Ruby apps.
-   **2. High Portability:** Create a runtime that works wherever standard Ruby does (maybe even `mruby`!).
-   **3. Leverage Wasm's Strengths:** Bring Wasm's advantages *into* the Ruby ecosystem.

----

# Wasm Strength #1: Language Agnostic

-   Serves as a compile target for many languages (`Rust`, `Go`, `C++`).
-   **Key Point:** `C` support potentially allows C-based languages (**Ruby**, Python, etc.) to run via Wasm.

----

# Wasm Strength #2: Embeddable & Portable

-   Relatively simple core spec leads to **small, efficient runtimes**.
-   Easy to **embed securely** within diverse applications.
-   *(Perspective: The browser is just one prominent example of an embedding host)*.

----

# Wasm Strength #3: Enabling Polyglot Systems

-   Combine **language agnosticism** + **embeddability**.
-   Future potential: Build applications by combining components written in **different languages**, choosing the best tool for each job.

----

# The Big Picture: Wasm's Value

-   Wasm's value extends **far beyond just the browser**.
-   Enables **flexible** and **powerful** new ways to construct software across many environments.