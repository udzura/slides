---
marp: true
theme: default
paginate: true
size: 16:9
title: "Uzumibiの紹介: Rubyを書けばCloudflare Workerにそのままデプロイできるってマ！？"
description: "Cloudflare Tech Talk in Fukuoka rehearsal"
style: |
  :root {
    --cf: #f38020;
    --ink: #1f2937;
    --paper: #fffdf9;
  }
  section {
    background: var(--paper);
    color: var(--ink);
    font-size: 29px;
    padding: 54px 76px;
  }
  h1 {
    color: var(--cf);
    font-size: 48px;
    letter-spacing: -0.03em;
    border-bottom: 3px solid #fed7aa;
    padding-bottom: 14px;
  }
  h2 {
    color: var(--cf);
    font-size: 34px;
    letter-spacing: -0.03em;
  }
  section.hero {
    display: flex;
    flex-direction: column;
    justify-content: center;
    background: linear-gradient(135deg, #fffdf9 0%, #fff3e8 100%);
  }
  section.hero h1 {
    font-size: 52px;
    margin-bottom: 0.2em;
    border-bottom: none;
    padding-bottom: 0;
  }
  .sub { color: #6b7280; font-size: 26px; }
  ul { margin-top: 0.9em; }
  li { line-height: 1.45; margin: 0.3em 0; }
  li::marker { color: var(--cf); }
  section::after { color: #9a3412; font-size: 16px; }
  .diagram {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin: 42px 0 28px;
  }
  .node {
    flex: 1;
    min-height: 72px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 14px 12px;
    text-align: center;
    line-height: 1.25;
    border: 2px solid #fed7aa;
    border-radius: 12px;
    background: #ffffff;
    font-weight: bold;
  }
  .node.core {
    border-color: var(--cf);
    background: #fff3e8;
    color: #9a3412;
  }
  .node.wasm {
    border-color: #c4b5fd;
    background: #faf5ff;
    color: #5b21b6;
  }
  .node.list { font-size: 23px; }
  .arrow {
    flex: 0 0 26px;
    color: var(--cf);
    font-size: 34px;
    font-weight: bold;
    text-align: center;
  }
  .down {
    color: var(--cf);
    font-size: 34px;
    font-weight: bold;
    text-align: center;
    margin: 6px 0;
  }
  .platforms {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 12px auto;
    max-width: 860px;
  }
  .platforms .node { font-size: 24px; }
  .stack {
    max-width: 760px;
    margin: 18px auto;
  }
  .stack.compact-stack { margin: 0 auto; }
  .compact-stack .layer { padding: 8px 16px; }
  .compact-stack .down {
    font-size: 24px;
    line-height: 0.8;
    margin: 0;
  }
  .compact-stack .caption { font-size: 17px; }
  .layer {
    border: 2px solid #fed7aa;
    border-radius: 10px;
    background: #ffffff;
    padding: 13px 20px;
    text-align: center;
    font-weight: bold;
  }
  .layer.core {
    border-color: var(--cf);
    background: #fff3e8;
    color: #9a3412;
  }
  .caption {
    color: #6b7280;
    font-size: 22px;
    text-align: center;
  }
----

<!--
_class: hero
-->

# Uzumibiの紹介, そしてUzumibi2 ...？

## Rubyを書けばCloudflare Workerにそのままデプロイできるってマ⁉️

<br>

Cloudflare Tech Talk in Fukuoka<br>
<span class="sub">Uchio Kondo / @udzura</span>

---

# Cloudflare WorkersでRubyを動かしたい！

- Cloudflare WorkersでRubyのコードを動かしたい

---

# Cloudflareは激アツプラットフォーム

- Cloudflare Workersがフロントエンドの人を中心に大流行

---

# Rubyコミュニティからあまり注目されていなくて、勿体無い

- Rubyを書きたいので、これらの技術に触れることが難しい

---

# 令和の時代、Railsをデプロイする先の選定は大変

- デプロイ先をどう選ぶか

---

# 無料でサクッと始められるCloudflare Workersは「強い」です

- 無料で始められる

---

# `ruby.wasm`は動かせるらしい

- RubyをWasmで動かす取り組みはある

---

# しかし、10MB近くの容量になるとのことで敷居が高い

- 無料枠では動かせない
- 課金したプランで無理やり使うことになる

---

# もっとサクッとRubyのコードを動かしたい

- Rubyのコードをサクッと動かしたい

---

# 今できていることの軸

- Uzumibiの紹介
- 仕組み
- すぐに試せること

---

# Uzumibiの紹介

- Uzumibi is 何

---

# Uzumibi is 何

- Cloudflare WorkersでRubyのコードを動かすためのもの

---

# Uzumibi: Rubyをいろいろな場所へ

<div class="diagram">
  <div class="node">Ruby app</div>
  <div class="arrow">→</div>
  <div class="node core">Uzumibi</div>
  <div class="arrow">→</div>
  <div class="node">Cloudflare Workers<br>Fastly Compute<br>Google Cloud Run</div>
</div>

<p class="caption">プラットフォームごとに adapter / template を用意する</p>

---

# できること（Cloudflare限定で）

- Cloudflare WorkersでRubyアプリケーションを実行する

---

# ライブデモでデプロイしちゃう

- デプロイしちゃう

---

# 仕組み

- 独自のmruby VM
- Rust
- Wasm
- Cloudflare Workers

---

# 独自のmruby VM（Rust）

- `mruby/edge`

---

# RustなのでWasmにできる

- RustからWebAssemblyを生成する

---

# WasmはCloudflare WorkersのV8で動く

- Cloudflare WorkersのV8でWasmを実行する

---

# リクエストをWasmに渡して、Rubyを実行する

- HTTPリクエストをエンコードしてWasmに渡す
- Rubyバイトコードを実行する
- Rubyがリクエストを解釈する
- RubyのレスポンスをWorkersへ返却する

---

# HTTP request → Ruby → HTTP response

<div class="diagram">
  <div class="node">HTTP<br>request</div>
  <div class="arrow">→</div>
  <div class="node">Worker<br>JavaScript</div>
  <div class="arrow">→</div>
  <div class="node wasm">encoded<br>request</div>
  <div class="arrow">→</div>
  <div class="node core">Wasm<br>Ruby bytecode</div>
  <div class="arrow">→</div>
  <div class="node">Ruby<br>router</div>
</div>

<div class="diagram">
  <div class="node">HTTP response</div>
  <div class="arrow">←</div>
  <div class="node">Worker JavaScript</div>
  <div class="arrow">←</div>
  <div class="node wasm">Wasm response</div>
  <div class="arrow">←</div>
  <div class="node core">Ruby response</div>
</div>

---

# すぐに試せますし、無料枠で動きます

- Uzumibiを試せる

---

# これからやろうとしていることの軸

- せっかくなので、エコシステムが強いPicoRubyも動かしたい

---

# PicoRubyをCloudflare Workersで動かしたい

- PicoRubyには強いエコシステムがある

---

# やっていること

- PicoRubyをCloudflare Workersで動くWasmにビルドした
- Rack互換レイヤを実装した
- `app.rb` の開発時自動リロードも実装しておいた

---

# PicoRubyをWorkersで動かす構成

<div class="stack compact-stack">
  <div class="layer">Cloudflare Workers<br><span class="caption">request / response</span></div>
  <div class="down">↓ ↑</div>
  <div class="layer wasm">Wasm host</div>
  <div class="down">↓ ↑</div>
  <div class="layer core">Rack互換レイヤ</div>
  <div class="down">↓ ↑</div>
  <div class="layer">PicoRuby + <code>app.rb</code><br><span class="caption">開発時は自動リロード</span></div>
</div>

---

# Rack互換レイヤを実装した

- Rack互換レイヤを実装した

---

# Rack互換の考え方

- PerlのPSGI
- PythonのWSGI

---

# Rack: サーバとフレームワークの間の規約

<div class="diagram">
  <div class="node list">Server<br><br>Puma<br>Unicorn<br>WEBrick<br>CGI<br>...</div>
  <div class="arrow">↔</div>
  <div class="node core">Rack<br><br><code>env</code><br><code>[status, headers, body]</code></div>
  <div class="arrow">↔</div>
  <div class="node list">Framework<br><br>Rails<br>Sinatra<br>Hanami<br>Roda<br>...</div>
</div>

<p class="caption">アプリケーションとサーバの間の規約。PSGI / WSGI と同じ考え方。</p>

---

# `app.rb` の開発時自動リロードも実装しておいた

- おまけ的な機能

---

# さらに…

- Rackをサポートした
- 「Rubyで有名な」フレームワークを動かしたい

---

# Railsは流石に無理…

- Railsは流石に無理

---

# 現状、ワイのプロジェクトではSinatraが動いている

- 本物のSinatraを動かしている

---

# 容量も余裕がある

- 非圧縮で700KiB台
- 圧縮後は300KiB以下

---

# ただし、まだバグがある

- 正規表現のバグ
- バイトコードコンパイラのバグ

---

# upstreamではいずれも修正済み

- upstreamではいずれも修正済み

---

# 逆に言えば、今やこれだけの非互換しかない

- mrubyすごっ

---

# まとめ

- Wasm最高！
- 本物のSinatraがCloudflare Workerで動くかもしれない
- 今でもRubyでそれっぽいDSLは試せます

---

# お試しください

- Uzumibi
- PicoRuby on Cloudflare Workers
