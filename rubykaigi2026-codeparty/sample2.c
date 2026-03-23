#include <stdio.h>
#include <stdlib.h>

int main()
{
    char *buf = (char *)malloc(64);
    snprintf(buf, 64, "Hello, RubyKaigi!");

    free(buf);

    // 解放済みメモリへアクセス（use-after-free）
    printf("%s\n", buf); // 未定義動作！
    return 0;
}
