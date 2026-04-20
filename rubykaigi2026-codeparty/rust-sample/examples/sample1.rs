struct Data {
    value: i32,
}

fn main() {
    let p: &Data = create_value();
    //     ^^^^
    // pはmain()のスコープが終わるまで有効な参照を期待している
    // → ライフタイム 'a はmain()のスコープと同じ長さが必要

    println!("{}", p.value); // ← ここでまだ使いたい！
}

fn create_value<'a>() -> &'a Data {
    let x = Data { value: 42 };
    &x // コンパイルエラー
}
