# go-toto

スライド「Goの紹介＋バックエンドエンジニアのための負荷試験」のサンプル実装。
Go + echo + SQLite で動く小さな TODO API。

## 起動

```sh
cd misc/go-toto
go mod tidy
go run .
```

`http://localhost:8080` で起動。DBファイルは `todo.db` (env `TODO_DB` で変更可)。

## エンドポイント

| Method | Path          | 説明        |
| ------ | ------------- | ----------- |
| GET    | `/healthz`    | ヘルスチェック |
| GET    | `/todos`      | 一覧取得    |
| POST   | `/todos`      | 作成        |
| GET    | `/todos/:id`  | 1件取得     |
| PUT    | `/todos/:id`  | 更新        |
| DELETE | `/todos/:id`  | 削除        |

## 動作確認

```sh
# 作成
curl -s -XPOST localhost:8080/todos \
  -H 'Content-Type: application/json' \
  -d '{"title":"buy milk"}'

# 一覧
curl -s localhost:8080/todos

# 更新
curl -s -XPUT localhost:8080/todos/1 \
  -H 'Content-Type: application/json' \
  -d '{"done":true}'

# 削除
curl -s -XDELETE localhost:8080/todos/1
```

## k6 で負荷試験

```sh
k6 run k6/scenario.js
```
