----
marp: true
theme: default
paginate: true
size: 16:9
title: "Uzumibiの紹介: Rubyを書けばCloudflare Workerにそのままデプロイできるってマ！？"
description: "Cloudflare Tech Talk / Uzumibi introduction"
style: |
  :root {
    --cf: #f38020;
    --ink: #1f2937;
    --purple: #6d28d9;
    --soft: #fff3e8;
    --line: #fed7aa;
  }
  section {
    background: #fffdf9;
    color: var(--ink);
    font-size: 27px;
    padding: 52px 72px;
  }
  h1, h2 { color: var(--cf); letter-spacing: -0.03em; }
  h1 { font-size: 48px; }
  h2 { font-size: 34px; }
  strong { color: var(--purple); }
  code { color: #7c2d12; }
  pre {
    background: #1f2937;
    border-radius: 16px;
    box-shadow: none;
    font-size: 20px;
    line-height: 1.35;
    padding: 18px 24px;
  }
  pre code { color: #f9fafb; }
  section table { font-size: 22px; }
  section th { color: #9a3412; }
  section.hero {
    display: flex;
    flex-direction: column;
    justify-content: center;
    background: linear-gradient(135deg, #fffdf9 0%, #fff3e8 100%);
  }
  section.hero h1 { font-size: 52px; margin-bottom: 0.2em; }
  section.dark {
    background: #1f2937;
    color: #f9fafb;
  }
  section.dark h1, section.dark h2 { color: #fdba74; }
  section.dark strong { color: #fcd34d; }
  section.lead h1 { font-size: 56px; }
  .sub { color: #6b7280; font-size: 26px; }
  .muted { color: #6b7280; }
  .tiny { font-size: 18px; color: #6b7280; }
  .accent { color: var(--cf); }
  .tag {
    display: inline-block;
    padding: 5px 14px;
    border: 2px solid var(--cf);
    border-radius: 999px;
    color: #9a3412;
    font-weight: bold;
    margin-right: 8px;
    font-size: 20px;
  }
  .flow { display: flex; align-items: stretch; gap: 14px; margin-top: 28px; }
  .flow .box {
    flex: 1;
    border: 2px solid var(--line);
    border-radius: 16px;
    background: #fff;
    padding: 20px 16px;
    text-align: center;
    font-weight: bold;
  }
  .flow .arrow {
    flex: 0 0 30px;
    align-self: center;
    color: var(--cf);
    font-size: 34px;
    text-align: center;
  }
  .flow .wasm { border-color: #a78bfa; background: #faf5ff; }
  .flow .ruby { border-color: #fb7185; background: #fff1f2; }
  .split { display: flex; gap: 38px; align-items: center; }
  .split > * { flex: 1; }
  .quote {
    border-left: 9px solid var(--cf);
    padding: 18px 28px;
    background: var(--soft);
    font-size: 36px;
    font-weight: bold;
    line-height: 1.35;
  }
  .big { font-size: 48px; font-weight: bold; line-height: 1.2; }
  .service-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; margin-top: 18px; }
  .service {
    border-left: 8px solid var(--cf);
    background: #fff;
    padding: 14px 18px;
    border-radius: 0 10px 10px 0;
  }
  .service b { color: #9a3412; }
  .feature { color: #9a3412; font-size: 21px; }
  .center { text-align: center; }
----

<!--
_class: hero
-->

# Uzumibiの紹介:

## Rubyを書けばCloudflare Workerに<br>そのままデプロイできるってマ！？

<br>

Cloudflare Tech Talk in Fukuoka<br>
<span class="sub">Uchio Kondo / @udzura</span>

---

# 今日の結論

<div class="quote">
  Cloudflare Workers は Rubyist にも面白い。<br>
  <strong>だから、Rubyで入れる足場を作った。</strong>
</div>

<div class="flow">
  <div class="box">Rubyで書く</div>
  <div class="arrow">→</div>
  <div class="box wasm">小さな Wasm にする</div>
  <div class="arrow">→</div>
  <div class="box">Cloudflare Workers</div>
</div>

---

<!--
_class: hero
-->

# Workers、ずっと楽しそう

- エッジで小さなアプリやAPIを動かせる
- binding で KV・Queues・Access などにつながる
- TypeScript / Hono を中心に、いい開発体験が育っている

<p class="big accent">「これ、Rubyで書きたいな……」</p>

---

# でも Rubyist は、ちょっと入りづらい

<div class="split">

<div>

### Workersの典型的な景色

```ts
export default {
  async fetch(req, env) {
    await env.MY_QUEUE.send({ url: req.url });
    return Response.json({ ok: true });
  }
};
```

</div>

<div>

### Rubyistの気持ち

<p class="big">Rubyが書けないなら、<br>触る理由がない……？</p>

</div>

</div>

---

# `ruby.wasm` があるじゃん？

<div class="split">

<div>

- もちろん、CRubyをWasmで動かす取り組みはある
- ただしWorkersに気軽に載せるには、ランタイムが大きい
- 小さく素早く配るWorkerと、少し噛み合いにくかった

</div>

<div class="quote">
  Rubyが悪いのではない。<br>
  <strong>WorkersでRubyを動かすための<br>別の作り方が必要だった。</strong>
</div>

</div>

<p class="tiny">※ バイナリサイズはRuby機能・ビルド条件・圧縮方法で変わります。</p>

---

<!--
_class: lead
-->

# なら、Rubyで書けない世界に<br>Rubyで切り込むしかない

<p class="big">それが Rubyist では？</p>

---

# 作戦: Wasmを使おう

<div class="flow">
  <div class="box">Cloudflare Worker<br><span class="muted">JavaScript host</span></div>
  <div class="arrow">↔</div>
  <div class="box wasm">WebAssembly<br><span class="muted">小さく・持ち運べる</span></div>
  <div class="arrow">↔</div>
  <div class="box ruby">Ruby VM<br><span class="muted">Ruby app を実行</span></div>
</div>

<br>

- CRubyより、組み込み向けの **mruby** が相性よさそう
- Rubyのアプリは、ビルド時にバイトコードへコンパイルして埋め込む

---

# でも mruby をそのまま固めればいい？

<div class="split">

<div>

### 期待

<p class="big">軽量なRuby<br>＋ Wasm</p>

</div>

<div>

### 現実

- mrubyはC言語の資産
- 制御フローに `setjmp` / `longjmp` を使う
- Wasmにしたときの構成や出力を、細かく制御したい

</div>

</div>

---

# そういえば、趣味で作っていた

<div class="flow">
  <div class="box ruby">mruby VM を<br>Rustで実装</div>
  <div class="arrow">＋</div>
  <div class="box wasm">Rustの<br>Wasm ecosystem</div>
  <div class="arrow">＝</div>
  <div class="box"><strong>mruby/edge</strong></div>
</div>

<br>

<p class="big">これをWorkersに持ち込んだら、<br>どうなる？</p>

---

<!--
_class: dark
-->

# JavaScript と Wasm の間に<br>グルーコードを書いてみた

<div class="flow">
  <div class="box">`Request` を読む</div>
  <div class="arrow">→</div>
  <div class="box wasm">Wasmへ渡す</div>
  <div class="arrow">→</div>
  <div class="box ruby">Rubyを呼ぶ</div>
  <div class="arrow">→</div>
  <div class="box">`Response` を返す</div>
</div>

<br>

<p class="big">割とシュッと動いたぞ！？</p>

---

<!--
_class: hero
-->

# ということで

# mruby/edge + Uzumibi

<p class="big">RubyをWorkersへ持ち込む<br>フレームワークになりました。</p>

---

# Uzumibi とは何か

<div class="service-grid">
  <div class="service"><b>Ruby HTTP framework</b><br>Sinatra風のルーティング</div>
  <div class="service"><b>project generator</b><br>Cloudflare用の一式を生成</div>
  <div class="service"><b>mruby/edge runtime</b><br>Rust製Ruby VMをWasm化</div>
  <div class="service"><b>platform adapter</b><br>Workers APIとRubyを接続</div>
</div>

<br>

<span class="tag">Ruby</span><span class="tag">Wasm</span><span class="tag">Cloudflare Workers</span>

---

# まずはプロジェクトを作る

```bash
cargo install uzumibi-cli
uzumibi new --template cloudflare hello-uzumibi
cd hello-uzumibi
pnpm install
pnpm run dev
```

```text
hello-uzumibi/
├── lib/app.rb          # ここをRubyで書く
├── src/index.js        # Workersの入口
├── wasm-app/           # Rust + 埋め込みRuby
└── wrangler.jsonc      # Cloudflare bindingの設定
```

---

# `lib/app.rb` を書く

```ruby
class App < Uzumibi::Router
  get "/hello/:name" do |req, res|
    res.return(
      200,
      { "content-type" => "application/json" },
      JSON.generate({ hello: req.params[:name] })
    )
  end
end

$APP = App.new
```

<p class="feature">Rubyを変更したら `pnpm run dev` でビルドしてWorkerを再起動。</p>

---

# 動いているものは、こういう構成

<div class="flow">
  <div class="box">HTTP Request<br><span class="muted">Cloudflare edge</span></div>
  <div class="arrow">→</div>
  <div class="box">`src/index.js`<br><span class="muted">Worker host</span></div>
  <div class="arrow">→</div>
  <div class="box wasm">Wasm<br><span class="muted">mruby/edge + Uzumibi</span></div>
  <div class="arrow">→</div>
  <div class="box ruby">`app.rb`</div>
</div>

<br>

<div class="flow">
  <div class="box ruby">Ruby Response</div>
  <div class="arrow">←</div>
  <div class="box wasm">Wasm memory</div>
  <div class="arrow">←</div>
  <div class="box">Workers `Response`</div>
</div>

---

# Rubyから、Cloudflareの機能も使いたい

<div class="service-grid">
  <div class="service"><b>Workers KV</b><br>小さな値を読む・書く</div>
  <div class="service"><b>Secrets</b><br>Worker environment bindingを読む</div>
  <div class="service"><b>Cloudflare Access</b><br>ログイン済みユーザーを取得</div>
  <div class="service"><b>Queues</b><br>リクエストから仕事を切り離す</div>
</div>

<br>

```bash
# HTTP + 外部Workers API
uzumibi new --template cloudflare --features enable-external my-app

# Queue consumer（上の機能を含む）
uzumibi new --template cloudflare --features queue my-consumer
```

---

# KV: Rubyで小さな状態を読む・書く

```ruby
get "/counter" do |req, res|
  count = (Uzumibi::KV.get("counter") || "0").to_i
  res.return(200, { "content-type" => "application/json" },
             JSON.generate({ count: count }))
end

post "/counter/increment" do |req, res|
  count = (Uzumibi::KV.get("counter") || "0").to_i + 1
  Uzumibi::KV.set("counter", count.to_s)
  res.return(200, {}, "#{count}\\n")
end
```

<p class="feature">`UZUMIBI_KV` binding を `wrangler.jsonc` に設定して使います。</p>

---

# Secrets: Rubyに秘密を書かない

```ruby
post "/webhook" do |req, res|
  signing_secret = Uzumibi::Secret.get("SIGNING_SECRET")

  unless valid_signature?(req.raw_body, signing_secret)
    res.return(401, {}, "invalid signature\\n")
  else
    res.return(204, {}, "")
  end
end
```

<div class="quote">
  ソースコードではなく、<strong>Workerの環境 binding</strong> から読む。
</div>

---

# Access: 社内ツールをRubyで守る

```ruby
Uzumibi::Access.team = "my-team"

get "/admin" do |req, res|
  token = req.cookie["CF_Authorization"]
  identity = Uzumibi::Access.get_identity(token)

  res.return(200, { "content-type" => "text/plain" },
             "Hello, #{identity.email}!\\n")
end
```

<p class="feature">Accessで保護されたリクエストの `CF_Authorization` cookie を渡し、identityを取得します。</p>

---

# Queue: HTTPを「積むだけ」にする

<div class="flow">
  <div class="box">Webhook<br>request</div>
  <div class="arrow">→</div>
  <div class="box ruby">Ruby router<br>`Queue.send`</div>
  <div class="arrow">→</div>
  <div class="box">Cloudflare<br>Queue</div>
  <div class="arrow">→</div>
  <div class="box ruby">Ruby consumer<br>`on_receive`</div>
</div>

<br>

- リクエストは **202 Accepted** ですぐ返す
- 失敗時はconsumer側で `retry` できる

---

# Queue producer: Rubyで積む

```ruby
post "/jobs" do |req, res|
  Uzumibi::Queue.send("UZUMIBI_QUEUE", req.raw_body)

  res.return(
    202,
    { "content-type" => "text/plain" },
    "queued\\n"
  )
end
```

<p class="feature">引数はQueueのリソース名ではなく、Wranglerで設定した <code>binding</code> 名。</p>

---

# Queue consumer: Rubyで受けてリトライ

```ruby
class Consumer < Uzumibi::Consumer
  def on_receive(message)
    payload = JSON.parse(message.body)
    deliver_notification(payload)
    message.ack!
  rescue => error
    debug_console("failed: #{error.message}")
    message.retry(delay_seconds: 10)
  end
end

$CONSUMER = Consumer.new
```

<p class="feature">`lib/consumer.rb` に書く。QueueテンプレートはHTTP requestを受けず、event consumerとして動きます。</p>

---

# どんなものに向いている？

| やりたいこと | Uzumibi + Workers の形 |
|:---|:---|
| 小さなJSON API | Ruby router + Workers |
| 社内向け管理画面 | Ruby router + Access + Secrets |
| Webhook連携 | Rubyで検証 → Queueに投入 |
| 設定や軽い状態 | Ruby + Workers KV |
| バックグラウンド処理 | Ruby Queue Consumer |

---

# 現在地: できることと、割り切ること

<div class="split">

<div>

### できる

- RubyでHTTP routing
- Workersのbindingと連携
- Wasmとして小さく配る

</div>

<div>

### 割り切る

- CRubyの全機能・native extensionではない
- Rubyの変更はビルド時に埋め込む
- Cloudflare固有APIは、他テンプレートへの完全な移植性を約束しない

</div>

</div>

---

<!--
_class: hero
-->

# まとめ

<div class="quote">
  Workersが面白そうなのに、Rubyが書けない。<br>
  だったら <strong>Rubyを書けるようにした。</strong>
</div>

<br>

- **mruby/edge**: Rust製の軽量Ruby VM
- **Uzumibi**: RubyをWasm経由でWorkersへ持ち込む足場
- **Cloudflare連携**: KV / Secrets / Access / Queues

<br>

<span class="accent">https://github.com/mrubyedge/uzumibi</span>

---

<!--
_class: hero
-->

# ありがとうございました！

<p class="big">RubyでWorkers、やっていきましょう。</p>

<br>

<span class="sub">Uzumibi documentation: https://mrubyedge.github.io/uzumibi/</span>
