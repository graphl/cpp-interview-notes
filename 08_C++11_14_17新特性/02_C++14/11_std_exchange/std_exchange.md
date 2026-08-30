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

## 使用方法

```cpp
#include <iostream>
#include <utility>

class Socket {
public:
    explicit Socket(int fd = -1) : fd_(fd) {}

    Socket(Socket&& other) noexcept
        : fd_(std::exchange(other.fd_, -1)) {}

    Socket& operator=(Socket&& other) noexcept {
        if (this != &other) {
            close();
            fd_ = std::exchange(other.fd_, -1);
        }
        return *this;
    }

    int release() noexcept { return std::exchange(fd_, -1); }
    int get() const noexcept { return fd_; }

private:
    void close() noexcept { /* fd_ >= 0 时关闭系统资源 */ }
    int fd_;
};

int main() {
    Socket first{10};
    Socket second{std::move(first)};
    std::cout << first.get() << ' ' << second.get() << '\n';
}
```

调用后，目标对象一定已经被赋予新值，而函数返回旧值。它适合“取走并复位”以及移动操作，但不会自动释放旧值所代表的资源，资源类仍要先完成必要清理。
