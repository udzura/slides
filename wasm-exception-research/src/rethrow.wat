(module
  (tag $error (param i32))
  (func (export "answer") (result i32)
    block $outer (result i32)
      try_table (catch $error $outer)
        block $saved (result exnref)
          try_table (catch_all_ref $saved)
            i32.const 42
            throw $error
          end
          unreachable
        end
        ;; Outside the inner try_table: rethrow the saved exception reference.
        throw_ref
      end
      unreachable
    end))
