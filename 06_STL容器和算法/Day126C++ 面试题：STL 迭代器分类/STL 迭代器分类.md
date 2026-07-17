# C++ 面试题：STL 迭代器分类

## 1. 核心结论

STL 迭代器按能力从弱到强分为多类。

常见分类：

1. 输入迭代器
2. 输出迭代器
3. 前向迭代器
4. 双向迭代器
5. 随机访问迭代器

---

## 2. 分类表

| 迭代器 | 能力 | 典型容器 |
|---|---|---|
| 输入迭代器 | 只读，单向一次遍历 | `istream_iterator` |
| 输出迭代器 | 只写，单向一次遍历 | `ostream_iterator` |
| 前向迭代器 | 可多次单向遍历 | `forward_list` |
| 双向迭代器 | 可前后移动 | `list`、`map`、`set` |
| 随机访问迭代器 | 支持 `+`、`-`、下标 | `vector`、`deque`、`array` |

---

## 3. 为什么 list 不能用 std::sort？

`std::sort` 要求随机访问迭代器。

`list` 只有双向迭代器，所以不能使用：

```cpp
std::sort(lst.begin(), lst.end());  // 错误
```

应该用：

```cpp
lst.sort();
```

---

## 4. 迭代器能力示例

```cpp
auto it = v.begin();
it = it + 3;     // vector 支持
```

```cpp
auto it = lst.begin();
// it = it + 3;  // list 不支持
+++it;           // 只能一步一步走
```

---

## 5. 面试回答

STL 迭代器根据能力分为输入、输出、前向、双向和随机访问迭代器。不同算法对迭代器能力有要求，比如 `std::sort` 需要随机访问迭代器，所以能用于 `vector`，不能用于 `list`。
