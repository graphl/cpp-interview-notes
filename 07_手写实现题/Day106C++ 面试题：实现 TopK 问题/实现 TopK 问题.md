# C++ 面试题：实现 TopK 问题

## 1. 考点

TopK 问题是从大量数据中找最大或最小的 K 个数。

常见方案：

1. 排序
2. 堆
3. 快速选择

---

## 2. 找最大的 K 个数：小根堆

```cpp
#include <queue>
#include <vector>

std::vector<int> topK(const std::vector<int>& nums, int k) {
    std::priority_queue<int, std::vector<int>, std::greater<int>> heap;

    for (int x : nums) {
        if (static_cast<int>(heap.size()) < k) {
            heap.push(x);
        } else if (x > heap.top()) {
            heap.pop();
            heap.push(x);
        }
    }

    std::vector<int> ans;
    while (!heap.empty()) {
        ans.push_back(heap.top());
        heap.pop();
    }
    return ans;
}
```

---

## 3. 为什么找最大 K 个用小根堆？

堆中只保存当前最大的 K 个数。

小根堆堆顶是这 K 个数里最小的。

如果新元素比堆顶大，说明它应该进入 TopK，于是弹出堆顶，插入新元素。

---

## 4. 复杂度

| 方法 | 时间复杂度 | 空间复杂度 | 适用场景 |
|---|---|---|---|
| 排序 | O(n log n) | 视排序而定 | 数据量较小 |
| 堆 | O(n log k) | O(k) | 海量数据 |
| 快速选择 | 平均 O(n) | O(1) | 内存中数组 |

---

## 5. 面试回答

TopK 常用小根堆或大根堆。如果要找最大的 K 个数，用大小为 K 的小根堆，堆顶保存当前 TopK 中最小的数。遍历数组时，如果新元素比堆顶大，就替换堆顶。整体时间复杂度是 O(n log k)，适合海量数据。
