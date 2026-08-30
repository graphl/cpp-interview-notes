# C++17：`std::any`

`std::any` 通过类型擦除保存任意满足要求的单个值：

```cpp
std::any value = 42;

if (auto number = std::any_cast<int>(&value)) {
    std::cout << *number;
}
```

按值或引用形式错误转换会抛出 `std::bad_any_cast`；指针形式失败时返回空指针。

`any` 适合类型集合开放的接口，但会失去编译期穷举检查，并可能产生动态分配。候选类型固定时优先考虑 `variant`。

## 初始化、赋值与访问

```cpp
#include <any>
#include <iostream>
#include <string>

int main() {
    std::any value;                           // 空对象
    value = 42;                               // 保存 int
    std::cout << std::any_cast<int>(value) << '\n';

    value.emplace<std::string>(5, 'x');       // 原地构造 string
    if (auto text = std::any_cast<std::string>(&value))
        std::cout << *text << '\n';

    std::cout << value.type().name() << '\n'; // 查询运行期类型
    value.reset();                            // 销毁内部对象
    std::cout << std::boolalpha << value.has_value() << '\n';
}
```

常用接口是 `has_value()`、`type()`、`emplace<T>()`、`reset()` 和 `any_cast<T>()`。`any` 保存的是对象副本，所存类型需要可复制构造；若需要保存独占资源，通常改用多态接口、`shared_ptr` 或封闭的 `variant`。
