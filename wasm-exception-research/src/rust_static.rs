#[link(name = "sjlj-standard", kind = "static")]
unsafe extern "C" {
    fn probe() -> i32;
}

#[unsafe(no_mangle)]
pub extern "C" fn rust_c_probe() -> i32 {
    // The C longjmp stays inside probe; the Rust panic is caught separately.
    let c_result = unsafe { probe() };
    let panic_result = std::panic::catch_unwind(|| panic!("intentional panic"));
    if c_result == 42 && panic_result.is_err() {
        42
    } else {
        -1
    }
}
