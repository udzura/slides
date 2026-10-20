# Wasm 例外命令の変更：調査と実験

調査日：2026-10-19。仕様・公式ドキュメントと、手元のコンパイラでの実測を区別して記載する。

**発表の中心にできる結論**：Wasm の例外処理は、Legacy の `try` / `catch` / `rethrow` から、`try_table` と例外参照 `exnref` / `throw_ref` を使う方式に変わった。C の `setjmp` / `longjmp` もこの変更の影響を受ける。Rust と C を組み合わせる場合、アプリのオプションだけでなく、Rust の標準ライブラリを含む全入力の方式を揃える必要がある。**リンク成功は実行可能性を保証しない。**

## 1. 用語と命令

### まず三つを分ける

| 方式 | 実現方法 | 今回の区別 |
| --- | --- | --- |
| Emscripten の JS ベース例外 | JS の例外処理と補助関数を利用 | Wasm Legacy EH とは別物 |
| Wasm Legacy EH | `try`, `catch`, `catch_all`, `rethrow`, `delegate`, `throw` | 旧提案に基づくネイティブ Wasm 命令 |
| 標準の Wasm EH | `try_table`, `throw`, `throw_ref`、型 `exnref` | 新方式。WebAssembly 3.0 の仕様に掲載 |

「古い例外」と言うと JS ベースと Legacy Wasm EH の両方を指し得るので、発表では明示的に分ける。[Emscripten の例外サポート](https://emscripten.org/docs/porting/exceptions.html)、[WebAssembly 3.0 の命令定義](https://webassembly.github.io/spec/core/syntax/instructions.html#control-instructions)

旧提案から現在の方式への変更は 2023 年 10 月の CG 会合で合意された。新方式では捕捉した例外そのものを参照値として扱える。ハンドラの構造に依存する再送出から、値を使った再送出へ変わったことが重要で、単なる命令名の変更ではない。[現行 EH explainer](https://github.com/WebAssembly/spec/blob/main/proposals/exception-handling/Exceptions.md)、[当時の議事録](https://github.com/WebAssembly/meetings/blob/main/main/2023/CG-10.md#exception-handling-vote-on-proposal-to-re-introduce-exnref)

### Legacy の使い方

`try` の本体に続けて `catch tag` / `catch_all` とハンドラ本体を置く。タグ付きの捕捉ではペイロードを受け取る。`rethrow` は捕捉スコープを深さで指定して再送出し、`delegate` は外側へ例外処理を委ねる。例外オブジェクト自体を `exnref` の値として持ち回る機能はない。[Legacy explainer](https://github.com/WebAssembly/exception-handling/blob/main/proposals/exception-handling/legacy/Exceptions.md)

自作の実行可能な [src/legacy.wat](src/legacy.wat) より：

```wat
(tag $error (param i32))
(func (export "answer") (result i32)
  try (result i32)
    i32.const 42
    throw $error
  catch $error
    ;; スタック上にペイロードの 42 が来る
  end)
```

### 新方式の使い方

`try_table` の先頭に「どの例外を、どのラベルへ渡すか」を列挙する。ハンドラは分岐先に置く。`block` のラベルへ分岐すると、その `block` の末尾を抜けた位置に移動する。[標準の制御命令](https://webassembly.github.io/spec/core/syntax/instructions.html#control-instructions)

自作の [src/standard.wat](src/standard.wat) は、同じく 42 を返す：

```wat
(tag $error (param i32))
(func (export "answer") (result i32)
  block $caught (result i32)
    try_table (catch $error $caught)
      i32.const 42
      throw $error
    end
    unreachable
  end)
```

`unreachable` はこの例で通常経路が到達しないことを表す。捕捉時には `block` から出るので、実行されない。

| `try_table` の節 | 条件 | 分岐先に渡る値 |
| --- | --- | --- |
| `catch tag label` | タグ一致 | ペイロード |
| `catch_ref tag label` | タグ一致 | ペイロードと例外参照 |
| `catch_all label` | 捕捉可能な例外すべて | なし |
| `catch_all_ref label` | 捕捉可能な例外すべて | 例外参照 |

ここでの `catch` などは **`try_table` の即値に含まれる節**であり、Legacy の独立した `catch` 命令とは異なる。`throw_ref` はスタック上の例外参照を再送出する。[現行 EH explainer](https://github.com/WebAssembly/spec/blob/main/proposals/exception-handling/Exceptions.md)

[src/rethrow.wat](src/rethrow.wat) は `catch_all_ref` で受けた参照を、内側の `try_table` の外で `throw_ref` し、外側で捕捉して 42 を返す。3 本ともアセンブルして Node.js で実行し、戻り値を検証済み。

### バイトコードの目印

| 要素 | バイト値 | 判別上の注意 |
| --- | --- | --- |
| Legacy `try` | `06` | 旧方式の目印 |
| Legacy `catch` | `07` | 旧方式の目印 |
| `throw` | `08` | 新旧共通。これだけでは判別できない |
| Legacy `rethrow` | `09` | 旧方式の目印 |
| `throw_ref` | `0a` | 新方式の目印 |
| Legacy `delegate` | `18` | 旧方式の目印 |
| Legacy `catch_all` | `19` | 旧方式の目印 |
| `try_table` | `1f` | 新方式の目印 |

出典：[Legacy の符号化](https://github.com/WebAssembly/exception-handling/blob/main/proposals/exception-handling/legacy/Exceptions.md#control-flow-instructions)、[新方式の符号化](https://github.com/WebAssembly/spec/blob/main/proposals/exception-handling/Exceptions.md#control-flow-instructions)。バイナリの任意の位置に同じバイトがあっても命令とは限らないので、必ず逆アセンブルして見る。

タグは型だけでなく同一性で照合する。別インスタンスで独立に作った同じ形のタグは別物である。また Wasm の trap（`unreachable`、メモリ範囲外アクセスなど）は Wasm の例外ハンドラでは捕捉しない。JS の `try/catch` で外から観測することとは区別する。[EH explainer のタグ・trap の説明](https://github.com/WebAssembly/spec/blob/main/proposals/exception-handling/Exceptions.md)

## 2. C の最小例と Emscripten オプション

### なぜ C から例外命令が出るか

C に C++ の `throw` / `catch` はないが、Emscripten は `setjmp` / `longjmp` を Wasm EH で実装できる。公式の [C setjmp-longjmp Support](https://emscripten.org/docs/porting/setjmp-longjmp.html) を根拠に、自作の最小例を用意した。既存プロジェクトの大きなコードを取り込む必要はなかった。

[src/sjlj.c](src/sjlj.c) の本質は次の部分（保存ファイルには混在実験用のマクロも含む）：

```c
#include <setjmp.h>
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

int main(void) {
  return probe() == 42 ? 0 : 1;
}
```

`noinline` は呼び出しを残して逆アセンブルを読みやすくするため。`setjmp` は初回 0、`longjmp` 後に 42 を返す。stdio を使わず、結果は終了コードで検証する。C 規格上の呼び出し位置の制約に合わせ、`setjmp` を `switch` の制御式に置いた。[C11 草案 N1570 §7.13.1.1](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)

### オプションの二軸

| 目的 | コンパイルとリンクの両方で渡すもの |
| --- | --- |
| C の JS ベース SjLj | `-sSUPPORT_LONGJMP=emscripten` |
| C の Wasm Legacy SjLj | `-sSUPPORT_LONGJMP=wasm -sWASM_LEGACY_EXCEPTIONS=1` |
| C の標準 Wasm SjLj | `-sSUPPORT_LONGJMP=wasm -sWASM_LEGACY_EXCEPTIONS=0` |
| C++ の JS ベース例外 | `-fexceptions` |
| C++ の Wasm Legacy 例外 | `-fwasm-exceptions -sWASM_LEGACY_EXCEPTIONS=1` |
| C++ の標準 Wasm 例外 | `-fwasm-exceptions -sWASM_LEGACY_EXCEPTIONS=0` |

C++ の行は公式文書と実装の確認であり、この実験では C++ の実行比較はしていない。`WASM_LEGACY_EXCEPTIONS=0` だけで EH 自体が有効になるわけではない。C では `SUPPORT_LONGJMP=wasm` が重要。[例外サポート](https://emscripten.org/docs/porting/exceptions.html)、[SjLj サポート](https://emscripten.org/docs/porting/setjmp-longjmp.html)、[設定リファレンス](https://emscripten.org/docs/tools_reference/settings_reference.html#wasm-legacy-exceptions)

手元の 6.0.9 では `WASM_LEGACY_EXCEPTIONS` の既定値は `true`。`-fwasm-exceptions` を使うと既定の SjLj は Wasm 方式になるが、それだけで新命令には切り替わらない。ローカルの `src/settings.js` と `tools/building.py` でも確認した。

### 実行コマンド

このディレクトリで：

```sh
EMCC=/opt/homebrew/opt/emscripten/bin/emcc
mkdir -p build

# 旧方式
"$EMCC" src/sjlj.c -O1 -g2 \
  -sSUPPORT_LONGJMP=wasm -sWASM_LEGACY_EXCEPTIONS=1 \
  -c -o build/legacy.o
"$EMCC" build/legacy.o -O1 -g2 \
  -sSUPPORT_LONGJMP=wasm -sWASM_LEGACY_EXCEPTIONS=1 \
  -o build/legacy.js

# 新方式
"$EMCC" src/sjlj.c -O1 -g2 \
  -sSUPPORT_LONGJMP=wasm -sWASM_LEGACY_EXCEPTIONS=0 \
  -c -o build/standard.o
"$EMCC" build/standard.o -O1 -g2 \
  -sSUPPORT_LONGJMP=wasm -sWASM_LEGACY_EXCEPTIONS=0 \
  -o build/standard.js

node build/legacy.js
node build/standard.js
wasm-objdump -dx build/legacy.wasm
wasm-objdump -dx build/standard.wasm
```

`-g2` は関数名を残すために使った。全実験を行う場合は後述の Python スクリプトを使う。

### 実測結果

| C の方式 | Wasm サイズ | JS サイズ | 実行 | 主な命令 |
| --- | ---: | ---: | --- | --- |
| JS ベース | 1,239 B | 19,489 B | exit 0 | この例では Wasm EH 命令なし |
| Legacy | 884 B | 18,372 B | exit 0 | `try`, `catch`, `throw` |
| 標準 | 908 B | 18,374 B | exit 0 | `try_table`, `throw` |

このサイズは `-O1 -g2` の極小例と生成 JS 全体の値。新方式の方が常に小さい／速いとは言えず、速度も測定していない。

実際の逆アセンブルの抜粋：

```text
# Legacy
000117: 06 40                      |         try
000119: 10 82 80 80 80 00          |           call 2 <jump>
00011f: 0c 04                      |           br 4
000121: 07 80 80 80 80 00          |         catch 0

# 標準
000117: 02 7f                      |         block i32
000119: 1f 40 01 00 80 80 80 80 00 |           try_table catch 0 0
000122: 00                         |
000123: 10 82 80 80 80 00          |             call 2 <jump>
```

後者の `1f` は命令、`40` はブロック型、`01` は節の数、次の `00` は `catch` の種別。続いてタグ index とラベル index が来る。最終行の `00` は前行の即値の続きで、`unreachable` 命令ではない。

`__wasm_longjmp` 内の `throw 0` は両方に出る。捕捉したペイロードから対象のジャンプ環境を調べる処理はコンパイラ／libc が生成する。この C 例は例外参照を直接再送出する必要がないので、新方式でも `throw_ref` は出ない。`throw_ref` の実例は WAT と Rust の実験にある。

詳細：[Legacy 逆アセンブル](results/legacy-disassembly.txt)、[標準 逆アセンブル](results/standard-disassembly.txt)、[JS 方式](results/js-disassembly.txt)。

## 3. 不一致を作って観察する

### 3.1 最終リンクのフラグだけ変えても直らない

Legacy の `legacy.o` を `WASM_LEGACY_EXCEPTIONS=0` でリンクした。リンクも実行も成功したが、最終 Wasm の `try` / `catch` は残った。

これは非 LTO の `.o` に既に命令が生成されているため。**最終リンク設定は入力 `.o` を遡って新方式で再コンパイルしない。** LTO の経路は今回未検証。[実行ログ](results/legacy-object-standard-link.txt)、[残った命令](results/link-only-disassembly.txt)

また、旧・新の `.o` はどちらも `target_features` に `+exception-handling` を持つ。このメタデータだけでは方式を判別できなかった。[旧オブジェクト](results/legacy-object.txt)、[新オブジェクト](results/standard-object.txt)

### 3.2 C 同士でも、最適化で失敗が顕在化する

同じ `sjlj.c` を関数名だけ変えて旧・新それぞれで `.o` にし、[mixed.c](src/mixed.c) から両方を呼んだ。

| 最終リンクの方式 | リンク最適化 | リンク | Node.js 実行 |
| --- | --- | --- | --- |
| Legacy / 標準のいずれでも | `-O0` | 成功 | 成功 |
| Legacy / 標準のいずれでも | `-O1` | 成功 | 成功 |
| Legacy / 標準のいずれでも | `-O2` | 成功 | **CompileError** |

`-O2` では逆アセンブル上で両方の処理が `main` に入り、同じ関数に `try` と `try_table` が存在する。エラーは `main` のコンパイル時に出た。`-O0/-O1` で動いたことを混在互換性の保証と解釈してはいけない。この環境では関数配置／最適化によって結果が変わった、という実測である。

```text
Compiling function #1:"main" failed:
module uses a mix of legacy and new exception handling instructions
```

[O2 のログ](results/mixed-standard-O2-run.txt)、[O2 の逆アセンブル](results/mixed-standard-O2-disassembly.txt)、[O1 の逆アセンブル](results/mixed-standard-O1-disassembly.txt)。V8 にも混在を拒否する [公式テスト](https://github.com/v8/v8/blob/main/test/mjsunit/wasm/mixed-eh-invalid.js) がある。今回作った [同一関数の最小 WAT](src/mixed-same-function.wat) でも拒否を確認した。

### 3.3 Rust + Emscripten + C：標準ライブラリが残る

[src/rust_main.rs](src/rust_main.rs) は C の `probe()` が 42 を返すことと、Rust の `panic!` を `catch_unwind` で捕捉できることを確認する。C の `longjmp` は C の中で完結し、Rust フレームを飛び越えない。

| ビルド | 結果 |
| --- | --- |
| Rust 本体 Legacy + C Legacy + 配布済み std | リンク・実行成功 |
| Rust 本体 標準 + C 標準 + 配布済み std | リンク成功、読み込み時 **CompileError** |
| 上の失敗 Wasm を Binaryen で標準方式へ変換 | 実行・検証成功 |
| Rust 本体・C・std を標準方式で再ビルド | 実行・検証成功 |

「Rust 本体 標準」は次の設定を明示した状態：

```sh
-C panic=unwind
-C target-feature=+exception-handling
-C llvm-args=-wasm-use-legacy-eh=0
-C link-arg=-fwasm-exceptions
-C link-arg=-sWASM_LEGACY_EXCEPTIONS=0
```

それでも配布済み `std` には設定が適用されず、失敗する。[ビルドコマンド](results/rust-standard-build.txt)、[読み込みエラー](results/rust-standard-run.txt)

最終 Wasm の命令数を調べると：

| 命令 | 配布済み std と混在 | Binaryen 変換後 | std 再ビルド後 |
| --- | ---: | ---: | ---: |
| `try` | 106 | 0 | 0 |
| `try_table` | 7 | 113 | 373 |
| `rethrow` | 63 | 0 | 0 |
| `throw_ref` | 2 | 72 | 141 |

再ビルド前後でビルド経路やデバッグ設定も異なるため、命令数の大小を性能比較には使わない。ここでの目的は旧命令の残存確認。

今回の rustc と配布 std では Legacy 統一が動いた。Rust 全体がどのターゲットでも同じ既定方式だと一般化しない。`wasm32-unknown-unknown` と `wasm32-unknown-emscripten` の既定値やランタイムは別に確認する。[Rust の Emscripten ターゲット文書](https://doc.rust-lang.org/rustc/platform-support/wasm32-unknown-emscripten.html#enabled-webassembly-features)

### 3.4 Cの静的ライブラリをCargoからリンクする（10月21日追試）

発表の状況に合わせ、同じCコードを `emar` で `libsjlj-standard.a` にまとめ、同じCargoプロジェクト・Rustコード・新EH設定で配布済みstdと再ビルドしたstdを比較した。

```sh
python3 run-rust-c-library.py
```

[再現スクリプト](run-rust-c-library.py) はCのコンパイル・アーカイブ作成から、`cargo +nightly build` と `cargo +nightly -Zbuild-std build` の比較、Nodeでの実行、最終Wasmの命令数の記録まで行う。nightly、rust-src、ターゲットの配布std、Cargoの依存キャッシュが揃った手元の環境で `--offline` 実行した。Cには `-sSUPPORT_LONGJMP=wasm -sWASM_LEGACY_EXCEPTIONS=0`、Rustのコード生成には `-C llvm-args=-wasm-use-legacy-eh=0`、最終リンクにも新EHとWasm SjLjの設定を指定している。完全な値は [RUSTFLAGS](results/c-library-rustflags.txt) に保存した。

| stdの供給方法 | Cargoビルド | Node実行 | 最終Wasmの `try` / `rethrow` |
| --- | --- | --- | --- |
| rustup配布のビルド済みstd | 成功 | 読み込み時に混在エラー、exit 1 | 106 / 63 |
| 同じ設定で `-Zbuild-std` | 成功 | CのlongjmpとRustのpanic捕捉に成功、exit 0 | 0 / 0 |

成功ログの `intentional panic` はテストで意図的に起こすpanicの診断表示で、続いて `C longjmp=42; Rust panic caught` が出る。CのlongjmpはCの関数内で捕捉しており、Rustフレームをまたぐunwindは試していない。旧命令の残存と読み込みの成否を比較したもので、命令数の性能比較ではない。

[結果集計](results/c-library-summary.json)、[読み込み失敗](results/c-library-prebuilt-run.txt)、[再ビルド後の成功](results/c-library-rebuilt-run.txt)、[stdの再コンパイルログ](results/c-library-rebuilt-build.txt)。

10月21日に確認したRust公式文書も、Emscriptenの版と設定に合わせて `cargo +nightly -Zbuild-std build` でstdを再ビルドするよう案内している。[Emscripten ABI Compatibility](https://doc.rust-lang.org/rustc/platform-support/wasm32-unknown-emscripten.html#emscripten-abi-compatibility)。nightlyのCargoとrustc、および `rust-src` が必要なことは [Cargoのbuild-std文書](https://doc.rust-lang.org/nightly/cargo/reference/unstable.html#build-std) に記載されている。`-Zbuild-std` 自体が新EHを選ぶわけではなく、Rustのコード生成とリンクの設定を揃えた上でstdまで再コンパイルする点が肝になる。

### 3.5 llvm-objdumpでRust staticlib内の新旧命令を調べる（10月21日追試）

`llvm-objdump -d` は `.a` のメンバーも逆アセンブルできる。Rustを新EHでコンパイルし、Cライブラリと配布済みstdを含めた静的ライブラリを作り、同じアーカイブ内に新旧の命令が残ることを確認した。[ソース](src/rust_static.rs) と [再現スクリプト](inspect-eh-archive.py) を保存した。

```sh
python3 inspect-eh-archive.py

EH='try_table|throw_ref|try|catch|catch_all|rethrow|delegate'
/opt/homebrew/opt/emscripten/libexec/llvm/bin/llvm-objdump \
  -d --triple=wasm32-unknown-unknown build/librust_c_mixed.a \
  | grep -E "[[:space:]]($EH)([[:space:]]|$)"
```

実測の抜粋（空白を整形し、末尾コメントを省略）：

```text
1a: 1f 40 01 02 00   try_table (catch_all 0)
2c: 06 40            try
3d: 19               catch_all
6e: 09 00            rethrow 0
```

`try_table` は今回コンパイルしたRustのメンバー、後の3命令は配布済み `panic_unwind` のメンバーにあった。`try_table (catch_all 0)` の `catch_all` は新命令の即値内の節なので、単独の旧 `catch_all` 命令と区別する。上の検索は「実際の命令位置のみを集計する」ものではなく、命令の候補を抽出して読むためのもの。スクリプトの集計は、アドレスとバイト列の直後にあるニーモニックだけを対象にしている。

Emscripten同梱LLVM 24.0.0gitで、同じ `.a` 内に `try_table` 5、`try` 709、`catch_all` 628、`rethrow` 456、`delegate` 78を確認した。アーカイブには最終リンクで使われないコードも入るので、前節の最終Wasmの命令数とは異なる。**アーカイブの混在は入力の所在を調べる手掛かりであり、最終Wasmの読み込み失敗をそれだけで確定するものではない。** 実行の成否は前節の最終成果物でも確認している。

元の例の ` try ` はタブ区切りや行末の `try` を取りこぼすため、`[[:space:]]` と行末も含む境界にした。また、旧方式の `catch` と `rethrow` も検索対象に加えた。`throw` は新旧共通なので判別には使わない。`--triple` は逆アセンブル対象の指定であり、命令形式の変換ではない。[LLVM公式マニュアル](https://llvm.org/docs/CommandGuide/llvm-objdump.html)

[実行コマンド](results/archive-eh-command.txt)、[抽出した命令](results/archive-eh-matches.txt)、[各命令の出自と集計](results/archive-eh-summary.json)。全逆アセンブルは `build/archive-eh-disassembly.txt` に保存した（Git管理外）。今回は非LTOのWasmオブジェクトを含むアーカイブを対象にしている。

## 4. 運用での対応

### 推奨：全ビルド入力の方式を揃える

1. 対応対象のブラウザ／Node／その他ランタイムを決め、Legacy か標準かを明示する。
2. C の `SUPPORT_LONGJMP`、C++ の `-fwasm-exceptions`、`WASM_LEGACY_EXCEPTIONS` をコンパイル・リンク両段階で揃える。
3. Rust 側はコード生成の `llvm-args` と最終リンクの `link-arg` を揃える。`link-arg` だけでは Rust のコード生成は切り替わらない。
4. 依存する `.a`、`.o`、Cargo 依存 crate、Rust `std`、Emscripten の各システムライブラリ／Ports も確認し、異なる設定のキャッシュを再利用しない。
5. 最終 `.wasm` の命令を検査し、配布対象ランタイムで実際に instantiate して、正常経路だけでなく `longjmp` / panic / cleanup 経路を動かす。

Rust 公式も Emscripten のバージョンと設定によって ABI が変わり、アプリ・標準ライブラリ・他言語コードの ABI を合わせるために `-Zbuild-std` を使う方針を説明している。[Emscripten ABI Compatibility](https://doc.rust-lang.org/rustc/platform-support/wasm32-unknown-emscripten.html#emscripten-abi-compatibility)

### 実測済みの std 再ビルド

[run-recovery.py](run-recovery.py) が以下の設定を組み立てる。`EMCC` と `C_OBJECT` はそれぞれ emcc と標準方式で作った C オブジェクトの絶対パスにする。

```sh
export RUSTFLAGS="-C linker=$EMCC -C panic=unwind \
-C target-feature=+exception-handling \
-C llvm-args=-wasm-use-legacy-eh=0 \
-C link-arg=-fwasm-exceptions \
-C link-arg=-sWASM_LEGACY_EXCEPTIONS=0 \
-C link-arg=$C_OBJECT"
cargo +nightly -Zbuild-std build \
  --manifest-path rust-demo/Cargo.toml \
  --target wasm32-unknown-emscripten
```

今回の既定 toolchain は nightly なので、保存スクリプトは `cargo -Zbuild-std` を実行した。`rust-src` と必要な Cargo キャッシュは既に揃っており、`--offline` でも成功した。他環境で依存不足なら `rust-src` の追加と初回の依存取得が必要になる。[再ビルド結果](results/rust-rebuild-std.txt)、[実行結果](results/rust-rebuilt-run.txt)

実際のプロジェクトで C を `cc` crate や CMake からビルドするなら、そのビルドシステムにも C 用設定を渡す必要がある。`RUSTFLAGS` を設定しただけで C のコンパイル設定まで変わるとは限らない。

### 変換による対応も可能だが、範囲を限定する

Binaryen 133 の次の変換で、今回の混在 Wasm は動作するようになった。

```sh
wasm-opt build/rust-standard.wasm --translate-to-exnref -g \
  -o build/rust-translated.wasm
```

実験スクリプトでは元の JS/Wasm を保持し、別名 JS の参照先だけ変換後 Wasm に合わせている。[変換ログ](results/rust-translate.txt)、[実行ログ](results/rust-translated-run.txt)、[検証ログ](results/rust-translated-validate.txt)

`--translate-to-new-eh` はこの版では旧名、`--translate-to-exnref` が現行名。`--emit-exnref` は要求した最適化パスの後に変換する CLI オプション。[Binaryen の CLI 実装](https://github.com/WebAssembly/binaryen/blob/main/src/tools/wasm-opt.cpp)

これは命令形式の変換であり、JS ベース例外と Wasm EH の ABI 差や、他の ABI 不一致を修復する保証はない。ソースから揃えて再ビルドできるならその方針を基本とし、変換を採用する場合も最終成果物で例外経路を試験する。

今回、最初に `--all-features` まで付けると Node と手元の wasm-tools が読めない import の形式が出た。不要な機能を全部有効にする設定を外すと通った。保存スクリプトは成功したコマンドを使い、入力が必要とする機能だけ扱う。

### `panic=abort` は意味を変える

`panic=abort` にすれば「Rust の panic を捕捉して復帰する」という要件を満たさなくなる。さらに C 側の `setjmp` / `longjmp` が Wasm EH を生成することは別問題なので、混在対策の万能スイッチにはしない。

言語をまたぐ unwind の可否も、命令形式とは別の問題。`extern "C-unwind"` を付ければ C++ 例外を Rust の `catch_unwind` で自由に扱える、という話でもない。本実験ではその境界を越える例外を扱っていない。動的リンク・異なるモジュール間の例外伝播も未検証。[Rustonomicon: FFI and unwinding](https://doc.rust-lang.org/nomicon/ffi.html#ffi-and-unwinding)

## 5. 環境と追加ツール

| 項目 | 実測した版 |
| --- | --- |
| OS/アーキテクチャ | macOS / aarch64 |
| Emscripten | `6.0.9-git`（指定の Homebrew emcc） |
| emcc の Clang | `24.0.0git` |
| Node.js / V8 | `26.8.1` / `14.6.202.34-node.28` |
| Rust | `1.100.0-nightly (8fa1c96cf 2026-08-17)` |
| Rust の LLVM | `23.1.0` |
| wasm-objdump | WABT `1.0.39` |
| wasm-tools | `1.218.0` |
| wasm-opt | Binaryen `133` |

`wasm-objdump` は Binaryen ではなく **WABT** のツール。`wasm-opt` / `wasm-dis` は Binaryen、`wasm-tools` は別のツール群である。今回の目的に追加インストールは不要だった。

実行環境の基準として、手元の Emscripten 6.0.9 の `tools/feature_matrix.py` は標準 EH に Chrome 137、Firefox 131、Safari 18.4、Node 24.15 を設定している。これは **Emscripten 側の互換性テーブル**であり、こちらが全バージョンを実機検証したという意味ではない。[同版のソース](https://github.com/emscripten-core/emscripten/blob/6.0.9/tools/feature_matrix.py)

本調査での実行検証は Node 26.8.1。発表で対象範囲を広げるなら、古い Node、Chrome/Firefox/Safari、非 JS ランタイム（Wasmtime など）を別途試験するとよい。「Wasm EH 対応」とだけ表示されている場合、それが Legacy か標準かも確認する。

## 6. 保存したものと再実行

```sh
cd /Users/udzura/ghq/github.com/udzura/slides/wasm-exception-research
python3 run.py
python3 run-recovery.py
```

- `src/`：C、Rust、WAT、WAT 実行確認用 JS のソース。
- `rust-demo/`：標準ライブラリ再ビルド用の最小 Cargo プロジェクト。
- `run.py`：C の三方式、新旧混在、リンク設定だけの変更、配布済み std を使う Rust の比較。
- `run-recovery.py`：Binaryen 変換、std 再ビルド、命令数の集計、WAT 実行。
- `results/`：コマンド、終了コード、実行ログ、小さい C バイナリの逆アセンブルと WAT、集計 JSON。
- `build/`：生成 JS/Wasm/.o、Cargo の成果物、大きい Rust 逆アセンブル。手元には残すが `.gitignore` の対象。

各実験は失敗ケースも記録して次へ進む設計。スクリプト自体の終了コード 0 を「全ケース成功」と読まず、`summary.json` / `recovery-summary.json` と各ログを見る。想定する失敗は mixed の O2、配布済み std と新方式の Rust、同一関数に新旧命令を置いた WAT。

Web の文書は調査時点のもの。ローカルの実験版は上表とログに固定し、将来再実行すると既定値・命令・互換性が変わり得る点を明示しておく。

## 7. 学習用には Clang と Emscripten のどちらが小さいか（10月20日追試）

同じ LLVM、同じターゲットと最適化・EH 方式なら、Emscripten だから命令が増えるとは限らない。ヘッダ不要の `catch-only.cpp` を、同梱 Clang の直接呼び出しと `em++` でそれぞれ `-O1`・標準 EH・オブジェクト出力にしたところ、**両方 626 bytes、`cmp` でバイナリ全体が一致**した。再現は `sh compare-clang.sh`。命令列は `results/catch-*-disassembly.txt` に保存した。

この例は外部の `may_throw()` を呼び、C++ の `catch (...)` で捕捉して 42 を返すだけ。単独実行用ではなく、未解決の例外ランタイム呼び出しも残した命令観察用 `.o` である。C の SjLj 例とのサイズ差には、ソース内容とリンク段階の違いもあるので、コンパイラの優劣の比較には使わない。

学習の順序としては、手書き WAT → この C++ の `.o` → C の SjLj → Rust を含む最終リンク、が読みやすい。純粋な命令の意味なら WAT が最小。生成命令を学ぶなら Clang でも em++ でも `-c` 出力が適している。最終実行ファイルでは libc・例外ランタイム・起動処理などが加わるため、対象関数を切り出して読む。

同じ `catch-only.cpp` を `em++` で Legacy / 標準 EH にコンパイルして比較するには、`sh compare-cpp-eh.sh` を実行する。逆アセンブルは `results/catch-legacy-disassembly.txt` と `results/catch-standard-disassembly.txt`、コンパイラの版は `results/catch-eh-compiler.txt` に保存する。Legacy は `try` / `catch`、標準は `block` と `try_table catch 0 0` を生成し、捕捉後の処理は内側のブロックの後ろに置かれる。`__cxa_begin_catch` / `__cxa_end_catch` の呼び出しは両方式に残る。スライドではこの命令列からローカル変数・スタックポインタ操作などを省略して示している。
