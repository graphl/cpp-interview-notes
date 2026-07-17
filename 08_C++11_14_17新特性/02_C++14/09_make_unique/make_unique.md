# C++14：`std::make_unique`

`std::make_unique` 创建对象并返回对应的 `unique_ptr`：

```cpp
auto object = std::make_unique<Widget>(1, "worker");
auto array = std::make_unique<int[]>(100);
```

它避免显式使用 `new`，类型只需书写一次，并使对象创建后立即进入 RAII 管理。

版本辨析：

```text
std::unique_ptr、std::make_shared：C++11
std::make_unique：                C++14
```

对于需要自定义删除器的 `unique_ptr`，通常仍需显式构造智能指针。
