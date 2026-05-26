----
marp: true
header: "ミリしらAI勉強会 #3"
footer: "presentation by Uchio Kondo"
theme: default
paginate: true
style: |
  h1 { color: #0f7f85; }
  h2 { color: #0f7f85; }
  section.profile img {
    position: absolute;
    top: 25%;
    left: 65%;
    overflow: hidden !important;
    border-radius: 50% !important;
  }
  section.hero h1 {
    font-size: 2.5em;
    text-align: center;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 80%;
  }
----

# ミリしらAI勉強会 #4 へようこそ！

----
<!--
_class: hero
-->

# llama2.c で<br />推論エンジン？を学ぶ

----

<!--
_class: profile
-->

# 自己紹介

- 近藤うちお (各種ID: @udzura)
- エンジニアカフェ ハッカーサポーター
- 所属: 株式会社SmartHR プロダクトエンジニア
- 普段はインフラエンジニア？
- AIの他はWasmとかCloudflare Workers、eBPFに興味がある

----

# やったこと

- llama2.c をRustに移植してみた(AIが)
- その後コードを読んでみた

----

# 経緯の説明

- きしださんに「llama2.c を自分の好きな言語に翻訳すると勉強になるよと言われた」
- <s>たまには</s> 素直にやってみるか〜って思ったのでやってみた

----

# llama2.c とは？

- ローカルマシンで推論するやつ
- 「推論エンジン」らしい

https://note.com/bakushu/n/nd834ff25394f

----

# How to 動かす

- 用意するものは
    - 学習済みモデル
    - トークナイザ

----

# 早速Rustに移植したやつ

- AIに、以下を食わせました

```
llama 2 modelをC言語で実装したllama2.cを、Rustに移植してください。

C実装は llama2.c/run.c にあります。
その他実装の詳細はREADMEなどを確認してください
Rustはできる限り依存ライブラリを使わない、平易でストレートなRustのコードにしてください。
必要に応じてコメントを日本語で付与してもOKです。
```

----

# Done

- Codexのちょっとのリクエストで移植完了した
- https://github.com/udzura/llama2-rs-study

----

# 動かしてみる

- ただし、トークナイザの生成はllama2.cにやらせないとダメらしい

```
cd llamac.c
curl -L -o stories15M.bin \
  https://huggingface.co/karpathy/tinyllamas/resolve/main/stories15M.bin
python3 tokenizer.py --tokenizer-model=./tokenizer.model
cp *.bin ../work
cd ..
cargo build --release
./target/release/llama2-rs work/stories15M.bin -z work/tokenizer.bin \
  -n 256 -i "Hello world"
```

----

```
 Hello world Show. Everyday, there was a little girl named May. She was 3 years old,
 and she loved to explore.
 On one special day, May went out for a walk. She wanted to see the world Janet. As she walked,
 she noticed a colorful rainbow. She went to the rainbow and started to look at it.
 Suddenly, a big scary cat appeared and tried to catch May Janet.
 May was scared and she ran back home. But before she did, the cat started to chase her. Maya was so scared,
 she screamed for help.
 Suddenly, two brave kids in a small, long whip appeared.
 They started to fight over the chalk. The kids were very brave,
 but Maya was too small to fight over the chalk. The kids stopped fighting and stepped back.
 "Come back here!" said the kids. "We will save you!"
 Just then, a big, friendly dog appeared in the room. The dog barked at the kids and scared them away.
 Mayy was so relieved. She was very thankful for her friends and brother. The k
 achieved tok/s: 152.60323159784562
```

----
<!--
_class: hero
-->

# 楽しい！

----

# 最低限の仕組みを知りたい...

- generate関数を追ってみる
- （ここでVSCodeに切り替え）

----

```rs
 fn generate(
     transformer: &mut Transformer,
     tokenizer: &mut Tokenizer,
     sampler: &mut Sampler,
     prompt: Option<&str>,
     steps: usize,
 ) {
     // プロンプト未指定時は空文字として扱う。
     let prompt = prompt.unwrap_or("");
 
     // 入力文字列をトークン列へ変換する（BOS あり、EOS なし）。
     let mut prompt_tokens = Vec::with_capacity(prompt.len() + 3);
     tokenizer.encode(prompt, true, false, &mut prompt_tokens);
     // 先頭トークンがない状態は異常として終了。
     if prompt_tokens.is_empty() {
         eprintln!("something is wrong, expected at least 1 prompt token");
         process::exit(1);
     }
 
     // 1トークン目のウォームアップを除いて速度計測するための開始時刻。
     let mut start: u128 = 0;
     // まずはプロンプト先頭トークンから推論を開始する。
     let mut token = prompt_tokens[0] as usize;
     let mut pos = 0usize;
 
     // 最大 steps まで 1 トークンずつ自己回帰生成する。
     while pos < steps {
         // 現在 token/pos の前向き計算で次トークン logits を得る。
         let logits = transformer.forward(token, pos);
         // プロンプト処理中は強制的に次のプロンプトトークンを使い、
         // それ以降はサンプラで確率的に次トークンを選ぶ。
         let next = if pos < prompt_tokens.len() - 1 {
             prompt_tokens[pos + 1] as usize
         } else {
             sampler.sample(&mut logits.to_vec())
         };
         pos += 1;
 
         // BOS(=1) が出たらシーケンス終端として打ち切る。
         if next == 1 {
             break;
         }
 
         // 予測トークンを文字列へ復号して逐次表示する。
         let piece = tokenizer.decode(token as i32, next as i32);
         safe_print(&piece);
         token = next;
 
         // 初回反復は遅く出やすいので、速度計測の開始は2反復目以降にする。
         if start == 0 {
             start = now_ms();
         }
     }
     println!();
 
     // 経過時間から tokens/sec を表示する。
     if pos > 1 {
         let end = now_ms();
         if end > start {
             eprintln!(
                 "achieved tok/s: {}",
                 (pos - 1) as f64 / ((end - start) as f64) * 1000.0
             );
         }
     }
 }
```

----

## TokenizerやTransformerは何してる

- なんか関数がいっぱいでわかんないっピ...

----

## 次回の宿題

- わかんないところを調べます！（AIと一緒に）
