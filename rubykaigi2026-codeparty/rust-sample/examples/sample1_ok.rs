struct Data {
    value: i32,
}

fn create_value() -> Data {
    let x = Data { value: 42 };
    x // 値を返す（ムーブ）
}

fn main() {
    let v = create_value();
    println!("{}", v.value); // 42 — 安全！
}
