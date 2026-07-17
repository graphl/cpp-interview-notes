# C++ 面试题：实现 strcpy

## 1. 考点

`strcpy` 用来把源字符串拷贝到目标缓冲区，直到遇到 `'\0'` 为止。

面试主要考：

1. 指针判空
2. 返回目标地址
3. 是否拷贝字符串结束符 `'\0'`
4. 目标空间是否足够
5. 源和目标内存重叠问题

---

## 2. 基本实现

```cpp
#include <cassert>

char* my_strcpy(char* dest, const char* src) {
    assert(dest != nullptr && src != nullptr);

    char* ret = dest;

    while ((*dest++ = *src++) != '\0') {
    }

    return ret;
}
```

---

