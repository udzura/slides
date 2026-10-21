#include <stdio.h>

int probe(void);
int rust_library_probe(void);

int main(void) {
  int c_result = probe();
  int rust_result = rust_library_probe();
  if (c_result != 42 || rust_result != 1) return 1;
  puts("C main: longjmp=42; Rust library: panic caught");
  return 0;
}
