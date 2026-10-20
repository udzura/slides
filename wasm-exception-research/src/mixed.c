int legacy_probe(void);
int standard_probe(void);
int main(void) {
  return legacy_probe() == 42 && standard_probe() == 42 ? 0 : 1;
}
