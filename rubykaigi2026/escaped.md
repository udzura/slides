----

```bash
$ cargo install uzumibi-cli
$ uzumibi new --template cloudflare --features enable-external my-app
```

----

```
my-app/
├── Cargo.toml
├── lib
│   └── app.rb
├── package.json
├── src
│   └── index.js
├── vitest.config.js
├── wasm-app
│   ├── build.rs
│   ├── Cargo.toml
│   └── src
│       └── lib.rs
└── wrangler.jsonc

5 directories, 9 files
```

----

# The Generated `app.rb`

<br />
<br />

```ruby
# Any Rubyist can guess what this does...
class App < Uzumibi::Router
  get "/" do |req, res|
    res.status_code = 200
    res.headers = {
      "content-type" => "text/plain",
      "x-powered-by" => "#{RUBY_ENGINE} #{RUBY_VERSION}"
    }
    res.body = "It works!\n"
    res
  end
end

$APP = App.new
```

<!--
```ruby
    res.headers = {
      "content-type" => "application/json"
    }
    res.body = JSON.generate({"message" => "It works!"})
```

-->

----

# Artifact Size

- WebAssembly file: **1.2MiB** before compression
- After gzip: **~370KiB**
- Easily fits within **Cloudflare Workers free plan**

<!--
-->

----

```
Total Upload: 1224.92 KiB / gzip: 369.05 KiB
Your Worker has access to the following bindings:
Binding                                    Resource            
env.UZUMIBI_KV_DATA (UzumibiKVObject)      Durable Object      
env.ASSETS                                 Assets              

Uploaded sample-app-xxx (7.59 sec)
Deployed sample-app-xxx triggers (1.53 sec)
  https://sample-app-xxx.udzura.workers.dev
Current Version ID: 2bfc85d2-7582-436a-98fd-xxxxxxxx

```

----
