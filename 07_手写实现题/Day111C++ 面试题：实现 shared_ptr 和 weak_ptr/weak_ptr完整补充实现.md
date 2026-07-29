# C++ 面试题：补全 shared_ptr 和 weak_ptr

## 1. 为什么必须有两种引用计数

`shared_ptr` 管理对象生命周期，`weak_ptr` 只观察对象。控制块因此要分别保存：

1. 强引用计数：归零时销毁对象。
2. 弱引用计数：强、弱计数都归零时销毁控制块。

如果只保存一个计数，既无法让 `weak_ptr` 在对象销毁后判断过期，也无法确定控制块何时释放。

## 2. 非线程安全教学实现

```cpp
#include <cstddef>
#include <utility>

template <typename T>
class SharedPtr;

template <typename T>
class WeakPtr;

template <typename T>
struct ControlBlock {
    explicit ControlBlock(T* value)
        : ptr(value), strong_count(1), weak_count(0) {}

    T* ptr;
    std::size_t strong_count;
    std::size_t weak_count;
};

template <typename T>
class SharedPtr {
    friend class WeakPtr<T>;

    struct AddStrongRef {};

    SharedPtr(ControlBlock<T>* block, AddStrongRef)
        : block_(block) {
        ++block_->strong_count;
    }

public:
    SharedPtr() noexcept = default;

    explicit SharedPtr(T* ptr)
        : block_(ptr ? new ControlBlock<T>(ptr) : nullptr) {}

    SharedPtr(const SharedPtr& other) noexcept
        : block_(other.block_) {
        add_ref();
    }

    SharedPtr(SharedPtr&& other) noexcept
        : block_(std::exchange(other.block_, nullptr)) {}

    SharedPtr& operator=(SharedPtr other) noexcept {
        swap(other);
        return *this;
    }

    ~SharedPtr() {
        release();
    }

    void swap(SharedPtr& other) noexcept {
        std::swap(block_, other.block_);
    }

    T* get() const noexcept {
        return block_ ? block_->ptr : nullptr;
    }

    T& operator*() const {
        return *get();
    }

    T* operator->() const noexcept {
        return get();
    }

    explicit operator bool() const noexcept {
        return get() != nullptr;
    }

    std::size_t use_count() const noexcept {
        return block_ ? block_->strong_count : 0;
    }

private:
    void add_ref() noexcept {
        if (block_) {
            ++block_->strong_count;
        }
    }

    void release() noexcept {
        if (!block_) {
            return;
        }

        if (--block_->strong_count == 0) {
            delete block_->ptr;
            block_->ptr = nullptr;

            if (block_->weak_count == 0) {
                delete block_;
            }
        }
        block_ = nullptr;
    }

    ControlBlock<T>* block_ = nullptr;
};

template <typename T>
class WeakPtr {
public:
    WeakPtr() noexcept = default;

    WeakPtr(const SharedPtr<T>& owner) noexcept
        : block_(owner.block_) {
        add_ref();
    }

    WeakPtr(const WeakPtr& other) noexcept
        : block_(other.block_) {
        add_ref();
    }

    WeakPtr(WeakPtr&& other) noexcept
        : block_(std::exchange(other.block_, nullptr)) {}

    WeakPtr& operator=(WeakPtr other) noexcept {
        swap(other);
        return *this;
    }

    ~WeakPtr() {
        release();
    }

    void swap(WeakPtr& other) noexcept {
        std::swap(block_, other.block_);
    }

    bool expired() const noexcept {
        return !block_ || block_->strong_count == 0;
    }

    std::size_t use_count() const noexcept {
        return block_ ? block_->strong_count : 0;
    }

    SharedPtr<T> lock() const noexcept {
        if (expired()) {
            return {};
        }
        return SharedPtr<T>(block_, typename SharedPtr<T>::AddStrongRef{});
    }

private:
    void add_ref() noexcept {
        if (block_) {
            ++block_->weak_count;
        }
    }

    void release() noexcept {
        if (!block_) {
            return;
        }

        if (--block_->weak_count == 0 &&
            block_->strong_count == 0) {
            delete block_;
        }
        block_ = nullptr;
    }

    ControlBlock<T>* block_ = nullptr;
};
```

## 3. 生命周期检查

```cpp
SharedPtr<int> owner(new int(42));
WeakPtr<int> observer(owner);

{
    SharedPtr<int> copy = observer.lock();
    // copy 存在，强引用计数为 2。
}

owner = {};
// 对象已经销毁，但 observer 仍可安全访问控制块。

SharedPtr<int> missing = observer.lock();
// missing 为空。
```

对象和控制块的释放顺序是：

```text
strong_count 变成 0
-> 销毁 T
-> weak_count 也为 0 时销毁控制块
```

## 4. 教学实现的边界

1. 计数不是原子变量，不支持并发复制、销毁同一个控制块。
2. `expired()` 与 `lock()` 之间没有原子性保证；真实实现必须原子地“强计数非零则加一”。
3. 没有自定义删除器、分配器、别名构造和 `enable_shared_from_this`。
4. 直接用同一个裸指针构造两个 `SharedPtr`，仍会产生两个控制块和重复释放。
5. 标准库通常让控制块隐含持有一个弱计数，具体计数布局属于实现细节。

## 5. 面试口述版

`shared_ptr` 增加强计数，`weak_ptr` 只增加弱计数。强计数归零时对象立即销毁；只要还有弱引用，控制块就继续存在，因此 `weak_ptr` 可以判断对象是否过期。`lock()` 成功时必须原子地增加强计数并返回新的 `shared_ptr`，否则对象可能在检查和加计数之间被另一个线程销毁。
