# C++14：Lambda 初始化捕获

初始化捕获允许在捕获列表中定义并初始化闭包成员，也称广义捕获。

```cpp
auto ptr = std::make_unique<int>(42);

auto task = [value = 10, p = std::move(ptr)] {
    return value + *p;
};
```

它的重要用途是把 `unique_ptr` 等只能移动的对象转移进闭包。示例中的 `p` 是闭包成员；移动后外部 `ptr` 通常为空。

易错点：捕获成员变量时不能直接写成员名，通常捕获 `this`，或使用初始化捕获保存所需值。

## 使用方法

```cpp
#include <iostream>
#include <memory>
#include <utility>

int main() {
    int base = 10;
    auto ptr = std::make_unique<int>(32);

    // value 是值副本；owned 通过移动取得 unique_ptr 所有权
    auto task = [value = base, owned = std::move(ptr)]() mutable {
        ++value;
        return value + *owned;
    };

    std::cout << task() << '\n';   // 调用闭包
    std::cout << std::boolalpha << (ptr == nullptr) << '\n';
}
```

初始化捕获的通用格式是 `[闭包成员名 = 初始化表达式]`。捕获后使用的是闭包成员名，而不是外部变量名。值捕获默认不能修改；需要修改闭包内副本时在参数列表后加 `mutable`。

异步执行时优先捕获所需值或移动资源；捕获局部变量引用后让 Lambda 逃离当前作用域会产生悬空引用。
