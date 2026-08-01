# C++ 面试题：实现简化版 optional

## 1. optional 的核心状态

`optional<T>` 不是“一个 T 加一个空指针”，而是一块足以容纳 T 的存储，加上“其中是否存在 T 对象”的状态：

```text
engaged_ = false：只有原始存储，没有 T 对象
engaged_ = true ：存储中已经构造了一个 T
```

## 2. 教学实现

```cpp
#include <cassert>
#include <cstddef>
#include <memory>
#include <new>
#include <type_traits>
#include <utility>

template <typename T>
class Optional {
public:
    Optional() noexcept = default;

    Optional(const T& value) {
        emplace(value);
    }

    Optional(T&& value) {
        emplace(std::move(value));
    }

    Optional(const Optional& other) {
        if (other.engaged_) {
            emplace(*other);
        }
    }

    Optional(Optional&& other) noexcept(
        std::is_nothrow_move_constructible<T>::value) {
        if (other.engaged_) {
            emplace(std::move(*other));
        }
    }

    ~Optional() {
        reset();
    }

    template <typename... Args>
    T& emplace(Args&&... args) {
        reset();
        ::new (static_cast<void*>(storage_))
            T(std::forward<Args>(args)...);
        engaged_ = true;
        return *ptr();
    }

    void reset() noexcept {
        if (engaged_) {
            ptr()->~T();
            engaged_ = false;
        }
    }

    bool has_value() const noexcept {
        return engaged_;
    }

    T& value() {
        assert(engaged_);
        return *ptr();
    }

    const T& value() const {
        assert(engaged_);
        return *ptr();
    }

    T& operator*() { return value(); }
    const T& operator*() const { return value(); }

private:
    T* ptr() noexcept {
        return std::launder(reinterpret_cast<T*>(storage_));
    }

    const T* ptr() const noexcept {
        return std::launder(reinterpret_cast<const T*>(storage_));
    }

    alignas(T) unsigned char storage_[sizeof(T)];
    bool engaged_ = false;
};
```

## 3. 状态变化

```text
empty --emplace--> engaged
engaged --reset--> empty
engaged --emplace--> destroy old T -> construct new T -> engaged
```

如果新构造函数抛异常，旧值已经被 reset，当前教学实现保持 empty。完整 `std::optional` 还要实现赋值、比较、异常类型和大量条件启用规则。

## 4. 面试口述版

optional 内部保存一块对齐的未初始化存储和一个 engaged 标志。存在值时通过 placement new 在存储上构造 T，reset 或析构时显式调用 T 的析构函数。难点不是 bool 标志，而是只在对象生命周期确实开始后访问它，并正确处理拷贝、移动和构造异常。
