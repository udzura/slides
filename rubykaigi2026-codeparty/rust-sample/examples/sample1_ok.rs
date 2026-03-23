fn create_value() -> i32 {
    let x = 42;
    x // 値を返す（ムーブ）
}

fn main() {
    let v = create_value();
    println!("{}", v); // 42 — 安全！
}
