---
marp: true
theme: kaigi-on-rails-2026
paginate: true
size: 16:9
---

<!-- _class: cover -->
<!-- _paginate: false -->

---

<!-- _class: title -->

# Your Slide Title

## Your Name Here

---

<!-- _class: section -->

# Today’s Topics

---

<!-- _class: section-plain -->

# Today’s Topics

---

# Title Text

- Your Name
- More Profile

---

<!-- _class: split -->

# Title Text

- Body Level One
  - Body Level Two
    - Body Level Three
      - Body Level Four
        - Body Level Five

![](assets/sample-1.png)

---

<!-- _class: message -->

# Title Text

Your Message

Your Message

Your Message

Your Message

![](assets/sample-2.png)

---

<!-- _class: figure -->

# Title Text

## Sub Title

![](assets/sample-3.png)

---

<!-- _class: quote -->

# “Insert quote here”

## –DHH

---

<!-- _class: body -->

- Body Level One
  - Body Level Two
    - Body Level Three
      - Body Level Four
        - Body Level Five

---

<!-- _class: full -->

![](assets/sample-3.png)

---

# Design Assets

- **Funnel Display** / Noto Sans JP
- `#ceff05` lime — `#ff58af` pink — `#ff2d8b` magenta
- ロゴ・カタカナロゴ・ハチ公・ハザードテープ

---

<!-- _class: plain -->

---

<!-- _class: invert -->

# invert

黒文字にライム地。強調は **マゼンタ** になる。

---

<!-- _class: scrim -->

# scrim

- 背景の絵が濃いところでも本文を読ませたいときに使う
- 日本語混じりの本文でも行送りが崩れないことの確認
- `code` やリンクもそのまま置ける

```ruby
class Talk < ApplicationRecord
  belongs_to :speaker
end
```

---

# Code Sample

- The code is below:

```rb
def fib(n) # Fib using recur
  case n
  when 0..1
    1
  else
    fib(n - 1) + fib(n - 2)
  end
end
```

```js
// Immediate call
(function() { console.log("Foo"); return 1; })();
```

---

<!-- _footer: Marp の `footer` ディレクティブがそのまま**字幕**になる。 -->

# Subtitles

- English on the slide
- Japanese underneath

---

<!-- _footer: Marp の `footer` ディレクティブがそのまま**字幕**になる。<br>英語のスライドに日本語の補足を添えるときに使う。長い時、2行の時はこうなる。 -->

# Subtitles

- English on the slide
- Japanese underneath
