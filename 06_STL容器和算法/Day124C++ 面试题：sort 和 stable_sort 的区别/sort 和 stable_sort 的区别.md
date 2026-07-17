# C++ 面试题：sort 和 stable_sort 的区别

## 1. 核心结论

`sort` 不保证稳定性。

`stable_sort` 保证稳定性。

稳定性指的是：相等元素排序后相对顺序不变。

---

## 2. 对比表

| 对比点 | `sort` | `stable_sort` |
|---|---|---|
| 稳定性 | 不稳定 | 稳定 |
| 时间复杂度 | O(n log n) | O(n log n) |
| 空间开销 | 通常较小 | 通常需要额外空间 |
| 适用迭代器 | 随机访问迭代器 | 随机访问迭代器 |

---

## 3. 示例

```cpp
struct Student {
    std::string name;
    int score;
};

std::stable_sort(students.begin(), students.end(),
    [](const Student& a, const Student& b) {
        return a.score < b.score;
    });
```

如果两个学生分数相同，`stable_sort` 保持它们原来的相对顺序。

---

## 4. 注意点

`std::sort` 不能用于 `list`：

```cpp
std::list<int> lst;
// std::sort(lst.begin(), lst.end());  // 错误
lst.sort();
```

因为 `std::sort` 需要随机访问迭代器。

---

## 5. 面试回答

`sort` 和 `stable_sort` 都是排序算法，时间复杂度通常是 O(n log n)。区别是 `stable_sort` 保证稳定性，相等元素的相对顺序不变，但通常需要额外空间；`sort` 不保证稳定性，空间开销一般更小。
