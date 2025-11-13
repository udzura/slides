----
marp: true
theme: default
paginate: true
title: WebAssemblyの利用とAI時代に向けた応用例
description: For seckun 2025
image: https://udzura.jp/slides/2025/seckun/ogp.png#TODO
size: 16:9
style: |
  h1 { color: #0f7f85; }
  h2 { color: #00c4cc; }
  section li { color: #23221f; }
  section.hero > h1 { font-size: 50pt; }
  section.profile img {
    position: absolute;
    top: 25%;
    left: 65%;
    overflow: hidden !important;
    border-radius: 50% !important;
  }
----
<!--
_class: hero
-->


# WebAssemblyの利用と<br>AI時代に向けた応用例

### Presentation by Uchio Kondo @ seckun 2025

---

<!--
_class: profile
-->

# 自己紹介

- 近藤うちお (@udzura)
- エンジニアカフェ ハッカーサポーター
- 所属: 株式会社SmartHR プロダクトエンジニア
- 『入門eBPF』（オライリージャパン）という
本を共同翻訳しました

![w:370](image.png)

---
<!--
_class: hero
-->

# 今日のモチベーションを"対話"する時間

### 相互自己紹介ともいう

---
<!--
_class: hero
-->

# wasmとは何かワークショップ

---
<!--
_class: hero
-->

# wasmの概要

-----

# WebAssembly (wasm) とは？

  - **様々な言語をブラウザ上で動かすための技術**
      - C/C++、Rust、Go、Python、Ruby などをサポート
  - **仕組み:**
    1.  各言語のコードをWasm形式のバイナリーにコンパイル
    2.  そのバイナリーをブラウザ内で実行

-----

![bg](image-1.png)

<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>

> https://udzura.jp/slides/2025/rubykaigi/#16

<!--
  IMAGE_ONLY
-->

-----

# Why WebAssembly?

  - **メリット:**
      - JavaScript以外の言語をブラウザで利用可能
      - コンパイルによる**高速化や最適化**が期待できる

-----

# wasmの実行環境はブラウザだけではない

  - wasmバイナリーの形式にしてしまえば、どこでも動かせる:
      - ブラウザ内
      - ターミナル (CLI)
      - 組み込み環境
      - ミドルウェア内 (例: Envoy)
  - 「どんな言語でも書けるし、どんな場所でも動かせる」

---

![bg](image-3.png)

---
<!--
_class: hero
-->

# wasm を動かしてみよう<br>（ターミナル）

---

# setup

- Windows...???
- WSLでなんとか頑張れるかもしれない

----

## 1. Wasmtime のインストール
```bash
# macOS / Linux
curl https://wasmtime.dev/install.sh -sSf | bash

# または Homebrew (macOS)
brew install wasmtime

# インストール確認
wasmtime --version
```

----

## 2. Rust + wasm32-wasi ターゲットのインストール
```bash
# Rust のインストール
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# インストール後、シェルを再起動するか以下を実行
source "$HOME/.cargo/env"

# wasm32-wasi ターゲットの追加
rustup target add wasm32-wasip1

# インストール確認
rustc --version
rustup target list | grep wasm32-wasip1
```

----

## 3. wasm-tools のインストール
```bash
# cargo 経由でインストール
cargo install wasm-tools

# インストール確認
wasm-tools --version
```

---

# wasm プログラムの作成

---

# WAT形式のコードを覚えよう

- WAT (WebAssembly Text Format) とは
    - WebAssemblyのテキスト表現形式で、人間が読み書きできるようにしたもの
    - バイナリ形式(.wasm)と1対1で相互変換可能
        - 命令は直接記述する
    - S式(S-expression)の構文を採用し、Lispに似た括弧ベースの記法

---

# addの実装

```wasm
(module
  ;; add関数: 2つのi32整数を受け取り、その合計を返す
  (func $add (export "add") (param $a i32) (param $b i32) (result i32)
    local.get $a
    local.get $b
    i32.add
  )
)
```

---

# コンパイルと実行

```bash
wasm-tools parse add.wat -o add.wasm
wasmtime --invoke 'add' add.wasm 10 20
# 出力: 30
```

---

### フィボナッチ数の計算

```wasm
(module
  (func $fibonacci (export "fibonacci") (param $n i32) (result i32)
    local.get $n
    i32.const 2
    i32.lt_s
    if
      i32.const 1
      return
    end
    local.get $n
    i32.const 1
    i32.sub
    call $fibonacci
    local.get $n
    i32.const 2
    i32.sub
    call $fibonacci
    i32.add
  )
)
```

---

```bash
wasm-tools parse fibonacci.wat -o fibonacci.wasm
wasmtime --invoke fibonacci fibonacci.wasm 10
# 出力: 89
```

---

### 文字の表示（ようやくhello world）

```wasm
(module
  (import "wasi_snapshot_preview1" "fd_write" 
    (func $fd_write (param i32 i32 i32 i32) (result i32)))
  (memory 1)
  (export "memory" (memory 0))
  (data (i32.const 8) "Hello, World!\n")
  
  (func $main (export "_start")
    i32.const 0
    i32.const 8
    i32.store
    
    i32.const 4
    i32.const 14
    i32.store
    
    i32.const 1
    i32.const 0
    i32.const 1
    i32.const 20
    call $fd_write
    drop
  )
)
```

---

```bash
wasm-tools parse helloworld.wat -o helloworld.wasm
wasmtime helloworld.wasm
# 出力: Hello, World!
```

---

# wasm を動かしてみよう（ブラウザ）

---

# fibを動かしてみよう

```html
<html>
  <head>
    <title>My first wasm</title>
    <script async type="text/javascript">
      WebAssembly.instantiateStreaming(fetch("fibonacci.wasm"), {}).then(
      (obj) => {
        let answer = obj.instance.exports.fibonacci(20);
        alert("answer: fib(20) = " + answer.toString());
      });
    </script>
  </head>
  <body>
    <h1>Wasm working on browser</h1>
  </body>
</html>
```

---

# このファイルを...

```bash
# fibonacci.wasm と同じディレクトリに保存
vim index.html
python3 -m http.server 8080
```

- `http://localhost:8080` にアクセスしよう

---

# hello world を動...かせる？

（質問タイム）

- hello worldってブラウザで動くの？
- どう動くの？
- さっきのファイルはどう変える？

---

# 実験結果

---

# 動かすために

- あと一つ必要なものがある

---

# WASIについて

- **WASI (WebAssembly System Interface) とは？**
    - Wasm VMで「Hello World」のようなOS機能（標準出力など）を使うための**抽象化されたインターフェース**
- Wasmバイナリー内でWASI仕様を満たす関数を呼び出すことで、システム機能を利用できる
- **例:** 標準出力に書き出す命令

---

![bg](image-2.png)

---

# ブラウザでWASIをエミュレートしよう

---

```html
<html>
  <head>
    <title>My first wasm</title>
    <!-- browser_wasi_shim をCDNから読み込む -->
    <script async type="module">
      import {
        WASI, File, OpenFile, ConsoleStdout
      } from 'https://cdn.jsdelivr.net/npm/@bjorn3/browser_wasi_shim@0.4.2/+esm';

      let fds = [
        new OpenFile(new File([])), // stdin
        ConsoleStdout.lineBuffered(msg => console.log(`[stdout] ${msg}`)),
        ConsoleStdout.lineBuffered(msg => console.warn(`[stderr] ${msg}`)),
      ];
      let wasi = new WASI([], [], fds);
      let importObject = { "wasi_snapshot_preview1": wasi.wasiImport };
      WebAssembly.instantiateStreaming(fetch("helloworld.wasm"), importObject).then(
        (obj) => { wasi.start(obj.instance); });
    </script>
  </head>
  <body>
    <h1>Wasm working on browser</h1>
  </body>
</html>
```


---

# 動作確認

---

# ここまでのまとめ

- Wasmの基本的な概念を理解した
- Wasmのダンプルコードを書いてみた
- WasmをCLI、ブラウザでそれぞれ動かした

---
<!--
_class: hero
-->

# AI時代に向けた実践

### 大学の授業なのでかっこよく言ってみた...

---

# wasmのサンドボックスについて

- Wasmはセキュリティを考慮して設計されている
  - **メモリ分離:** Wasmモジュールは独自の線形メモリ空間内でのみ動作し、ホスト環境のメモリに直接アクセスできない
  - **スタック保護:** 呼び出しスタックはホスト環境から分離され、スタックオーバーフロー攻撃を緩和
  - **WASI (WebAssembly System Interface):** システム呼び出しへのアクセスは capability-based な権限モデルで制御
  - などなど...

---

# 参考になるであろう資料

- [n月刊ラムダノート Vol.4, No.1(2024)](https://www.lambdanote.com/products/nmonthly-vol-4-no-1-2024-ebook)
  - #2 WebAssemblyの制約を越える（齋藤優太）
    - 齋藤さんはruby.wasmやswiftwasm/WasmKitの開発者

![bg right:30% w:250](image-4.png)

---

# WASIを少し深掘りする

- OSについて
    - 「システムコール」って聞いたことがありますか？
    - 「システムコール」にはどんなものがありますか？
    - 「ファイルをオープンする」ってどんなシステムコールですか？

---

# WASIで「ファイルをオープンする」話

---

# preopensの仕組み

- ホスト側でのWasmモジュール起動時に、アクセスを許可するディレクトリを事前にファイルディスクリプタとして開いておく仕組み
    - preopensで指定されたディレクトリ配下のみにアクセスが制限
    - それ以外のファイルシステムは完全に不可視となる
- デフォルトではホストのファイルシステムに一切アクセスできない
    - allow-list 方式

---

![bg](image-5.png)

---
<!--
_class: hero
-->

# 応用例

---

# AIエージェントの動作と課題

---

# システム操作を制御し切れないかもしれない問題

- 予期しない/誤ったファイル削除操作をする可能性がある
    - 例: `~/` と誤って `/` を指定して削除する
    - 例: プロジェクト外の重要なファイルを削除する
- LLMの性質上、プロンプトなどで完全に防ぐのは困難

---

# FYI: Xでバズった例

- https://x.com/mugisus/status/1940127947962396815

---

# 防御策の例

- よくある方法は、エージェントをコンテナで実行させる
    - 動作、起動、設定が煩雑
    - 特にMacのdockerなどでは、ホスト/ゲストのファイル共有をすると遅い
    - その他オーバーヘッドが無視しづらい
- LinuxではseccompやLSMも活用可能
    - Macでは...？

---

# ここでwasmのサンドボックスを活用できないか？

---

# rm コマンドをwasmで置き換えるアイデア

- rm コマンド自体をWasmで実装し、任意のランタイム（wasmtime）など経由で実行する
    - wasmtimeのオプションで、共有するディレクトリをプロジェクト内部のみに限定する
    - これによりプロジェクト外のファイルを操作できなくする
- wasmtimeをラップするrmコマンドをシェルで実装すれば、エージェントからは隠蔽される
    - エージェントの `$PATH` 設定以外何も変更する必要がない

---

# 実装例

- 今回、Rustにより簡易的に実装してみた
- https://github.com/udzura/seckun_rm
- HACK:
    - WASIはまだ `getcwd()` 相当のサポートが弱い
    - `PWD` という環境変数を現在ディレクトリの代わりにした

---

# ビルドしてみよう

```bash
git clone https://github.com/udzura/seckun_rm.git
cd seckun_rm
cargo build --target wasm32-wasip1 --release
# out: target/wasm32-wasip1/release/rm.wasm
file target/wasm32-wasip1/release/rm.wasm
```

---

# 同梱している `rm.sh` を確認しよう

```bash
#!/usr/bin/env bash

RM_WASM_PATH=${RM_WASM_PATH:-target/wasm32-wasip1/release/rm.wasm}
wasmtime --dir `pwd` --env PWD=`pwd` $RM_WASM_PATH "$@"
```

---

# 動作確認

```bash
export SECKUN_RM_WASM=$(pwd)/target/wasm32-wasip1/release/rm.wasm
touch hoge.txt
./rm.sh -iv hoge.txt
./rm.sh -iv /etc/hosts # これは消せる？
```



---

# AIエージェントにこのrmを使わせる

- 事前準備としてこの `rm.sh` を `rm` として保存し、実行権限を付与する

```bash
mkdir -p ~/.local/bin
cp rm.sh ~/.local/bin/rm
chmod +x ~/.local/bin/rm
# rmを編集してSECKUN_RM_WASMのパスを修正する
```

---

- Gemini CLIの例
  - 簡易的に実行時のPATHを変更。ちゃんとやるなら設定を永続化

```bash
export PATH=~/.local/bin:$PATH
gemini
```

<!-- TODO: Claude Codeの例 -->

---

# 防御できているか確認しよう

- Use your prompt!!

---

# 今日のまとめ

- Wasmの基本的な概念、利用方法を理解した
- Wasmのサンドボックス特性を活かした応用例を紹介した
- AIエージェントの安全なシステム操作にWasmを活用するアイデアを示した