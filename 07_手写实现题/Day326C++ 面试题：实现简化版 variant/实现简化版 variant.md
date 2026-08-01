# C++ 面试题：实现简化版 variant

## 1. variant 的核心不是类型擦除

`variant<T, U, ...>` 的候选类型集合在编译期已经确定。它通常包含：

```text
一块足够容纳最大候选类型的对齐存储
+ 一个记录当前有效类型的索引
```

这和 `any` 不同：

- `variant` 是封闭类型集合，通过索引判断当前类型；
- `any` 是开放类型集合，通常使用类型擦除和运行时类型信息。

下面实现只支持两个不同的候选类型，用来展示对象生命周期管理。

## 2. 教学实现

```cpp
#include <cstddef>
#include <new>
#include <stdexcept>
#include <type_traits>
#include <utility>

template <typename T, typename U>
class Variant2 {
    static_assert(!std::is_same<T, U>::value,
                  "Variant2 requires two different types");

    using Storage = std::aligned_union_t<0, T, U>;
    static constexpr std::size_t npos = 2;

public:
    explicit Variant2(const T& value) {
        emplace<T>(value);
    }

    explicit Variant2(T&& value) {
        emplace<T>(std::move(value));
    }

    explicit Variant2(const U& value) {
        emplace<U>(value);
    }

    explicit Variant2(U&& value) {
        emplace<U>(std::move(value));
    }

    Variant2(const Variant2& other) {
        copy_from(other);
    }

    Variant2(Variant2&& other) noexcept(
        std::is_nothrow_move_constructible<T>::value &&
        std::is_nothrow_move_constructible<U>::value) {
        move_from(std::move(other));
    }

    Variant2& operator=(const Variant2& other) {
        if (this != &other) {
            reset();
            copy_from(other);
        }
        return *this;
    }

    Variant2& operator=(Variant2&& other) noexcept(
        std::is_nothrow_move_constructible<T>::value &&
        std::is_nothrow_move_constructible<U>::value) {
        if (this != &other) {
            reset();
            move_from(std::move(other));
        }
        return *this;
    }

    ~Variant2() {
        reset();
    }

    template <typename V, typename... Args>
    V& emplace(Args&&... args) {
        static_assert(std::is_same<V, T>::value ||
                      std::is_same<V, U>::value,
                      "V is not an alternative");
        reset();
        V* object = ::new (static_cast<void*>(&storage_))
            V(std::forward<Args>(args)...);
        index_ = std::is_same<V, T>::value ? 0 : 1;
        return *object;
    }

    template <typename V>
    bool holds_alternative() const noexcept {
        static_assert(std::is_same<V, T>::value ||
                      std::is_same<V, U>::value,
                      "V is not an alternative");
        const std::size_t expected =
            std::is_same<V, T>::value ? 0 : 1;
        return index_ == expected;
    }

    template <typename V>
    V& get() {
        if (!holds_alternative<V>()) {
            throw std::runtime_error("bad Variant2 access");
        }
        return *pointer<V>();
    }

    template <typename V>
    const V& get() const {
        if (!holds_alternative<V>()) {
            throw std::runtime_error("bad Variant2 access");
        }
        return *pointer<V>();
    }

    std::size_t index() const noexcept {
        return index_;
    }

    bool valueless() const noexcept {
        return index_ == npos;
    }

    void reset() noexcept {
        if (index_ == 0) {
            pointer<T>()->~T();
        } else if (index_ == 1) {
            pointer<U>()->~U();
        }
        index_ = npos;
    }

private:
    template <typename V>
    V* pointer() noexcept {
        return std::launder(reinterpret_cast<V*>(&storage_));
    }

    template <typename V>
    const V* pointer() const noexcept {
        return std::launder(reinterpret_cast<const V*>(&storage_));
    }

    void copy_from(const Variant2& other) {
        if (other.index_ == 0) {
            emplace<T>(*other.pointer<T>());
        } else if (other.index_ == 1) {
            emplace<U>(*other.pointer<U>());
        }
    }

    void move_from(Variant2&& other) {
        if (other.index_ == 0) {
            emplace<T>(std::move(*other.pointer<T>()));
        } else if (other.index_ == 1) {
            emplace<U>(std::move(*other.pointer<U>()));
        }
    }

    Storage storage_;
    std::size_t index_ = npos;
};
```

`index_` 只有在 placement new 构造成功后才更新。如果构造抛异常，对象保持无值状态，析构时不会访问尚未开始生命周期的对象。

## 3. 生命周期变化

```text
无值
-> placement new 构造候选对象
-> 写入有效索引
-> get 前检查索引
-> reset 时按索引调用正确析构函数
-> 回到无值
```

移动构造后，源对象仍然保存原候选类型，只是内部值处于该类型合法但未指定的移动后状态。

## 4. 与 std::variant 的差距

1. 标准 `variant` 支持任意数量候选类型。
2. 标准版本默认构造第一个候选类型，本版本没有默认构造函数。
3. 标准版本提供 `visit`、`get_if`、比较和完整的条件启用规则。
4. 本版本赋值只有基本异常保证：新对象构造失败后可能变成无值。
5. 标准术语是 `valueless_by_exception`，完整实现要精确处理赋值和类型切换。
6. `std::aligned_union` 在 C++23 中已弃用；C++23 实现可改用对齐字节数组等存储方案。

## 5. 面试口述版

variant 在编译期知道所有候选类型，因此可以分配一块能容纳最大候选对象的原始存储，再用索引记录当前有效类型。构造时 placement new，切换类型或析构时根据索引调用正确析构函数，访问时先检查索引。它的核心是判别联合和对象生命周期，不是 any 那种开放式类型擦除。
