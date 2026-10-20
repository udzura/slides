# udzura-archive

スライド一覧サイトの `docs/assets/archive.css` に合わせた Marp テーマ。
生成り `#f6f4ee`、墨色 `#252924`、朱色 `#b53d27`、細い罫線と左揃えの見出しを使う。
16:9（1280×720）を想定。外部フォントや画像への依存はない。

Markdown の frontmatter で指定する：

```yaml
marp: true
theme: udzura-archive
paginate: true
size: 16:9
header: "**Uchio Kondo** / Slides"
footer: "イベント名"
```

リポジトリルートからテーマを明示する場合：

```sh
marp --no-stdin fukuokawasm-1/index.md --theme themes/udzura-archive.css --html -o fukuokawasm-1/index.html
```

`fukuokawasm-1` には `.marprc.cjs` があるので、同ディレクトリでは以下でもよい：

```sh
cd fukuokawasm-1
marp --no-stdin index.md -o index.html
```

利用できるスライド単位のクラス：

- `<!-- _class: hero -->`：左揃えの大きなタイトルと朱色のドット。
- `<!-- _class: small-code -->`：長めのコード用（20px）。
- `<!-- _class: references -->`：参考資料用。

VS Code は `markdown.marp.themes` に `themes/udzura-archive.css` を登録する。
本文の中に CSS をコピーせず、テーマファイル側で調整する。
