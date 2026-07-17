## 7. noexcept 的作用是什么？

`noexcept` 表示函数承诺不会抛出异常。

```cpp
void func() noexcept;
```

作用：

1. 告诉调用者该函数不会抛异常。
2. 帮助编译器做优化。
3. 影响标准库容器的移动行为。
4. 如果 `noexcept` 函数内部异常逃出，会调用 `std::terminate()`。

常见面试点：

```cpp
class A {
public:
    A(A&& other) noexcept {
        // move
    }
};
```

如果移动构造函数是 `noexcept`，`std::vector` 扩容时更倾向于使用移动构造；否则可能退回使用拷贝构造，以保证异常安全。

## 8. throw; 和 throw e; 有什么区别？

`throw;` 用于重新抛出当前捕获到的异常，保留原始异常类型。

```cpp
try {
    throw std::runtime_error("error");
} catch (const std::exception& e) {
    throw;
}
```

`throw e;` 会重新抛出一个新的异常对象，可能发生对象切片。

```cpp
try {
    throw std::runtime_error("error");
} catch (const std::exception& e) {
    throw e;
}
```

结论：

- 想原样继续抛出异常，用 `throw;`。
- 不推荐用 `throw e;` 重新抛异常。

## 9. 什么是异常安全？

异常安全指代码在异常发生后，仍能保持资源不泄漏、对象状态不被破坏。

常见等级：

1. 基本保证：异常发生后，资源不泄漏，对象仍处于有效状态。
2. 强保证：异常发生后，程序状态回滚到操作之前。
3. 不抛保证：函数保证不抛出异常，通常配合 `noexcept`。

示例：

```cpp
class Buffer {
private:
    std::vector<int> data_;

public:
    void append(int value) {
        data_.push_back(value);
    }
};
```

`std::vector::push_back` 本身提供较好的异常安全保证，因此这里可以借助标准库容器减少手动资源管理风险。

## 10. RAII 和异常有什么关系？

RAII 是 C++ 中管理资源的核心思想，和异常机制非常契合。

RAII 的核心：

- 在构造函数中获取资源。
- 在析构函数中释放资源。
- 依靠对象生命周期自动管理资源。

异常发生时，栈展开会自动调用局部对象析构函数，因此 RAII 可以保证资源被释放。

推荐：

```cpp
std::unique_ptr<int> p = std::make_unique<int>(10);
```

不推荐：

```cpp
int* p = new int(10);
throw std::runtime_error("error");
delete p; // 执行不到，内存泄漏
```

## 11. C++ 标准异常类有哪些？

常见标准异常类都继承自 `std::exception`。

常见类型：

- `std::exception`
- `std::runtime_error`
- `std::logic_error`
- `std::bad_alloc`
- `std::out_of_range`
- `std::invalid_argument`
- `std::length_error`

示例：

```cpp
try {
    std::vector<int> v;
    v.at(10);
} catch (const std::out_of_range& e) {
    std::cout << e.what() << std::endl;
}
```

`v.at(10)` 会进行边界检查，越界时抛出 `std::out_of_range`。

## 12. new 失败时会发生什么？

普通 `new` 分配失败时会抛出 `std::bad_alloc`。

```cpp
try {
    int* p = new int[100000000000];
} catch (const std::bad_alloc& e) {
    std::cout << e.what() << std::endl;
}
```

如果不想抛异常，可以使用 `std::nothrow`：

```cpp
int* p = new (std::nothrow) int[100000000000];
if (p == nullptr) {
    std::cout << "alloc failed" << std::endl;
}
```

