# C++ 面试题：shared_ptr 的引用计数原理

## 1. 核心结论

`shared_ptr` 通过控制块保存引用计数。

每拷贝一个 `shared_ptr`，强引用计数加一；每析构一个 `shared_ptr`，强引用计数减一。

当强引用计数变为 0 时，释放被管理对象。

---

## 2. 控制块里有什么？

控制块通常包含：

1. 强引用计数
2. 弱引用计数
3. 删除器
4. 分配器
5. 被管理对象相关信息

---

## 3. 示例

```cpp
auto p1 = std::make_shared<int>(10);  // use_count = 1
auto p2 = p1;                         // use_count = 2

p2.reset();                           // use_count = 1
p1.reset();                           // use_count = 0，释放对象
```

---

## 4. weak_ptr 的关系

`weak_ptr` 只增加弱引用计数，不增加强引用计数。

对象是否释放取决于强引用计数是否为 0。

控制块本身通常要等强引用和弱引用都为 0 才释放。

---

## 5. 注意点

不要用同一个裸指针构造多个独立的 `shared_ptr`：

```cpp
int* p = new int(10);
std::shared_ptr<int> a(p);
std::shared_ptr<int> b(p);  // 错误，两个控制块，可能 double free
```

---

## 6. 面试回答

`shared_ptr` 的引用计数存放在控制块中。拷贝 `shared_ptr` 时强引用计数加一，析构或 reset 时减一；当强引用计数为 0 时释放对象。`weak_ptr` 不增加强引用计数，只影响弱引用计数，控制块通常在强弱引用都为 0 后释放。
