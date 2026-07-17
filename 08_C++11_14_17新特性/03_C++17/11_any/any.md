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
