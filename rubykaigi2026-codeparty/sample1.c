#include <stdio.h>
#include <stdlib.h>

struct Data
{
    int value;
};

struct Data *create_value()
{
    struct Data x = {42};
    return &x; // ローカル変数のアドレスを返している！
}

int main()
{
    struct Data *p = create_value();
    // pはすでに無効なメモリを指している（dangling pointer）
    printf("%d\n", p->value); // 未定義動作！
    return 0;
}
