# C++17：`std::apply` 和 `std::invoke`

`std::apply` 把元组元素展开为函数实参：

```cpp
auto args = std::make_tuple(1, 2);
int result = std::apply(
    [](int a, int b) { return a + b; }, args);
```

`std::invoke` 统一调用普通函数、函数对象、成员函数指针和成员数据指针：

```cpp
std::invoke(&Worker::run, worker, 42);
```

二者都是通用调用设施：`apply` 负责展开元组，`invoke` 负责统一不同可调用对象的调用语法。

## 使用方法

```cpp
#include <functional>
#include <iostream>
#include <tuple>

struct Worker {
    int factor{2};
    int run(int value) const { return value * factor; }
};

int add(int a, int b) { return a + b; }

int main() {
    auto args = std::make_tuple(3, 4);
    std::cout << std::apply(add, args) << '\n';       // 展开为 add(3, 4)

    Worker worker;
    std::cout << std::invoke(&Worker::run, worker, 5) << '\n';
    std::cout << std::invoke(&Worker::factor, worker) << '\n';

    auto bound = [&worker](int value) {
        return std::invoke(&Worker::run, worker, value);
    };
    std::cout << bound(6) << '\n';
}
```

`invoke` 的第一个参数可以是普通函数、Lambda、函数对象、成员函数指针或成员数据指针。调用成员指针时必须继续传入对象、对象指针或 `reference_wrapper`。
