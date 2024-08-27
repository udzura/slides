#include <emscripten.h>

void log_value(int size);

int EMSCRIPTEN_KEEPALIVE calc_plus(int n, int m) {
  log_value(n + m);
  return 0;
}
