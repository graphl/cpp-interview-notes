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
