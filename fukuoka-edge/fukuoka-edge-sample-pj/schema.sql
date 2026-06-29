-- D1 用の最小スキーマ。`npm run db:apply` で適用できる。
DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id   INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  age  INTEGER NOT NULL
);

INSERT INTO users (name, age) VALUES
  ('udzura', 38),
  ('alice', 25),
  ('bob', 17);
