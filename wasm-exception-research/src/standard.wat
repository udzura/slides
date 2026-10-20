(module
  (tag $error (param i32))
  (func (export "answer") (result i32)
    block $caught (result i32)
      try_table (catch $error $caught)
        i32.const 42
        throw $error
      end
      unreachable
    end))
