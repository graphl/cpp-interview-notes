# C++ 面试题：实现 memcpy

## 1. 考点

`memcpy` 按字节拷贝一段内存。

面试主要考：

1. `void*` 指针转换
2. 按字节复制
3. 返回目标地址
4. `memcpy` 和 `memmove` 的区别
5. 内存重叠问题

---

## 2. 基本实现

```cpp
#include <cassert>
#include <cstddef>

void* my_memcpy(void* dest, const void* src, size_t n) {
    assert(dest != nullptr && src != nullptr);

    unsigned char* d = static_cast<unsigned char*>(dest);
    const unsigned char* s = static_cast<const unsigned char*>(src);

    void* ret = dest;

    while (n--) {
        *d++ = *s++;
    }

    return ret;
}
```

---

## 3. 为什么用 `unsigned char*`？

因为 C/C++ 中字节级内存访问通常使用 `char*`、`unsigned char*` 或 `std::byte*`。

`void*` 不能直接解引用，也不能直接做指针递增。

---

## 4. 内存重叠问题

```cpp
char s[] = "abcdef";
my_memcpy(s + 2, s, 4);  // 重叠，结果不可靠
```

`memcpy` 不处理重叠。

如果源区域和目标区域可能重叠，应该使用 `memmove`。

---

## 5. 面试回答

`memcpy` 是按字节复制内存，参数是 `void*`，实现时需要转成 `unsigned char*` 来逐字节操作。它返回目标地址。需要特别说明的是，`memcpy` 不保证处理内存重叠，重叠场景应该使用 `memmove`。
