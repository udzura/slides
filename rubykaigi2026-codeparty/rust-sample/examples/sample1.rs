fn main() {
    let p: &i32 = create_value();
    //     ^^^^
    // pはmain()のスコープが終わるまで有効な参照を期待している
    // → ライフタイム 'a はmain()のスコープと同じ長さが必要

    println!("{}", p); // ← ここでまだ使いたい！
}

fn create_value<'a>() -> &'a i32 {
    let x = 42;
    // xはここで破棄される... 'a（= main()のスコープ）より短い！
    &x // コンパイルエラー
}
