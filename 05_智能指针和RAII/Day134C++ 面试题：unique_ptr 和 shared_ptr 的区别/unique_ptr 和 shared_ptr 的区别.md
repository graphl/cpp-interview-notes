# C++ 面试题：unique_ptr 和 shared_ptr 的区别

## 1. 核心结论

`unique_ptr` 表示独占所有权。

`shared_ptr` 表示共享所有权。

---

## 2. 对比表

| 对比 | `unique_ptr` | `shared_ptr` |
|---|---|---|
| 所有权 | 独占 | 共享 |
| 拷贝 | 禁止 | 允许 |
| 移动 | 支持 | 支持 |
| 开销 | 小 | 较大，有控制块和原子计数 |
| 释放时机 | 所有者销毁时 | 最后一个所有者销毁时 |
| 循环引用 | 无 | 可能出现 |

---

## 3. unique_ptr 示例

```cpp
auto p1 = std::make_unique<int>(10);
auto p2 = std::move(p1);
```

移动后，`p1` 变为空，所有权转移给 `p2`。

---

## 4. shared_ptr 示例

```cpp
auto p1 = std::make_shared<int>(10);
auto p2 = p1;
```

`p1` 和 `p2` 共同拥有同一个对象。

---

## 5. 如何选择？

优先使用 `unique_ptr`。

只有确实需要共享所有权时，才使用 `shared_ptr`。

---

## 6. 面试回答

`unique_ptr` 是独占式智能指针，不允许拷贝，只能移动，开销小，适合明确单一所有者的场景。`shared_ptr` 是共享式智能指针，通过引用计数管理生命周期，允许多个指针共同拥有对象，但开销更大，并且可能产生循环引用。
