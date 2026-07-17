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
