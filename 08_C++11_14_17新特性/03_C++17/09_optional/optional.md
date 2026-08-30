# C++17：`std::optional`

`optional<T>` 表示一个可能存在、也可能不存在的 `T`。

```cpp
std::optional<int> find_id(std::string_view name) {
    if (name == "root") return 0;
    return std::nullopt;
}

if (auto id = find_id("root")) {
    use(*id);
}
```

它适合代替特殊哨兵值或可空输出参数。访问前可用 `has_value()`、布尔转换或 `value_or()` 判断。

`optional` 只能表达有值或无值，无法携带详细错误原因；需要错误码或错误对象时应选择更合适的结果类型。

## 初始化、调用与访问

```cpp
#include <iostream>
#include <optional>
#include <string>

std::optional<std::string> find_user(int id) {
    if (id == 100) return std::string{"Alice"};
    return std::nullopt;
}

int main() {
    std::optional<std::string> result;       // 无值初始化
    result = find_user(100);                 // 函数调用和赋值

    if (result) std::cout << *result << '\n';
    std::cout << result.value() << '\n';
    std::cout << find_user(200).value_or("unknown") << '\n';

    result.emplace(5, 'x');                  // 原地构造 "xxxxx"
    result.reset();                          // 销毁内部值，恢复无值状态
}
```

| 操作 | 用法 |
|---|---|
| 无值初始化 | `std::optional<T> value;` 或 `std::nullopt` |
| 有值初始化 | `std::optional<T> value{x};` |
| 判断 | `if (value)`、`has_value()` |
| 访问 | `*value`、`value()`、`value_or(defaultValue)` |
| 原地构造 | `emplace(args...)` |
| 清空 | `reset()` |

空对象上调用 `value()` 会抛出 `std::bad_optional_access`；空对象上直接解引用属于未定义行为。
