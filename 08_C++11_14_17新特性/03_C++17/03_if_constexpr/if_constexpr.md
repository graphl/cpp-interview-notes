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

## 使用方法

```cpp
#include <iostream>
#include <string>
#include <type_traits>

template <typename T>
void print_value(const T& value) {
    if constexpr (std::is_pointer_v<T>) {
        if (value) std::cout << *value << '\n';
    } else if constexpr (std::is_integral_v<T>) {
        std::cout << "integer: " << value << '\n';
    } else {
        std::cout << value << '\n';
    }
}

int main() {
    int number = 7;
    print_value(number);
    print_value(&number);
    print_value(std::string{"text"});
}
```

条件必须能在编译期转换为 `bool`。被丢弃分支仍需满足基本语法，并且其中与模板参数无关的错误仍可能立即报错。它适合替代一部分 SFINAE，但不等同于 C++20 Concepts。
