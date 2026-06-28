----
marp: true
theme: default
paginate: true
title: "Cloudflare って実際どんなサービスが使えるん？の話"
description: "Fukuoka.edge Cloudflare services summary draft"
style: |
  h1 { color: #ea580c; }
  h2 { color: #ea580c; }
  section li { color: #3f3f46; }
  section table { font-size: 20pt; }
  section th { color: #9a3412; }
  section.hero {
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  section.hero > h1 { font-size: 48pt; }
----
<!--
_class: hero
-->

# Cloudflare って実際どんなサービスが使えるん？の話

### Fukuoka.edge

---

# 背景

- Cloudflare がずっと話題なのでキャッチアップしている
- 個人的にも Cloudflare で使えるフレームワークを開発中
  - 建て付けとしては Cloudflare 専用ではない
- 9月に ........

---

# 今日見るもの

- コンピューティング
- ストレージ
- 非同期ジョブ
- 認証
- その他気になる・試したいもの

---

# コンピューティング

### Workers / Pages / Containers

- Pages: 静的サイトとフロントエンド寄りのデプロイ基盤
  - 最近は Workers でだいたい代替可能らしい
- Workers: リクエストごとに軽量に動くエッジ実行環境
- Containers: コンテナを Cloudflare 上で動かす新しい選択肢

---

# Workers と Containers

| サービス | 得意なこと | 使いどころ |
|:---|:---|:---|
| Workers | 軽量・高速なリクエスト処理 | API、認証前段、キャッシュ制御、Webhook |
| Containers | 既存のコンテナ資産や長めの処理 | 既存アプリの移植、重めの処理、特殊なランタイム |

---

# 今日は Workers メインで

- エッジランタイムとしての基本単位
- Cloudflare の各サービスと binding でつながる
- 小さく始めやすく、周辺サービスを試しやすい

---

# ストレージ

| サービス | 向いているデータ | 例 |
|:---|:---|:---|
| R2 | 巨大なファイル・大量のデータ | 画像・動画、PDF、AIモデル、バックアップファイル |
| KV | 小さくて、世界中で「すぐ読みたい」データ | ユーザーのセッション情報、アプリの設定値、リダイレクトURL |
| D1 | 構造化された、関係性のあるデータ | ユーザーのアカウント情報、注文履歴、ブログの投稿データ |
| Durable Objects | リアルタイムに「状態」が変わるデータ | チャットの接続状態、オンラインゲームの部屋、共同編集エディタのデータ |

---

# R2

- S3 互換のオブジェクトストレージ
- 大きなファイルや大量のデータを置く
- 画像・動画・PDF・バックアップなどに向く

---

# KV

- グローバルに読める key-value store
- 小さくて、世界中で「すぐ読みたい」データ向け
- 設定値、セッション情報、リダイレクト先など

---

# D1

- SQLite ベースのサーバーレスデータベース
- 構造化された、関係性のあるデータ向け
- SQL クエリが必要なものに向く

---

# Durable Objects

- 一貫性のある状態を持てるオブジェクト
- リアルタイムに状態が変わるデータ向け
- チャット、オンラインゲームの部屋、共同編集など

---

# 非同期ジョブ

- Queues: バックグラウンド処理やリトライに使えるキュー
- Producer がメッセージを積む
- Consumer が非同期に処理する
- 外部 API 連携、メール送信、重い処理の分離などに使える

---

# 認証

- Access: アプリケーションの前段に置ける認証・認可
- Google Workspace、GitHub、OIDC などと連携できる
- 社内向けツールや管理画面を守る用途に便利そう

---

# その他気になる・試したい

- Flagship
- Vectorize
- AI Gateway / Workers AI
- Workflows

---

# 今日のまとめ

- Workers を中心に、かなり多くの部品がそろっている
- ストレージは用途ごとに選ぶのが大事
- Queues や Access まで見ると、アプリの周辺もかなり作れそう

---

<!--
_class: hero
-->

# まずは Workers から

---

<!--
_class: hero
-->

# おしまい

