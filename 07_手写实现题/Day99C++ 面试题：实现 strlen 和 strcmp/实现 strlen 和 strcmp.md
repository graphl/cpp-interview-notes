# C++ 面试题：实现 strlen 和 strcmp

## 1. 实现 strlen

`strlen` 统计字符串长度，不包含结尾的 `'\0'`。

```cpp
#include <cassert>
#include <cstddef>

size_t my_strlen(const char* s) {
    assert(s != nullptr);

    const char* p = s;
    while (*p != '\0') {
        ++p;
    }

    return p - s;
}
```

---

## 2. 实现 strcmp

`strcmp` 按字典序比较两个 C 字符串。

```cpp
#include <cassert>

int my_strcmp(const char* s1, const char* s2) {
    assert(s1 != nullptr && s2 != nullptr);

    while (*s1 && *s1 == *s2) {
        ++s1;
        ++s2;
    }

    return static_cast<unsigned char>(*s1) -
           static_cast<unsigned char>(*s2);
}
```

---

## 3. 注意点

| 函数 | 注意点 |
|---|---|
| `strlen` | 不统计 `'\0'` |
| `strcmp` | 返回值只关心正负零，不要求必须返回 -1 或 1 |
| 两者 | 参数为空都是未定义行为 |

---

## 4. 为什么转成 `unsigned char`？

避免 `char` 默认有符号时，高位字符比较出现平台差异。

---

## 5. 面试回答

`strlen` 从字符串首地址开始遍历，直到遇到 `'\0'`，返回指针差值。`strcmp` 逐字符比较两个字符串，遇到不同字符或结束符时返回字符差值，返回值正负表示大小关系。
