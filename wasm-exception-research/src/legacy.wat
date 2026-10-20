(module
  (tag $error (param i32))
  (func (export "answer") (result i32)
    try (result i32)
      i32.const 42
      throw $error
    catch $error
      ;; Payload (42) is now on the operand stack.
    end))
