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
