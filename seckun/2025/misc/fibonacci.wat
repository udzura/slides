(module
  (func $fibonacci (export "fibonacci") (param $n i32) (result i32)
    local.get $n
    i32.const 2
    i32.lt_s
    if
      i32.const 1
      return
    end
    local.get $n
    i32.const 1
    i32.sub
    call $fibonacci
    local.get $n
    i32.const 2
    i32.sub
    call $fibonacci
    i32.add
  )
)
