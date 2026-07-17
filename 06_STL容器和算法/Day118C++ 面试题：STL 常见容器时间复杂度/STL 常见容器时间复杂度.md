# C++ 面试题：STL 常见容器时间复杂度

## 1. 顺序容器

| 容器 | 随机访问 | 头插 | 尾插 | 中间插入删除 |
|---|---|---|---|---|
| `vector` | O(1) | O(n) | 均摊 O(1) | O(n) |
| `deque` | O(1) | O(1) | O(1) | O(n) |
| `list` | O(n) | O(1) | O(1) | 已有迭代器 O(1) |
| `forward_list` | O(n) | O(1) | O(n) | 已有前驱 O(1) |
| `array` | O(1) | 不支持 | 不支持 | 不支持 |

---

## 2. 关联容器

| 容器 | 查找 | 插入 | 删除 | 是否有序 |
|---|---|---|---|---|
| `map` | O(log n) | O(log n) | O(log n) | 有序 |
| `set` | O(log n) | O(log n) | O(log n) | 有序 |
| `multimap` | O(log n) | O(log n) | O(log n) | 有序 |
| `multiset` | O(log n) | O(log n) | O(log n) | 有序 |

---

## 3. 无序关联容器

| 容器 | 平均查找 | 平均插入 | 平均删除 | 最坏情况 |
|---|---|---|---|---|
| `unordered_map` | O(1) | O(1) | O(1) | O(n) |
| `unordered_set` | O(1) | O(1) | O(1) | O(n) |

---

## 4. 容器适配器

| 容器 | 主要操作 | 复杂度 |
|---|---|---|
| `stack` | `push` / `pop` / `top` | O(1) |
| `queue` | `push` / `pop` / `front` | O(1) |
| `priority_queue` | `push` / `pop` / `top` | O(log n) / O(log n) / O(1) |

---

## 5. 面试回答

STL 容器复杂度取决于底层结构。连续数组类容器随机访问快，但中间插删慢；链表插删快但随机访问慢；红黑树容器查找插删是 O(log n)；哈希容器平均 O(1)，但最坏可能 O(n)。
