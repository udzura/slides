----
marp: true
# theme: seckun
paginate: true
title: WebAssemblyと安全なプログラム実行
description: For SECKUN 2025
# header: "Running ruby.wasm on Pure Ruby Wasm Runtime"
image: https://udzura.jp/slides/2025/seckun/#TODO
size: 16:9
----

# WebAssemblyと安全なプログラム実行

- SECKUN 2025
- Uchio Kondo

----
<!--
_class: profile
-->

# 講師について

- 近藤宇智朗
- 所属: SmartHR
- インフラ・基盤っぽいことをするProduct Engineer

----

# ToC

- この講義の前提知識の整理
- WebAssemblyとは何か
- WebAssemblyを動かす
    - 簡単なWebAssemblyに触れる
    - PC上でWebAssemblyを動かす
- WebAssembly System Interface (WASI) について
- WASI のサンドボクシング
    - ユースケース考
- 発展的な話題

----
<!--
_class: hero
-->

# この講義の前提知識の整理

----
<!--
_class: hero
-->

# WebAssemblyとは何か

----

# WebAssemblyとは何か

* Web上で高速に動作するバイナリ形式の実行ファイル
* JavaScript以外の言語で書かれたコードをWebブラウザで実行可能にする技術
* 2019年にW3Cの標準として正式に承認された比較的新しい技術

----

# WebAssemblyの呼び方について

* 略称：**Wasm**（ワズム）
* 「Web」という名前だが、実際にはWeb以外でも利用可能

----

# WebAssemblyの実行環境

* **ブラウザ環境**：Chrome、Firefox、Safari、Edge等の主要ブラウザで対応
* **サーバサイド環境**：Node.js、Deno、WASMRuntimeを使用してサーバでも実行可能
* **エッジコンピューティング**：Cloudflare Workers等のエッジ環境でも動作
* **スタンドアロン**：WASI（WebAssembly System Interface）によりOS上で直接実行

----

# 対応プログラミング言語

* **C/C++**：Emscriptenを使用してコンパイル
* **Rust**：wasm-packツールチェーンでビルド
* **Go**：Go 1.11以降でネイティブサポート/tinygoも作成可能
* **C#/.NET**：Blazor WebAssemblyで対応
* **Python**：Pyodideプロジェクトで実行可能
* **その他**：AssemblyScript、Kotlin、Swift等も対応中

----

# WebAssemblyの主要な特徴

* **高速性**：ネイティブに近い実行速度を実現
* **安全性**：サンドボックス環境で実行され、メモリ安全
* **ポータビリティ**：異なるプラットフォーム間で同一のバイナリが動作
* **コンパクト性**：効率的なバイナリ形式で小さなファイルサイズ

----

# 主要なユースケース

* **ゲーム開発**：Unityやアンリアルエンジンのゲームをブラウザで実行
* **画像・動画処理**：PhotoshopやFigma等のクリエイティブツール
* **科学計算**：数値計算や機械学習モデルの実行
* **既存アプリの移植**：デスクトップアプリケーションのWeb化
* **暗号化処理**：ブラウザサイドでの高速な暗号化・復号化処理

----
<!--
_class: hero
-->

# WebAssemblyを動かす


----

# WebAssemblyの動かしかた - 概要

* **Step 1**：C/C++、Rust等でソースコードを作成
* **Step 2**：WebAssembly用にコンパイルして.wasmファイルを生成
* **Step 3.1**：JavaScriptから.wasmファイルを読み込み
* **Step 3.2**：ブラウザで実行・動作確認

----

# Step 1: C言語でサンプルコード作成

```c
// math.c
int add(int a, int b) {
    return a + b;
}

int multiply(int a, int b) {
    return a * b;
}

int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
```

* シンプルな数学関数を定義
* WebAssemblyにエクスポートする関数を作成

----

# Step 2: Emscriptenでコンパイル

```bash
# Emscriptenのインストール（初回のみ）
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk
./emsdk install latest
./emsdk activate latest

# .wasmファイルの生成
emcc math.c -o math.wasm \
  -s EXPORTED_FUNCTIONS='["_add", "_multiply", "_factorial"]' \
  -s EXPORTED_RUNTIME_METHODS='["ccall", "cwrap"]'
```

* Emscripten：C/C++をWebAssemblyにコンパイルするツール
* EXPORTED_FUNCTIONSで外部から呼び出す関数を指定

----

# Step 3: JS + HTMLファイルでブラウザ実行

```html
<!DOCTYPE html>
<html>
<head>
    <title>WebAssembly Demo</title>
</head>
<body>
    <h1>WebAssembly 実行例</h1>
    <div id="result">読み込み中...</div>
    <button onclick="runCalculation()">計算実行</button>
    
    <script>
        let wasmFunctions;
        
        async function init() {
            const wasmModule = await WebAssembly.instantiateStreaming(
                fetch('math.wasm')
            );
            wasmFunctions = wasmModule.instance.exports;
            document.getElementById('result').textContent = '準備完了';
        }
        
        function runCalculation() {
            if (wasmFunctions) {
                const result = wasmFunctions.add(15, 25);
                document.getElementById('result').textContent = 
                    `WebAssemblyで計算: 15 + 25 = ${result}`;
            }
        }
        
        init();
    </script>
</body>
</html>
```

* HTTPサーバー経由でアクセス（file://では動作しない場合がある）

----

# wasmtimeランタイムでの実行

```bash
# wasmtimeのインストール
curl https://wasmtime.dev/install.sh -sSf | bash

# C言語からWASIターゲット用にコンパイル
clang --target=wasm32-wasi -o math.wasm math.c

# wasmtimeで直接実行
wasmtime math.wasm
```

* **wasmtime**：WebAssemblyのスタンドアロンランタイム
* **WASI**：WebAssembly System Interface（システムコール標準）
* ブラウザを使わずにコマンドラインから直接.wasmファイルを実行

----
<!--
_class: hero
-->

# WebAssembly System Interface (WASI) について

----

# WASI（WebAssembly System Interface）とは

* **定義**：WebAssemblyがOS機能にアクセスするための標準インターフェース
* **目的**：ブラウザ外でWebAssemblyを安全に実行可能にする
* **提供機能**：ファイルシステム、ネットワーク、環境変数等へのアクセス
* **セキュリティ**：サンドボックス化されたシステムコール
* **ポータビリティ**：異なるOS間でも同一のWASMバイナリが動作

----

# WASIが解決する問題

* **従来の課題**：WebAssemblyはブラウザ内のサンドボックスでしか動作できない
* **WASIの解決策**：安全性を保ちながらシステムリソースへアクセス可能
* **具体例**：
  - ファイルの読み書き
  - コマンドライン引数の取得
  - 環境変数の参照
  - 標準入出力の使用

----

# WASI対応のC言語サンプル

```c
// wasi_example.c
#include <stdio.h>

int main() {
    printf("Hello from WebAssembly!\n");
    
    int a = 10, b = 20;
    int sum = a + b;
    
    printf("計算結果: %d + %d = %d\n", a, b, sum);
    
    return 0;
}
```

----

```bash
# コンパイルと実行
clang --target=wasm32-wasi -o wasi_example.wasm wasi_example.c
wasmtime wasi_example.wasm

# 出力:
# Hello from WebAssembly!
# 計算結果: 10 + 20 = 30
```

----
<!--
_class: hero
-->

# WASI のサンドボクシング

----
<!--
_class: hero
-->

# 発展的な話題

----

