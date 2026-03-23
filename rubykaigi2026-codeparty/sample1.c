#include <stdio.h>
#include <stdlib.h>

int *create_value()
{
    int x = 42;
    return &x; // ローカル変数のアドレスを返している！
}

int main()
{
    int *p = create_value();
    // pはすでに無効なメモリを指している（dangling pointer）
    printf("%d\n", *p); // 未定義動作！
    return 0;
}
