---
marp: true
theme: default
paginate: true
size: 16:9
title: "Uzumibiの紹介: Rubyを書けばCloudflare Workerにそのままデプロイできるってマ！？"
description: "Cloudflare Tech Talk in Fukuoka rehearsal"
---

# Cloudflare WorkersでRubyを動かしたい！

- Cloudflare WorkersでRubyのコードを動かしたい

---

# CFは激アツプラットフォーム

- Cloudflare Workersがフロントエンドの人を中心に大流行

---

# Rubyコミュニティからあまり注目されていなくて、勿体無い

- Rubyを書きたいので、これらの技術に触れることが難しい

---

# 令和の時代、Railsをデプロイする先の選定は大変

- デプロイ先をどう選ぶか

---

# 無料でサクッと始められるCF Workersは「強い」です

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

# できること（CF限定で）

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

# WasmはCF WorkersのV8で動く

- Cloudflare WorkersのV8でWasmを実行する

---

# リクエストをWasmに渡して、Rubyを実行する

- HTTPリクエストをエンコードしてWasmに渡す
- Rubyバイトコードを実行する
- Rubyがリクエストを解釈する
- RubyのレスポンスをWorkersへ返却する

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

- PicoRubyをCF Workersで動くWasmにビルドした
- Rack互換レイヤを実装した
- `app.rb` の開発時自動リロードも実装しておいた

---

# Rack互換レイヤを実装した

- Rack互換レイヤを実装した

---

# Rack互換の考え方

- PerlのPSGI
- PythonのWSGI

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
- 本物のSinatraがCF Workerで動くかもしれない
- 今でもRubyでそれっぽいDSLは試せます

---

# お試しください

- Uzumibi
- PicoRuby on Cloudflare Workers
