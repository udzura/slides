----
marp: true
title: 超入門 よかBPF for PHPer（とApacher）
description: 於 【非公式】PHPカンファレンス福岡2024・前日Meetup (2024/6/20)
header: "超入門 よかBPF for PHPer"
footer: "presentation by Uchio Kondo"
image: https://udzura.jp/slides/2024/mf-fukuoka-tech-lt/indexv2.png#fixme
theme: fukuokarb
paginate: true
----

<!--
_class: hero
-->

# 超入門 よかBPF

## for PHPer （とApacher）

----
<!--
class: profile
style: section.profile ul { width: 110% }
-->

# 近藤うちお

- 所属: 株式会社ミラティブ
- 福岡市エンジニアカフェ
ハッカーサポーター
- フィヨルドブートキャンプ
アドバイザー
- 普段はGoでミドルウェア開発
- 『入門 eBPF』（オライリージャパン）翻訳しました何卒

![bg right w:82%](./profile2.png)

---
<!--
_class: normal
-->

# 今日の内容

- PHPカンファレンス福岡CfPに出したプロポーザルの内容を大胆に抜粋
- 5分でよかBPF体験しましょう

---
<!--
_class: normal
-->

# 今日の結論ファースト

![bg h:400 right](book.png)

- よか本なので読んで
- ジュンク堂にも丸善にも<br>あるけね

----

<!--
_class: hero
-->

# よかBPFを完全理解する

----

<!--
_class: normal
-->

# eBPF とは？

* Linuxの最新技術: 特殊なバイトコードを動的ロードしてカーネルで動かせる
* 以下の目的で使える
  * ネットワークのフィルター（iptables等の代わり他）
  * Observability系ツール（なんでも観測）
  * セキュリティ系のツール
* BPFと呼んでもeBPFと呼んでもいい

## よかBPFとは？

* 良いBPFのこと

----

<!--
_class: hero
-->

# よかBPFとPHPerの関わり

## よかBPF、肌で感じましょう（demoを見るという意味）

----

<!--
_class: normal
-->

# 前提: 多くの言語やミドルウェアには<br>「eBPF用のフックポイント」がある

* USDT（User Statically Defined Tracepoint）という
  - RubyとかPythonとかmemcachedとかにはある
* 実は、もともとDTraceのためのトレース設定
  - そもそも正確にはeBPF専用でもないが、まあ...
* C言語的にはDTrace用のマクロ定義をそのままLinuxでも使うイメージ

----

<!--
_class: normal
-->

# もちろんPHPにもある

- phpinfo() で DTrace のとこがenabledならOK<br><br>
 ![w:120%](./enabled.png)

----

<!--
_class: normal
-->

# うちのはdisabledやが？

- 自前でビルドすればOK....
- ......

```
# e.g.
$ apt install めっちゃたくさんのパッケージ
$ PHP_BUILD_CONFIGURE_OPTS='--enable-dtrace --with-apxs2' \
    php-build 8.3.8 /opt/php
```

- また、 `/etc/apache2/envvars` に `export USE_ZEND_DTRACE=1` を追記
  - 参考: [eBPF+USDTでphpをトレースしてみる、php-fpmとmod-phpでもやる](https://dasalog.hatenablog.jp/entry/2020/12/27/191953)

----

<!--
_class: normal
-->

# 何が測れる？

- `bpftrace` っちコマンドでわかるっちゃね
- 詳細な内容は俺もわからん、雰囲気でやってく

```
$ sudo bpftrace -l 'usdt:/usr/lib/apache2/modules/libphp.so:*'
usdt:/usr/lib/apache2/modules/libphp.so:php:compile__file__entry
usdt:/usr/lib/apache2/modules/libphp.so:php:compile__file__return
usdt:/usr/lib/apache2/modules/libphp.so:php:error
usdt:/usr/lib/apache2/modules/libphp.so:php:exception__caught
usdt:/usr/lib/apache2/modules/libphp.so:php:exception__thrown
usdt:/usr/lib/apache2/modules/libphp.so:php:execute__entry
usdt:/usr/lib/apache2/modules/libphp.so:php:execute__return
usdt:/usr/lib/apache2/modules/libphp.so:php:function__entry
usdt:/usr/lib/apache2/modules/libphp.so:php:function__return
usdt:/usr/lib/apache2/modules/libphp.so:php:request__shutdown
usdt:/usr/lib/apache2/modules/libphp.so:php:request__startup
```

----

<!--
_class: normal
-->

# 計っちゃいますか

- bpftrace はこういうスクリプトを書くと、レイテンシを可視化できる
- 今回はcompile file？のレイテンシ測っちゃいますかね

```awk
usdt:/usr/lib/apache2/modules/libphp.so:php:compile__file__entry {
  @start[tid] = nsecs;
}
usdt:/usr/lib/apache2/modules/libphp.so:php:compile__file__return
  /@start[tid]/ {
  @ns[str(arg0)] = hist(nsecs - @start[tid]); delete(@start[tid]);
}
```

- ちなファイルごとにわかりますから

----

<!--
_class: normal
-->

# ベンチケース

- ケース: WordPressを初回ロードした時の "compile file" の計測
- abだとしんどそうなのでブラウザで何回か叩く

```
$ sudo bpftrace compile.bt
Attaching 2 probes...
^C
```

----

<!--
_class: normal
-->

# 結果

```
@ns[/var/www/html/wordpress/wp-includes/class-wp-recovery-mode-cook]:
[64K, 128K)            2 |@@@@@@@@@@@@@@@@@@@@@@@@@@                          |
[128K, 256K)           4 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[256K, 512K)           3 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@             |
[512K, 1M)             1 |@@@@@@@@@@@@@                                       |

@ns[/var/www/html/wordpress/wp-includes/class-wp-query.php]:
[1M, 2M)               3 |@@@@@@@@@@@@@@@@@@@@@@                              |
[2M, 4M)               7 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|

@ns[/var/www/html/wordpress/wp-includes/class-wp-post.php]:
[64K, 128K)            9 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[128K, 256K)           1 |@@@@@                                               |

@ns[/var/www/html/wordpress/wp-includes/class-wp-post-type.php]:
[128K, 256K)           1 |@@@@@                                               |
[256K, 512K)           9 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
...
```

----

<!--
_class: normal
-->

# ところで、BPFでやるメリットは？

* 他の計測コマンド（特にstrace）と比べて
  - strace等は仕組み上一瞬プログラムを止めるので遅くなる
  - eBPFはカーネルで非同期にイベントを受け取るので高速
* 言語ごとのプロファイラと比べて
  - 言語より下のOSと横断で計測できる
  - 言語機能の基盤の部分（リクエストとかコンパイルとか）
  のメトリックがある
  - プロファイルのための特別の仕組みが(USDT以外...)不要
    - ライブ環境で動くコードにいきなり使える

----

<!--
_class: hero
-->

# まとめ

---
<!--
_class: normal
-->

# 今日の結論

![bg h:400 right](book.png)

- よか本なので読んで
- ジュンク堂にも丸善にも<br>あるけね
