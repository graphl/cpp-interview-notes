# C++17：`if constexpr`

`if constexpr` 在编译期选择分支，未选中的分支不会针对当前模板实例进行实例化。

```cpp
template <typename T>
auto length(const T& value) {
    if constexpr (std::is_integral_v<T>) {
        return value;
    } else {
        return value.size();
    }
}
```

普通 `if` 的两个分支都必须对当前类型合法；`if constexpr` 可以丢弃不适用的模板代码。

它不等于 `constexpr` 函数：前者用于编译期分支，后者表示函数可以参与常量表达式求值。
