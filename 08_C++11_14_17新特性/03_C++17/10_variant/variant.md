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
