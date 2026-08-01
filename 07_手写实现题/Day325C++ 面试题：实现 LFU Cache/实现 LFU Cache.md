# C++ 面试题：实现 LFU Cache

## 1. LFU 和 LRU 的区别

- LRU 淘汰最久没有访问的元素；
- LFU 淘汰访问频率最低的元素；
- 多个元素频率相同时，通常再淘汰其中最久未使用的元素。

要让 `get` 和 `put` 平均都是 `O(1)`，需要同时维护：

```text
key -> value、frequency、在频次链表中的位置
frequency -> 该频次下按新旧排列的 key 链表
min_frequency -> 当前最小频次
```

## 2. 教学实现

```cpp
#include <cstddef>
#include <list>
#include <unordered_map>

class LFUCache {
    struct Entry {
        int value;
        int frequency;
        std::list<int>::iterator position;
    };

public:
    explicit LFUCache(std::size_t capacity) : capacity_(capacity) {}

    bool get(int key, int& value) {
        auto it = entries_.find(key);
        if (it == entries_.end()) {
            return false;
        }
        value = it->second.value;
        touch(it);
        return true;
    }

    void put(int key, int value) {
        if (capacity_ == 0) {
            return;
        }

        auto it = entries_.find(key);
        if (it != entries_.end()) {
            it->second.value = value;
            touch(it);
            return;
        }

        if (entries_.size() == capacity_) {
            auto bucket = frequency_keys_.find(min_frequency_);
            const int victim = bucket->second.back();
            bucket->second.pop_back();
            if (bucket->second.empty()) {
                frequency_keys_.erase(bucket);
            }
            entries_.erase(victim);
        }

        min_frequency_ = 1;
        auto& keys = frequency_keys_[1];
        keys.push_front(key);
        entries_.emplace(
            key, Entry{value, 1, keys.begin()});
    }

private:
    using EntryIterator = std::unordered_map<int, Entry>::iterator;

    void touch(EntryIterator it) {
        Entry& entry = it->second;
        const int old_frequency = entry.frequency;
        auto bucket = frequency_keys_.find(old_frequency);
        bucket->second.erase(entry.position);

        if (bucket->second.empty()) {
            frequency_keys_.erase(bucket);
            if (min_frequency_ == old_frequency) {
                ++min_frequency_;
            }
        }

        ++entry.frequency;
        auto& new_bucket = frequency_keys_[entry.frequency];
        new_bucket.push_front(it->first);
        entry.position = new_bucket.begin();
    }

    std::size_t capacity_;
    int min_frequency_ = 0;
    std::unordered_map<int, Entry> entries_;
    std::unordered_map<int, std::list<int>> frequency_keys_;
};
```

每个频次链表的头部表示该频次下最近访问的 key，尾部表示最久未访问的 key。淘汰时从最小频次链表尾部删除。

## 3. 状态变化

一次命中会执行：

```text
从旧 frequency 链表删除 key
-> 如果旧链表为空，必要时更新 min_frequency
-> frequency 加一
-> 插入新 frequency 链表头部
```

插入新 key 时频次为 1，因此 `min_frequency` 必须重置为 1。

## 4. 复杂度和注意点

- 哈希表平均查找 `O(1)`；
- 已知迭代器后，链表删除和头插都是 `O(1)`；
- `get`、更新和淘汰的平均复杂度都是 `O(1)`；
- 频次可能长期增长，生产版本可做衰减或重新归一化；
- 当前版本不是线程安全的；
- `unordered_map` 分配失败时的强异常保证未完整处理。

## 5. 面试口述版

LFU 需要两层索引：第一张哈希表根据 key 找到值、频次和链表位置；第二张哈希表根据频次找到同频 key 的 LRU 链表；再维护全局最小频次。访问时把 key 从频次 `f` 移到 `f+1` 的链表头，淘汰时删除最小频次链表尾部，因此平均 `get` 和 `put` 都能做到 `O(1)`。
