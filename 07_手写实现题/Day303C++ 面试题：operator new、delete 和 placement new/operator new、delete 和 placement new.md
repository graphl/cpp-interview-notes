# C++ 面试题：operator new、delete 和 placement new

## 1. 先分清四个概念

```text
new T(args...)
  = 调用 operator new 取得原始存储
  + 在存储上构造 T

delete ptr
  = 调用 T 的析构函数
  + 调用 operator delete 释放原始存储
```

`operator new` 名字里虽然有 new，但它只分配原始字节，不负责构造对象。`placement new` 则不分配内存，只在调用者提供的地址上构造对象。

## 2. 类专属的 operator new/delete

```cpp
#include <cstdlib>
#include <iostream>
#include <new>

class Widget {
public:
    explicit Widget(int value) : value_(value) {
        std::cout << "construct Widget\n";
    }

    ~Widget() {
        std::cout << "destroy Widget\n";
    }

    static void* operator new(std::size_t size) {
        std::cout << "allocate " << size << " bytes\n";

        if (void* ptr = std::malloc(size)) {
            return ptr;
        }
        throw std::bad_alloc{};
    }

    static void operator delete(void* ptr) noexcept {
        std::cout << "release storage\n";
        std::free(ptr);
    }

private:
    int value_;
};
```

调用：

```cpp
Widget* p = new Widget(42);
delete p;
```

执行顺序为：

```text
Widget::operator new
  -> Widget::Widget
  -> Widget::~Widget
  -> Widget::operator delete
```

如果构造函数抛异常，new 表达式会调用与分配形式匹配的 `operator delete` 归还原始存储，对象析构函数不会执行，因为对象没有构造完成。

## 3. placement new

```cpp
#include <cstddef>
#include <new>
#include <utility>

template <typename T, typename... Args>
T* construct_at(void* storage, Args&&... args) {
    return ::new (storage) T(std::forward<Args>(args)...);
}

template <typename T>
void destroy_at(T* object) noexcept {
    object->~T();
}

alignas(Widget) std::byte storage[sizeof(Widget)];

Widget* object = construct_at<Widget>(storage, 42);
destroy_at(object);
```

这里的 `storage` 由调用者拥有，所以只能显式调用析构函数，不能写 `delete object`。`delete` 会尝试释放并非由普通 `operator new` 返回的存储。

## 4. 常见追问

### new 和 malloc 的失败行为有什么不同？

普通 `operator new` 默认失败时抛出 `std::bad_alloc`；`malloc` 失败时返回空指针。`new (std::nothrow) T` 才使用返回空指针的形式。

### 为什么 delete[] 不能替代 delete？

数组 new 表达式需要记录并销毁多个元素，具体元数据布局由实现决定。分配和释放形式不匹配属于未定义行为。

### placement new 会释放旧对象吗？

不会。在同一存储上构造新对象前，调用者必须先正确结束旧对象生命周期，并保证大小、对齐和后续指针使用满足语言规则。

## 5. 面试口述版

new 表达式包含分配和构造两个阶段，delete 表达式包含析构和释放两个阶段。operator new/delete 只负责原始存储，可以被全局或类专属重载。placement new 不分配内存，只在指定地址开始对象生命周期，因此常用于容器、对象池和 allocator，析构及存储释放必须由调用者分别负责。
