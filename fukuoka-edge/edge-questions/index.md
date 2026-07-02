----
marp: true
theme: default
paginate: true
title: "エッジランタイム質問タイム"
description: "Fukuoka.edge"
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

# エッジランタイム質問タイム

### Fukuoka.edge

---

# 進め方

- 挙手で聞きます！
- 回答内容について深掘り質問するかもしれません！

---

<!--
_class: hero
-->

# 1. 導入

---

# Q1. 普段、エッジランタイムをどのくらい触っていますか？

1. 業務でゴリゴリ本番運用している
2. 個人開発や検証ステージで触っている
3. これから触りたい、今日はキャッチアップに来た

<!--
Comment: まず会場の経験値を確認して、このあとの話の深さを合わせる。
-->

---

# Q2. 普段のメインの主戦場はどこですか？

1. AWS / Google Cloud などのメガクラウド
2. Cloudflare や Vercel などのエッジプラットフォーム
3. オンプレや VPS

<!--
Comment: エッジをどの世界から見ている人が多いかを把握する。
-->

---

<!--
_class: hero
-->

# 2. なぜエッジを使うのか？

---

# Q3. エッジランタイムに一番期待していることは？

1. 圧倒的な低遅延
2. サーバー管理からの解放、手軽なデプロイ
3. インフラコストを抑えること
4. 下り転送量無料などの特定の強み

<!--
Comment: 低遅延だけでなく、運用や課金の期待も拾う。R2 の話への導線にする。
-->

---

<!--
_class: hero
-->

# 3. 深掘り

---

# Q4. エッジからデータを触るとき、どうしますか？

1. D1 や KV など、エッジネイティブなストレージに寄せる
2. 外部のクラウドサービスのRDBなどにエッジから接続する
3. エッジは認証前段やプロキシと割り切り、データは触らない

<!--
Comment: ストレージパートの前に聞くと、D1/KV/R2/DO の使い分けに入りやすい。
-->

---

# Q5. エッジの結果整合性、許容できますか？

1. 全然OK、ユースケースを選べば問題ない
2. かなり気を遣うので、怖さはある

<!--
Comment: KV の反映ラグで悩む人が多ければ、Durable Objects や Flagship の話につなげる。
-->

---

<!--
_class: hero
-->

# 4. 応用・未来

---

# Q6. Cloudflare の新しめの機能、どれが気になりますか？

1. Flagship: エッジ完結の高速なフラグ判定
2. Vectorize: エッジで RAG や AI 検索
3. Queues / Access などの実務寄りサービス

<!--
Comment: 後半でどの話題に厚めに反応するかを見る。まとめの話題選びにも使える。
-->

---

# 結果を受けて

- なんかいい感じに将来の自分がまとめるであろう


