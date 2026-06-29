# fukuoka-edge-sample-pj

Cloudflare の基本サービスを **1 つの Worker** にまとめて、動作をまとめて確認できるサンプルです。
スライド `fukuoka-edge/cf-matome` の内容に対応しています。

対象サービス:

- **R2** … S3 互換オブジェクトストレージ
- **KV** … グローバル key-value store
- **D1** … SQLite ベースのサーバーレス DB
- **Durable Objects** … 一貫性のある状態を持つオブジェクト
- **Queues** … 非同期ジョブ（producer / consumer を同居）
- **Access** … 前段認証の JWT 検証

## セットアップ

```sh
npm install

# Cloudflare にログイン
npx wrangler login

# 各リソースを作成（出力された id を wrangler.jsonc に転記する）
npx wrangler kv namespace create MY_KV
npx wrangler r2 bucket create fukuoka-edge-bucket
npx wrangler d1 create fukuoka-edge-db
npx wrangler queues create fukuoka-edge-jobs

# D1 のスキーマを適用（ローカル）
npm run db:apply
```

`wrangler.jsonc` の `<...>` プレースホルダ（KV id / D1 id / Access の
TEAM_DOMAIN・POLICY_AUD）を自分の値に置き換えてください。

## ローカル起動

```sh
npm run dev
```

## エンドポイント

| メソッド / パス | サービス | 内容 |
|:---|:---|:---|
| `GET /` | - | エンドポイント一覧 |
| `GET /kv` | KV | 前回アクセス時刻を読み、現在時刻を TTL 付きで保存 |
| `PUT /r2/:key` | R2 | リクエストボディを `:key` で保存 |
| `GET /r2/:key` | R2 | `:key` を取得 |
| `GET /d1?minAge=18` | D1 | `age >= minAge` のユーザーを SELECT |
| `GET /counter/:room` | Durable Objects | 部屋ごとにアクセス回数をカウント |
| `POST /jobs` | Queues | ボディをジョブとして積む（consumer がログ出力） |
| `GET /whoami` | Access | JWT を検証し email / sub を返す |

### 動作例

```sh
curl http://localhost:8787/kv
curl -X PUT http://localhost:8787/r2/hello.txt --data 'world'
curl http://localhost:8787/r2/hello.txt
curl 'http://localhost:8787/d1?minAge=18'
curl http://localhost:8787/counter/room-1   # 叩くたびに増える
curl -X POST http://localhost:8787/jobs -d '{"hello":"queue"}'
```

> `GET /whoami` は Cloudflare Access の背後にデプロイした場合のみ JWT が付与されます。
> ローカルではトークンが無いため 403 になります（検証フローのサンプルとして参照してください）。

## デプロイ

```sh
npm run db:apply:remote
npm run deploy
```
