---
marp: true
theme: rubykaigi2026
backgroundImage: url(./bg-2026.002.png)
title: "Code Social @ RubyKaigi 2026 / Ruby x Rust Table"
paginate: false
style: |
    section.hero h1 { font-size: 64pt; }
    section.hero h2 { text-align: center; }
    li { font-size: 24pt; }
---

<!-- タイトル原文: コード懇親会 @ RubyKaigi 2026 / Ruby x Rust 分科会 -->

<!--
_class: hero
_backgroundImage: url(./bg-2026.002.png)
-->

# Beginning Ruby x Rust

## Code Social @ RubyKaigi 2026 / Ruby x Rust Table

<!-- コード懇親会 @ RubyKaigi 2026 / Ruby x Rust テーブル -->
---

# Today's Agenda

- Why Rust helps — with a focus on memory safety
- Writing gems in Rust — developer experience benefits
- How to create a Rust gem with bundler
- Summary

<!-- 今日のアジェンダ -->
<!-- Rustのメリット — メモリ安全性を中心に -->
<!-- Rustでgemを書く — 開発体験のメリット -->
<!-- bundlerを使ったRust gem作成手順 -->
<!-- まとめ -->
---

<!--
_class: hero0
_backgroundImage: url(./bg-2026.003.png)
-->

# Benefits of Rust

<!-- Rustのメリット -->
---

# There are many benefits, so I will share my personal take.

<!-- 色々あるので、個人の感想だけ共有します -->
---

<!--
_class: hero0
_backgroundImage: url(./bg-2026.003.png)
-->

# Memory safety above all

<!-- とにかくメモリ安全 -->
---

# Language features that enable memory safety

- Ownership
- Borrowing
- Lifetimes
- (Memory safety is not the only benefit, of course,<br>but I am introducing it here because it is a major one.)

<!-- Rustのメモリ安全性のための文法的機能 -->
<!-- 所有権 -->
<!-- 借用 -->
<!-- ライフタイム -->
<!-- （メモリ安全性のみがメリットでもないとは思うのですが<br>大きなメリットということでこの文脈で紹介します） -->
---

# Specifically

- Rust checks **ownership** and **borrowing** at compile time.
- It prevents dangling pointers, use-after-free, and similar issues as **compile errors**.
- It achieves memory safety without GC, balancing performance and safety.
- Entire categories of memory bugs that plagued C/C++ for years can disappear.

<!-- 具体的には -->
<!-- Rustはコンパイル時に **所有権(ownership)** と **借用(borrow)** をチェック -->
<!-- ダングリングポインタ、use-after-freeなどを **コンパイルエラー** で防止 -->
<!-- GCなしでメモリ安全を実現 → パフォーマンスと安全性を両立 -->
<!-- C/C++で長年悩まされてきたメモリバグのカテゴリがまるごと消える -->
---

<!--
_class: hero0
_backgroundImage: url(./bg-2026.003.png)
-->

# The "power" of lifetimes

<!-- ライフタイムの「力」 -->
---

# What is a dangling pointer?

- A pointer that continues to reference memory that has already been freed or destroyed.
- In C, you can easily create one by returning the address of a local variable.

<!-- dangling pointerとは？ -->
<!-- すでに解放・破棄されたメモリ領域を指し続けているポインタのこと -->
<!-- Cでは関数のローカル変数のアドレスを返すだけで簡単に作れてしまう -->
---

```c
#include <stdio.h>
#include <stdlib.h>

struct Data { int value; };

struct Data *create_value()
{
    struct Data x = {42};
    return &x; // returns the address of a local variable!
}

int main()
{
    struct Data *p = create_value();
    // p already points to invalid memory (dangling pointer)
    printf("%d\n", p->value); // undefined behavior!
    return 0;
}
```

----

# Example of a dangling pointer in C

- `x` disappears from the stack when the function exits.
- The returned pointer is already invalid -> **undefined behavior**.

<!-- Cでdangling pointerになる例 -->
<!-- `x` は関数を抜けるとスタックから消える -->
<!-- 返されたポインタはもう無効 → **未定義動作** -->
---

# Run example

```bash
$ clang sample1.c -w -Oz -o sample1.out
$ ./sample1.out                        
-281521464 # ???
```

- NOTE: `-w` suppresses warnings, but the compiler does warn in normal settings.

<!-- 実行例 -->
<!-- NOTE: `-w` で警告を消しているが、実際はコンパイラが警告してくれはする -->
---

<!--
_class: hero
-->

# Rust is safe here

<!-- Rustなら大丈夫 -->
---

```rust
struct Data {
    value: i32,
}

fn create_value<'a>() -> &'a Data {
    let x = Data { value: 42 };
    &x
}
```

The compiler tells you:

```
error[E0515]: cannot return reference to local variable `x`
  --> examples/sample1.rs:17:5
   |
17 |     &x // compile error
   |     ^^ returns a reference to data owned by the current function
```

-> With lifetimes, **you cannot create a dangling pointer in the first place**.

<!-- コンパイラが教えてくれる： -->
<!-- → ライフタイムの仕組みにより、**dangling pointerはそもそも作れない** -->
---

# Extra: what is a lifetime?

- Every Rust reference `&T` is tied to a **lifetime**.
- The compiler verifies that referenced data lives longer than the reference itself.

<!-- 補足: ライフタイムとは何か -->
<!-- Rustの参照 `&T` には必ず **ライフタイム（生存期間）** が紐づく -->
<!-- コンパイラは「参照先のデータが、参照より長く生きているか」を検証する -->
---

# The previous code, again

```rust
fn create_value<'a>() -> &'a Data {
    //                   ^^^^ there is no data that can satisfy this lifetime!
    // x is only alive within this function
    let x = Data { value: 42 };
    &x // you cannot create a reference that outlives this function
}
```

<!-- さっきのコードをもう一度 -->
---

- `'a` = "the lifetime expected by the caller"
- `x` is dropped when the function exits, so it cannot satisfy `'a` -> **compile error**.
- C has no such mechanism, so it relies purely on programmer care.

<!-- `'a` = 「呼び出し元が期待する生存期間」 -->
<!-- `x` は関数を抜けると破棄される → `'a` を満たせない → **コンパイルエラー** -->
<!-- Cにはこの仕組みがないので、プログラマの注意力だけが頼り -->
---

# From the caller's perspective...

<br />

```rust
fn main() {
    let p: &Data = create_value();
    //     ^^^^^
    // p expects a valid reference until the end of main() scope
    // → lifetime 'a2 must be as long as main() scope

    println!("{}", p.value); // <- we still want to use it here!
}

fn create_value<'a>() -> &'a Data {
    let x = Data { value: 42 };
    // x is dropped here... shorter than 'a2 (= main() scope)!
    &x // compile error
}
```

<!-- 呼び出し元から見ると... -->
---

# The correct Rust approach

```rust
fn create_value() -> Data {
    let x = Data { value: 42 };
    x // return the value (move)
}

fn main() {
    let v = create_value();
    println!("{}", v.value); // 42 - safe!
}
```

<!-- Rustで正しく書くなら -->
----

- Return the value itself instead of a reference -> ownership is moved.
- The compiler optimizes memory placement appropriately.
- We will discuss moves in more detail next.
- If you need explicit heap allocation, use `Box<i32>`.

<!-- 参照ではなく値そのものを返す → 所有権がムーブされる -->
<!-- コンパイラがメモリ上の位置をいい感じにする -->
<!-- ムーブの話は次に詳しく -->
<!-- ヒープに明示的に置きたければ `Box<i32>` を使う -->
---

<!--
_class: hero0
_backgroundImage: url(./bg-2026.003.png)
-->

# The "power" of ownership

<!-- 所有権の「力」 -->
---

# What is use-after-free?

- Accessing memory again after it was released by `free()` or similar.
- The pointer variable still exists after free, so code can keep using it by mistake.
- It can lead to serious vulnerabilities like data corruption, crashes, or arbitrary code execution.
- It is frequently reported in browsers and OS kernels.

<!-- use-after-freeとは？ -->
<!-- `free()` などで解放済みのメモリに再びアクセスしてしまうこと -->
<!-- 解放後もポインタ変数自体は残っているため、コード上は普通にアクセスできてしまう -->
<!-- データ破壊、クラッシュ、任意コード実行など深刻な脆弱性につながる -->
<!-- ブラウザやOSカーネルでも頻繁に報告される -->
---

# Example of use-after-free in C

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    char *buf = (char *)malloc(64);
    snprintf(buf, 64, "Hello, RubyKaigi!");

    free(buf);

    // access freed memory (use-after-free)
    // `buf` still looks usable even after `free()`
    printf("%s\n", buf); // undefined behavior!
    return 0;
}
```

<!-- Cでuse-after-freeになる例 -->
---

# Attack verification

```bash
$ clang sample2.c -fsanitize=address -O0 -o sample2.out
$ ./sample2.out
=================================================================
==14745==ERROR: AddressSanitizer: heap-use-after-free on address 0x606000000260
    at pc 0x000101423808 bp 0x00016f092680 sp 0x00016f091e10
READ of size 2 at 0x606000000260 thread T0
    #0 0x000101423804 in printf_common(void*, char const*, char*)+0x64c(libclang_rt.asan_osx_dynamic.dylib:arm64e+0x1b804)
    #1 0x0001014245c4 in printf+0x68(libclang_rt.asan_osx_dynamic.dylib:arm64e+0x1c5c4)
    #2 0x000100d6c838 in main+0x58 (sample2.out:arm64+0x100000838)
    #3 0x000182cf9d50  (<unknown module>)

0x606000000260 is located 0 bytes inside of 64-byte region [0x606000000260,0x6060000002a0)
freed by thread T0 here:
    #0 0x000101445424 in free+0x7c (libclang_rt.asan_osx_dynamic.dylib:arm64e+0x3d424)
    #1 0x000100d6c820 in main+0x40 (sample2.out:arm64+0x100000820)
    #2 0x000182cf9d50  (<unknown module>)

previously allocated by thread T0 here:
    #0 0x000101445330 in malloc+0x78 (libclang_rt.asan_osx_dynamic.dylib:arm64e+0x3d330)
    #1 0x000100d6c800 in main+0x20 (sample2.out:arm64+0x100000800)
    #2 0x000182cf9d50  (<unknown module>) ...
```

<!-- 攻撃の検証 -->
----

# Note:

- This time, we intentionally let ASan (AddressSanitizer) detect the bug.
- ASan adds overhead; execution time is often around 2x.

<!-- 今回は、ASan（AddressSanitizer）に敢えて検出させて確認 -->
<!-- ちなみにASan有効はオーバーヘッドがあり、一般に実行時間は x2 程度になるそう -->
---

<!--
_class: hero
-->

# Rust is safe here

<!-- Rustなら大丈夫 -->
---

# Equivalent code

```rust
fn main() {
    let buf = String::from("Hello, RubyKaigi!");

    drop(buf); // explicitly free

    println!("{}", buf); // compile error！
}
```

<!-- 同等のコード -->
---

# The compiler tells you:

<br />

```
error[E0382]: borrow of moved value: `buf`
 --> examples/sample2.rs:6:20
  |
2 |     let buf = String::from("Hello, RubyKaigi!");
  |         --- move occurs because `buf` has type `String`,
  |             which does not implement the `Copy` trait
3 |
4 |     drop(buf); // explicitly free
  |          --- value moved here
5 |
6 |     println!("{}", buf); // compile error！
  |                    ^^^ value borrowed here after move
```

-> **A freed value can never be used again**. The compiler guarantees this.

<!-- コンパイラが教えてくれる： -->
<!-- → **解放済みの値は二度と使えない**。コンパイラが保証する -->
---

# Why Rust prevents use-after-free

- `drop(buf)` **moves ownership** of `buf`.
- In Rust, passing a value to a function means moving ownership.
- After a move, the original variable is no longer usable - this is a core ownership rule.

<!-- なぜuse-after-freeを防げるのか -->
<!-- `drop(buf)` は `buf` の **所有権をムーブ** している -->
<!-- Rustでは値を関数に渡す = 所有権の移動（ムーブ） -->
<!-- ムーブ後の変数はもう**使えない** — これが所有権システムの基本ルール -->
---

# What does that mean?

```rust
fn take_ownership(s: String) {
    // we do not use s here, but...
    // s is dropped in this scope
}

fn main() {
    let buf = String::from("hello");
    take_ownership(buf); // ownership moves
    // println!("{}", buf); // compile error! same reason as drop
}
```

<!-- どういうこと？ -->
---

# `drop()` is a common idiom

- `drop()` is not magical; it simply **takes a value and does nothing else**.
- The ownership system itself makes use-after-free structurally impossible.

<!-- `drop()` はよくあるイディオム -->
<!-- `drop()` は特別な関数ではなく、ただ **値を受け取って何もしない** だけとわかる -->
<!-- 所有権の仕組みそのものが、use-after-freeを構造的に不可能にしている -->
---

# Summary

- For a data type `Type`:
- Any number of immutable references (`&Type`) can exist at once (many readers).
- Only one mutable reference (`&mut T`) can exist at a time (single writer).
- You cannot create a mutable reference while immutable references exist.
- You cannot create immutable references while a mutable reference exists.

<!-- まとめ -->
<!-- あるデータ `Type` に対して: -->
<!-- 不変参照（`&Type`）は、何個でも作れる（みんなで同時に読める） -->
<!-- 可変参照（`&mut T`）は、1つしか作れない（書き込めるのは1人だけ） -->
<!-- 不変参照が残っていると可変参照は作れない -->
<!-- 可変参照が残っていると不変参照は作れない -->
---

<!--
_class: hero
-->

# Sharing one by one prevents bugs!!!

<!-- 一つ一つやることでバグを防ぐ！！！ -->
---

<!--
_class: hero0
_backgroundImage: url(./bg-2026.003.png)
-->

# Write gems with Rust?

<!-- Rustを使ってgemを書く？ -->
---

# Benefits of writing gems in Rust

- Of course, Rust is safer than C, and there are many other advantages too.

<!-- Rustでgemを書くメリット -->
<!-- 無論、 C と比べた安全性はあるが、他にも色々紹介 -->
---

# Define your types first

- **Design from types**
- You can build your architecture by writing function signatures.
- Express your domain model clearly with `struct` and `enum`.
- Freedom from C's `void *` hell.

<!-- 型を決めよう -->
<!-- **型から設計できる** -->
<!-- 関数のシグネチャを書くだけで設計の骨格ができる -->
<!-- `struct` / `enum` でドメインモデルを明確に表現 -->
<!-- Cの `void *` 地獄からの解放 -->
---

<!--
_class: hero
-->

# Feel the power of types (vibe)

<!-- 型の力（雰囲気）を感じよう -->
---

```rust
use magnus::{function, prelude::*, Error, Ruby};

// type signatures directly serve as API docs
fn fizzbuzz(n: u64) -> String {
    // strong types = strong pattern matching
    match (n % 3, n % 5) {
        (0, 0) => "FizzBuzz".to_string(),
        (0, _) => "Fizz".to_string(),
        (_, 0) => "Buzz".to_string(),
        _      => n.to_string(),
    }
}

#[magnus::init]
fn init(ruby: &Ruby) -> Result<(), Error> {
    ruby.define_global_function("fizzbuzz", function!(fizzbuzz, 1));
    Ok(())
}
```

---

# Strong editor support

- **rust-analyzer** provides excellent type inference, completion, and refactoring support.
- It shows argument and return types inline.
- It shows compile errors in real time, so you catch mistakes immediately.
- This is a development experience C extension gems never quite had.
- Great linters like clippy are also easy to integrate.

<!-- エディタの支援が強力 -->
<!-- **rust-analyzer** が型推論・補完・リファクタリングを強力サポート -->
<!-- 関数の引数の型、返り値の型をインラインで表示 -->
<!-- コンパイルエラーをリアルタイムで表示 → 書いた瞬間に間違いがわかる -->
<!-- Cのext gemでは得られなかった開発体験 -->
<!-- clippy などの優れたリンターも簡単に連携可能 -->
---

# Access Rust's ecosystem and assets

- **crates.io** has over 100,000 libraries.
- `serde` - fast multi-format serialization/deserialization.
- `rayon` - easy data parallelism.
- `tokio` - async runtime.
- You can use them by adding one line to `Cargo.toml`.
- No painful dependency build setup like in C.

<!-- Rustのライブラリ・資産を使える -->
<!-- **crates.io** に10万以上のライブラリ -->
<!-- `serde` — 高速なマルチフォーマット対応のシリアライズ/デシリアライズ -->
<!-- `rayon` — お手軽データ並列処理 -->
<!-- `tokio` — 非同期ランタイム -->
<!-- `Cargo.toml` に一行追加するだけで使える -->
<!-- Cのように依存ライブラリのビルド設定で苦しまない -->
---

# By the way...

- One of Cargo's creators is **Yehuda Katz**, who also created bundler.
- No wonder it feels so easy to use.

<!-- ちなみに... -->
<!-- 💡 実はCargoの作者の一人は **Yehuda Katz** — bundlerの作者でもある -->
<!-- そりゃ〜使いやすいよね！ -->
---

<!--
_class: hero0
_backgroundImage: url(./bg-2026.003.png)
-->

# How to create a gem with bundler

<!-- bundlerを使ったgem作成手順 -->
---

# Create a Rust gem project

<br />
<br />

```bash
$ bundle gem my_rust_gem --ext=rust
```

- Specifying `--ext=rust` generates a Rust extension template.
- Supported in bundler 2.4+.

<!-- Rust gem のプロジェクトを作る -->
<!-- `--ext=rust` を指定するだけでRust拡張のひな形ができる -->
<!-- bundler 2.4+ で対応 -->
---


```
my_rust_gem/
├── bin
│   └── ...
├── Cargo.toml
├── ext
│   └── my_rust_gem
│       ├── Cargo.toml
│       ├── extconf.rb
│       └── src
│           └── lib.rs
├── Gemfile
├── lib
│   ├── my_rust_gem
│   │   └── version.rb
│   └── my_rust_gem.rb
├── my_rust_gem.gemspec
├── Rakefile
├── README.md
├── sig
│   └── my_rust_gem.rbs
└── test
    ├── my_rust_gem_test.rb
    └── test_helper.rb

9 directories, 15 files
```

---

# Generated Rust code

```rust
// ext/my_rust_gem/src/lib.rs
use magnus::{function, prelude::*, Error, Ruby};

fn hello(subject: String) -> String {
    format!("Hello from Rust, {subject}!")
}

#[magnus::init]
fn init(ruby: &Ruby) -> Result<(), Error> {
    let module = ruby.define_module("MyRustGem")?;
    module.define_singleton_method("hello", function!(hello, 1))?;
    Ok(())
}
```

<!-- 生成されるRustコード -->
----

- The **magnus** crate is Rust bindings for Ruby's C API.
- `#[magnus::init]` defines the Ruby extension entry point.
- It provides intuitive APIs like `define_module` and `define_global_function`.

<!-- **magnus** クレート = RubyのC APIのRustバインディング -->
<!-- `#[magnus::init]` でRuby拡張のエントリポイントを定義 -->
<!-- `define_module`, `define_global_function` など直感的なAPIが用意される -->
---

# Build and use it

```bash
# Build
$ bundle install
$ bundle exec rake compile

# Try
$ bundle exec ruby -e "
    require 'my_rust_gem'
    puts MyRustGem.hello('RubyKaigi')
  "
Hello from Rust, RubyKaigi!
```

<!-- ビルドして使う -->
----

- Of course, install Rust and Cargo beforehand.
- `rake compile` builds Cargo output into `.so` / `.bundle`.
- After that, you use it just like a normal gem.

<!-- もちろん、事前にRustとCargoをインストールしてください！ -->
<!-- `rake compile` で Cargo → `.so` / `.bundle` をビルド -->
<!-- あとは普通のgemと同じように使える -->
---

# Want to try writing one now?

- Docs: https://docs.rs/magnus/latest/magnus/#examples
- Honestly, with editor completion, you can probably get pretty far quickly.

<!-- いきなり書いてみる？ -->
<!-- ドキュメント: https://docs.rs/magnus/latest/magnus/#examples -->
<!-- 多分... 補完に任せればなんとなく書けるんじゃないかなあ -->
---

<!--
_class: hero0
_backgroundImage: url(./bg-2026.003.png)
-->

# Wrapping Up

---

# Summary

- **Rust is memory-safe** - it prevents dangling pointers, use-after-free, and more **at compile time**.
- **Writing gems in Rust** has major benefits.
- Type-driven design, strong editor support, and rich libraries.
- **bundler supports `--ext=rust`** - you can start right now.
- Ruby flexibility x Rust safety/productivity = clear types = feels great.

<!-- まとめ -->
<!-- **Rustはメモリ安全** — dangling pointer、use-after-freeなどなどを **コンパイル時に防止** -->
<!-- **Rustでgemを書く** メリットは大きい -->
<!-- 型による設計、エディタ支援、豊富なライブラリ -->
<!-- **bundlerが `--ext=rust` をサポート** — 今すぐ始められる -->
<!-- Rubyの柔軟さ × Rustの安全性・生産性 = 型が決まる = 気持ちいい！ -->
---

# References

- [magnus - Rust bindings for Ruby](https://github.com/matsadler/magnus)
- [The Rust Programming Language (Japanese)](https://doc.rust-jp.rs/book-ja/)
- [bundler extension guide](https://bundler.io/guides/creating_gem.html)
- [Official guide for writing Ruby gems in Rust](https://www.rust-lang.org/)

<!-- 参考リンク -->
<!-- [magnus — RubyのRustバインディング](https://github.com/matsadler/magnus) -->
<!-- [The Rust Programming Language (日本語)](https://doc.rust-jp.rs/book-ja/) -->
<!-- [bundler拡張ガイド](https://bundler.io/guides/creating_gem.html) -->
<!-- [RustでRuby gemを書くガイド (公式)](https://www.rust-lang.org/) -->
---

# Bonus content

- Let's try writing a JSON parser in Rust:
- https://gist.github.com/udzura/b0ad405eeb3f799752f5ce9509aa3c64

<!-- おまけコンテンツ -->
<!-- RustでJSONパーサを書いてみよう: -->
---

<!--
_class: hero0
_backgroundImage: url(./bg-2026.003.png)
-->

# Defining types feels good...

<center>

(型を決めると気持ちいい...)

</center>

<!-- 型を決めると気持ちいい... -->
---

```rust
#[derive(Debug, Default)]
struct VM {
    globals: HashMap<String, Value>,
    call_stack: Vec<Rc<RefCell<Frame>>>,
    gc_root: Option<Rc<RefCell<GcObject>>>,
}

#[derive(Debug, Clone)]
struct Frame {
    parent: Option<Weak<RefCell<Frame>>>,
    locals: HashMap<String, Value>,
    pc: usize,
    is_rescue: bool,
}

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
enum Value {
    Integer(i64),
    Str(Rc<RefCell<String>>),
    Array(Rc<RefCell<Vec<Value>>>),
    Object(Rc<RefCell<GcObject>>),
    Nil,
}

#[derive(Debug, Clone, Default, PartialEq)]
struct GcObject {
    class_name: String,
    ivars: HashMap<String, Value>,
    next: Option<Rc<RefCell<GcObject>>>,
    marked: bool,
}
```
