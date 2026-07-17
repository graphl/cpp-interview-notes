# C++ 面试题：实现 strstr 和 KMP

## 1. 考点

`strstr(text, pattern)` 返回模式串第一次出现的位置。暴力匹配最坏是 O(nm)，KMP 利用已经匹配的信息把复杂度降到 O(n + m)。

面试主要考：

1. 字符串边界
2. 暴力匹配
3. 前缀函数 `lps`
4. 匹配失败时如何回退
5. 时间和空间复杂度

---

## 2. 暴力实现

```cpp
#include <cstddef>

const char* my_strstr(const char* text, const char* pattern) {
    if (!text || !pattern) return nullptr;
    if (*pattern == '\0') return text;

    for (const char* start = text; *start != '\0'; ++start) {
        const char* a = start;
        const char* b = pattern;
        while (*a != '\0' && *b != '\0' && *a == *b) {
            ++a;
            ++b;
        }
        if (*b == '\0') return start;
    }
    return nullptr;
}
```

标准 `strstr` 对非法指针没有定义；这里返回空指针只是教学接口选择。

---

## 3. KMP 实现

`lps[i]` 表示 `pattern[0..i]` 的最长相等真前缀和真后缀长度。

```cpp
#include <cstddef>
#include <string>
#include <string_view>
#include <vector>

std::vector<size_t> build_lps(std::string_view pattern) {
    std::vector<size_t> lps(pattern.size(), 0);
    for (size_t i = 1, len = 0; i < pattern.size();) {
        if (pattern[i] == pattern[len]) {
            lps[i++] = ++len;
        } else if (len > 0) {
            len = lps[len - 1];
        } else {
            lps[i++] = 0;
        }
    }
    return lps;
}

size_t kmp_find(std::string_view text, std::string_view pattern) {
    if (pattern.empty()) return 0;

    std::vector<size_t> lps = build_lps(pattern);
    for (size_t i = 0, j = 0; i < text.size();) {
        if (text[i] == pattern[j]) {
            ++i;
            ++j;
            if (j == pattern.size()) return i - j;
        } else if (j > 0) {
            j = lps[j - 1];
        } else {
            ++i;
        }
    }
    return std::string_view::npos;
}
```

---

## 4. KMP 为什么不回退主串？

假设已经匹配了 `j` 个字符后失败。`lps[j - 1]` 告诉我们：已匹配部分的后缀和模式串前缀有多长相同。模式串直接移动到这个前缀继续比较，主串下标 `i` 不需要回退。

---

## 5. 复杂度和常见错误

1. 暴力算法：最坏 O(nm)，额外空间 O(1)
2. KMP：构造 `lps` 为 O(m)，匹配 O(n)，空间 O(m)
3. 空模式串应匹配在位置 0
4. 回退应写 `j = lps[j - 1]`，不能简单写 `--j`
5. 构造 `lps` 失败时也要继续利用较短公共前后缀

---

## 6. 面试回答

暴力 `strstr` 从每个起点逐字符匹配，最坏 O(nm)。KMP 为模式串预处理最长公共前后缀数组，匹配失败时让模式串回退到仍可能匹配的位置，而主串不回退，因此整体复杂度是 O(n + m)。
