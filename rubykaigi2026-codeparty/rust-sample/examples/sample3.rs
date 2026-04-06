fn main() {
    let mut numbers = vec![1, 2, 3, 4, 5];

    // ① ここで numbers の「不変の借用（読み取り専用のアクセス権）」がループ全体に渡って開始される
    for n in &numbers {
        println!("processing: {}", n);
        
        if *n == 2 {
            // ② ループの途中で要素を削除しようとする
            // remove() は numbers 全体を変更するため、「可変の借用（排他アクセス権）」を要求する
            numbers.remove(2); 
        }

        // c.f. 参照のみの借用は問題ない
        println!("readonly: len = {}", numbers.len());
    } // ③ 不変の借用はループが終わるここまで続く
}