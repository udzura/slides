(module
  ;; add関数: 2つのi32整数を受け取り、その合計を返す
  (func $add (export "add") (param $a i32) (param $b i32) (result i32)
    local.get $a
    local.get $b
    i32.add
  )
)