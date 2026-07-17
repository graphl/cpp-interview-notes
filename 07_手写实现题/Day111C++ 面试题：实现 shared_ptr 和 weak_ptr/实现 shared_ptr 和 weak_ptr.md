# C++ 面试题：实现 shared_ptr 和 weak_ptr

## 1. 考点

手写 `shared_ptr` 主要考资源管理和引用计数。
如果继续追问 `weak_ptr`，核心就是解决循环引用问题。

面试主要考：

1. RAII
2. 控制块
3. 强引用计数
4. 弱引用计数
5. 拷贝构造和赋值运算符
6. 析构时何时释放对象、何时释放控制块
7. 循环引用问题

---

## 2. 简化版 shared_ptr

```cpp
#include <cstddef>
#include <utility>

template <typename T>
class SharedPtr {
public:
    SharedPtr() = default;

    explicit SharedPtr(T* ptr)
        : ptr_(ptr), count_(ptr ? new size_t(1) : nullptr) {}

    SharedPtr(const SharedPtr& other)
        : ptr_(other.ptr_), count_(other.count_) {
        if (count_) {
            ++(*count_);
        }
    }

    SharedPtr& operator=(const SharedPtr& other) {
        if (this != &other) {
            release();
            ptr_ = other.ptr_;
            count_ = other.count_;
            if (count_) {
                ++(*count_);
            }
        }
        return *this;
    }

    ~SharedPtr() {
        release();
    }

    T& operator*() const {
        return *ptr_;
    }

    T* operator->() const {
        return ptr_;
    }

    T* get() const {
        return ptr_;
    }

    size_t use_count() const {
        return count_ ? *count_ : 0;
    }

private:
    void release() {
        if (!count_) {
            return;
        }

        --(*count_);
        if (*count_ == 0) {
            delete ptr_;
            delete count_;
        }

        ptr_ = nullptr;
        count_ = nullptr;
    }

    T* ptr_ = nullptr;
    size_t* count_ = nullptr;
};
```

---

## 3. 更接近真实实现：控制块

真实 `shared_ptr` 通常不会只保存一个计数指针，而是有控制块：

```cpp
struct ControlBlock {
    size_t strong_count;
    size_t weak_count;
};
```

对象什么时候释放？

1. `strong_count == 0` 时释放管理的对象
2. `strong_count == 0 && weak_count == 0` 时释放控制块

---

## 4. weak_ptr 的作用

`weak_ptr` 不增加强引用计数，不控制对象生命周期。
它主要用来观察对象是否还活着，避免循环引用。

典型循环引用：

```cpp
struct B;

struct A {
    std::shared_ptr<B> b;
};

struct B {
    std::shared_ptr<A> a;
};
```

`A` 持有 `B`，`B` 又持有 `A`，两个对象的引用计数都无法归零。
解决方式是把其中一边改成 `std::weak_ptr`。

---

## 5. 注意点

1. 拷贝时引用计数加一
2. 析构时引用计数减一
3. 引用计数为零时释放对象
4. 赋值运算符要处理自赋值
5. 真实 `shared_ptr` 的引用计数修改通常是原子操作
6. `shared_ptr<T>(this)` 很危险，容易产生两个控制块
7. 推荐使用 `make_shared`，对象和控制块可以一次分配

---

## 6. 面试回答

`shared_ptr` 的核心是控制块和引用计数。多个 `shared_ptr` 共享同一个控制块，拷贝时强引用计数加一，析构时强引用计数减一。当强引用计数变成零时释放对象。如果还有 `weak_ptr` 观察这个对象，控制块不能立刻释放，要等弱引用计数也归零。`weak_ptr` 不延长对象生命周期，主要用来解决 `shared_ptr` 的循环引用问题。
