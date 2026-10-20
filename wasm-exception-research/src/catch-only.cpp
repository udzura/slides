extern void may_throw();

int catch_only() {
  try {
    may_throw();
    return 0;
  } catch (...) {
    return 42;
  }
}
