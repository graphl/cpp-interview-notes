# C++ 面试题：lower_bound 和 upper_bound

## 1. 核心结论

`lower_bound` 找第一个大于等于目标值的位置。

`upper_bound` 找第一个大于目标值的位置。

---

## 2. 示例

```cpp
std::vector<int> v = {1, 2, 2, 2, 3, 4};

auto l = std::lower_bound(v.begin(), v.end(), 2);
auto r = std::upper_bound(v.begin(), v.end(), 2);
```

结果：

```text
lower_bound 指向第一个 2
upper_bound 指向 3
```

区间 `[l, r)` 就是所有等于 2 的元素。

---

## 3. 统计出现次数

```cpp
int count = std::upper_bound(v.begin(), v.end(), 2) -
            std::lower_bound(v.begin(), v.end(), 2);
```

---

## 4. 前提条件

使用二分查找类算法，区间必须已经有序。

```cpp
std::sort(v.begin(), v.end());
```

---

## 5. 面试回答

`lower_bound` 返回第一个不小于目标值的位置，`upper_bound` 返回第一个大于目标值的位置。它们要求区间有序，底层是二分查找。常用于查找范围、统计某个值出现次数、插入位置判断。
