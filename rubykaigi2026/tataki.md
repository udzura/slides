----
marp: true
theme: rubykaigi2026
paginate: true
backgroundImage: url(./bg-2026.002.png)
title: "Uzumibi: Reinventing mruby for the Edges"
description: "On RubyKaigi 2026 Hakodate / Uzumibi: Reinventing mruby for the Edges"
# header: "Uzumibi: Reinventing mruby for the Edges"
image: https://udzura.jp/slides/2026/rubykaigi/ogp.png
size: 16:9
----

# Uzumibi: Reinventing mruby for the Edges

- SmartHRのプロダクトエンジニア、近藤です。SmartHRは日本最大の人事SaaSを提供するスタートアップです。RubyKaigi 2026のプラチナスポンサーでもあります。
- 日本のほぼ反対のサイド、九州、福岡から来ました。

# 函館へようこそ！

- 初めて北海道、函館に来ました。
- このような素晴らしい街で公演ができて嬉しいです。

----

# 函館は歴史が深い街です。

----

# 五稜郭の戦い

- 日本史上での最後の内戦「五稜郭の戦い」が行われた土地でもあります。
- 五稜郭公園は美しい公園ですが、平和について思いを馳せたいですね。

----

# また、文学的でもあります

----

# 石川啄木

- 日本を代表する明治時代の歌人の一人石川啄木は一時期函館に住みました。
- 彼は全国を転々としましたが、最も愛した街は函館だったそうです。
- 函館には彼の墓地まであります。

----

- 少し脇道に逸れて、彼の短歌を一つ引用します。函館の大森浜をモチーフとした説があります。

----

> 「東海の小島の磯の白砂に　われ泣きぬれて　蟹とたわむる」

----

- 二つの点で私はこの歌に共感します。

----

- 一つは、この歌は創作での苦しみを描いたものだという点にです。
- 私自身が若い頃、自分の思った通りのプログラムを作れず、苦しんだことを思い浮かべます。

----

- もう一つは、私が今、まさに泣きながら蟹と戯れているところだからです。
- 今日紹介するプロダクトはRustで書かれていますからね。

----

# 自己紹介

- 近藤宇智朗
- 日本の反対側、九州、福岡から来ました。
- SmartHRという、日本最大の人事労務プラットフォームを運営するスタートアップで働いています。本日のゴールドスポンサーでもあります。

----

# 本日のテーマ

- Uzumibiについて

----

# Uzumibiとは？

- Rubyでエッジとサーバレスのプラットフォーム上のアプリケーションを開発するためのフレームワーク

----

# 特徴

- ジェネレータにより複数のプラットフォームに対応
- Sinatra風の覚えやすいDSL
- (Cloudflareなら) Durable Object, Queue, Accessなど連携機能もサポート
- 軽量

----

# Get started

- まずは動かしてみましょう
  - ！！実際はその場でデプロイします

```
$ cargo install uzumibi-cli@0.7.0
$ uzumibi new -t cloudflare --features enable-external myapp
```

- Rustのcargoでインストールできます
- Cloudflare Workers向けのテンプレートを指定してプロジェクトを作成できます

----

- このようなコードが生成されます

```
TBA
```

----

- app.rb がデフォルトで生成されます。
- Rubyistならこのコードをなんとなく読めると思います。
- 少し変更して、KVSにアクセスするようにします。

----

- デプロイをしてみましょう。
- 容量をご覧ください。圧縮前1.5MBのコード、圧縮後には500KB程度になります。
- この容量は、Cloudflare Workersの無料プランの範囲に余裕で収まります。

----

- 実際にアクセスしてみると、Rubyのコード動作していることがわかります。
- KVSもちゃんと動いていますね。

----

- この通り、Uzumibiにより、Rubyで快適にエッジのアプリケーション開発ができることを示しました。
- 今回はCloudflare Workersを例にしましたが、サーバレス環境であるCloud Runに関しても同様に動かすことができます。

----

- そして実は、このUzumibiは、mruby/edgeというmrubyランタイムベースにしています。
- Uzumibiの威力を理解するために、mruby/edgeの近年の大進歩について話していこうと思います。

----

# mruby/edgeとは何か？

- mruby/edgeは私が2024年から開発している、自作のmrubyランタイムです。
- 予告の通り、全てRustで書かれています。
- WebAssemblyにコンパイルされることを前提に設計されています。
- ポータブルなWebAssemblyを作れるので、エッジでの使用が可能です。また、生成されるアーティファクトの小ささから、サーバレス環境での使用にも向いているはずです。

----

# CRuby.wasm

- 圧縮後500KBという非常に小さなアーティファクトは、ruby.wasmでは実現が困難なものかと思います。
  - 例えば、CRuby.wasmは、圧縮前で約20MB、単純にgzip圧縮したらXX MBとなりました。
- ところで、mrubyには、元々の思想として「必要ないコードをランタイムに含まない」というものがあります。
- 「エッジ等で必要な機能だけを選択してビルドする」という選択肢を取るため、mrubyをベースにするアイデアを思いつきました。

<!-- TODO: 最新の容量を調べる -->

----

# 現状のmruby/picorubyの

- ところが、Matz official mrubyはその内部実装でsetjmp/longjmpを使用しています。これが問題を難しくしています。
- 実はWasmのコア命令にはgotoに類する命令が存在しません。したがってsetjmp/longjmpを使用しているコードをWasmにコンパイルする場合、外部ツールを用いたハックを行うか、提案中のGAでない例外命令に変換することになります。
- 例えば、Emscriptenはsetjmp/longjmpを使用しているコードをコンパイルする際、setjmp/longjmpの呼び出しを検出して、独自のランタイム関数を呼び出すようにコードを書き換え、動作させています。
- picorubyでもwasmを生成できますが、現状では同じく
  - コンパイラでsetjump/longjmpを使用しているのを確認しています。

----

# 真にポータブルなWasmを求めて

- Emscriptenに依存すると、wasmにはEmscriptenのランタイムが含まれることになります。生成されるアーティファクトをコントロールしづらいです。
- また、Emscriptenが勝手にいくつかの関数をimport/exportしてしまいます。

----

- このような背景から、既存のRubyあるいはmrubyの実装に単純には乗っかれないなと思いました。
- よって、Rustによる再実装という選択肢を取りました。
- Rustには他にもいくつかのメリットがありました。
  - 高度な型システムを持っていることによる生産性、安全性
  - WebAssemblyをはじめとした強力な周辺のエコシステム
- もちろん、「一度はVMを自分で実装してみたい」という個人的な動機もありました。

----

# mruby/edge の振り返り

----

# 2024年

- ここまで話したようなモチベーションで開発した結果、RubyKaigiで発表した
- しかしPoCという他ない完成度だった...。

----

# 2025年

- 2025年冒頭に再会〜2月
  - 今の方針では行き詰まるので、 mruby/c の実装などを深く読み込み、参考にしてVMを再作成した

----

- まず命令のカバレッジをあげるぞ！って思って以下のPDCAを回した
  - この命令出るかな？というRubyのサンプルコードを探す
  - 最小の例を作る
  - mrubyで動くのを確認
  - バイトコードを作ってmruby/edgeで動かす
  - 動くようになるまでやる
  - 元の例をe2eテストにする

----

# 実装の苦労話

----

# 実装の前提知識

- mrubyの命令はこういう感じ
- レジスタマシン

----

# レジスタマシンに必要なデータ構造

<!-- https://scrapbox.io/udzura-lofi-memo/mruby%2Fc_1.x%E7%B3%BB%E3%81%AE%E3%82%B3%E3%83%BC%E3%83%89%E3%81%A7%E5%AD%A6%E3%81%B6mruby_VM -->

- レジスタを保持するコンテナ
- IREPへの参照
- program counter
- callinfo のスタック（呼び出した関数のコンテクスト情報など）
- (mrubyはデータのためのスタックを持っていないので不要)

----

```rust
pub struct VM {
    pub id: usize,
    pub irep: Rc<IREP>,
    pub pc: Cell<usize>,
    pub regs: [Option<Rc<RObject>>; MAX_REGS_SIZE],
    pub current_regs_offset: usize,
    pub current_callinfo: Option<Rc<CALLINFO>>,
    pub globals: RHashMap<String, Rc<RObject>>,
    pub consts: RHashMap<String, Rc<RObject>>,
    //...
}
```

----

- IREPの構造
- CALLINFOの構造

----

```rust
pub struct IREP {
    pub nlocals: usize,
    pub nregs: usize,
    pub rlen: usize,
    pub code: Vec<Op>,
    pub syms: Vec<RSym>,
    pub pool: Vec<RPool>,
    pub catch_target_pos: Vec<usize>,
    // ...
}

#[derive(Debug, Clone)]
pub struct CALLINFO {
    pub prev: Option<Rc<CALLINFO>>,
    pub method_id: RSym,
    pub pc_irep: Rc<IREP>,
    pub current_regs_offset: usize,
    pub target_class: TargetContext,
    pub n_args: usize,
    // ...
}
```

----

# regs がHashMapではなく配列である理由

- レジスタを保持するコンテナはMapでは持たないようにした
- 内部的にはスライス
- スタックが積まれるごとに、スライスの開始を移動する
  - 副産物
  - スタックオーバーフローも勝手に検出するようになる

----

```rust
regs: [Option<Rc<RObject>>; 256]   // VM構造体に1本だけある
current_regs_offset: usize         // 「今のフレームの先頭」を指す

// Rustメソッド呼び出し = オフセットをずらす
// イメージ
vm.current_regs_offset += a as usize;  // 呼び出し → 前にずらす
// ... メソッド実行 ...
vm.current_regs_offset -= a as usize;  // 復帰 → 元に戻す
```

----

```rust
// 呼び出しスタックの復元 = CALLINFO に offset を保存
// in op_send
let callinfo = CALLINFO {
     current_regs_offset: vm.current_regs_offset,  // 今のオフセットを退避
     pc: vm.pc.get(),
     pc_irep: vm.current_irep.clone(),
     // ...
};

// vm.current_regs_offset をスライドする処理...
// irepを付け替える処理、pcを変更する処理など

// in op_return
let ci = vm.current_callinfo.take().unwrap();
// 元のciに復帰する処理の後で
vm.current_regs_offset = ci.current_regs_offset;
```

----

# 実装上の工夫

----

# Rustのtraitを再利用

- `Hash`, `PartialEq` などはRustレベルで実装した
- そうすると内部でHashMapなどや比較の演算子などをそのまま使えるので...。

----

- 例えばHashの実際の構造体
  - >  Ruby の Hash を、Rust 標準の HashMap に直接マッピングしています。キー探索・挿入・削除すべて HashMap の実装にそのまま乗る設計です。Value 側が (key, value) のタプルなのは、元の Ruby キーオブジェクトも保持するためです。

```rust
pub type RHash = HashMap<ValueHasher, (Rc<RObject>, Rc<RObject>)>;
#[derive(Debug, Clone, PartialEq, Eq, Hash)]  // ← derive(Hash) がポイント
 pub enum ValueHasher {
     Bool(bool),
     Integer(i64),
     Float(Vec<u8>),   // f64 は Eq 不可なのでバイト列に変換
     Symbol(String),
     String(Vec<u8>),
     Class(String),
 }
// 各バリアントの中身が bool, i64, String, Vec<u8> などすべて Rust 標準で Hash + Eq を持つ型なので、derive(Hash) だけで自動導出
```

----

- hash_set等の実装が非常にシンプルになる

```rust
pub fn mrb_hash_set_index(
    this: Rc<RObject>,
    key: Rc<RObject>,
    value: Rc<RObject>,
) -> Result<Rc<RObject>, Error> {
    let hash: &RefCell<_> = match &this.value {
        RValue::Hash(a) => a,
        _ => {
            return Err(Error::RuntimeError(
                "Hash#[] must called on a hash".to_string(),
            ));
        }
    };
    let mut hash = hash.borrow_mut();
    let hashed: ValueHasher = key.as_hash_key()?;
    hash.insert(hashed, (key.clone(), value.clone()));
    Ok(value.clone())
}
```

----

# クロージャとUpvalueの実装

----

# ENV構造体

```rust
pub struct ENV {
     pub upper: Option<Rc<ENV>>,                          // 外側のENV（チェーン）
     pub current_regs_offset: usize,                      // 生成時のレジスタオフセット
     pub captured: RefCell<Option<Vec<Option<Rc<RObject>>>>>, // キャプチャ済みレジスタ
     pub is_expired: Cell<bool>,                          // 生成元フレームが終了したか
 }
```

----

# lambdaの生成時に:

```rust
let environ = ENV {
     upper: vm.upper.clone(),                    // 外側の環境をチェーン
     current_regs_offset: vm.current_regs_offset, // 今のオフセットを記録
     is_expired: Cell::new(false),               // まだ生きている
     captured: RefCell::new(None),               // まだキャプチャしない
 };
 // Proc に environ を持たせる
 RProc { environ: Some(environ), ... }
```

- 生成時点では captured は None。レジスタのコピーを **していない**

----

TODO

----

- フレームが終了する瞬間に、レジスタの内容を captured にコピーし、expired = true にする

```rust
// op_return 内
 let regs0_cloned = vm.current_regs()[0..nregs].to_vec();
 if let Some(environ) = vm.cur_env.get(&vm.current_irep.__id) {
     environ.capture_no_clone(regs0_cloned);  // レジスタをコピー保存
     environ.expire();                         // expired フラグを立てる
}
```

----

```rust
fn op_getupvar(vm, operand) {
     let (a, b, c) = operand.as_bbb()?;  // a=格納先, b=変数位置, c=何段上か
 
     // c 段上の ENV をたどる
     let mut environ = vm.upper;
     for _ in 0..c { environ = environ.upper; }
 
     if !environ.expired() {
         // 生成元がまだ実行中 → regs を直接参照
         let up_regs = &vm.regs[environ.current_regs_offset..];
         vm.current_regs()[a] = up_regs[b].clone();
     } else {
         // 生成元が return 済み → キャプチャ済みデータから読む
         let captured = environ.captured.borrow();
         vm.current_regs()[a] = captured[b].clone();
     }
 }
```

----

# 継承ツリーの再現

```rust
pub struct RClass {
     pub module: Rc<RModule>,                   // メソッドテーブル・定数を持つ
     pub super_class: Option<Rc<RClass>>,       // 親クラスへのリンク
     pub singleton_class_ref: RefCell<Option<Rc<RClass>>>,
     pub is_singleton: bool,
     pub extended_modules: RefCell<Vec<Rc<RModule>>>,
 }
```

----

- 特にClassインスタンスの特異メソッドは特殊

```ruby
# 普通のインスタンス
irb(main):002* class Foo
irb(main):003> end
=> nil
irb(main):004* class Bar < Foo
irb(main):005> end
=> nil
irb(main):006> Bar.new.class.ancestors
=> [Bar, Foo, Object, JSON::GeneratorMethods, PP::ObjectMixin, Ruby::Box::Loader, Kernel, BasicObject]
irb(main):007> Bar.new.singleton_class.ancestors
=> [#<Class:#<Bar:0x0000000128ecf7e0>>, Bar, Foo, Object, JSON::GeneratorMethods, PP::ObjectMixin, Ruby::Box::Loader, Kernel, BasicObject]

# Classのインスタンス
irb(main):008> Bar.singleton_class.ancestors
=> 
[#<Class:Bar>,
 #<Class:Foo>,
 #<Class:Object>,
 #<Class:BasicObject>,
 Class,
 Module,
 Object,
 JSON::GeneratorMethods,
 PP::ObjectMixin,
 Ruby::Box::Loader,
 Kernel,
 BasicObject]
```

----

- メソッド探索（value.rs:1041-1061）は単純な再帰

```rust
fn find_method(&self, name: &str) -> Option<RProc> {
     if let Some(p) = self.module.find_method(name) { return Some(p); }
     // singleton なら extended modules も探索
     match &self.super_class {
         Some(sc) => sc.find_method(name),   // 親クラスへ再帰
         None => None,
     }
 }
```

----

# obj の特異クラス  ──super──▶  obj のクラス(Foo)  ──super──▶  ... Object

```rust
fn initialize_or_get_singleton_class(self, vm) -> Rc<RClass> {
     let sclass = RClass::new_singleton(
         &class_name,
         Some(self.get_class(vm).clone()),  // super = 自分のクラス
         ...
     );
 }
```

----

# Classインスタンスの場合

```rust
fn initialize_or_get_singleton_class_for_class(self, vm) -> Rc<RClass> {
     let super_class = match &class.super_class {
         Some(parent) => {
             let parent_obj = RObject::class(parent.clone(), vm);
             parent_obj.initialize_or_get_singleton_class_for_class(vm)  // ← 再帰！
         }
         None => vm.get_class_by_name("Class"),
     };
     let sclass = RClass::new_singleton(&class_name, Some(super_class), ...);
 }
```

- Foo < Bar のとき、Foo の特異クラスの super は Bar の特異クラス
- 再帰的に親クラスの特異クラスを生成する

----

# 例外の実装

```ruby
begin
  raise RuntimeError, "foobar"
rescue ArgumentError => e
  p e
ensure
  p "done"
end
```

----

バイトコード

```
irep 0x101244900 nregs=8 nlocals=2 pools=2 syms=4 reps=0 ilen=57
local variable names:
  R1:e
catch type: ensure   begin: 0000 end: 0043 target: 0043
catch type: rescue   begin: 0000 end: 0010 target: 0013
file: /tmp/exc.rb
    2 000 GETCONST	R3	RuntimeError	
    2 003 STRING	R4	L[0]	; foobar
    2 006 SSEND		R2	:raise	n=2
    2 010 JMP		043
    2 013 EXCEPT	R2		
    3 015 GETCONST	R3	ArgumentError	
    3 018 RESCUE	R2	R3
    3 021 JMPIF		R3	028	
    3 025 JMP		041
    3 028 MOVE		R1	R2		; R1:e
    4 031 MOVE		R3	R1		; R1:e
    4 034 SSEND		R2	:p	n=1
    4 038 JMP		043
    4 041 RAISEIF	R2		
    4 043 EXCEPT	R4		
    6 045 STRING	R6	L[1]	; done
    6 048 SSEND		R5	:p	n=1
    6 052 RAISEIF	R4		
    6 054 RETURN	R2		
    6 056 STOP
```

----

# バイトコードを追う

```
     2 006 SSEND    R2  :raise  n=2     ← 例外発生！ → catch target 013 へジャンプ
     2 013 EXCEPT   R2                  ← (a) 例外オブジェクトを R2 に取り出す
     3 018 RESCUE   R2  R3              ← (b) R2 が R3(ArgumentError) の is_a? を判定
     3 021 JMPIF    R3  028             ←     マッチしたら 028 へ
     3 025 JMP      041                 ←     マッチしなければ 041 へ
     3 028 MOVE     R1  R2              ←     e = 例外オブジェクト
     4 034 SSEND    R2  :p  n=1         ←     p(e) 実行
     4 038 JMP      043                 ←     ensure ブロックへ
     4 041 RAISEIF  R2                  ← (c) 未処理なら再 raise
     4 043 EXCEPT   R4                  ←     ensure 開始: 残存例外を取り出す
     6 052 RAISEIF  R4                  ←     ensure 終了後、例外があれば再 raise
```

----

# 例外が起こると

```rust
// vm.rs
match consume_expr(self, op.code, ...) {
     Err(e) => {
         // self == VM構造体の例外フィールドに、例外オブジェクトを格納する
         self.exception = Some(Rc::new(RException::from_error(self, &e)));
         continue;  // ループ先頭へ
     }
}
```

- ループ先頭で、例外があれば 現在の PC より後ろにある最も近い catch target にジャンプする処理が入っている。

----

# 各命令の詳細

```
 EXCEPT R[a]
    vm.exception.take() → R[a] に格納	例外を VM から取り出してレジスタに移す
 RESCUE R[a] R[b]
    R[a].is_a?(R[b]) → 結果を R[b] に	型マッチ判定（rescue ArgumentError の部分）
 RAISEIF R[a]	R[a]
    が例外なら Err() を返す	未処理例外の再送出
```

----

# cf. break の実装

- gotoがないので！
- 一旦例外の一種として実装した

----

```rust
pub enum Error {
    General,
    Internal(String),
    InvalidOpCode,
    RuntimeError(String),
    ArgumentError(String),
    RangeError(String),
    TypeMismatch,
    NoMethodError(String),
    NameError(String),
    ZeroDivisionError,

    TaggedError(&'static str, String),

    Break(Rc<RObject>),
    BlockReturn(usize, Rc<RObject>),
}
```

----

# breakの仮実装

- 上に遡る＋「そのブロックを呼び出した場所」を見つけたら止まる 方針
- TODO: ensureの確認が雰囲気

----

# ここまでのまとめ

- mruby/edgeを「Rubyらしく」動かすためにさまざまな再実装を頑張った
- 2025年11月なかばあたりには
- 基本的な命令はサポートできた

----

- サポート状況のテーブル

<!-- 今度作ります -->

----

# 標準ライブラリが欲しい

- 「あとはやるだけ」
- とはいえ貢献者も期待できない

----

# AIというコントリビュータを見つけた

- 基盤は整ったので、AIに書かせた！
- そうしたら割と素早くできた...
- mruby/c のヘッダを見ながら同じ程度のメソッドを実装させた
- テストの書き方も整えていたおかげで、QAもまあやりやすかった

----

# かなりRubyらしいコードが書けるようになった

- これが2月頭のこと

----

# じゃあ、本格的なアプリケーションを作りたい

----

# Uzumibiの開発

- 時期は少し前後する。
- edgeを名乗りつつエッジで動かすのを試していなかった
- （動く日が来るとは思っていなかったんで...）

----

# 試みにCloudflare Workersで動かすコードを書いた

- Cloudflare Workersでは、素直にWasmを使える
- 必要な関数を実装してデータをやり取りし、最終的にCloudflare Workersのインタフェースと合わせる

----

# いや普通に動くじゃ〜ん

- 12月末の段階で、Cloudflare Workers上で動くコードができてしまった。
- https://github.com/mrubyedge/uzumibi/pull/1

----

# しかも...!?

- バイナリちっさい！
- しかも、Cloudflare Workersの無料プランの範囲で余裕で収まる
  - この時点で、標準ライブラリをある程度整えてもまだ容量的に余裕だろうと見積もれた

----

# ということで

- 他のプラットフォームも調べて、同じようにspikeコードを書いた
- 真面目に対応した。

----

# 各プラットフォームのサポート状況

- Beggining Uzumibiのあの表

----

# 連携サービスの利用もOK

- Cloudflare Workers
- Durable ObjectベースのKVSとQueueが使える（もちろんただのFetchも可能）
- また、JWTトークンを検証し、Accessと連携してユーザ情報も取得可能

----

# 外部サービスの抽象化レイヤを入れたい

- 現状、Cloudflare WorkersとCloud Runまでは対応
- Google Cloudの以下サービスが使える状態で、Cloudflare Workers向けとほぼ同じコードが動く
  - Firestore for KV
  - Cloud Pub/Sub for Queue
  - Identity Aware Proxy for Access
    - JWTの検証もできる
- それ以降は様子を見ながら対応します...コントリビューションを歓迎します

----

# Uzumibiのふりかえり

- 基盤ができた以上、「普通に動いてしまっている」
- なのでUzumibiをタイトルにしているが、RubyKaigiらしいHackは、あまりいうことがない...。
- 設計思想が完全に刺さったため。本当に素直に作りたいものを作れた。
  - ポータブルで、import/exportする関数も完全にコントロールできるWasmを生成すること
  - アーティファクトをなるべく小さくすること
- 大事なのは正しい道具を作ることだと実感した。

----

# ぜひ試してみてください。

----

# 今後の課題

----

# 非同期プログラミングとの向き合い

----

# Wasmと非同期プログラミング

- Wasmは第一の要求としてJavaScriptと連携して動くことが求められる
- JavaScriptではIOに関する関数は基本的に非同期（ブラウザ/サーバサイドどちらも）

----

# Cloudflare Workersの非同期API

- Durable ObjectやQueueなどの連携機能も非同期APIで提供されている
- もちろん、 `fetch()` のような基本的な関数もそう
- ここで困ったこと
    - Wasmにimport関数として渡して、Wasmの中から連携機能を呼び出すしかないのだが、
    - 普通Wasmはimport関数として非同期関数を渡せない

----

# 現状どうしているか？

- asyncify というツール/ライブラリを使って、擬似的にWasmインスタンスに非同期関数を渡す方法をとっている
- 大きなデメリットとしてバイナリサイズの肥大化がある
  - 非同期化のためにラッパーのような実装を生成するため。大体1.5倍になるとされている
  - 元々、バイナリサイズの問題を重要視して開発したのに、ここで肥大化するのはいただけない。

----

# 他のプラットフォームでも重要

- Cloud Run実装では汎用的なサーバライブラリ（hyper, tokio）を用いている。
- 本当は非同期を完全にサポートした方が最善のパフォーマンスになる。
- 現状は一部妥協しているとこもある。

----

# 例えば

- IOが必要な操作を単一のスレッドで実行するようになっている。
- tokioの仕様上こうするか、channelを使ってIOを担当するスレッドと通信するかのどちらかになる。

----

# 非同期のサポートは今後の課題

- Cloud Runで使う前提なので、単一プロセスでマルチコアを使う方針ではなく、小さなコンテナを数多く起動する方針をとれば運用できると踏んでこうした
- サーバレスに割り切ったとも言えるが、汎用的な状態ではない

----

# 現状のVMの実装

- 非常に単純な命令ループを、動機的に回すようになっている。
- ここで、VMは単なるステートマシンなので、
  - なんとなく非同期との相性は悪くないように思えるのだが...。

----

# mruby/edgeの非同期VM？

- どこかのタイミングで、非同期プログラミングに特化したVMを作るかもしれない
- VM自体が、任意のタイミングで停止し、再開できるようにできていればいいと思うが...。
- 実装方法の検討から

----

# もし、動くものがあればここでデモできる。あと1週間やで!!!

- 大丈夫です。木曜日の午前に完成したってデモはできる。

----

# まとめ

- mruby/edge を進化させた結果、エッジで本当に使えるようになったと思います
- エッジの可能性に触れたことがない方も多いと思います。
- 今後も開発と情報発信をしていきます。試してみてください！