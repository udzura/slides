fn main() {
    let buf = String::from("Hello, RubyKaigi!");

    drop(buf); // 明示的に解放

    println!("{}", buf); // コンパイルエラー！
}
