# C++14：`constexpr` 增强

C++14 放宽了 `constexpr` 函数体限制，允许局部变量、循环、条件分支和修改局部状态。

```cpp
constexpr int factorial(int n) {
    int result = 1;
    for (int i = 2; i <= n; ++i) {
        result *= i;
    }
    return result;
}

static_assert(factorial(5) == 120, "error");
```

`constexpr` 函数不保证每次都在编译期执行。只有用于常量表达式上下文并满足相关条件时，才必须在编译期求值。

## 使用方法

```cpp
#include <array>
#include <iostream>

constexpr int factorial(int n) {
    int result = 1;
    for (int i = 2; i <= n; ++i) result *= i;
    return result;
}

int main() {
    constexpr int size = factorial(5); // 编译期调用
    std::array<int, size> buffer{};     // 用作模板实参
    static_assert(size == 120, "unexpected result");

    int n;
    std::cin >> n;
    std::cout << factorial(n) << '\n'; // 同一函数也可在运行期调用
}
```

只有常量实参、函数体可用于常量求值并且调用结果进入常量上下文时，编译器才必须完成编译期计算。`constexpr` 适合尺寸、查表数据、协议常量和编译期校验。
