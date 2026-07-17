# C++ 面试题：实现 HashMap

## 1. 考点

手写 `HashMap` 主要考哈希表的底层结构。
面试中一般不要求实现完整 STL，只要能讲清楚冲突处理和扩容即可。

面试主要考：

1. 哈希函数
2. 桶数组
3. 哈希冲突
4. 拉链法
5. 负载因子
6. 扩容和 rehash
7. 平均时间复杂度

---

## 2. 拉链法实现

```cpp
#include <functional>
#include <list>
#include <utility>
#include <vector>

template <typename K, typename V>
class HashMap {
public:
    explicit HashMap(size_t bucket_count = 16)
        : buckets_(bucket_count), size_(0) {}

    void put(const K& key, const V& value) {
        if (load_factor() > 0.75) {
            rehash(buckets_.size() * 2);
        }

        size_t idx = index(key);
        for (auto& kv : buckets_[idx]) {
            if (kv.first == key) {
                kv.second = value;
                return;
            }
        }

        buckets_[idx].push_back({key, value});
        ++size_;
    }

    bool get(const K& key, V& value) const {
        size_t idx = index(key);
        for (const auto& kv : buckets_[idx]) {
            if (kv.first == key) {
                value = kv.second;
                return true;
            }
        }
        return false;
    }

    bool erase(const K& key) {
        size_t idx = index(key);
        auto& bucket = buckets_[idx];

        for (auto it = bucket.begin(); it != bucket.end(); ++it) {
            if (it->first == key) {
                bucket.erase(it);
                --size_;
                return true;
            }
        }

        return false;
    }

    size_t size() const {
        return size_;
    }

private:
    using Bucket = std::list<std::pair<K, V>>;

    size_t index(const K& key) const {
        return std::hash<K>{}(key) % buckets_.size();
    }

    double load_factor() const {
        return static_cast<double>(size_) / buckets_.size();
    }

    void rehash(size_t new_bucket_count) {
        std::vector<Bucket> old_buckets = std::move(buckets_);
        buckets_.clear();
        buckets_.resize(new_bucket_count);
        size_ = 0;

        for (const auto& bucket : old_buckets) {
            for (const auto& kv : bucket) {
                put(kv.first, kv.second);
            }
        }
    }

    std::vector<Bucket> buckets_;
    size_t size_;
};
```

---

## 3. 为什么需要 rehash？

桶数量固定时，元素越来越多，冲突会越来越严重。
一旦链表过长，查找就会退化成 O(n)。

所以哈希表会根据负载因子扩容：

```cpp
load_factor = 元素个数 / 桶个数
```

当负载因子超过阈值，比如 `0.75`，就扩容并重新计算每个元素所在的桶。

---

## 4. 复杂度

理想情况下：

1. 插入：平均 O(1)
2. 查找：平均 O(1)
3. 删除：平均 O(1)

最坏情况下，如果所有 key 都落在同一个桶里，会退化成 O(n)。

---

## 5. 注意点

1. 哈希冲突不可避免
2. 拉链法实现简单，但链表太长会影响性能
3. 扩容后必须重新计算桶下标
4. `unordered_map` 的迭代器可能因 rehash 失效
5. 真实实现还要考虑 allocator、异常安全、移动语义、迭代器等

---

## 6. 面试回答

`HashMap` 底层一般是桶数组，每个 key 通过哈希函数映射到一个桶。不同 key 可能落到同一个桶，这就是哈希冲突，常见解决方式是拉链法。插入和查找时先定位桶，再在桶内查找 key。当元素变多、负载因子过高时，需要扩容并 rehash。理想情况下增删查改平均 O(1)，但冲突严重时会退化。
