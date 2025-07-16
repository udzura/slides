# WasmでAI Agentを作って見た

## きっかけ
  - rm -rf / するエージェント
  - コンテナ使え？それはそう
  - Macでコンテナちょっとだるくない？
  - Wasm + WASIでできるはず？
## Wasmでエージェントって作れるの？
  - 言語: Rust
  - 基本的にはAPIを叩くだけ
  - Claudeにががっと作らせて手直し
## 困ったこと
  - コネクションが切れる... TLSじゃないじゃん！
    - opensslをwasm上で！？
  - ureq というやつを使い出した
  - ureq の依存
    - rustls = pure rust tls これならいける？
    - 依存関係のビルドにwasi-sdkは必要だった
  - ビルドできたが権限？ ???
    - 雰囲気でこのオプションにした
  - 証明書が...
    - ここはnon verify(TODO)
    - 多分root CAをwasi環境に送り込めばいける
  - ファイルにアクセスさせてみる
    - /etc/hosts を見ようとしないので無理やる見せるinstruction
    - Wasmなしで実行
    - wasmtime + ホストファイルシステム共有なしで実行
  - まとめ
    - 全部WasmのシェルでもできたらAgentが捗るんじゃね？作るの大変だけど...
    - 何でもかんでもRustに移植されてるしいつかは？