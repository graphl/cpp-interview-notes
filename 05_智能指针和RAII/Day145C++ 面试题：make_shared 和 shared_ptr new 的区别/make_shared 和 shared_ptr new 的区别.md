# C++ 面试题：make_shared 和 shared_ptr(new) 的区别

## 1. 核心结论

`make_shared` 通常一次分配内存，同时存放对象和控制块。

`shared_ptr(new T)` 通常至少两次分配：一次对象，一次控制块。

---

## 2. 示例

```cpp
auto p1 = std::make_shared<int>(10);
```

```cpp
std::shared_ptr<int> p2(new int(10));
```

---

## 3. make_shared 优点

1. 内存分配次数更少
2. 性能更好
3. 异常安全性更好
4. 写法更简洁

---

## 4. 什么时候不适合 make_shared？

如果对象很大，并且有 `weak_ptr` 长时间存在：

1. 强引用为 0 时，对象会析构
2. 但控制块还要等弱引用为 0 才释放
3. `make_shared` 对象和控制块在同一块内存中，可能导致对象占用的整块内存延迟释放

---

## 5. 面试回答

`make_shared` 通常会把对象和控制块放在一次内存分配中，效率更高，也更异常安全；`shared_ptr(new T)` 往往需要分别分配对象和控制块。一般推荐使用 `make_shared`，但如果需要自定义删除器或希望对象内存和控制块分开管理，可以使用 `shared_ptr(new T, deleter)`。
