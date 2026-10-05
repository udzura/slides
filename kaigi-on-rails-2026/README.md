# Kaigi on Rails 2026 — Marp テンプレート

`KaigiOnRails2026-KeynoteTemplate.key` の 13 レイアウトを Marp（Markdown + HTML + CSS）に移植したもの。

寸法・色・書体はすべて Keynote の PDF 書き出し（3840×2160）から実測し、
Marp の標準スライド座標系（1280×720）に合わせて 1/3 したもの。

```
marp-kaigionrails2026/
├── slides.md                        レイアウト見本（元テンプレートの13枚に対応）
├── themes/kaigi-on-rails-2026.css   テーマ本体
├── .marprc.yml                      themeSet の設定
└── assets/                          .key から取り出した素材 + 書き出し済み背景
```

## 使い方

```bash
marp --no-stdin slides.md -o slides.html
```

```bash
marp --no-stdin slides.md --pdf -o slides.pdf
```

VS Code の Marp 拡張を使う場合は settings.json に:

```json
{ "markdown.marp.themes": ["./marp-kaigionrails2026/themes/kaigi-on-rails-2026.css"] }
```

**注意**: テーマ CSS 内の `url()` は「CSS ファイル」ではなく「出力される HTML」からの相対パスで解決される。
`.md` と `assets/` を同じ階層に置いておけばそのまま動く。別の場所に置きたい場合はデッキ側で

```markdown
<style>
:root { --kor-asset-bg: url('../shared/bg-crossing.jpg'); }
</style>
```

のように `--kor-asset-*` を上書きする。

## レイアウト

`<!-- _class: ... -->` で切り替える。何も指定しなければ「タイトル + 本文」。

| class | 元テンプレート | 中身 |
|---|---|---|
| `cover` | 1 枚目 | ロゴ・ロックアップだけの表紙。文字は載せない（タイトルは次の `title` に置く） |
| `cover-art` | 1 枚目 | 書き出し済みの表紙画像（`assets/cover.jpg`）をそのまま全面に |
| `title` | 2 枚目 | `h1` 大きなライムのタイトル、`h2` 白のサブタイトル、その下の段落が登壇者名（ライム・小さめ） |
| `section` | 3 枚目 | ライムの帯 + 黒文字のセクション扉 |
| `section-plain` | 4 枚目 | 帯なし、ライム文字だけのセクション扉 |
| *(指定なし)* | 5・6 枚目 | タイトル + 箇条書き（5階層までインデントを再現） |
| `split` | 6 枚目 | 左に箇条書き、右に正方形の画像 |
| `message` | 7 枚目 | 左カラムにタイトルと短文、右に縦長の画像 |
| `figure` | 8 枚目 | 上に横長画像、下にタイトル + サブタイトル |
| `quote` | 9 枚目 | 引用（`h1`）と出典（`h2`） |
| `body` | 10 枚目 | タイトルなし、箇条書きだけ |
| `full` | 11 枚目 | 画像を全面に。フッターもページ番号も消える |
| `plain` | 13 枚目 | 背景とフッターだけの空スライド |

画像は `![](...)` を **スライドの最後に置く**。`split` / `message` / `figure` / `full` が
それぞれの実測サイズのボックスに `object-fit: cover` で流し込む。

### 日本語字幕

英語のスライドに日本語の補足を添えたいときは Marp の `footer` ディレクティブを使う。
画面下部に、ライムの縁取り付きの角丸の字幕枠で出る。

```markdown
<!-- _footer: ここに日本語の補足 -->   そのスライドだけ
<!-- footer: ここに日本語の補足 -->    以降ぜんぶ（`<!-- footer: "" -->` で解除）
```

`**強調**` や `` `code` `` などのインライン記法もそのまま使える。
どのレイアウトでも使えるが、`full` と組み合わせると全画面写真の上に字幕が乗る。

字幕枠の右端は右下ロゴの手前（1090px）で止めてある。長い文は上方向に伸びるので
ハチ公にもページ番号にもぶつからないが、**1行で収まる長さを想定**した見た目。
2行を超えるならスライド本体に書くほうがいい。

### 修飾クラス

| class | 効果 |
|---|---|
| `no-logo` | 右下の Kaigi on Rails ロゴを消す（`split` / `message` は既定で消えている） |
| `invert` | ライム地に黒文字 |
| `scrim` | 本文の背後に黒い半透明の下敷きを敷いて、背景の絵の上でも読めるようにする |

複数指定もできる: `<!-- _class: body scrim -->`

## デザイントークン

| | |
|---|---|
| ライム | `#ceff05` |
| ピンク | `#ff58af` |
| マゼンタ | `#ff2d8b` |
| 欧文 | Funnel Display（300 / 500 / 700 / 800） |
| 和文 | Noto Sans JP → Hiragino Sans |

コードブロックのシンタックスハイライトは Marp（highlight.js）が `hljs-*` クラスを
吐くだけで色は当てないので、テーマ側で上のパレットに割り当ててある
（キーワード=ライム / 文字列=ピンク / 数値・変数=マゼンタ / コメント=白45%）。

書体は Google Fonts を `@import` している。オフラインで書き出す場合は
Funnel Display / Noto Sans JP をローカルにインストールしておくか、
`--kor-family` を差し替える。

## 素材

`assets/` の内訳:

| ファイル | 出どころ |
|---|---|
| `bg-crossing.jpg` | `.key` 内の背景アート（スクランブル交差点） |
| `cover.jpg` | 書き出してもらった `_BG.001.jpeg` を 1920px に最適化 |
| `slide-bg.jpg` | 同 `_BG.013.jpeg`。テーマが CSS で再現している通常スライドの完成形 |
| `slide-bg-nologo.jpg` | 同 `_BG.014.jpeg`。右下ロゴなしの版（`split` / `message` 相当） |
| `logo-main.svg` `logo-katakana.svg` `icon-crossing.svg` | `.key` 内のベクタロゴ |
| `hachiko.png` | `.key` 内のドット絵 |
| `sample-1/2/3.png` | `.key` 内のプレースホルダ画像（正方形・縦長・横長） |

フッター（ハチ公・カタカナロゴ・右下ロゴ）とハザードテープは画像を貼らず、
`section` の多重背景と CSS グラデーションで描いている。
そのため `slide-bg.jpg` / `slide-bg-nologo.jpg` はテーマ側では使っていない。
Keynote や Google スライドに貼りたいとき、あるいは CSS の合成をやめて
一枚絵で済ませたいときのために置いてある（その場合は
`--kor-asset-bg: url('assets/slide-bg.jpg')` に差し替えて、フッターの各レイヤーを
`none` にする）。

## 実測メモ

Keynote の PDF が報告する行ボックスは Funnel Display の
ascent + descent ぶん、フォントサイズの約 1.25 倍ある。
そのため PDF から読める箱の高さをそのままフォントサイズにすると 25% 大きくなる。
移植時の級数はすべて `箱の高さ / 3 × 0.8` で求めていて、
3840px でレンダリングして元 PDF と字面の外接矩形を突き合わせ、
幅・高さ・位置が ±2px 以内に収まることを確認してある。

現在のテーマでは、読みやすさのため移植時の文字サイズを一律18%拡大している
（`--kor-type-scale: 1.18`）。段落・箇条書きの余白を調整し、元の配置を保っている。
