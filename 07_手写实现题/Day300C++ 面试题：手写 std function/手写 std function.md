# C++ 面试题：手写 std::function

## 1. 考点

`std::function<R(Args...)>` 能保存普通函数、函数对象和 lambda。它的核心不是函数指针，而是类型擦除。

面试主要考：

1. 类型擦除
2. 虚函数或函数表
3. 完美转发
4. 深拷贝
5. 空调用对象
6. 小对象优化

---

## 2. 简化实现

```cpp
#include <cstddef>
#include <functional>
#include <memory>
#include <stdexcept>
#include <type_traits>
#include <utility>

template <typename Signature>
class Function;

template <typename R, typename... Args>
class Function<R(Args...)> {
    struct Concept {
        virtual ~Concept() = default;
        virtual R invoke(Args&&... args) = 0;
        virtual std::unique_ptr<Concept> clone() const = 0;
    };

    template <typename F>
    struct Model final : Concept {
        explicit Model(F function) : function(std::move(function)) {}

        R invoke(Args&&... args) override {
            return std::invoke(function, std::forward<Args>(args)...);
        }

        std::unique_ptr<Concept> clone() const override {
            return std::make_unique<Model>(function);
        }

        F function;
    };

public:
    Function() noexcept = default;
    Function(std::nullptr_t) noexcept {}

    template <typename F,
              typename D = std::decay_t<F>,
              typename = std::enable_if_t<!std::is_same_v<D, Function>>>
    Function(F&& function)
        : target_(std::make_unique<Model<D>>(std::forward<F>(function))) {}

    Function(const Function& other)
        : target_(other.target_ ? other.target_->clone() : nullptr) {}

    Function(Function&&) noexcept = default;

    Function& operator=(Function other) noexcept {
        swap(other);
        return *this;
    }

    explicit operator bool() const noexcept {
        return static_cast<bool>(target_);
    }

    R operator()(Args... args) const {
        if (!target_) {
            throw std::bad_function_call();
        }
        return target_->invoke(std::forward<Args>(args)...);
    }

    void swap(Function& other) noexcept {
        target_.swap(other.target_);
    }

private:
    std::unique_ptr<Concept> target_;
};
```

---

## 3. 类型擦除怎么工作？

调用方只看到统一的 `Concept` 接口。每一种具体可调用类型 `F` 都被包装进 `Model<F>`。调用发生时通过虚函数进入 `Model<F>::invoke`，再调用真正的函数对象，因此容器不需要在编译期知道 `F`。

---

## 4. 为什么需要 clone？

`target_` 使用 `unique_ptr` 保存多态对象，不能直接拷贝。复制 `Function` 时，通过虚函数 `clone()` 创建具体 `Model<F>` 的副本，从而实现值语义。

这也意味着本简化版本要求目标 `F` 可拷贝，与 `std::function` 的传统语义一致。只支持移动的调用对象应使用 C++23 的 `std::move_only_function` 或单独设计包装器。

---

## 5. 与标准库版本的差距

1. 每个目标都动态分配内存
2. 没有小对象优化 SBO
3. 没完整实现 `target_type()`、`target<T>()` 等接口
4. 构造约束和 `noexcept` 条件不完整
5. 没有针对函数指针、成员指针等类型做空间和性能优化

标准实现通常在对象内部预留一小块缓冲区，小函数对象直接原地保存，较大对象才进行堆分配。

---

## 6. 面试回答

`std::function` 使用类型擦除统一保存不同的可调用对象。可以定义抽象调用接口，再用模板派生类保存具体 lambda 或函数对象，通过虚函数转发调用。为了保持值语义，复制时需要虚拟 `clone`。实际标准库通常还会使用小对象优化，避免小 lambda 每次都进行堆分配。
