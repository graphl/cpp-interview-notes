# C++ 面试题：resize 和 reserve 的区别

## 1. 核心结论

`reserve` 只改变容量 `capacity`，不改变元素个数 `size`。

`resize` 改变元素个数 `size`，必要时也会改变容量。

---

## 2. 示例

```cpp
std::vector<int> v;

v.reserve(10);
std::cout << v.size() << std::endl;      // 0
std::cout << v.capacity() << std::endl;  // >= 10

v.resize(10);
std::cout << v.size() << std::endl;      // 10
```

---

## 3. 对比表

| 对比点 | `reserve` | `resize` |
|---|---|---|
| 改变 size | 不改变 | 改变 |
| 改变 capacity | 可能改变 | 可能改变 |
| 是否构造元素 | 不构造 | 会构造或析构元素 |
| 常见用途 | 提前分配空间 | 调整元素个数 |

---

## 4. 常见错误

```cpp
std::vector<int> v;
v.reserve(10);
v[0] = 1;  // 错误，size 仍然是 0
```

应该写：

```cpp
v.resize(10);
v[0] = 1;
```

或者：

```cpp
v.reserve(10);
v.push_back(1);
```

---

## 5. 面试回答

`reserve` 是预留容量，只影响 `capacity`，不会创建元素，也不会改变 `size`；`resize` 是改变元素个数，会构造新元素或析构多余元素。提前知道元素数量时，可以用 `reserve` 减少扩容次数。
