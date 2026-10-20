unsafe extern "C" {
    fn probe() -> i32;
}
fn main() {
    // The C longjmp is caught inside probe, so it never crosses a Rust frame.
    assert_eq!(unsafe { probe() }, 42);
    let result = std::panic::catch_unwind(|| panic!("intentional panic"));
    assert!(result.is_err());
    println!("C longjmp=42; Rust panic caught");
}
