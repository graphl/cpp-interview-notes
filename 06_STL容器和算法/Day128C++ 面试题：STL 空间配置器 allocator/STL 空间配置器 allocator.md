# C++ 面试题：STL 空间配置器 allocator

## 1. 核心结论

`allocator` 是 STL 用来管理内存分配和对象构造的组件。

它把“分配原始内存”和“构造对象”分开。

---

## 2. 为什么需要 allocator？

容器需要做两件不同的事：

1. 申请一块原始内存
2. 在这块内存上构造对象

例如 `vector` 扩容时，会先申请更大的原始空间，再把已有元素移动构造过去。

---

## 3. 简化理解

```cpp
std::allocator<int> alloc;

int* p = alloc.allocate(10);     // 分配 10 个 int 的原始空间
alloc.construct(p, 1);           // 在 p 上构造 int
alloc.destroy(p);                // 析构对象
alloc.deallocate(p, 10);         // 释放原始空间
```

现代 C++ 中直接调用 `construct/destroy` 的方式已有变化，但思想仍然是分离内存和对象生命周期。

---

## 4. new 和 allocator 的区别

| 对比 | `new` | `allocator` |
|---|---|---|
| 分配内存 | 是 | 是 |
| 构造对象 | 是 | 可分离控制 |
| 释放内存 | `delete` | `deallocate` |
| 容器适配 | 不灵活 | 适合 STL 容器 |

---

## 5. 面试回答

STL 的 allocator 负责容器底层内存管理。它的核心价值是把内存分配和对象构造分离，使容器可以先申请一段原始内存，再按需构造元素。`vector` 这类容器正是依赖这种机制管理容量和元素生命周期。
