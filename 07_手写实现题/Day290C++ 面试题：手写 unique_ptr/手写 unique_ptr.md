# C++ 面试题：手写 unique_ptr

## 1. 考点

`unique_ptr` 表示独占所有权：同一时刻只有一个智能指针负责对象生命周期。

面试主要考：

1. RAII
2. 禁止拷贝、允许移动
3. 移动构造和移动赋值
4. `release`、`reset`、`swap`
5. 自定义删除器
6. 异常安全和空指针处理

---

## 2. 简化实现

```cpp
#include <cstddef>
#include <utility>

template <typename T>
struct DefaultDelete {
    void operator()(T* ptr) const noexcept {
        delete ptr;
    }
};

template <typename T, typename Deleter = DefaultDelete<T>>
class UniquePtr {
public:
    constexpr UniquePtr() noexcept = default;

    explicit UniquePtr(T* ptr) noexcept : ptr_(ptr) {}

    UniquePtr(T* ptr, Deleter deleter) noexcept
        : ptr_(ptr), deleter_(std::move(deleter)) {}

    ~UniquePtr() {
        if (ptr_) {
            deleter_(ptr_);
        }
    }

    UniquePtr(const UniquePtr&) = delete;
    UniquePtr& operator=(const UniquePtr&) = delete;

    UniquePtr(UniquePtr&& other) noexcept
        : ptr_(other.release()),
          deleter_(std::move(other.deleter_)) {}

    UniquePtr& operator=(UniquePtr&& other) noexcept {
        if (this != &other) {
            reset();
            deleter_ = std::move(other.deleter_);
            ptr_ = other.release();
        }
        return *this;
    }

    T* get() const noexcept { return ptr_; }
    Deleter& get_deleter() noexcept { return deleter_; }
    const Deleter& get_deleter() const noexcept { return deleter_; }

    explicit operator bool() const noexcept { return ptr_ != nullptr; }
    T& operator*() const { return *ptr_; }
    T* operator->() const noexcept { return ptr_; }

    T* release() noexcept {
        return std::exchange(ptr_, nullptr);
    }

    void reset(T* ptr = nullptr) noexcept {
        T* old = std::exchange(ptr_, ptr);
        if (old) {
            deleter_(old);
        }
    }

    void swap(UniquePtr& other) noexcept {
        using std::swap;
        swap(ptr_, other.ptr_);
        swap(deleter_, other.deleter_);
    }

private:
    T* ptr_ = nullptr;
    Deleter deleter_{};
};
```

标准库实现通常会利用空基类优化或 C++20 的 `[[no_unique_address]]`，避免无状态删除器额外占空间。这里保留普通成员以兼容 C++17。

---

## 3. 为什么不能拷贝？

如果两个对象都保存同一个裸指针，它们析构时会发生 double free。独占所有权只能转移，不能复制，因此删除拷贝操作，提供移动操作。

```cpp
UniquePtr<int> a(new int(10));
UniquePtr<int> b = std::move(a);
// 此时 a 为空，b 负责释放对象
```

---

## 4. release 和 reset 的区别

1. `release()`：放弃所有权并返回裸指针，不释放对象
2. `reset(p)`：释放当前对象，再接管 `p`
3. `get()`：只观察裸指针，不改变所有权

调用 `release()` 后必须把返回的指针交给新的所有者，否则会泄漏。

---

## 5. 复杂度和注意点

所有权操作都是 O(1)。需要注意：

1. 删除器的调用不应抛异常
2. 数组需要 `delete[]`，完整标准库通过偏特化支持 `unique_ptr<T[]>`
3. 标准库还支持不同指针、删除器类型之间的转换
4. `reset(get())` 会先释放对象再保存悬空指针，属于错误用法
5. 这个版本是教学实现，没有覆盖标准库全部约束和类型特征

---

## 6. 面试回答

`unique_ptr` 用 RAII 管理独占资源，析构时调用删除器。为避免多个所有者导致重复释放，它删除拷贝构造和拷贝赋值，只支持移动转移所有权。`release` 只放弃所有权，`reset` 会释放旧资源并接管新资源，自定义删除器则让它可以管理文件、句柄等非 `new` 资源。
