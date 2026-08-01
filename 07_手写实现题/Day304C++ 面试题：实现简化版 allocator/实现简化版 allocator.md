# C++ 面试题：实现简化版 allocator

## 1. allocator 解决什么问题

容器必须区分：

```text
capacity 范围：已经取得原始存储，但不一定存在对象
size 范围：对象已经构造，生命周期正在进行
```

allocator 把原始存储的申请/释放交给 `allocate/deallocate`，把对象生命周期交给 `construct/destroy` 或 `std::allocator_traits`。

## 2. 最小无状态 allocator

```cpp
#include <cstddef>
#include <limits>
#include <new>
#include <utility>

template <typename T>
class SimpleAllocator {
public:
    using value_type = T;

    SimpleAllocator() noexcept = default;

    template <typename U>
    SimpleAllocator(const SimpleAllocator<U>&) noexcept {}

    T* allocate(std::size_t count) {
        if (count > std::numeric_limits<std::size_t>::max() / sizeof(T)) {
            throw std::bad_array_new_length{};
        }

        // 只取得足以容纳 count 个 T 的原始存储，不构造 T。
        return static_cast<T*>(::operator new(count * sizeof(T)));
    }

    void deallocate(T* ptr, std::size_t) noexcept {
        // 此时对应对象必须已经全部析构。
        ::operator delete(ptr);
    }

    template <typename U, typename... Args>
    void construct(U* ptr, Args&&... args) {
        ::new (static_cast<void*>(ptr)) U(std::forward<Args>(args)...);
    }

    template <typename U>
    void destroy(U* ptr) noexcept {
        ptr->~U();
    }
};

template <typename T, typename U>
bool operator==(const SimpleAllocator<T>&,
                const SimpleAllocator<U>&) noexcept {
    // 无状态 allocator 的任意实例都能释放彼此申请的内存。
    return true;
}

template <typename T, typename U>
bool operator!=(const SimpleAllocator<T>& lhs,
                const SimpleAllocator<U>& rhs) noexcept {
    return !(lhs == rhs);
}
```

使用方式：

```cpp
#include <vector>

std::vector<int, SimpleAllocator<int>> values;
values.push_back(10);
values.push_back(20);
```

## 3. vector 扩容时发生什么

```text
allocator.allocate(new_capacity)
  -> 获得一片尚无 T 对象的新存储
  -> 逐个移动构造或拷贝构造现有元素
  -> 已成功迁移后销毁旧元素
  -> allocator.deallocate(old_storage)
```

如果中途构造失败，容器必须销毁已经在新存储中构造成功的对象并释放新存储。能否保留旧容器状态，取决于元素移动/拷贝的异常性质和容器提供的异常保证。

## 4. 为什么标准库常通过 allocator_traits 调用

`std::allocator_traits<A>` 为 allocator 提供统一适配层，可以补齐默认类型和默认操作，并处理 allocator 在容器拷贝、移动、交换时是否传播。现代代码通常让 traits 调用 `construct` 和 `destroy`，而不是直接依赖 allocator 必须定义这些成员。

## 5. 面试口述版

allocator 的关键作用是把原始存储管理与对象生命周期分离。allocate 只申请能容纳若干 T 的存储，construct 才在指定位置开始对象生命周期；destroy 结束生命周期，deallocate 最后归还存储。vector 扩容正是先分配新存储、迁移构造元素、销毁旧元素，再释放旧存储。
