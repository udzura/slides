----
marp: true
theme: rubykaigi2025
paginate: true
backgroundImage: url(./rubykaigi2025_bg.004.jpeg)
title: Running ruby.wasm on Pure Ruby WASM Runtime
description: On RubyKaigi 2025 Matzyama / Running ruby.wasm on Pure Ruby WASM Runtime
# header: "Running ruby.wasm on Pure Ruby WASM Runtime"
image: https://udzura.jp/slides/2025/rubykaigi/ogp.png
size: 16:9
----

Running ruby.wasm on Pure Ruby WASM Runtime
=============

----

# 自己紹介

- Uchio Kondo
- Product Engineer at SmartHR

----

# 今日のテーマ: Wardite

- Pure Ruby WebAssembly Runtimeです
- WebAssembly って何？
- WebAssembly Runtimeって何？

----

# WebAssembly とは何か

- WebAssemblyは
  - バイナリ形式の一種の命令セットアーキテクチャ
  - 元々ウェブブラウザ上で実行されることを目的としていた
  - 近年はサーバーサイドやIoTデバイスなど、様々な環境で利用されている

----

# WebAssembly　はブラウザで動く

- こういうCのコードをwasmにコンパイルして動かせる

----

# WebAssembly はどこでも動く

- cli commandにwasmバイナリを渡せば動く
- 後述するが、VM実行環境を組み込んだアプリケーションの内部でも動かせる

----

# WebAssembly 実行の流れ

- ここにtokyo12で作った図解を置く
- まずソースコード
- それをコンパイル
- wasmバイナリをランタイムで実行

----

# WebAssembly Runtime とは何か

- WebAssemblyを実行するための環境 = WebAssembly Runtime
- ブラウザもRuntime
- 代表的な実装は wasmtime、wasmedge
- 言語内部に組み込める実装もある
    - Go = wazero, Swift = swiftwasm
    - これらの実装はその言語でpureな実装をしている

----

# ということで、Warditeとは

- Pure Rubyで書かれたWebAssembly Runtime
- Rubyで書かれているので、Rubyの中でWebAssemblyを動かすことができる
- すぐ試す場合、コマンドラインツールも用意している

----

# Warditeの設計方針

- Rubyの標準・標準添付ライブラリだけに依存する
  - 特にコア部分（後述）はRubyの標準ライブラリだけで実装する
- rbs-inlineを全面的に採用する

----

# Warditeの実装状況

- WebAssembly Core Specの実装
  - 基本的な部分は終わった
  - 十分なテストはこれからとなる
- WASI p1
  - WASI p1の一部関数を実装
  - ruby.wasm の動作に必要なものは一通り実装できているはず

----

# WebAssembly Core Specとは何か

- WebAssemblyの基本的な仕様のセット
  - WebAssemblyのバイナリ形式とテキスト形式、命令セット、型システム、メモリモデルなどを定義している
  - ランタイムはこれらの仕様を実装すれば、バイナリを動作させられる
- WASI、Componentn Modelのような仕様は
  - Core Specの上に成り立っている

----

# WASIとは何か

- WebAssembly System Interface
- WebAssemblyのCore Spec自体には、OSとのやり取りの定義はない
- WASIは、WebAssemblyがOSとやり取りするためのAPIを定義している

----

# Why Wardite？

----

# Warditeの目的

- Rubyで、wasmの言語への組み込み活用のユースケースを広げたい
- 可搬性（Rubyが動けば動く/あるいはmrubyなどで動く）が高い実装が欲しい
- Ruby自体のパフォーマンステストの助けになると嬉しい

----

# 本音

- Just for fun
- wasmの勉強

----

# WebAssemblyの可能性

- そもそもwasmに大きな可能性を感じており、Rubyでのアクセスパスを増やしたい

----

# WebAssemblyの可能性

- 言語アグノスティックな部分への期待
- シンプルなCoreの興味深さ
- アプリケーション組み込みの可能性

----

# 言語アグノスティックな部分

- 様々なコンパイル型言語で、wasmターゲットをサポートしている
  - Rust、Go、C/C++、Swift、Zig、Dart、Scala...
  - LLVM
- C言語を経由で数多くの資産がwasmに...
  - C言語で書かれた言語もある。Ruby、Python、Lua、Perl...

----

# シンプルなCoreの興味深さ

- WebAssembly Core Specは、シンプルさと合理性をキープしている様に思える
  - そのため、実装が比較的容易
  - ランタイム自体を色々なところに埋め込みやすい
- 拡張仕様についいては...諸説あるが...

----

# アプリケーション組み込みの可能性

- アプリケーション組み込み実行への適正
  - ランタイムも小さくできがちで、各環境に組み込みやすい
  - 実際各言語でのランタイム実装が出てきている
    - Goのwazeroによるpure goプラグイン機構
      - Goでは普通できない動的ロードの実現

----

# アプリケーション組み込みの可能性

- ブラウザ実行も、「ブラウザにwasm runtimeが組み込まれている」と考えた方が正しそう

----

# 言語組み込みの可能性

- 組み込み実行への強さ
  - 設定言語としてのwasm
    - envoy、fluent-bit、...
    - wasmbots
  - mrubyもLuaもピンチ！

----

# JVMとの違い？

- JVMにあまり詳しくないのでツッコミ歓迎です
- JVMは以下の様な部分への意識が弱そうに思える。違ったらごめんね

----

# JVMとの違い？

- 言語アグノスティックな点
  - C言語資産、LLVMとの相性がよいwasmは、「どんな言語でもwasmに移植できる」という点の強みがありそう。
  - 理論上は。

----

# JVMとの違い？

- アプリケーション組み込みというフィールド
  - JVMもアプリケーション組み込みは可能だが、wasmはさらに適性がありそう
  - 今の時点でwasmによる設定言語実装、各言語製のランタイムなど多数

----

# JVMとの違い？

- 全体に色々拡張はあるけどwasmのコアはシンプルに保ちたい方向性があり、それがうまく作用してそう

----

# Warditeの作り方

----

# Warditeの開発の歴史

- いくつかのマイルストーンがあった
  - ゴリラ本の移植(Hello, World)
  - Core Specの基本的な命令のカバー
  - grayscaleサンプルプログラムの動作
  - ruby.wasmの起動
  - ruby.wasmでrequireの動作

----

# ゴリラ本の移植

- ゴール: Hello, Worldが動く
- 必要な実装
  - 基本的なVM構造と命令
    - ローカル変数、グローバル変数（＋制御構文）
    - メモリの確保と解放
    - 関数のimport/exportセクション
    - WASIのfd_write()だけはサポート

----

# ゴリラ本とは？

- RustでWebAssemblyの基本的な実装を学ぶための本
- ほなRubyで書くか〜RBS全体に使えば元コードがRustでもいけるっしょ

----

# 苦労した点

- 基本的な実装をえいやとやったので大変だった
- Rustの参考実装があったので助かった

----

# バイナリフォーマット

- leb128という数値表現の実装が必要で、自作した

----

# Core Specの基本的な命令のカバー

- Hello worldが動いたので、もう少し実装を進めたい
- ゴール
  - Core Specの基本的な命令をカバーする
  - 一応この時点で「ruby.wasmを動かしたい」という気持ちがあったので、どういう命令が使われているかは調べた

----

# wasmの命令セット

- 基本的な範囲と、拡張セットがある
- 基本的な範囲は、Core Specに書いてある
- 拡張セットについて
  - GC、atomic、reference types、simd、multi-value、exception handling...
  - この辺りはおいおいやる

----

# 苦労した点

- いやめっちゃ数多いやん...（めっちゃ、でもない？）

----

# 数値演算系をなるべく宣言的に実装したい

- 数値演算系はファイル生成で対応している
- Rake taskでgenerator作った

----

# TBD: 次のマイルストーン

----

	Warditeの開発の歴史
		マイルストーン //  [* TODO]！ここをこれから詳しく書く ref [Wardite開発の歴史を思い出したい] 他
			ゴリラ本の実装
			全実装のカバー
			grayscaleサンプルプログラムの動作
   	上の中でwasm specを動かす話が出る
 		ruby.wasmの起動
 		ruby.wasmでrequireを動かす（予定）
 	最後に、ruby.wasmの動作デモ
 パフォーマンス計測との向き合い（経過でも）
	 最初のパフォーマンス改善
	 	簡単
	 インスタンス作りすぎ問題
	 	よく使うやつのメモ化
	 	インスタンス作成自体を削減してみるか...
	 YJITの影響
	 	バージョンが上がると確かに高速になる話か
 今後について
 	全体的なリファクタ、　パフォーマンスに加えて...
 	core specのカバレッジ向上
 	component model対応
