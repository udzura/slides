----
marp: true
theme: default
paginate: true
title: "Cloudflare って実際どんなサービスが使えるん？の話"
description: "Fukuoka.edge Cloudflare services summary draft"
style: |
  h1 { color: #F38020; }
  h2 { color: #F38020; }
  section li { color: #404041; }
  section table { font-size: 20pt; }
  section th { color: #c1440e; }
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
| KV | 小さくて、世界中で「すぐ読みたい」データ | ユーザーのセッション情報、アプリの設定値、リダイレクトURL |
| D1 | 構造化された、関係性のあるデータ | ユーザーのアカウント情報、注文履歴、ブログの投稿データ |
| R2 | 巨大なファイル・大量のデータ | 画像・動画、PDF、AIモデル、バックアップファイル |
| Durable Objects | リアルタイムに「状態」が変わるデータ | チャットの接続状態、オンラインゲームの部屋、共同編集エディタのデータ |

---

# KV

- グローバルに読める key-value store
- 小さくて、世界中で「すぐ読みたい」データ向け
- 設定値、セッション情報、リダイレクト先など
- 読み込みは爆速、書き込みは結果整合（反映に少し時間）

---

# KV のコード例

```jsonc
// wrangler.jsonc
"kv_namespaces": [
  { "binding": "MY_KV", "id": "<namespace_id>" }
]
```

```ts
// TTL 付きで保存（例: セッションを 1 時間）
await env.MY_KV.put("session:123", JSON.stringify(user), {
  expirationTtl: 3600,
});

// 取得（type: "json" で自動パース）
const user = await env.MY_KV.get("session:123", { type: "json" });
```

---

# D1

- SQLite ベースのサーバーレスデータベース
- 構造化された、関係性のあるデータ向け
- SQL クエリが必要なものに向く

---

# D1 のコード例

```jsonc
// wrangler.jsonc
"d1_databases": [
  { "binding": "DB", "database_name": "my-db", "database_id": "<id>" }
]
```

```ts
// プレースホルダ (?) で安全にバインド
const { results } = await env.DB
  .prepare("SELECT * FROM users WHERE age > ?")
  .bind(20)
  .all();

// 書き込み
await env.DB.prepare("INSERT INTO users (name, age) VALUES (?, ?)")
  .bind("udzura", 41).run();
```

---

# R2

- S3 互換のオブジェクトストレージ
- 大きなファイルや大量のデータを置く
- 画像・動画・PDF・バックアップなどに向く
- 嬉しいポイント: **下りの転送量課金（egress）がゼロ**

---

# R2 のコード例

```jsonc
// wrangler.jsonc
"r2_buckets": [
  { "binding": "MY_BUCKET", "bucket_name": "my-bucket" }
]
```

```ts
export default {
  async fetch(req, env) {
    await env.MY_BUCKET.put("hello.txt", "world"); // 保存
    const obj = await env.MY_BUCKET.get("hello.txt"); // 取得
    if (!obj) return new Response("not found", { status: 404 });
    return new Response(obj.body); // ストリームでそのまま返せる
  },
};
```

---

# Durable Objects

- 一貫性のある状態を持てるオブジェクト
- リアルタイムに状態が変わるデータ向け
- チャット、オンラインゲームの部屋、共同編集など

---

# Durable Objects のコード例

```ts
import { DurableObject } from "cloudflare:workers";

export class Counter extends DurableObject {
  async fetch(req) {
    let v = (await this.ctx.storage.get("v")) ?? 0;
    await this.ctx.storage.put("v", ++v); // 単一インスタンスで整合
    return Response.json({ counter: v });
  }
}

export default {
  async fetch(req, env) {
    const id = env.COUNTER.idFromName("room-1"); // 名前で一意に
    return env.COUNTER.get(id).fetch(req);       // そのstubに転送
  },
};
```

---

# 非同期ジョブ

- Queues: バックグラウンド処理やリトライに使えるキュー
- Producer がメッセージを積む
- Consumer が非同期に処理する
- リクエストの応答を待たせず、重い処理を裏に逃がせる

---

# Queues のユースケース

| やりたいこと | なぜ Queues が嬉しいか |
|:---|:---|
| メール / 通知送信 | 送信失敗を自動リトライ、レスポンスを待たせない |
| 外部 API 連携 | 相手が遅い・落ちていても積んでおける |
| 重い処理の分離 | 画像変換・集計などをリクエストから切り離す |
| 流量ならし | バースト的なアクセスをバッチで平準化 |

---

# Queues のコード例（Producer）

```jsonc
// wrangler.jsonc
"queues": {
  "producers": [{ "queue": "jobs", "binding": "MY_QUEUE" }]
}
```

```ts
export default {
  async fetch(req, env) {
    // リクエストでは「積むだけ」、即レスポンス
    await env.MY_QUEUE.send({ url: req.url, at: Date.now() });
    return new Response("queued!");
  },
};
```

---

# Queues のコード例（Consumer）

```jsonc
// wrangler.jsonc
"queues": {
  "consumers": [{ "queue": "jobs", "max_batch_size": 10,
                  "max_batch_timeout": 5 }]
}
```

```ts
// 同じ Worker に queue ハンドラを生やす
export default {
  async queue(batch, env) {
    for (const msg of batch.messages) {
      try {
        await doHeavyJob(msg.body);
        msg.ack();          // 成功したら確定
      } catch {
        msg.retry();        // 失敗したら後で再配信
      }
    }
  }
};
```

---

# 認証

- Access: アプリケーションの前段に置ける認証・認可
- Google Workspace、GitHub、OIDC などと連携できる
- 社内向けツールや管理画面を守る用途に便利そう
- 認証を通ると、リクエストに **JWT が付与されて** 後段に届く

---

# Access: 認証情報の受け取り方

- Access を通過したリクエストには JWT が付く
  - ヘッダ: `Cf-Access-Jwt-Assertion`
  - （Cookie でも来るが、ヘッダ参照が推奨）
- Worker 側で **検証してから** 中身を信用する
  - 検証用の公開鍵: `${TEAM_DOMAIN}/cdn-cgi/access/certs`
  - `issuer`（チームドメイン）と `audience`（AUDタグ）を確認
- 検証後、`payload.email` / `payload.sub` で本人を特定できる

---

# Access のコード例

```ts
import { jwtVerify, createRemoteJWKSet } from "jose";

export default {
  async fetch(req, env) {
    const token = req.headers.get("cf-access-jwt-assertion");
    if (!token) return new Response("no token", { status: 403 });

    const JWKS = createRemoteJWKSet(
      new URL(`${env.TEAM_DOMAIN}/cdn-cgi/access/certs`));
    const { payload } = await jwtVerify(token, JWKS, {
      issuer: env.TEAM_DOMAIN,   // https://<team>.cloudflareaccess.com
      audience: env.POLICY_AUD,  // Application の AUD タグ
    });

    return new Response(`Hello ${payload.email}!`); // 本人が分かる
  },
};
```

---

# その他気になる・試したい

- Flagship ← 特に気になる
- Vectorize ← 特に気になる
- AI Gateway / Workers AI
- Workflows

---

# Flagship とは

- Cloudflare 製の **フィーチャーフラグ** サービス（2026〜, beta）
- コードを再デプロイせずに機能の ON/OFF・段階的ロールアウト
- 評価が **エッジの isolate 内で完結**（ネットワークホップなし）
  - 内部実装が Workers + Durable Objects + KV で構成
  - 設定は DO に書き込み → KV に配布 → 各エッジでローカル評価
- **OpenFeature 準拠**（`@cloudflare/flagship`）
  - boolean / 文字列 / 数値 / JSON を返せる
  - ターゲティングルール、割合ロールアウトに対応

---

# Vectorize とは

- グローバル分散の **ベクトルデータベース**
- 「意味が近いもの」を検索できる（埋め込みベクトルで類似検索）
  - 普通のDB:「title に 'refund' を含む行」
  - Vectorize:「'返金できますか？' と意味が近いもの」
- 用途: 意味検索 / レコメンド / 分類 / 異常検知 / **RAG**
- Workers AI で埋め込み生成 → Vectorize に保存・検索、と相性◎

```ts
// 類似ベクトルを上位 5 件取得
const matches = await env.VECTORIZE.query(queryVector, { topK: 5 });
```

---

# サンプルプロジェクト

- 各サービスの動作をまとめて試せる Worker を用意
  - https://github.com/udzura/slides/tree/master/fukuoka-edge/fukuoka-edge-sample-pj
- 1 つの Worker に R2 / KV / D1 / DO / Queues / Access を同居
  - `GET /kv`, `GET /d1`, `PUT /r2/:key`, `GET /counter/:room` ...
- `wrangler dev` でローカル起動 → 各エンドポイントを叩くだけ
  - READMEを見て設定してください

---

# 今日のまとめ

- Workers を中心に、かなり多くの部品がそろっている
- ストレージは用途ごとに選ぶのが大事
- Queues や Access まで見ると、アプリの周辺もかなり作れそう
- Flagship / Vectorize など新しめのサービスも面白い

---

<!--
_class: hero
-->

# まずは触ってみよう！！！１;

---

<!--
_class: hero
-->

# おしまい

