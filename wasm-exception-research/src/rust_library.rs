#[unsafe(no_mangle)]
pub extern "C" fn rust_library_probe() -> i32 {
    // Catch the panic within Rust; no unwind crosses the C ABI boundary.
    let result = std::panic::catch_unwind(|| panic!("intentional library panic"));
    i32::from(result.is_err())
}
