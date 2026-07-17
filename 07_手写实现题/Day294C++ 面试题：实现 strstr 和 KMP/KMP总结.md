# C++面试题: KMP

## 1. KMP 解决什么问题？

KMP（Knuth-Morris-Pratt）用于在主串 `text` 中查找模式串 `pattern` 第一次出现的位置。

暴力匹配发生失配时，会更换主串起点并重新比较，最坏时间复杂度为 `O(nm)`。KMP 利用已经匹配的字符和模式串自身的结构，使主串下标不回退，将总时间复杂度降为 `O(n + m)`。

```text
暴力匹配：失配后，主串和模式串都可能回退
KMP：     失配后，主串不回退，只移动模式串
```

---

## 2. KMP 的核心：LPS 数组

`lps` 是 longest proper prefix which is also suffix 的缩写。

`lps[i]` 表示在子串 `pattern[0..i]` 中，最长相等真前缀和真后缀的长度。

- 前缀必须从下标 `0` 开始；
- 后缀必须在下标 `i` 结束；
- 真前缀不能等于整个子串。

以模式串 `ABABCABAB` 为例：

```text
pattern: A B A B C A B A B
index:   0 1 2 3 4 5 6 7 8
lps:     0 0 1 2 0 1 2 3 4
```

例如：

- `ABAB` 的最长相等真前后缀是 `AB`，所以 `lps[3] = 2`；
- `ABABCABAB` 的最长相等真前后缀是 `ABAB`，所以 `lps[8] = 4`。

有些资料使用 `next` 数组，并令 `next[0] = -1`。这是另一套定义，公式也不同。面试时应先说明采用哪种定义，不能把 `next` 和 `lps` 的写法混在一起。

---

## 3. 构造 LPS 数组

维护两个下标：

- `i`：当前正在计算 `lps[i]`；
- `len`：当前候选公共前后缀的长度，也是下一次要比较的位置。

```cpp
#include <cstddef>
#include <string_view>
#include <vector>

std::vector<std::size_t> build_lps(std::string_view pattern) {
    std::vector<std::size_t> lps(pattern.size(), 0);

    std::size_t i = 1;
    std::size_t len = 0;

    while (i < pattern.size()) {
        if (pattern[i] == pattern[len]) {
            // 当前公共前后缀可以继续延长。
            lps[i] = len + 1;
            ++i;
            ++len;
        } else if (len != 0) {
            // 当前长度失败，尝试次长公共前后缀。
            // i 不移动，因为 lps[i] 还没有确定。
            len = lps[len - 1];
        } else {
            // 已经不存在更短的候选公共前后缀。
            lps[i] = 0;
            ++i;
        }
    }

    return lps;
}
```

构造过程可以记成三种情况：

```text
字符相等：lps[i] = len + 1，i 和 len 都加一
字符失配且 len > 0：len = lps[len - 1]，i 不动
字符失配且 len == 0：lps[i] = 0，i 加一
```

失配时不能简单写 `--len`。只有“同时也是前缀的后缀”才可能成为新的候选长度，而 `lps[len - 1]` 正好保存了这个信息。

---

## 4. KMP 匹配代码

匹配过程中：

- `i` 指向主串当前字符；
- `j` 指向模式串当前字符，同时表示已经匹配的字符数。

```cpp
std::size_t kmp_find(std::string_view text,
                     std::string_view pattern) {
    if (pattern.empty()) {
        return 0;
    }

    const auto lps = build_lps(pattern);
    std::size_t i = 0;
    std::size_t j = 0;

    while (i < text.size()) {
        if (text[i] == pattern[j]) {
            ++i;
            ++j;

            if (j == pattern.size()) {
                return i - j;
            }
        } else if (j != 0) {
            // 保持主串 i 不动，回退模式串下标。
            j = lps[j - 1];
        } else {
            // 模式串第一个字符便失配，只能检查主串下一字符。
            ++i;
        }
    }

    return std::string_view::npos;
}
```

---

