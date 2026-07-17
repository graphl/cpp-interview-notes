# C++ 面试题：list 和 forward_list 的区别

## 1. 核心结论

`list` 是双向链表。

`forward_list` 是单向链表。

---

## 2. 对比表

| 对比点 | `list` | `forward_list` |
|---|---|---|
| 底层结构 | 双向链表 | 单向链表 |
| 迭代方向 | 前后都能走 | 只能向前 |
| 内存开销 | 每个节点两个指针 | 每个节点一个指针 |
| `push_back` | 支持 | 不支持 |
| `size()` | 通常支持 O(1) | 标准不提供成员 `size()` |
| 插入删除 | 已有位置 O(1) | 需要前驱节点 |

---

## 3. forward_list 的特殊操作

因为单向链表删除节点需要知道前驱，所以它提供：

```cpp
insert_after
erase_after
```

示例：

```cpp
std::forward_list<int> fl = {1, 3};
auto it = fl.begin();
fl.insert_after(it, 2);
```

---

## 4. 使用场景

`forward_list` 更省内存，适合只需要单向遍历、节点很多的场景。

`list` 功能更完整，适合需要双向遍历的场景。

---

## 5. 面试回答

`list` 是双向链表，每个节点有前驱和后继指针，支持双向遍历。`forward_list` 是单向链表，每个节点只有后继指针，内存开销更小，但只能向前遍历，插入删除通常需要前驱节点，所以提供 `insert_after` 和 `erase_after`。
