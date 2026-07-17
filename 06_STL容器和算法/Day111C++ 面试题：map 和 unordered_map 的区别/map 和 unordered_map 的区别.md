# C++ 面试题：map 和 unordered_map 的区别

## 1. 核心结论

`map` 底层通常是红黑树，元素按 key 有序。

`unordered_map` 底层是哈希表，元素无序，平均查找更快。

---

## 2. 对比表

| 对比点 | `map` | `unordered_map` |
|---|---|---|
| 底层结构 | 红黑树 | 哈希表 |
| 是否有序 | 按 key 有序 | 无序 |
| 查找复杂度 | O(log n) | 平均 O(1)，最坏 O(n) |
| 插入删除 | O(log n) | 平均 O(1) |
| key 要求 | 支持 `<` 比较 | 支持 hash 和 `==` |
| 范围查询 | 支持 | 不适合 |
| 内存开销 | 树节点开销 | 桶数组 + 节点开销 |

---

## 3. 使用场景

用 `map`：

1. 需要有序遍历
2. 需要范围查询
3. 需要 `lower_bound`、`upper_bound`

用 `unordered_map`：

1. 只关心快速查找
2. 不关心顺序
3. 词频统计、缓存、索引表

---

## 4. 示例

```cpp
std::map<int, std::string> m;
m[2] = "b";
m[1] = "a";

// 输出顺序：1, 2
for (auto& [k, v] : m) {
    std::cout << k << " " << v << std::endl;
}
```

```cpp
std::unordered_map<int, std::string> um;
um[2] = "b";
um[1] = "a";

// 输出顺序不保证
for (auto& [k, v] : um) {
    std::cout << k << " " << v << std::endl;
}
```

---

## 5. 面试回答

`map` 底层是红黑树，key 有序，查找、插入、删除都是 O(log n)，适合有序遍历和范围查询。`unordered_map` 底层是哈希表，元素无序，平均查找 O(1)，适合快速查找，但哈希冲突严重时最坏可能退化到 O(n)。
