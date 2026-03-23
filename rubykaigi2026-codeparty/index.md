---
marp: true
theme: default
title: "コード懇親会 @ RubyKaigi 2026 / Ruby x Rust 分科会"
paginate: true
style: |
    h1 { color: #0f7f85; }
    h2 { color: #0f7f85; }
    section li { color: ##4e4c49 }
    section.hero > h1 { font-size: 70pt; }
    section.profile img {
        position: absolute;
        top: 25%;
        left: 65%;
        overflow: hidden !important;
        border-radius: 50% !important;
    }
---

<!-- _class: hero -->

# Beginning Ruby x Rust

コード懇親会 @ RubyKaigi 2026 / Ruby x Rust テーブル

---

# 今日のアジェンダ

- Rustのメリット — メモリ安全性を中心に
- Rustでgemを書く — 開発体験のメリット
- bundlerを使ったRust gem作成手順
- まとめ

---

# Rustのメリット

---

# 色々あるので、個人の感想だけ共有します

---

# とにかくメモリ安全

---

# Rustのメモリ安全性のための文法的機能

- 所有権
- 借用
- ライフタイム

---

# 具体的には

- Rustはコンパイル時に **所有権(ownership)** と **借用(borrow)** をチェック
- ダングリングポインタ、use-after-freeなどを **コンパイルエラー** で防止
- GCなしでメモリ安全を実現 → パフォーマンスと安全性を両立
- C/C++で長年悩まされてきたメモリバグのカテゴリがまるごと消える

---

# ライフタイムの「力」

---

# dangling pointerとは？

- すでに解放・破棄されたメモリ領域を指し続けているポインタのこと
- Cでは関数のローカル変数のアドレスを返すだけで簡単に作れてしまう

---

# Cでdangling pointerになる例

```c
#include <stdio.h>
#include <stdlib.h>

int *create_value() {
    int x = 42;
    return &x; // ローカル変数のアドレスを返している！
}

int main() {
    int *p = create_value();
    // pはすでに無効なメモリを指している（dangling pointer）
    printf("%d\n", *p); // 未定義動作！
    return 0;
}
```

- `x` は関数を抜けるとスタックから消える
- 返されたポインタはもう無効 → **未定義動作**

---

# 実行例

```bash
$ clang sample1.c -w -Oz -o sample1.out
$ ./sample1.out                        
-281521464 # ???
```

- NOTE: `-w` で警告を消しているが、実際はコンパイラが警告してくれはする

---

# Rustなら大丈夫

```rust
fn create_value() -> &i32 {
    let x = 42;
    &x // コンパイルエラー！
}
```

コンパイラが教えてくれる：

```
error[E0515]: cannot return reference to local variable `x`
  --> examples/sample1.rs:13:5
   |
13 |     &x // コンパイルエラー
   |     ^^ returns a reference to data owned by the current function
```

→ ライフタイムの仕組みにより、**dangling pointerはそもそも作れない**

---

# 補足: ライフタイムとは何か

- Rustの参照 `&T` には必ず **ライフタイム（生存期間）** が紐づく
- コンパイラは「参照先のデータが、参照より長く生きているか」を検証する

---

# さっきのコードをもう一度

```rust
fn create_value<'a>() -> &'a i32 {
//                        ^^^^ このライフタイムを満たすデータがない！
    let x = 42; // xのライフタイムはこの関数内だけ
    &x          // 関数の外まで生きる参照は作れない
}
```

- `'a` = 「呼び出し元が期待する生存期間」
- `x` は関数を抜けると破棄される → `'a` を満たせない → **コンパイルエラー**
- Cにはこの仕組みがないので、プログラマの注意力だけが頼り

---

# 呼び出し元から見ると...

```rust
fn main() {
    let p: &i32 = create_value();
    //     ^^^^
    // pはmain()のスコープが終わるまで有効な参照を期待している
    // → ライフタイム 'a はmain()のスコープと同じ長さが必要

    println!("{}", p); // ← ここでまだ使いたい！
}

fn create_value<'a>() -> &'a i32 {
    let x = 42;
    // xはここで破棄される... 'a（= main()のスコープ）より短い！
    &x // コンパイルエラー
}
```

---

# Rustで正しく書くなら

```rust
fn create_value() -> i32 {
    let x = 42;
    x // 値を返す（ムーブ）
}

fn main() {
    let v = create_value();
    println!("{}", v); // 42 — 安全！
}
```

- 参照ではなく値そのものを返す → 所有権がムーブされる
    - コンパイラがメモリ上の位置をいい感じにする
    - ムーブの話は次に詳しく
- ヒープに明示的に置きたければ `Box<i32>` を使う

---

# 所有権の「力」

---

# use-after-freeとは？

- `free()` などで解放済みのメモリに再びアクセスしてしまうこと
- 解放後もポインタ変数自体は残っているため、コード上は普通にアクセスできてしまう
- データ破壊、クラッシュ、任意コード実行など深刻な脆弱性につながる
- ブラウザやOSカーネルでも頻繁に報告される

---

# Cでuse-after-freeになる例

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    char *buf = (char *)malloc(64);
    snprintf(buf, 64, "Hello, RubyKaigi!");

    free(buf);

    // 解放済みメモリへアクセス（use-after-free）
    printf("%s\n", buf); // 未定義動作！
    return 0;
}
```

- `free()` の後も `buf` はそのまま使えてしまう

---

# 攻撃の検証

```bash
$ clang sample2.c -fsanitize=address -O0 -o sample2.out
$ ./sample2.out
=================================================================
==14745==ERROR: AddressSanitizer: heap-use-after-free on address 0x606000000260 at pc 0x000101423808 bp 0x00016f092680 sp 0x00016f091e10
READ of size 2 at 0x606000000260 thread T0
    #0 0x000101423804 in printf_common(void*, char const*, char*)+0x64c (libclang_rt.asan_osx_dynamic.dylib:arm64e+0x1b804)
    #1 0x0001014245c4 in printf+0x68 (libclang_rt.asan_osx_dynamic.dylib:arm64e+0x1c5c4)
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

- 今回は、ASan（AddressSanitizer）に敢えて検出させて確認
- ちなみにASan有効はオーバーヘッドがあり、一般に実行時間は x2 程度になるそう

---

# Rustなら大丈夫

```rust
fn main() {
    let buf = String::from("Hello, RubyKaigi!");

    drop(buf); // 明示的に解放

    println!("{}", buf); // コンパイルエラー！
}
```

---

# コンパイラが教えてくれる：

```
error[E0382]: borrow of moved value: `buf`
 --> examples/sample2.rs:6:20
  |
2 |     let buf = String::from("Hello, RubyKaigi!");
  |         --- move occurs because `buf` has type `String`,
  |             which does not implement the `Copy` trait
3 |
4 |     drop(buf); // 明示的に解放
  |          --- value moved here
5 |
6 |     println!("{}", buf); // コンパイルエラー！
  |                    ^^^ value borrowed here after move
```

→ **解放済みの値は二度と使えない**。コンパイラが保証する

---

# なぜuse-after-freeを防げるのか

- `drop(buf)` は `buf` の **所有権をムーブ** している
- Rustでは値を関数に渡す = 所有権の移動（ムーブ）
- ムーブ後の変数はもう**使えない** — これが所有権システムの基本ルール

---

# どういうこと？

```rust
fn take_ownership(s: String) {
    // s を使っていない、が...
    // sはこのスコープで破棄される
}

fn main() {
    let buf = String::from("hello");
    take_ownership(buf); // 所有権がムーブ
    // println!("{}", buf); // コンパイルエラー！dropと同じ理由
}
```

---

# `drop()` はよくあるイディオム

- `drop()` は特別な関数ではなく、ただ **値を受け取って何もしない** だけとわかる
- 所有権の仕組みそのものが、use-after-freeを構造的に不可能にしている

---

# Rustを使ってgemを書く？

---

# Rustでgemを書くメリット

- 無論、 C と比べた安全性はあるが、他にも色々紹介

---

# 型を決めよう

- **型から設計できる**
  - 関数のシグネチャを書くだけで設計の骨格ができる
  - `struct` / `enum` でドメインモデルを明確に表現
  - Cの `void *` 地獄からの解放

---

# 型の力（雰囲気）

```rust
use magnus::{function, prelude::*, Error, Ruby};

// 型シグネチャがそのままAPIドキュメントになる
fn fizzbuzz(n: u64) -> String {
    // 型が強力＝パターンマッチが強力
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

# エディタの支援が強力

- **rust-analyzer** が型推論・補完・リファクタリングを強力サポート
    - 関数の引数の型、返り値の型をインラインで表示
    - コンパイルエラーをリアルタイムで表示 → 書いた瞬間に間違いがわかる
    - Cのext gemでは得られなかった開発体験
- clippy などの優れたリンターも簡単に連携可能

---

# Rustのライブラリ・資産を使える

- **crates.io** に10万以上のライブラリ
- 例：
  - `serde` — 高速なマルチフォーマット対応のシリアライズ/デシリアライズ
  - `rayon` — お手軽データ並列処理
  - `tokio` — 非同期ランタイム
- `Cargo.toml` に一行追加するだけで使える
- Cのように依存ライブラリのビルド設定で苦しまない

---

# ちなみに...

- 💡 実はCargoの作者の一人は **Yehuda Katz** — bundlerの作者でもある
  - そりゃ〜使いやすいよね！

---

# bundlerを使った手順

---

# Rust gem のプロジェクトを作る

```bash
$ bundle gem my_rust_gem --ext=rust
```

- `--ext=rust` を指定するだけでRust拡張のひな形ができる
- bundler 2.4+ で対応

---

# できるプロジェクト構造

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

# 生成されるRustコード (ext/my_rust_gem/src/lib.rs)

```rust
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

- **magnus** クレート = RubyのC APIのRustバインディング
- `#[magnus::init]` でRuby拡張のエントリポイントを定義
- `define_module`, `define_global_function` など直感的なAPIが用意される

---

# ビルドして使う

- もちろん、事前にRustとCargoをインストールしてください！

```bash
# ビルド
$ bundle install
$ bundle exec rake compile

# 試す
$ bundle exec ruby -e "require 'my_rust_gem'; puts MyRustGem.hello('RubyKaigi')"
Hello from Rust, RubyKaigi!
```

- `rake compile` で Cargo → `.so` / `.bundle` をビルド
- あとは普通のgemと同じように使える

---

# いきなり書いてみる？

- ドキュメント: https://docs.rs/magnus/latest/magnus/#examples
- 多分... 補完に任せればなんとなく書けるんじゃないかなあ

---

# まとめ

- **Rustはメモリ安全** — dangling pointer、use-after-freeなどなどを **コンパイル時に防止**
- **Rustでgemを書く** メリットは大きい
  - 型による設計、エディタ支援、豊富なライブラリ
- **bundlerが `--ext=rust` をサポート** — 今すぐ始められる
- Rubyの柔軟さ × Rustの安全性・生産性 = 型が決まる = 気持ちいい！

---

# 参考リンク

- [magnus — RubyのRustバインディング](https://github.com/matsadler/magnus)
- [The Rust Programming Language (日本語)](https://doc.rust-jp.rs/book-ja/)
- [bundler拡張ガイド](https://bundler.io/guides/creating_gem.html)
- [RustでRuby gemを書くガイド (公式)](https://www.rust-lang.org/)

---

# 型を決めると気持ちいい...

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
