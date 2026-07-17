# C++ 面试题：placement new 是什么

## 1. 核心结论

`placement new` 可以在已经分配好的内存上构造对象。

它只调用构造函数，不负责分配内存。

---

## 2. 示例

```cpp
#include <new>

char buffer[sizeof(int)];

int* p = new (buffer) int(10);
```

这里的 `buffer` 是已有内存，`placement new` 在这块内存上构造了一个 `int`。

---

## 3. 对象析构

对于非平凡析构类型，需要手动调用析构函数：

```cpp
class A {
public:
    A() {}
    ~A() {}
};

char buffer[sizeof(A)];
A* p = new (buffer) A();
p->~A();
```

注意：不能对 `p` 调用 `delete`，因为内存不是 `new` 分配的。

---

## 4. 使用场景

1. 内存池
2. STL allocator
3. 对象复用
4. 高性能场景中分离内存分配和对象构造

---

## 5. 面试回答

`placement new` 是在指定内存地址上构造对象，它不会分配内存，只调用构造函数。使用后如果对象有析构逻辑，需要手动调用析构函数，并且不能直接 `delete` 这个对象，因为底层内存不一定来自普通 `new`。
