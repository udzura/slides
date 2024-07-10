----
marp: true
title: eBPFと ともだち になる方法
description: 於eBPF Japan Meetup #1
header: eBPFと ともだち になる方法
footer: "presentation by Uchio Kondo"
image: https://udzura.jp/slides/2024/ebpfjapan-1/ogp.png#FIXME
theme: ebpfjapan
paginate: true
----

<!--
_class: hero
-->

# eBPFと ともだち になる方法

----
<!--
class: profile
style: section.profile ul { width: 110% }
-->

# 近藤うちお / @udzura

- 所属: 株式会社ミラティブ
- 福岡市エンジニアカフェ
ハッカーサポーター
- フィヨルドブートキャンプ
アドバイザー
- 普段はGoでミドルウェア開発
- 『入門 eBPF』（オライリージャパン）共同翻訳者

![bg right w:82%](./profile2.png)

----

<!--
_class: hero
-->

# eBPF Japan Meetup #1

----

<!--
_class: hero
-->

# 開催めでたい 🥳

----

<!--
_class: hero
-->

# 今日する話

- 作ったものを振り返ってみる
- bpfバイナリを深掘りしてみる
- 何故それをしているか？
- フリーでオープンなものをハックして楽しむ自由

----

<!--
_class: hero
-->

# @udzura 作ったもの

----

<!--
_class: hero
-->

# RbBCC

----

<!--
_class: hero
-->

# RbBCC

- BCC(libbcc)のRuby binding
- Rubyアソシエーション開発助成の対象（メンターはRubyコミッタ笹田さん）
- 正直eBPFの勉強のつもりで作った

----

<!--
_class: hero
-->

# RbBCC の様子

```ruby
```

----

<!--
_class: hero
-->

# RbBCC のdemo

----

<!--
_class: hero
-->

# [Marp](https://marpit.marp.app/)っちなん

- Markdownで原稿を書いたらスライドにしてくれるツール
- <s>RubyistだけどRabbitじゃなくてこっち使ってます...</s>

----

<!--
_class: hero
-->

# Marpのいいところ

----

<!--
_class: hero
-->

# Marpのいいところ(1)

- VSCodeの拡張が便利
- プレビュー機能で大体表示確認OK

----

<!--
_class: hero
-->

![bg h:550](./vscode.png)

----

<!--
_class: hero
-->

# Marpのいいところ(2)

- export フォーマットが多い
- HTML/PDF、ogp用の画像もOK

----

<!--
_class: hero
-->

# Marpのいいところ(3)

- テーマがCSSベース
- Webの知識で色々カスタマイズできる
  - 昔の個人サイトをいじってたときのCSS知識でも安心
- フォントも最近はwebフォントが多くて助かる

----

<!--
_class: hero
-->

# Marpのいいところ(4)

- HTMLベースで吐き出せるので、JavaScriptを埋め込める
- WASMも埋め込める
- インタラクティブコンテンツ！

----

<!--
_class: hero
-->

# まとめ

- 『入門eBPF』買ってください（突然の宣伝）

![bg h:400 right](./book.png)
