# C++ 面试题：实现 memmove

## 1. 考点

`memmove` 和 `memcpy` 都是按字节拷贝内存。
区别在于：`memmove` 必须正确处理源内存和目标内存重叠的情况。

面试主要考：

1. `void*` 指针转换
2. 按字节拷贝
3. 内存重叠判断
4. 正向拷贝和反向拷贝
5. `memcpy` 和 `memmove` 的区别

---

## 2. 实现

```cpp
#include <cassert>
#include <cstddef>

void* my_memmove(void* dest, const void* src, size_t n) {
    // 调试阶段检查空指针；标准库函数对非法指针通常不保证行为。
    assert(dest != nullptr && src != nullptr);

    // void* 不能直接解引用，也不能做指针运算。
    // 转成 unsigned char* 后，可以按字节拷贝原始内存。
    unsigned char* d = static_cast<unsigned char*>(dest);
    const unsigned char* s = static_cast<const unsigned char*>(src);

    // 源地址和目标地址相同，或者拷贝长度为 0，直接返回原始目标地址。
    if (d == s || n == 0) {
        return dest;
    }

    // 情况 1：目标区间在源区间前面，或者两个区间完全不重叠。
    // 这时从前往后拷贝不会覆盖还没读取的源数据。
    if (d < s || d >= s + n) {
        while (n--) {
            *d++ = *s++;
        }
    } else {
        // 情况 2：目标地址落在源区间内部，例如 my_memmove(s + 2, s, 4)。
        // 如果从前往后拷贝，会先覆盖后面还没读取的源数据。
        // 所以先移动到末尾，再从后往前拷贝。
        d += n;
        s += n;
        while (n--) {
            *--d = *--s;
        }
    }

    // memmove 和 memcpy 一样，返回原始目标地址，方便链式使用。
    return dest;
}
```

---

