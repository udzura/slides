----
marp: true
header: "Rubyをこじらせて"
footer: "presentation by Uchio Kondo"
theme: fukuokarb
paginate: true
----

<!--
_class: hero
-->

# Rubyをこじらせて

## &nbsp;Ruby is like a teenage angst to me

<!--
"こじらせる" means: to develop a kind of obsession or a heavy addiction with something; e.g. hobby, hard job, complex, etc.
-->

----
<!--
_class: profile
-->

# Uchio Kondo (@udzura)

- Affiliation: Mirrativ Inc.
- Hacker Supporter @Fukuoka City Engineer Cafe
- Advisor @Fjord Bootcamp
- Co-translator of "Leraning eBPF" (O'Reilly Japan)
- [RubyKaigi Speaker (2016 ~)](https://rubykaigi-speakers.vercel.app/speakers/Uchio+KONDO)
- RubyKaigi 2019 Local Organizer @ Fukuoka


![w:370](./rk2024-me-2.png)

<!--
- 所属: 株式会社ミラティブ
- 福岡市エンジニアカフェ ハッカーサポーター
- フィヨルドブートキャンプ アドバイザー
- 『入門 eBPF』（オライリージャパン）共同翻訳
- [RubyKaigi Speaker](https://rubykaigi-speakers.vercel.app/speakers/Uchio+KONDO) (2016 ~)
- RubyKaigi 2019 Local Organizer
-->

---
<!--
_class: hero
-->

# Recital of daily discipline

<!-- 生活発表 -->

---
<!--
_class: hero
-->

# Prospectus

<!-- 目論見書 -->

---
<!--
_class: hero
-->

# Reflection of daily discipline

---
<!--
_class: hero
-->

# Bibliographic commentary

<!-- 解題 -->

---
<!--
_class: hero
-->

# 2016

---
<!--
_class: hero
-->

# Haconiwa

---
<!--
_class: hero
-->

# Linux Container

---
<!--
_class: normal
-->

# Linux Container

- Focusing on container component technologies
  - Linux Namespace
  - cgroup
  - Capability, etc ...

---
<!--
_class: hero
-->

# (2017..2018)

---
<!--
_class: hero
-->

# 2019

---
<!--
_class: hero
-->

# Local Organizer @ Fukuoka

---
<!--
_class: hero
-->

# CRIU

---
<!--
_class: normal
-->

# CRIU

- Checkpoint and restore of processes (including containers)
  - Saves the process state to a file and restores it
  - Applied to speeding up Rails bootstrap in my case
  - Can also be used for live migration / other purposes

<!--
- プロセス（=コンテナも対象）のCheckpoint&Restore
  - プロセスの状態をファイルに保存し、再生する
  - 2019 ではRailsの起動高速化への応用
  - ライブマイグレーションほかにも使える
-->

---
<!--
_class: hero
-->

# 2021

---
<!--
_class: hero
-->

# eBPF

---
<!--
_class: normal
-->

# eBPF

- Technology for executing programs inside the Linux kernel
  - Which can use deeper functionarities than ordinary system calls
  - (A bit) safer than kernel modules
  - For Networking, Observability, Security...


<!--
- Linuxカーネル内部でプログラムを実行する技術
  - 普通のシステムコールより奥深い情報を使える
  - カーネルモジュールより**は**安全
  - ネットワーク、Observability、セキュリティ...
-->

---
<!--
_class: normal
-->

# Rucy - My product

- eBPF has a dedicated VM inside the kernel, and...
- Has a dedicated bytecode instruction set
  - Kinda like YARV (saying very roughly)
- Rucy **compiles** Ruby scripts into eBPF bytecode
  - Rucy = Ruby Compiler = RuC

<!-- 
- eBPFはカーネル内部に専用のVMを持つ＋
- 専用のバイトコード命令系をもつ
  - YARVみたいなもんですね〜（そう？）
- RucyはRubyのスクリプトをそのバイトコードに**コンパイル**する
  - Rucy = Ruby Compiler = RuC
-->

---
<!--
_class: hero
-->

# 2022

---
<!--
_class: hero
-->

# eBPF (BCC)

---
<!--
_class: normal
-->

# How is Rucy different from RbBCC?

- Rucy **compiles** Ruby scripts into their bytecode
  - It is AOT compiler
- RbBCC is basically an FFI for BCC (libbcc)
  - libbcc compiles C-like code into eBPF binaries on the fly
  - It is **JIT** compiler
  - Can use data sent from Ruby

<!--
# RucyとRbBCCはどう違うのか

- RucyはRubyのスクリプトをそのバイトコードに**コンパイル**する
  - Rucy = Ruby Compiler = RuC
- RbBCCは、そもそもBCC(libbcc)のFFI
- libbccは、C言語風のコードをその場でeBPFバイナリにコンパイルします
  - Rubyから送られてきたデータを使えるという話
-->

---
<!--
_class: normal
-->

# How is BCC different from compiled eBPF?

- Basically, eBPF is moving towards a **AOT-compiled** ecosystem
  - Search for `BPF CO-RE`, etc.
  - So the future is Rucy's side
- On the other hand, RbBCC can use most of the basic functions of eBPF
  - Many functions are properly ported
  - Sufficient enough for learning and small tools

<!--
# BCCはどう違うのか

- 基本的にeBPFは**コンパイル型**のエコシステムに移行中
  - BPF CO-RE などで検索
  - なので未来があるのはRucyの方
- 一方、RbBCCはeBPFの基本的な機能を大体使える
  - 多くの機能をちゃんと移植済み
  - 学習用、ちょっとしたツールには十分なつもり
-->

---
<!--
_class: hero
-->

# [PR]

<!--
- これを読むと解像度が上がる
- 鳥井さんのお力で文章も読みやすい！
-->

- Reading this book will increase your understanding
- Thanks to Tori-san, it is easy to read!

![bg right w:450](./book.png)

---
<!--
_class: hero
-->

# <s>2023</s>

---
<!--
_class: hero
-->

# 2024

---
<!--
_class: hero
-->

# WebAssembly

---
<!--
_class: normal
-->

# WebAssembly

- As you know, a technology for running code in browsers
  - But I **don't** think that's all
- IMO, it's the final answer for **embedded application** environments
  - Browsers are just "one of the embeddable environments"
  - Can be embedded in various applications with portable VM specifications
  - envoy, fluent-bit, Containers like youki...
- Someday, [even for real embedded systems](https://arxiv.org/html/2405.09213v1)

<!--
- ご存知、ブラウザでコードを動かす技術
- でも僕は**そうは思ってない**
- アプリ組み込み環境のファイナルアンサーだと思っている
  - ブラウザは「組み込める環境の一つ」にすぎない
  - ポータブルなVM仕様でいろんなアプリに組み込める
  - envoy, fluent-bit, Containers...
  - [いつかは本物の組み込みにも](https://arxiv.org/html/2405.09213v1)
-->

---
<!--
_class: normal
-->

# The "Web" part of WebAssembly

- **Web**Assembly will probably not be just for the web
- ... Just like eBPF is no longer "Berkeley **Packer Filter**"


<!--
- eBPFがもはや全く "Berkeley **Packer Filter**" でないように
- **Web**AssemblyもWebだけではなくなるのだろう
-->

---
<!--
_class: normal
-->

# Why Ruby for WebAssembly (again)

Ruby for "WebAssembly as an embedded environment" is desired
  - (At least there's one customer - it's ME!)
- I came to the initial idea; I could manege to do it with mruby

<!--
- 「組み込み環境としてのWebAssembly」のためのRubyが欲しい
  - （少なくとも僕はめっちゃ欲しいので...）
- mruby でゴニョっとすればいけるんじゃね？ というのが最初の発想
-->

---
<!--
_class: hero
-->

# Talk about this again later

---
<!--
_class: hero
-->

# Daily trends

---
<!--
_class: normal
-->

# Trends

- So-called low-level technologies?
- Lots of Linux stuff (it's coincidentally)
- I tried utilizing `${mysterious_tech}` from Ruby!

<!--
- 所謂低レイヤ？
- Linux ネタが多め（たまたま）
- ${謎技術} をRubyから使ってみた！
-->

---
<!--
_class: hero
-->

# Gave a jab to the lower layers from Ruby World

<!-- 低めのレイヤーにRubyでいっちょ噛み -->

- My fighting style

---
<!--
_class: normal
-->

# Gave a jab from Ruby World

- Long live low layers!
- It's also that ordinary web application engineers don't usually touch...

---
<!--
_class: hero
-->

# Why low-level?

---
<!--
_class: normal
-->

# Ruby has a weaker presence in the low-level (or SOTA) world

- A typical low-layer project...
  - Has no Ruby bindings
  - Has no Ruby sample code
    - Just has samples for like Go, Python, C++, and Rust
    - e.g. Supported languages for eBPF(BCC) are Python, Lua, C++
      - Go and Rust have SDKs for eBPF by volunteers

<!--
- Rubyのバインディングがない
- Rubyのサンプルコードがない
  - Go、Python、C++、そしてRust他みたいな
  - e.g. eBPF(BCC) の対応言語はPython、Lua、C++
    - GoとRustは有志がeBPF向けSDKを作っていた
-->

---
<!--
_class: normal
-->

# Desire to touch SOTA from Ruby

- The world of computers is constantly evolving
- Ruby may receive benefit from the results...
  - (such as gradual typing)
- **I want to use Ruby** even when touching advanced things

<!--
- コンピューターの世界は日々進歩しているらしい
- Rubyが成果を享受できることもあるが...（それこそ、漸進的型とか）
- 便利なものや進んだものに触れる時もRubyからがいい
-->

---
<!--
_class: normal
-->

# Desire to make technology my own

- I hate pretending to understand
  - Am I satisfied with doing "Getting Started"?
- Understand the essence through Ruby
  - They're often not assumed that you'll use them from Ruby
  - == Hack is required
  - Deepening understangings by hacking

<!--
- 自分ごとにしたい
- 「わかったつもりになる」のは嫌だ
  - Getting Started をやって満足？
- Ruby を通して、本質的な部分を理解する
  - Ruby から使うことをあまり想定していないことが多い = Hack必須
  - Hack することで深まる
-->

---
<!--
_class: normal
-->

# Do I really want to "contribute" to OSS?

- Actually, I'm not so interested...
  - Of course, I'll fix what I'm using and give back if it's open
- I don't feel like doing anything for a large OSS
  - Of course, I'll do it if it becomes "my own problem"
- Basically, I want to create something I'm convinced of
  - It just happens that they're low-level stuffs

<!--
- 実はあまり興味が...
  - もちろん使っているものは直す、オープンなら還元しますが
- 大きなOSSに何かしたいという気持ちが薄い
  - もちろん「自分ごと」になればやります
- 基本的には、自分が納得するものを作りたい
  - 納得できそうなものがたまたま低いレイヤに多い
-->

---
<!--
_class: hero
-->

# Create something<br>useful || interesting

---
<!--
_class: hero
-->

# mruby/edge in Depth

---
<!--
_class: hero
-->

# WebAssembly in Depth

---
<!--
_class: normal
-->

# Core WebAssembly

- Key specifications:
  - import/export Functions
  - Linear memory

> I'll omit the latter for today...

---
<!--
_class: normal
-->

# Making a smallest WebAssembly binary

- Written in C

```c
// sample.c
#include <emscripten.h>

void log_value(int size);

int EMSCRIPTEN_KEEPALIVE calc_plus(int n, int m) {
  log_value(n + m);
  return 0;
}
```

---
<!--
_class: normal
-->

# Compile it with emscripten

```
$ emcc -o sample.wasm --js-library ./lib.js --no-entry ./sample.c
cache:INFO:  - ok
```

- ※ lib.js is here

```js
mergeInto(LibraryManager.library, {
    log_value: function(value) { /* TODO */ }
});
```

---
<!--
_class: normal
-->

# Export section

```
$ wasm-objdump -x -j Export sample.wasm 

sample.wasm:    file format wasm 0x1

Section Details:

Export[10]:
 - memory[0] -> "memory"
 - func[2] <calc_plus> -> "calc_plus"
 - table[0] -> "__indirect_function_table"
 - func[3] <_initialize> -> "_initialize" ...
```

- Invoke `calc_plus()` from "browser"

---
<!--
_class: normal
-->

# Import section

```
$ wasm-objdump -x -j Import sample.wasm

sample.wasm:    file format wasm 0x1

Section Details:

Import[1]:
 - func[0] sig=2 <env.log_value> <- env.log_value
```

- Inject `log_value()` "browser" function into wasm instance

---
<!--
_class: normal
-->

# How to use in browser

```javascript
const obj = {
  env: {
    // Specify the browser-side function here
    log_value: function(value) {
      let log = "sample wasm! 12 + 34 = " + value.toString();
      document.getElementById("placeholder").innerText = log;
    }
  },
};

WebAssembly.instantiateStreaming(fetch("./sample.wasm"), obj).then(
  (obj) => {
    // Call the function defined in wasm here
    obj.instance.exports.calc_plus(12 + 34);
  },
);
```

---
<!--
_class: hero
-->

# Live demo

<script async type="text/javascript">
const importObject = {
  env: {
    log_value: function(value) {
      let log = "sample wasm! 12 + 34 = " + value.toString();
      document.getElementById("placeholder").innerText = log;
      console.log("OK");
    }
  },
};

window.fire = function() {
  WebAssembly.instantiateStreaming(fetch("./sample.wasm"), importObject).then(
    function (obj) {
      obj.instance.exports.calc_plus(12 + 34);
    },
  );
};
</script>

<div>
  Output: <strong style="color: blue; font-size: larger;" id="placeholder" onclick="fire();">{{here}}</strong>
</div>

---
<!--
_class: hero
-->

# The primary concept of WebAssembly


- Opinions are my own...


---
<!--
_class: hero
-->

# Simple

---
<!--
_class: normal
-->

# WASI is simple if you understand import/export

- WASI = A set of functions that represent "If you import and use them, you can cooperate with the system nicely"
- On the program side, you just need to use it according to the specification
- In WASI-compatible runtimes, you just need to prepare those import functions
  - It's like implementing system calls

<!--
- WASI = 「これをimportして使えばシステム操作がええ感じにできるで」という関数のセット
- プログラム側では仕様の通りに使えばいい
- WASI対応ランタイムでは、それらのimport用関数を準備すればいい
  - まさにシステムコールを実装するような感じ
-->

---
<!--
_class: normal
-->

# e.g. Emulating WASI in a browser

- https://github.com/bjorn3/browser_wasi_shim
- Implement the "system call" of `random_get` in browser JS

```typescript
random_get(buf: number, buf_len: number) {
    const buffer8 = new Uint8Array(...);
    // omit stuffs...
    for (let i = 0; i < buf_len; i += 65536) {
        crypto.getRandomValues(buffer8.subarray(i, i + 65536));
    }
}
```

---
<!--
_class: normal
-->

# What I want to do with mruby/edge is also simple

- To export Ruby method definitions as they are
- To be able to use imported functions as the Ruby level methods

---
<!--
_class: normal
-->

# Code image (to be implemented)

- This doesn't mean it will be implemented exactly this way...

```ruby
# @export!
# @rbs (Integer) -> Integeer
def fib(n)
  # ...
end

# @import!
# @rbs (String) -> void
def console_log(str) = __imported__!

def _start
  console_log("Hello World " + fib(10).to_s)
end
```

---
<!--
_class: hero
-->

# One More Thing

---
<!--
_class: hero
-->

# Future of WebAssembly

---
<!--
_class: hero
-->

# WebAssembly Component Model

---
<!--
_class: normal
-->

# WebAssembly Component Model

- Refer to interface of Core WASM
  - It's a bit fuzzy like a C DLL
- It would be convenient and safe if we define the "connection spec" properly
  - Types (which are also somewhat flexible and powerful)
  - Binary specification
  - Toolchain

<!--
- Core WASMのインタフェース
  - CのDLLのようにふわっとしたところがある
- 「繋がり部分」をきちっとしたら便利で安全になる
  - 型（それもある程度柔軟な）
  - バイナリ仕様
  - ツールチェイン
-->

---
<!--
_class: normal
-->

# Tools for the WebAssembly Component Model

- User-friendly typing system
  - WIT format
  - Can also be considered a kind of RPC
- Binary specification
  - Canonical ABI
- Toolchain
  - We can create more and more once the above is generally available

<!--
- いい感じの型
  - WIT形式
  - 一種のRPCとも言える
- バイナリ仕様
  - Canonical ABI
- ツールチェイン
  - 上記が揃ったらどんどん作れるはず
-->

---
<!--
_class: normal
-->

# FYI: WIT format

```lua
world rubyist-kaigi {
    export fib: func(n: i32) -> i32;

    import console_log: func(log: string);
}
```

---
<!--
_class: normal
-->

# FYI: Understanding Components by Hands-on

- "手書きで理解するWebAssembly Component Model"
  - (Understanding the WebAssembly Component Model by Hand Assemble)
  - https://nulab.com/ja/blog/nulab/webassembly-component-model/
  - https://nulab.com/ja/blog/nulab/webassembly-component-model-hello-world/

---
<!--
_class: normal
-->

# wasmCloud, Future for example

![bg right w:600](./wasmcloud.png)

- https://wasmcloud.com/
- A CNCF Sandbox Project

---
<!--
_class: normal
-->

# Running Ruby on wasmCloud

> If you prefer working in a language that isn't listed here, let us know!

- https://wasmcloud.com/docs/tour/hello-world?lang=unlisted

---
<!--
_class: normal
-->

# Example of running mruby/edge (roughly)

```rust
use mrubyedge::{mrb_helper, vm::RObject};
// ...
impl Guest for HttpServer {
    fn handle(_request: IncomingRequest, response_out: ResponseOutparam) {
        let write_response = |body: &str| { ... };
        let bin = include_bytes!("./fib.mrb");
        let rite = mrubyedge::rite::load(bin).unwrap();
        let mut vm = mrubyedge::vm::VM::open(rite);
        vm.prelude().unwrap(); //...
        match mrb_helper::mrb_funcall(&mut vm, &top_self, "fib".to_string(), &args) {
            Ok(val) => { write_response(&val) }
            Err(ex) => { dbg!(ex); }
        } //...
    }
}
```

---
<!--
_class: normal
-->

# Creating a WASM binary that contains mruby

```console
$ wash build
   Compiling http-hello-world v0.1.0 (/home/ubuntu/mrubyhttp)
    Finished `release` profile [optimized] target(s) in 0.29s

Component built and signed and can be found at "/../build/http_hello_world_s.wasm"

$ # The mruby binary is embedded
$ strings build/http_hello_world_s.wasm | grep MATZ
MATZ0000IREP

$ wasm-tools component wit build/http_hello_world_s.wasm | head -n 20
package root:component;

world root {
  import wasi:clocks/monotonic-clock@0.2.0;
  // ....

  // entry point
  export wasi:http/incoming-handler@0.2.0;
}
```

---
<!--
_class: normal
-->

# Running this WASM on wasmCloud

```console
$ wash app deploy wadm.yaml
$ wash app status rust-hello-world

rust-hello-world@ - Deployed                   
  Name                                         Kind           Status    
  http_component                               SpreadScaler   Deployed  
  httpserver -(wasi:http)-> http_component     LinkScaler     Deployed  
  httpserver                                   SpreadScaler   Deployed

$ curl localhost:8080
fib(15) = 610
```

---
<!--
_class: normal
-->

# wasmCloud concepts

![](./wasmcloud-zu.png)

---
<!--
_class: hero
-->

# Ruby wants to connect the world, too

---
<!--
_class: hero
-->

<div style="position: absolute; left: 62%; width: 30%; font-size: smaller;">

> I talked with @yu_suke1994 at tskaigi about the future of Ruby, and we agreed that the only way for Ruby to survive is to release a lightweight runtime that supports wasm soon and integrate it with the component model ecosystem. So, @udzura, please do your best!

</div>

<blockquote class="twitter-tweet"><p lang="ja" dir="ltr">.<a href="https://twitter.com/yu_suke1994?ref_src=twsrc%5Etfw">@yu_suke1994</a> と tskaigi で話した Ruby がこの先生きのこるにはという話、早いとこ wasm 対応の軽量ランタイム出して <a href="https://t.co/FRzMN9jsBj">https://t.co/FRzMN9jsBj</a> かなんかで component model エコシステムと統合されるしかねえ、という話になったので、 <a href="https://twitter.com/udzura?ref_src=twsrc%5Etfw">@udzura</a> さん頑張ってほしい</p>&mdash; mizchi (@mizchi) <a href="https://twitter.com/mizchi/status/1791299723355435147?ref_src=twsrc%5Etfw">May 17, 2024</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

---
<!--
_class: hero
-->

# Wrapping up

<!--
- Rubyで低レイヤにいっちょ噛みしてることについて、多くの人にとってはあまり馴染みのない話題が多かったでしょうので、解題をしました。
- 最近のWASM周りの仕事もレイヤは低いですが、皆さんに使ってもらえる可能性のある面白いものができるといいなと思っていたりします。
- またrubykaigiで話しかけてくださいね。
-->

----

<!--
_class: hero
-->

# See you in Matsuyama!
