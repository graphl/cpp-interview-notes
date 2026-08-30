# C++14：泛型 Lambda

C++14 允许 Lambda 形参使用 `auto`，编译器会为闭包类型生成函数调用运算符模板。

```cpp
auto add = [](auto a, auto b) {
    return a + b;
};

auto i = add(1, 2);       // int
auto d = add(1.5, 2.0);   // double
```

它适合编写与类型无关的局部操作。C++11 已支持 Lambda，但形参类型必须明确；泛型 Lambda 从 C++14 开始支持。

面试速答：泛型 Lambda 的本质是闭包类拥有一个模板化的 `operator()`，并不是把 Lambda 本身变成普通函数模板。

## 使用方法

```cpp
#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

int main() {
    // 1. 定义并初始化泛型 Lambda
    auto add = [](const auto& a, const auto& b) { return a + b; };

    // 2. 像函数一样调用；每组实参会实例化相应的 operator()
    std::cout << add(1, 2) << '\n';
    std::cout << add(std::string{"C++"}, std::string{"14"}) << '\n';

    // 3. 作为算法回调
    std::vector<int> values{3, 1, 2};
    std::sort(values.begin(), values.end(),
              [](const auto& lhs, const auto& rhs) { return lhs < rhs; });
}
```

形参写 `auto`、`const auto&` 或 `auto&&` 分别对应按值、只读引用和转发引用。大对象通常用 `const auto&`；需要修改实参时用 `auto&`。

编译：`g++ -std=c++14 demo.cpp`
