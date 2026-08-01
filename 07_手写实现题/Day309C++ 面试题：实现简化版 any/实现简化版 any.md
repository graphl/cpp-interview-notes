# C++ 面试题：实现简化版 any

## 1. any 为什么需要类型擦除

`any` 要在同一个非模板类型中保存任意可复制类型。外层对象不能提前知道内部类型，因此通过一个统一的虚接口擦除具体类型：

```text
Any -> unique_ptr<Placeholder>
                    ^
                    |
              Holder<int>
              Holder<string>
              Holder<UserType>
```

## 2. 教学实现

```cpp
#include <memory>
#include <stdexcept>
#include <type_traits>
#include <typeinfo>
#include <utility>

class Any {
private:
    struct Placeholder {
        virtual ~Placeholder() = default;
        virtual const std::type_info& type() const noexcept = 0;
        virtual std::unique_ptr<Placeholder> clone() const = 0;
    };

    template <typename T>
    struct Holder final : Placeholder {
        template <typename U>
        explicit Holder(U&& input) : value(std::forward<U>(input)) {}

        const std::type_info& type() const noexcept override {
            return typeid(T);
        }

        std::unique_ptr<Placeholder> clone() const override {
            return std::make_unique<Holder<T>>(value);
        }

        T value;
    };

public:
    Any() = default;

    template <typename T,
              typename U = std::decay_t<T>,
              typename = std::enable_if_t<!std::is_same<U, Any>::value>>
    Any(T&& value)
        : content_(std::make_unique<Holder<U>>(std::forward<T>(value))) {}

    Any(const Any& other)
        : content_(other.content_ ? other.content_->clone() : nullptr) {}

    Any(Any&&) noexcept = default;

    Any& operator=(Any other) {
        content_.swap(other.content_);
        return *this;
    }

    bool has_value() const noexcept {
        return static_cast<bool>(content_);
    }

    void reset() noexcept {
        content_.reset();
    }

    const std::type_info& type() const noexcept {
        return content_ ? content_->type() : typeid(void);
    }

    template <typename T>
    T& get() {
        using U = std::decay_t<T>;
        if (!content_ || content_->type() != typeid(U)) {
            throw std::bad_cast{};
        }
        return static_cast<Holder<U>*>(content_.get())->value;
    }

private:
    std::unique_ptr<Placeholder> content_;
};
```

## 3. 为什么需要 clone

外层只持有 `Placeholder*`，无法直接写出具体类型的拷贝构造。虚函数 `clone()` 会动态分派到正确的 `Holder<T>`，从而完成深拷贝。

## 4. 成本和边界

- 教学实现通常每次保存值都需要一次堆分配。
- 访问需要运行时类型检查，类型不匹配时失败。
- 完整实现可能使用小对象优化，把较小对象直接放进 Any 内部缓冲区。
- `any` 适合确实需要开放类型集合的场景；类型集合固定时，`variant` 通常更容易静态分析。

## 5. 面试口述版

any 通过类型擦除保存任意可复制对象。外层持有统一的抽象基类指针，每种实际类型由 Holder<T> 保存；type 提供运行时类型信息，clone 负责在不知道 T 的外层完成深拷贝。简化实现会产生虚调用和堆分配，生产实现通常还会加入小对象优化。
