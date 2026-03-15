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

# Ruby x Rust 入門

コード懇親会 @ RubyKaigi 2026 / Ruby x Rust 分科会

---

# 今日のアジェンダ

- Rustのメリット — メモリ安全性を中心に
- Rustでgemを書く — 開発体験のメリット
- bundlerを使ったRust gem作成手順
- まとめ

---

# Rustのメリット

---

# とにかくメモリ安全

- Rustはコンパイル時に **所有権(ownership)** と **借用(borrow)** をチェック
- ダングリングポインタ、use-after-free、二重解放などを **コンパイルエラー** で防止
- GCなしでメモリ安全を実現 → パフォーマンスと安全性を両立
- C/C++で長年悩まされてきたメモリバグのカテゴリがまるごと消える

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
 --> src/main.rs:3:5
  |
3 |     &x
  |     ^^ returns a reference to data owned by the current function
```

→ ライフタイムの仕組みにより、**dangling pointerはそもそも作れない**

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
- ヒープに置きたければ `Box<i32>` を使う

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
- 脆弱性の温床（CVEの常連）

---

# Rustなら大丈夫

```rust
fn main() {
    let buf = String::from("Hello, RubyKaigi!");

    drop(buf); // 明示的に解放

    println!("{}", buf); // コンパイルエラー！
}
```

コンパイラが教えてくれる：

```
error[E0382]: borrow of moved value: `buf`
 --> src/main.rs:5:20
  |
4 |     drop(buf);
  |          --- value moved here
5 |     println!("{}", buf);
  |                    ^^^ value used here after move
```

→ **解放済みの値は二度と使えない**。コンパイラが保証する

---

# 補足: なぜuse-after-freeを防げるのか

- `drop(buf)` は `buf` の **所有権をムーブ** している
- Rustでは値を関数に渡す = 所有権の移動（ムーブ）
- ムーブ後の変数はもう使えない — これが所有権システムの基本ルール

```rust
fn take_ownership(s: String) {
    // sはこのスコープで破棄される
}

fn main() {
    let buf = String::from("hello");
    take_ownership(buf); // 所有権がムーブ
    // println!("{}", buf); // コンパイルエラー！dropと同じ理由
}
```

- `drop()` は特別な関数ではなく、ただ **値を受け取って何もしない** だけ
- 所有権の仕組みそのものが、use-after-freeを構造的に不可能にしている

---

# Rustでgemを書く

---

# Rustでgemを書くメリット

- **型から設計できる**
  - 関数のシグネチャを書くだけで設計の骨格ができる
  - `struct` / `enum` でドメインモデルを明確に表現
  - Cの `void *` 地獄からの解放

---

# 型から設計できる — 例

```rust
use magnus::{function, prelude::*, Error, Ruby};

// 型シグネチャがそのままAPIドキュメントになる
fn fizzbuzz(n: u64) -> String {
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

---

# Rustのライブラリ・資産を使える

- **crates.io** に10万以上のライブラリ
- 例：
  - `serde` — 高速なシリアライズ/デシリアライズ
  - `regex` — 高速な正規表現エンジン
  - `rayon` — お手軽データ並列処理
  - `tokio` — 非同期ランタイム
- `Cargo.toml` に一行追加するだけで使える
- Cのように依存ライブラリのビルド設定で苦しまない

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
├── Cargo.toml          # Rustの依存管理
├── Gemfile
├── ext/
│   └── my_rust_gem/
│       ├── Cargo.toml   # 拡張本体のCargo設定
│       ├── extconf.rb   # ビルド設定
│       └── src/
│           └── lib.rs   # Rustのコード本体
├── lib/
│   └── my_rust_gem.rb   # Rubyのエントリポイント
├── my_rust_gem.gemspec
└── ...
```

---

# 生成されるRustコード (ext/.../src/lib.rs)

```rust
use magnus::{function, prelude::*, Error, Ruby};

fn hello(subject: String) -> String {
    format!("Hello from Rust, {subject}!")
}

#[magnus::init]
fn init(ruby: &Ruby) -> Result<(), Error> {
    ruby.define_global_function("hello", function!(hello, 1));
    Ok(())
}
```

- **magnus** クレート = RubyのC APIのRustバインディング
- `#[magnus::init]` でRuby拡張のエントリポイントを定義

---

# ビルドして使う

```bash
# ビルド
$ bundle exec rake compile

# 試す
$ bundle exec ruby -e "require 'my_rust_gem'; puts hello('RubyKaigi')"
Hello from Rust, RubyKaigi!
```

- `rake compile` で Cargo → `.so` / `.bundle` をビルド
- あとは普通のgemと同じように使える

---

# まとめ

- **Rustはメモリ安全** — dangling pointer、use-after-freeを **コンパイル時に防止**
- **Rustでgemを書く** メリットは大きい
  - 型による設計、エディタ支援、豊富なライブラリ
- **bundlerが `--ext=rust` をサポート** — 今すぐ始められる
- Rubyの柔軟さ × Rustの安全性・速度 = 最強の組み合わせ

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
