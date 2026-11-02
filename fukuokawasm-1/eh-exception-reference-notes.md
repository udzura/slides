# Wasm EHの例外参照と正常経路の分け方

Fukuoka.wasm #1の発表準備中に、「新方式ではthrowしたらスタックに例外のrefが入っている？」から確認したこと。2026-11-02。

## throwの直後に、使える例外参照が残るわけではない

`throw $error`は、スタック上のペイロードを取り出して例外を作り、通常の処理を中断してハンドラを探す。

例外参照が分岐先のスタックへ渡されるのは、`catch_ref`や`catch_all_ref`で捕捉したとき。ペイロードの42と、例外全体への参照は別の値。

`throw_ref`は参照を積む命令ではなく、スタックに積まれた例外参照を消費して、同じ例外を投げ直す命令。

## refあり／なしの違い

ここでのcatchは、旧形式の独立したcatch命令ではなく、`try_table`の先頭に並べる節。

| 節 | 捕捉対象 | 分岐先のスタックに渡すもの |
| --- | --- | --- |
| `catch $tag $label` | 指定タグの例外 | ペイロードだけ |
| `catch_ref $tag $label` | 指定タグの例外 | ペイロード、その上に例外参照 |
| `catch_all $label` | タグを問わない例外 | 何も渡さない |
| `catch_all_ref $label` | タグを問わない例外 | 例外参照だけ |

`_ref`は「ペイロードの代わりに参照」という意味ではない。特に`catch_ref`は両方を渡す。

例外参照はスタックの一番上。たとえばi32を一つ持つタグなら、`catch_ref`の分岐先には下から順に`42, 例外参照`が渡るので、受け取るblockの結果型は`(result i32 exnref)`にできる。

捕捉時に渡る参照自体は非nullの`(ref exn)`。nullも許す`exnref`（`(ref null exn)`の略）の値として保持できる。線形メモリのアドレスを表すi32のポインタとは異なる、不透明な参照。

`catch_all`系でもtrapは捕捉しない。

スライドとの対応：
- p11の`catch`は42だけを受け取る。
- p14の`catch_all_ref`は例外参照だけを受け取り、`throw_ref`に渡す。

## p14では、仮に正常経路へ進んでもnullにはならない

以下はタグ定義などを省いた、p14の抜粋。

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

- 実際には必ずthrowする。捕捉すると例外参照を渡して`$saved`を抜け、`unreachable`を飛ばして`throw_ref`へ進む。
- 仮にtry_tableの本体を正常終了し得る処理に変えたら、通常経路では直後の`unreachable`に進み、そこでtrapする。
- この`unreachable`はtry_tableの外にある。例外捕捉後に実行する命令ではない。

`(result exnref)`はブロックの結果型の宣言。「結果用の領域をnullで初期化する」という意味ではない。

nullを積むには明示的に`ref.null exn`と書く。ただしnullを`throw_ref`へ渡してもtrapするので、正常経路の代用にはならない。

## 正常経路を作る例①：returnで関数から戻る

以下の関数例では、同じmodule内に`(tag $error (export "error") (param i32))`を定義しておく。

```wat
(func (export "return_or_rethrow")
      (param $fail i32) (result i32)
  block $saved (result exnref)
    try_table (catch_all_ref $saved)
      local.get $fail
      if
        i32.const 42
        throw $error
      end
    end

    ;; 正常時は関数から直接戻る
    i32.const 0
    return
  end

  ;; 捕捉時だけ、参照を受け取って再送出
  throw_ref
)
```

- `$fail = 0`：try_tableを普通に抜け、0を返す。
- `$fail != 0`：例外を捕捉し、参照を渡して`$saved`を抜け、同じ例外を再送出する。

正常経路はreturnで関数を抜けるため、`$saved`の結果として例外参照を用意する必要がない。

## 正常経路を作る例②：外側のblockへbrし、処理を続ける

関数からreturnするしかないわけではない。外側に結果なしのblockを置き、正常時はそこへbrしてもよい。

```wat
(func (export "branch_or_rethrow")
      (param $fail i32) (result i32)
  block $normal
    block $saved (result exnref)
      try_table (catch_all_ref $saved)
        local.get $fail
        if
          i32.const 42
          throw $error
        end
      end

      ;; 正常時は外側のブロックを抜ける
      br $normal
    end

    ;; 捕捉時だけ通る
    throw_ref
  end

  ;; 正常経路の続き。ここに後続処理を書ける
  i32.const 0
)
```

- 正常時：`br $normal`で外側のblockを抜け、`throw_ref`も飛び越える。その後も同じ関数内で処理を続け、ここでは0を返す。
- 例外時：`catch_all_ref`が参照を渡して内側の`$saved`を抜け、`throw_ref`で再送出する。

要点は「正常経路と、例外参照を受け取る経路で、出口を分ける」こと。

`$normal`は結果を要求しない。正常経路でダミーの例外参照やnullを用意する必要はない。`br $normal`は内側の`$saved`もまとめて抜けるが、その結果を受け取る出口を通っているわけではない。

## 手元での確認

上の二つの関数を共通のタグと一緒にmoduleへ入れ、`wasm-tools parse`でバイナリ化して検証。

- どちらも引数0では戻り値0。
- どちらも引数1ではJavaScript側まで例外が伝播し、exportしたerrorタグとの一致と、ペイロード42を確認。

## 参照

- [EH explainer：捕捉時に渡す値と再送出](https://github.com/WebAssembly/spec/blob/main/proposals/exception-handling/Exceptions.md#throwing-an-exception)
- [EH explainer：throw_ref](https://github.com/WebAssembly/spec/blob/main/proposals/exception-handling/Exceptions.md#rethrowing-an-exception)
- [Wasm仕様：unreachable](https://webassembly.github.io/spec/core/exec/instructions.html#exec-unreachable)
- [Wasm仕様：blockとbr](https://webassembly.github.io/spec/core/exec/instructions.html#exec-br)
- [発表スライドのソース](https://github.com/udzura/slides/blob/master/fukuokawasm-1/index.md)

#WebAssembly #WAT #例外処理 #Fukuoka.wasm
