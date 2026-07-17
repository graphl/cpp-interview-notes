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
