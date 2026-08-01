# C++ 面试题：实现 vector 类

## 1. 这道题真正考什么

`vector` 不只是“会扩容的数组”。它必须把两种范围分开：

```text
data_                    data_ + size_           data_ + capacity_
  | 已构造、可访问的 T 对象 | 尚未构造的原始存储       |
  +----------------------+------------------------+
```

因此不能简单使用 `new T[capacity]` 模拟真实 vector：那会提前默认构造 capacity 个对象，也无法支持没有默认构造函数的类型。

## 2. 教学实现

下面使用 `std::allocator` 分离原始存储与对象生命周期。为了让核心流程清楚，只实现 Rule of Five、`push_back`、`reserve` 和下标访问。

```cpp
#include <cstddef>
#include <memory>
#include <utility>

template <typename T>
class Vector {
private:
    using Alloc = std::allocator<T>;
    using Traits = std::allocator_traits<Alloc>;

public:
    Vector() = default;

    Vector(const Vector& other) {
        if (other.size_ == 0) {
            return;
        }

        data_ = Traits::allocate(alloc_, other.size_);
        capacity_ = other.size_;

        try {
            for (; size_ < other.size_; ++size_) {
                Traits::construct(alloc_, data_ + size_, other.data_[size_]);
            }
        } catch (...) {
            release_storage();
            throw;
        }
    }

    Vector(Vector&& other) noexcept
        : data_(other.data_),
          size_(other.size_),
          capacity_(other.capacity_) {
        other.data_ = nullptr;
        other.size_ = 0;
        other.capacity_ = 0;
    }

    Vector& operator=(const Vector& other) {
        if (this != &other) {
            Vector temp(other);
            swap(temp);
        }
        return *this;
    }

    Vector& operator=(Vector&& other) noexcept {
        if (this != &other) {
            release_storage();
            data_ = other.data_;
            size_ = other.size_;
            capacity_ = other.capacity_;
            other.data_ = nullptr;
            other.size_ = 0;
            other.capacity_ = 0;
        }
        return *this;
    }

    ~Vector() {
        release_storage();
    }

    // 按值接收让参数先成为独立对象。
    // 即使调用 push_back(v[0]) 后发生扩容，也不会留下悬空引用。
    void push_back(T value) {
        if (size_ == capacity_) {
            reserve(capacity_ == 0 ? 1 : capacity_ * 2);
        }

        Traits::construct(alloc_, data_ + size_, std::move(value));
        ++size_;
    }

    void reserve(std::size_t new_capacity) {
        if (new_capacity <= capacity_) {
            return;
        }

        T* new_data = Traits::allocate(alloc_, new_capacity);
        std::size_t constructed = 0;

        try {
            // move_if_noexcept 在移动可能抛异常且 T 可复制时优先复制，
            // 尽量保留旧数组，从而提供强异常保证。
            for (; constructed < size_; ++constructed) {
                Traits::construct(
                    alloc_,
                    new_data + constructed,
                    std::move_if_noexcept(data_[constructed]));
            }
        } catch (...) {
            while (constructed > 0) {
                --constructed;
                Traits::destroy(alloc_, new_data + constructed);
            }
            Traits::deallocate(alloc_, new_data, new_capacity);
            throw;
        }

        destroy_elements();
        if (data_) {
            Traits::deallocate(alloc_, data_, capacity_);
        }

        data_ = new_data;
        size_ = constructed;
        capacity_ = new_capacity;
    }

    T& operator[](std::size_t index) noexcept {
        return data_[index];
    }

    const T& operator[](std::size_t index) const noexcept {
        return data_[index];
    }

    std::size_t size() const noexcept { return size_; }
    std::size_t capacity() const noexcept { return capacity_; }

    void swap(Vector& other) noexcept {
        using std::swap;
        swap(data_, other.data_);
        swap(size_, other.size_);
        swap(capacity_, other.capacity_);
    }

private:
    void destroy_elements() noexcept {
        while (size_ > 0) {
            --size_;
            Traits::destroy(alloc_, data_ + size_);
        }
    }

    void release_storage() noexcept {
        destroy_elements();
        if (data_) {
            Traits::deallocate(alloc_, data_, capacity_);
        }
        data_ = nullptr;
        capacity_ = 0;
    }

    Alloc alloc_;
    T* data_ = nullptr;
    std::size_t size_ = 0;
    std::size_t capacity_ = 0;
};
```

## 3. 扩容数据流

```text
申请更大的原始存储
  -> 在新存储中逐个移动/拷贝构造元素
  -> 如果失败，销毁已构造的新元素并释放新存储
  -> 全部成功后销毁旧元素
  -> 释放旧存储
  -> 切换 data、size、capacity
```

## 4. 复杂度和失效规则

- 下标访问为 `O(1)`。
- 尾部插入单次最坏为 `O(n)`，倍增扩容下均摊为 `O(1)`。
- reallocation 会使所有指针、引用和迭代器失效。
- 没有发生 reallocation 时，尾部插入仍会使原 `end()` 失效。

## 5. 教学实现边界

1. `push_back(T value)` 为了简化别名问题多了一次参数移动。
2. 没有实现插入、删除、迭代器、`emplace_back`、边界检查和 allocator 传播规则。
3. 如果 T 不可复制且其移动构造会抛异常，扩容失败后可能无法承诺旧元素值完全不变。
4. 真实标准库的增长倍率属于实现策略，不保证固定为 1.5 倍或 2 倍。

## 6. 面试口述版

vector 用连续原始存储保存 size 个已构造对象，同时记录 capacity。扩容时先申请更大存储，在新地址逐个移动或复制构造元素；全部成功后才销毁旧元素并释放旧存储。这样才能支持非默认构造类型并讨论异常保证。倍增策略使 push_back 的均摊复杂度为 O(1)，但扩容会让所有迭代器、指针和引用失效。

