# C++14：`std::integer_sequence`

`integer_sequence` 表示编译期整数序列，`index_sequence` 是元素类型为 `std::size_t` 的常用别名。

```cpp
template <typename Tuple, std::size_t... I>
void print_tuple(const Tuple& tuple, std::index_sequence<I...>) {
    using Expand = int[];
    (void)Expand{0, ((void)(std::cout << std::get<I>(tuple) << ' '), 0)...};
}
```

C++14 常借助初始化列表展开参数包；C++17 可以改用更简洁的折叠表达式。

它的主要用途是将元组下标变成模板参数包。C++17 的 `std::apply` 封装了这类常见操作。
