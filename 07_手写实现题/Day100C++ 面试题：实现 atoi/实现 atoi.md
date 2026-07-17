# C++ 面试题：实现 atoi

## 1. 考点

`atoi` 把字符串转换成整数。

面试主要考：

1. 跳过前导空格
2. 处理正负号
3. 处理非法字符
4. 整数溢出
5. 边界条件

---

## 2. 实现

```cpp
#include <climits>
#include <string>

int my_atoi(const std::string& s) {
    int i = 0;
    int n = static_cast<int>(s.size());

    while (i < n && s[i] == ' ') {
        ++i;
    }

    int sign = 1;
    if (i < n && (s[i] == '+' || s[i] == '-')) {
        sign = (s[i] == '-') ? -1 : 1;
        ++i;
    }

    long long ans = 0;
    while (i < n && s[i] >= '0' && s[i] <= '9') {
        ans = ans * 10 + (s[i] - '0');

        if (sign == 1 && ans > INT_MAX) {
            return INT_MAX;
        }
        if (sign == -1 && -ans < INT_MIN) {
            return INT_MIN;
        }

        ++i;
    }

    return static_cast<int>(sign * ans);
}
```

---

## 3. 示例

| 输入 | 输出 |
|---|---|
| `"42"` | `42` |
| `"   -42"` | `-42` |
| `"4193 with words"` | `4193` |
| `"words 987"` | `0` |

---

## 4. 面试回答

实现 `atoi` 时，先跳过前导空格，再判断正负号，然后逐位累积数字。累积过程中要检查是否超过 `int` 范围，正溢出返回 `INT_MAX`，负溢出返回 `INT_MIN`。
