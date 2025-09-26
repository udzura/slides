# 入門CarrierWave

## 〜禅とファイルアップロード移行技術〜

----

# 俺

- @udzura
- 趣味: satisfying動画の鑑賞

---

# 皆さんは

- ファイルをアップロードしていますか？

---

# CarrierWaveとは

- Ruby製のファイルアップロードライブラリ
- 画像のリサイズやサムネイル生成もできる


---

# CarrierWaveの使い方

- 留意点:
  - バージョン `1.3.2` の仕様やで
  - ...

---

```ruby
class AvatarUploader < CarrierWave::Uploader::Base
  def store_dir
    "uploads/#{model.class.to_s.underscore}/#{mounted_as}/#{model.id}"
  end
end

class User < ApplicationRecord
  mount_uploader :avatar, AvatarUploader
end
```

---

# `mount` すると

## モデルとしては
- `avatar`, `avatar=` というメソッドが生える
  - これはStringではなく、CarrierWave::Uploader::Baseのサブクラスのインスタンス

## DBとしては
- `avatar` というカラムに、avatarをrepresentする文字列が入る

---

# 本来、このavatarとそのavatarは別名にできたりする

```ruby
class User < ApplicationRecord
  mount_uploader :profile_image, AvatarUploader, mount_on: :avatar_full_path
end
```

---

# じゃあアップロードしましょう

```ruby
user = User.new
user.avatar = params[:file]
unless user.valid?
  raise "Hoge"
end
user.save!
```

---

# Things happening

---

# ファイルオブジェクトがアサインされてからの流れ

- `user.avatar = params[:file]` アサインが走る
  - `CarrierWave::Uploader::Base#cache!` が呼ばれる
  - **副作用で** 一時ディレクトリにファイルが保存される
    - 一時ディレクトリは `cache_path` に保存される
    - `cache_path` は `cache_dir` + `filename` で決まる

---

# ここで

- モデルのバリデーションが失敗したら...？

---

# cache idの概念

- `cache!` されると...
  - `cache_id` という一意な、推測不可能なIDが生成される
  - `cache_id` はDBに保存されない
    - そのユーザのセッションだけで使う想定
- `cache_key` で参照できる
  - 戻ってきたフォームでそれを参照して再送するようにできる

---

```ruby
def generate_cache_id
  # TBA
end
```

---

# cache idで本来のキャッシュを復元できる（ようになっている）

- 一度バリデーションに失敗してフォームに戻ってしまった
- 別のリクエストで一からファイルを構築する

---

# 実は

- `mount_uploader :avatar, AvatarUploader` で以下のメソッドも生えてくるのだ
  - `avatar_cache`
  - `avatar_cache=`

---

# `avatar_cache=` でcache idをセットする

```ruby
user = User.new
user.avatar_cache = params[:avatar_cache]
user.cached? # => true
# ...
```

---

# `avatar_cache=` で起こること（Retrieve）

- `CarrierWave::Uploader::Base#retrieve_from_cache!` が呼ばれる
  - `cache_id` から必要な情報が復元される
    - 必要に応じてフックも呼ばれる
  - `cache_path` が復元される
  - GCSなどにはすでにアップロードされているので、Pathがわかれば参照できる

---

# ということで非同期アップロードの仕組みについて

- TBA

---

# ここまでのまとめ

- ファイルがアップロードされると、まずfileのアサインで副作用が起き、キャッシュファイルがアップロードされる
- 一度アップされたら、`cache_id` を使ってキャッシュファイルを復元できる

---

# バリデーションが通ったら？

```ruby
user = User.new
user.avatar = params[:file]
unless user.valid?
  raise "Hoge"
end
## !!! 実はここまでの話しかしていない !!!
user.save!
```

---

# `save!` で何が起こる？

- `after_save` コールバックで `CarrierWave::Mount::Mounter#store!` が呼ばれる
  - `CarrierWave::Uploader::Base#store!` が呼ばれる
    - `store_path` （永続化パス）にファイルが保存される
      - `store_path` も似たように `store_dir` + `filename` で決まる
    - ここで、すでに実体はキャッシュパス側にあるので、再アップは必要ない
      - GCSなら copy_object を走らせて済ませている

---

# 無事保存できました

- めでたしめでたし...

---

# ちなみにアップしたファイルを参照するには？

- なんかこんな感じで、findしたら勝手にavatarが参照できるようになってるが

```ruby
user = User.find(params[:id])
render json: {avatar: user.avatar.url}
```

---

# 実はこの時:

- `avatar` メソッドを最初に呼んだ時にもRetrieveが走っている
  - DB上に保存されている方のavatarの文字列をもとに
  - `CarrierWave::Uploader::Base#retrieve_from_store!` が呼ばれる
    - `store_path` が決定される
    - GCSの永続化パスと無事一致すれば、アップしたファイルに再びアクセスできる

---

# CarrierWaveの全体像

図

---

# CarrierWaveの設計思想

- saveする前に一度キャッシュとして永続化する
  - そのキャッシュは、cache nameが分かれば復元できること
- saveしたら、キャッシュから永続化パスに移動する
  - その永続化パスは、DBに保存されている文字列から一意に復元できること

---

# CarrierWaveの利用においてはパスの設計がとても大事

---

# じゃあcache_path/store_pathはどう決まる？

- 現場のコード

---

TODO: ナガノさんがポケカをしてる時の画像を引用する

---

# どういうことが起こる？

- モデルの状態によりキャッシュのパスが違う...

---

# case 1 (申請)

---

# case 2 (招待)

---

# じゃあどうすれば...

---

# ここからは仮説レベルとなります

---

# 元の設計思想...

- saveする前に一度キャッシュとして永続化する
  - そのキャッシュは、cache nameが分かれば復元できること
- saveしたら、キャッシュから永続化パスに移動する
  - その永続化パスは、DBに保存されている文字列から一意に復元できること

---

# それに合わせればいいじゃない

- キャッシュが作られた段階で `cache_name -> cache_path` が一意に決まるようにすればいい
- 永続化パスも `DBの情報 -> store_path` が一意に決まるようにすればいい

---

# キャッシュの場合

- RedisにMappingを保持するしかないかな...
  - セッションだけ有効なので、DBじゃなくていいのでは
- キャッシュが作成されたタイミングでMappingを保持
- retrieveの最初のタイミングでMappingを参照してパスを復元
  - これでいけん？

---

# 永続化パスの場合

- カラムを新しく追加するしかないよな...
  - 利用箇所たくさんあるけど...
  - なのでまあUploaderごとにスコープ切ってやってこうなって
- カラムにフルパス（相当）を保持させる
  - 保持してなかったら一から計算すればOK

---

# 今日言ってない話

- versions 問題
- なんか画像が勝手に回転するやつ

---

# 将来のプラン(案)

- CarrierWaveにアップしたら別のストレージにもdouble writeする
- どこかで参照をスイッチする
- なんかこういう感じで囲ったら新しくなって欲しいけど、APIは未定

```ruby
ImageMigrationKun.use_new_storage do
  user.avatar = params[:file]
  user.save!
end
```

---

TODO: 坂の画像

---

# まとめ

- レガシーマイグレーションとディープダイブは楽しいですね