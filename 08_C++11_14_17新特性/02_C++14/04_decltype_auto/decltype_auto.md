# C++14：`decltype(auto)`

`decltype(auto)` 使用 `decltype` 规则推导类型，可以保留表达式的引用和 `const` 属性。

```cpp
int value = 10;

auto get_value() { return value; }             // int
decltype(auto) get_ref() { return (value); }   // int&
```

括号会影响 `decltype`：对未加括号的变量名得到声明类型，对一般表达式则根据值类别得到 `T&`、`T&&` 或 `T`。

最大风险是意外返回悬空引用：

```cpp
decltype(auto) bad() {
    int local = 0;
    return (local);  // 返回 int&，函数结束后悬空
}
```

## 使用方法

```cpp
#include <iostream>
#include <vector>

std::vector<int> values{10, 20};

decltype(auto) at(std::size_t index) {
    return (values[index]); // int&，保留下标表达式的引用属性
}

int main() {
    at(0) = 99;             // 函数调用结果可作为左值
    std::cout << values[0] << '\n';

    decltype(auto) ref = at(1); // ref 为 int&
    ref = 88;
}
```

选择规则：返回独立值时使用 `auto`；包装另一个 API 且必须原样保留引用和值类别时使用 `decltype(auto)`。写转发包装器时常与 `std::forward` 一起使用，但必须确认返回对象的生命周期长于返回引用。
