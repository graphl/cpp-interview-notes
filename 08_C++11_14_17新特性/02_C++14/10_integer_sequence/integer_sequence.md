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

## 使用方法

```cpp
#include <iostream>
#include <tuple>
#include <utility>

template <typename Tuple, std::size_t... I>
void print_impl(const Tuple& tuple, std::index_sequence<I...>) {
    using swallow = int[];
    (void)swallow{0, ((std::cout << (I == 0 ? "" : ", ")
                                  << std::get<I>(tuple)), 0)...};
}

template <typename... T>
void print_tuple(const std::tuple<T...>& tuple) {
    // 生成 0, 1, ..., sizeof...(T)-1 并传给实现函数
    print_impl(tuple, std::index_sequence_for<T...>{});
}

int main() {
    auto data = std::make_tuple(7, 3.5, "ready");
    print_tuple(data);
}
```

常用入口有 `std::make_index_sequence<N>`、`std::index_sequence<I...>` 和 `std::index_sequence_for<T...>`。业务代码很少直接保存该对象；它主要作为模板参数包展开的编译期载体。
