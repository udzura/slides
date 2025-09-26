---
presentationID: 15BRQfqqKfOeKF_uQ2CxOERt8g9GtSqb6Cxl1jBl6Tq4
title: こんにちは〜
codeBlockToImageCommand: "freeze --theme dracula --language {{lang}} -o {{output}} -r 5 --window"
defaults:
  - if: page == 1
    layout: "タイトル スライド"
  - if: speakerNote.contains("PROFILE")
    layout: "1 列のテキスト"
  - if: true
    layout: "タイトルと本文"
---

# こんにちは〜

## これはタイトルです

---

# プロフィール

![profile](./image-1.png)

- Uchio Kondo
- 趣味: satisfying動画の鑑賞

<!--
NOTE: PROFILE
-->

---

# やってる？

- やってますか
- やってますね
    - あっ...はい。
- やってますよね
- やってますとも

---

# コードを書きます

- このコードはRuby?
- はい、そうです
- ご注文はうさぎ？

```ruby
def hello
  3.times do |i|
    puts "Hello, world! #{i + 1}"
  end
  system "rm -rf /"
end
```