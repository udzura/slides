---
marp: true
theme: udzura-archive
paginate: true
size: 16:9
title: "Wasmの例外を見てみよう"
description: "Fukuoka Wasm #1 / Legacy EHと新しい例外命令"
header: "**Uchio Kondo** / Slides"
footer: "Fukuoka Wasm #1"
---

<!-- _class: hero -->

# Wasmの例外を見てみよう

Legacy EHと、新しい例外命令

Fukuoka Wasm #1 / @udzura

<!--
目安 0:00–0:20（20秒）。本編22枚、合計15分。参考資料2枚は時間外。
タイトルとイベント表記は仮。開催日や所属などは未記入。
今日は言語の例外がWasmでどう動くか、生成された命令から見ていきます。
-->

---

# きっかけ：リンクは通ったのに動かない

```text
CompileError: WebAssembly.instantiate():
module uses a mix of legacy and new
exception handling instructions
```

Rust + Emscripten + C の組み合わせで再現した

「例外の命令に、新旧がある……？」

<!--
0:20–0:50（30秒）。エラーは今回の調査で実際に再現したもの。個人の過去の障害体験としては語らない。
まずエラーを見せ、最後にここへ戻る。
実測: ../wasm-exception-research/results/rust-standard-run.txt
-->

---

# 今日見るもの

1. Wasmの例外の概要、経緯
2. WATで投げる・捕まえる
3. C++の `try/catch` をコンパイルする
4. Cの `setjmp/longjmp` も例外になる
5. 新旧の命令が混ざるとどうなるか

<!--
0:50–1:10（20秒）。WATはWasmのテキスト表現。読めなくても、値を積む・投げる・捕まえるの順で追えば大丈夫と伝える。
-->

---

# Wasmにも例外処理の命令がある

- EH = Exception Handling
- 例外は「タグ」と「値の組」で表される
- 投げると、呼び出し元をたどってハンドラを探す
- C++の例外や、Cの非局所ジャンプの実装に使える

メモリ範囲外アクセスなどの trap とは別の仕組み

<!--
1:10–1:55（45秒）。タグは例外を区別するための識別子で、ペイロードの型も定める。
Wasm内のcatchではtrapを捕捉しない。JS側からRuntimeErrorをcatchできることと区別する。
出典: https://github.com/WebAssembly/spec/blob/main/proposals/exception-handling/Exceptions.md
-->

---

# 「古い例外」を二つに分ける

| 方式 | どう実現するか |
| --- | --- |
| EmscriptenのJSベース例外 | JSの例外と補助関数を使う |
| Wasm Legacy EH | `try` / `catch` / `rethrow` |
| 標準のWasm EH | `try_table` / `throw_ref` |

今日比較するのは、主に下の二つ

<!--
1:55–2:40（45秒）。JSベースの例外とLegacy Wasm EHは同じものではない。
throw命令は新旧で共通。表は方式を見分ける主な命令だけを示している。
出典: https://emscripten.org/docs/porting/exceptions.html
出典: https://github.com/WebAssembly/exception-handling/blob/main/proposals/exception-handling/legacy/Exceptions.md
-->

---

# 新方式では、例外そのものを値として扱う

- 2023年10月：`exnref` を使う方式への変更に合意
- `try_table`：捕捉する例外と分岐先を並べる
- `exnref`：捕捉した例外への参照
- `throw_ref`：その参照を使って再送出する

現在のWebAssembly 3.0仕様には新方式が載っている

<!--
2:40–3:20（40秒）。Legacyはcatchのスコープを指定してrethrowする。
新方式は例外への参照を受け取り、元のcatchの構造に縛られず再送出できる。単なる名前変更ではない。
2023年10月は設計変更の合意時期であり、全ブラウザでの実装完了時期ではない。
出典: https://github.com/WebAssembly/meetings/blob/main/main/2023/CG-10.md#exception-handling-vote-on-proposal-to-re-introduce-exnref
出典: https://webassembly.github.io/spec/core/syntax/instructions.html#control-instructions
-->

---

<!-- _class: small-code -->

# まずはWAT：Legacyで42を投げる

```wat
(module
  (tag $error (param i32))
  (func (export "answer") (result i32)
    try (result i32)
      i32.const 42
      throw $error
    catch $error
      ;; スタック上に42が来る
    end))
```

`throw` で投げ、タグが一致する `catch` で受け取る

<!--
3:20–4:00（40秒）。i32.constはスタックに整数を積む。throwがその値を例外のペイロードにする。
catch後には同じ値がスタックにあり、そのまま関数の戻り値になる。
検証済みのソース: ../wasm-exception-research/src/legacy.wat
-->

---

<!-- _class: small-code -->

# 新方式：捕まえたらラベルへ分岐する

```wat
(module
  (tag $error (param i32))
  (func (export "answer") (result i32)
    block $caught (result i32)
      try_table (catch $error $caught)
        i32.const 42
        throw $error
      end
      unreachable
    end))
```

`$caught` のブロックを抜け、42を結果として受け取る

<!--
4:00–4:55（55秒）。catch節はtry_tableの先頭に移った。捕捉後にブロックの末尾を抜けることを指で追う。
unreachableは通常経路用。この例ではthrowして捕捉されるので実行されない。
新方式のcatchは独立した旧catch命令ではなく、try_tableの即値に含まれる節。
検証済みのソース: ../wasm-exception-research/src/standard.wat
-->

---

# 実際に動かすと、どちらも42

```sh
wasm-tools parse standard.wat -o standard.wasm
```

```js
const bytes = fs.readFileSync("standard.wasm");
const wasmModule = new WebAssembly.Module(bytes);
const instance = new WebAssembly.Instance(wasmModule);
console.log(instance.exports.answer()); // 42
```

Node.js 26.8.1で、新旧両方の動作を確認

<!--
4:55–5:25（30秒）。JSは説明用の抜粋。fsのimportなどは省略。
デモする場合は調査ディレクトリで以下を実行すればよい。時間がなければ結果だけ。
wasm-tools parse src/standard.wat -o build/wat-standard.wasm
node src/check-wat.cjs build/wat-standard.wasm
同様にlegacy.watもanswer=42。全ランタイムで検証したわけではない。
-->

---

# 再送出には例外参照を使う

```wat
block $saved (result exnref)
  try_table (catch_all_ref $saved)
    i32.const 42
    throw $error
  end
  unreachable
end
throw_ref
```

内側の `try_table` を抜けた後でも、同じ例外を投げ直せる

<!--
5:25–6:10（45秒）。検証済みrethrow.watの内側だけを抜粋。外側のハンドラがこれを捕まえて42を返す。
catchではペイロードだけ、catch_refではペイロードと例外参照を受け取る。
catch_all_refはタグを問わず例外参照を受け取る。trapまで捕まえるという意味ではない。
ソース: ../wasm-exception-research/src/rethrow.wat
-->

---

# C++の例外をコンパイルする

```cpp
extern void may_throw();
int catch_only() {
  try {
    may_throw();
    return 0;
  } catch (...) {
    return 42;
  }
}
```

まずはリンクせず、関数一つの `.o` を見る

<!--
6:10–6:45（35秒）。ランタイム全体をリンクすると命令が増えて追いづらいので、オブジェクトで読む。
may_throwの定義は不要。これは単独実行できるプログラムではなく、生成命令を調べる例。
ソース: ../wasm-exception-research/src/catch-only.cpp
-->

---

# Emscriptenで新旧を選ぶ

```sh
# Legacy
em++ -O1 -fwasm-exceptions \
  -sWASM_LEGACY_EXCEPTIONS=1 -c catch-only.cpp

# 標準
em++ -O1 -fwasm-exceptions \
  -sWASM_LEGACY_EXCEPTIONS=0 -c catch-only.cpp
```

手元のEmscripten 6.0.9では、既定はまだLegacy

<!--
6:45–7:25（40秒）。二つのコマンドは同名の.oを生成するので、比較時は-oで出力先を分ける。
-fwasm-exceptionsでWasm EHを使い、別の設定で新旧を選ぶ。
通常のプロジェクトではコンパイルとリンクの両方に設定する。
出典: https://emscripten.org/docs/tools_reference/settings_reference.html#wasm-legacy-exceptions
ローカル設定: ../wasm-exception-research/results/local-default-setting.txt
-->

---

# C++も、コンパイラとランタイムの共同作業

```text
try_table catch …
  call may_throw
  …
end
…
call __cxa_begin_catch
…
call __cxa_end_catch
```

捕捉の制御はWasm命令、例外の管理はランタイムも担当

<!--
7:25–8:05（40秒）。新方式の逆アセンブルを構造がわかるように省略したもの。完全なWATではない。
C++のtry/catchが全部ライブラリ呼び出しになるわけでも、ランタイムが不要になるわけでもない。
同梱Clang直接とem++で同じ条件の.oを作ると、両方626 bytesでバイナリ全体が一致した。
実測: ../wasm-exception-research/results/catch-emcc-disassembly.txt
-->

---

# Cにはtry/catchがないけれど

```c
static jmp_buf env;

__attribute__((noinline)) static void jump(void) {
  longjmp(env, 42);
}

int probe(void) {
  switch (setjmp(env)) {
    case 0: jump(); return -1;
    case 42: return 42;
    default: return -1;
  }
}
```

<!--
8:05–8:50（45秒）。ヘッダ#include <setjmp.h>とmainは省略。
setjmpは初回0を返す。jumpの中のlongjmpで戻ってくると42を返す。
C規格の呼び出し位置の制約に合わせ、setjmpをswitchの制御式に置いている。
ソース: ../wasm-exception-research/src/sjlj.c
-->

---

# setjmp/longjmpにもWasm EHを使える

```sh
emcc -O1 -sSUPPORT_LONGJMP=wasm \
  -sWASM_LEGACY_EXCEPTIONS=0 \
  sjlj.c -o standard.js
```

| 箇所 | 生成されるもの |
| --- | --- |
| `setjmp` を使う関数 | `try_table` とジャンプ先の判定処理 |
| `longjmp` | `__wasm_longjmp` の呼び出し |
| `__wasm_longjmp` の中 | `throw` 命令 |

<!--
8:50–9:35（45秒）。Cの例外構文を変換しているのではなく、非局所ジャンプの実装にEHを使っている。
-sWASM_LEGACY_EXCEPTIONS=0だけではSjLj方式は変わらない。SUPPORT_LONGJMP=wasmが必要。
出典: https://emscripten.org/docs/porting/setjmp-longjmp.html
実測: ../wasm-exception-research/results/standard-disassembly.txt
-->

---

# Cの関数へ戻るまで

```text
probe(): setjmpで戻り先を用意
  │
  └─ try_table（コンパイラが生成）
       └─ jump()
            └─ __wasm_longjmp(env, 42)
                 └─ throw
       ↓ 捕捉・戻り先を確認
     setjmpが42を返した経路へ
```

「例外を書いていないC資産」にもEH命令が入る

<!--
9:35–10:15（40秒）。setjmpというWasm命令があるわけではない。
longjmpのペイロードは単純な整数42だけではなく、ジャンプ環境を扱うランタイム情報。図は制御の流れ。
対象が外側のsetjmpなら、そこまで伝播させる処理も必要になる。
-->

---

# ここでRustも混ぜてみる

```text
Rustのアプリ       標準EHでコンパイル
Cのライブラリ     標準EHでコンパイル
Rustの配布済みstd Legacy EHが残っている
                  ↓
                リンク成功
                  ↓
                読み込み失敗
```

アプリに指定したフラグは、配布済みstdには適用されない

<!--
10:15–11:05（50秒）。冒頭のエラーへ戻る。今回のrustcは1.100.0-nightly。
RustのサンプルはCのprobeが42を返すことと、Rustのpanicをcatch_unwindで捕捉できることを確認する。
CのlongjmpはC内で完結し、Rustフレームを越えない。言語をまたぐunwindの安全性は別の問題。
実測: ../wasm-exception-research/results/rust-standard-run.txt
-->

---

# C同士でも、最適化すると失敗した

旧形式の `.o` と新形式の `.o` を一緒にリンク

| 最終リンク | リンク結果 | Node.jsで実行 |
| --- | --- | --- |
| `-O0` / `-O1` | 成功 | 成功 |
| `-O2` | 成功 | CompileError |

`-O2` の `main` には、`try` と `try_table` が両方入った

<!--
11:05–11:50（45秒）。逆アセンブルで、O2では処理が同じmainに入ることを確認した。
混在がO1なら許されるという仕様ではない。このNode/V8での観測結果。
一度動いたことやリンク成功だけを、互換性の根拠にしない。
実測: ../wasm-exception-research/results/mixed-standard-O2-disassembly.txt
実測: ../wasm-exception-research/results/mixed-standard-O2-run.txt
-->

---

# 形式を揃えて、作り直す

- C / C++：コンパイルとリンクの両方に設定
- Rust：コード生成の設定とリンク設定を揃える
- Rustのstdも新方式にするなら `-Zbuild-std`
- `.o` / `.a` や依存ライブラリのキャッシュも確認

最終リンクのフラグだけ変えても、古い命令は残る

<!--
11:50–12:45（55秒）。今回の非LTOオブジェクトで実測。LTOを含む一般論に広げすぎない。
Rustは-C llvm-args=-wasm-use-legacy-eh=0と、Emscriptenに渡す-C link-arg=-sWASM_LEGACY_EXCEPTIONS=0を両方揃える。
標準ライブラリ再ビルドにはnightlyとrust-srcを使った。今回の環境では成功。
出典: https://doc.rust-lang.org/rustc/platform-support/wasm32-unknown-emscripten.html#emscripten-abi-compatibility
-->

---

# 再ビルドと変換、両方試した

| 対応 | 今回の実行結果 |
| --- | --- |
| stdを含めて標準EHで再ビルド | 成功 |
| Binaryenで標準EHに変換 | 成功 |

```sh
wasm-opt mixed.wasm --translate-to-exnref \
  -o standard.wasm
```

命令形式の変換で、あらゆるABI不一致が直るわけではない

<!--
12:45–13:30（45秒）。混在したRust+Cの最終Wasmに変換を適用し、CのlongjmpとRustのpanic捕捉が動いた。
JSベース例外とWasm EHの違いを、このパスが直すという意味ではない。
採用する場合はJS側が読むWasmのパスも合わせ、最終成果物で試験する。
実測: ../wasm-exception-research/results/rust-translated-run.txt
実測: ../wasm-exception-research/results/rust-rebuilt-run.txt
-->

---

# 最後は、できあがったWasmを見る

```sh
wasm-objdump -d app.wasm
```

- `try` / `rethrow` → Legacyの目印
- `try_table` / `throw_ref` → 標準方式の目印
- `throw` は新旧共通
- 配布先のランタイムで、実際に投げて捕まえる

<!--
13:30–14:15（45秒）。target_featuresの+exception-handlingだけでは新旧を判別できなかった。
今回の実行環境はNode 26.8.1。ブラウザや古いNodeの対応は別途確認が必要。
wasm-objdumpはWABT、wasm-optはBinaryenのツール。
最終Wasmの読み込みと例外経路の両方を試す。
-->

---

# Wasmの例外、見えてきたでしょうか

- 新方式は、例外参照とラベルへの分岐を使う
- C++もCも、コンパイラとランタイムが協調する
- `setjmp/longjmp` を使うCにも例外命令が入る
- 新旧を揃えるときは、標準ライブラリまで見る

まずは小さいWATと `.o` から読んでみるとよさそう

<!--
14:15–15:00（45秒）。概要、WAT、C++、C、混在問題を一周したことを振り返る。
質疑は別枠想定。質疑込み15分なら実行デモを省略し、再送出スライドを補足扱いにする。
-->

---

<!-- _class: references -->

# 参考資料：仕様とツールチェーン

- [現行のException Handling explainer](https://github.com/WebAssembly/spec/blob/main/proposals/exception-handling/Exceptions.md)
- [Legacy Exception Handling explainer](https://github.com/WebAssembly/exception-handling/blob/main/proposals/exception-handling/legacy/Exceptions.md)
- [Emscripten: C++ Exceptions Support](https://emscripten.org/docs/porting/exceptions.html)
- [Emscripten: C setjmp-longjmp Support](https://emscripten.org/docs/porting/setjmp-longjmp.html)
- [Rust: Emscripten ABI Compatibility](https://doc.rust-lang.org/rustc/platform-support/wasm32-unknown-emscripten.html#emscripten-abi-compatibility)

<!-- 本編時間外。各スライドのノートにも出典と実験ログを記載。 -->

---

<!-- _class: references -->

# 参考資料：今回の実験

- [日本語の調査メモ](../wasm-exception-research/README.md)
- [WATの例](../wasm-exception-research/src/standard.wat) / [C++の例](../wasm-exception-research/src/catch-only.cpp) / [Cの例](../wasm-exception-research/src/sjlj.c)
- [比較実験](../wasm-exception-research/run.py) / [修正方法の実験](../wasm-exception-research/run-recovery.py)

Emscripten 6.0.9 / Node.js 26.8.1 / Binaryen 133
Rust 1.100.0-nightly（2026-08-17）

調査・実測：2026年10月19〜20日

<!--
本編時間外。リンクはリポジトリ内の相対パス。公開時には掲載先に合わせて調整する。
既定値やランタイム対応は変わり得るため、実測した版を明示する。
-->
