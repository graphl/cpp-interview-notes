# C++17：`std::variant`

`variant<Ts...>` 是类型安全的联合体，在任意时刻保存候选类型中的一个值。

```cpp
std::variant<int, std::string> value = "hello";

std::visit([](const auto& item) {
    std::cout << item;
}, value);
```

可以用 `holds_alternative<T>` 判断当前类型，用 `get<T>` 或 `get_if<T>` 访问。

错误调用 `get<T>` 会抛出 `std::bad_variant_access`；异常情况下还要了解 `valueless_by_exception()`。候选类型集合已知时，`variant` 通常比 `any` 更安全。

## 初始化、赋值与访问

```cpp
#include <iostream>
#include <string>
#include <variant>

using Result = std::variant<int, std::string>;

Result query(bool ok) {
    if (ok) return 200;
    return std::string{"network error"};
}

int main() {
    Result result{42};                        // 初始化为 int
    result = std::string{"ready"};            // 切换当前候选类型

    if (std::holds_alternative<std::string>(result))
        std::cout << std::get<std::string>(result) << '\n';

    if (auto number = std::get_if<int>(&result))
        std::cout << *number << '\n';         // 类型不匹配时返回 nullptr

    std::visit([](const auto& value) { std::cout << value << '\n'; },
               query(false));                 // 对当前类型统一分发
}
```

第一个候选类型必须可默认构造，`variant` 才能默认构造。候选中有重复类型时优先按索引访问；希望明确表达“尚无值”时可把 `std::monostate` 放在第一项。
