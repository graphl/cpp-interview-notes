# C++ 如何调用C 里面的库？

### 基本方法

假设有一个 C 头文件 **c_lib.h** 和对应的实现 **c_lib.c**：

```
// c_lib.h
#ifndef C_LIB_H
#define C_LIB_H

void c_function(int x);

#endif
// c_lib.c
#include <stdio.h>
#include "c_lib.h"

void c_function(int x) {
    printf("C function called with %d\n", x);
}
```

在 C++ 中使用时，头文件需要用 `extern "C"` 包起来：

```
// main.cpp
#include <iostream>

extern "C" {
#include "c_lib.h"
}

int main() {
    c_function(42);
    return 0;
}
```

编译：

```
gcc -c c_lib.c -o c_lib.o
g++ main.cpp c_lib.o -o main
```

###  

### C++ 调用 C 库函数的注意点

- **头文件要 `extern "C"` 包裹**，否则可能会链接错误。

- **编译方式**：C 源文件用 `gcc`（或 `g++ -x c`），C++ 源文件用 `g++`。

- **库链接**：如果是 `.a` 或 `.so`，直接用 `-l` 连接即可，比如：

  ```
  g++ main.cpp -L. -lc_lib -o main
  ```

- **数据结构兼容性**：C 里的 `struct`、`typedef` 可以直接在 C++ 用，但注意 C++ 里不能随便用 C 的关键字作为成员名。