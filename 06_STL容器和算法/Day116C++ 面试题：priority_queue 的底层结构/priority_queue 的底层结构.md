# C++ 面试题：priority_queue 的底层结构

## 1. 核心结论

`priority_queue` 是容器适配器，底层默认使用 `vector`，并通过堆算法维护堆结构。

默认是大根堆。

---

## 2. 默认定义

```cpp
std::priority_queue<int> pq;
```

等价于：

```cpp
std::priority_queue<int, std::vector<int>, std::less<int>> pq;
```

`std::less<int>` 表示大根堆，堆顶是最大值。

---

## 3. 小根堆

```cpp
#include <queue>
#include <vector>
#include <functional>

std::priority_queue<int, std::vector<int>, std::greater<int>> pq;
```

---

## 4. 常用操作复杂度

| 操作 | 复杂度 |
|---|---|
| `top` | O(1) |
| `push` | O(log n) |
| `pop` | O(log n) |
| 构造堆 | O(n) |

---

## 5. 面试回答

`priority_queue` 底层默认是 `vector`，通过堆算法维护优先级。默认比较器是 `less`，所以是大根堆，堆顶是最大元素。插入和删除堆顶都需要调整堆，复杂度是 O(log n)，访问堆顶是 O(1)。
