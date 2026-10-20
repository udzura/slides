#include <setjmp.h>

#ifndef PROBE
#define PROBE probe
#endif

static jmp_buf env;

__attribute__((noinline)) static void jump(void) {
  longjmp(env, 42);
}

int PROBE(void) {
  switch (setjmp(env)) {
    case 0: jump(); return -1;
    case 42: return 42;
    default: return -1;
  }
}

#ifndef LIBRARY_ONLY
int main(void) {
  return PROBE() == 42 ? 0 : 1;
}
#endif
