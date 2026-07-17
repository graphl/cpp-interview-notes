# C++14：`std::exchange`

`std::exchange(object, new_value)` 用新值替换对象，并返回替换前的旧值。

```cpp
int value = 10;
int old = std::exchange(value, 0);
// old == 10，value == 0
```

它常用于移动构造和状态切换：

```cpp
Socket(Socket&& other) noexcept
    : fd_(std::exchange(other.fd_, -1)) {}
```

注意：`std::exchange` 只是普通赋值操作，不保证线程安全，也不是原子交换；原子对象应使用其 `exchange` 成员函数。
