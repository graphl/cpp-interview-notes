# C++ 面试题：实现 LRU Cache

## 1. 考点

LRU 是 Least Recently Used，最近最少使用缓存。

要求：

1. `get` 时间复杂度 O(1)
2. `put` 时间复杂度 O(1)
3. 最近访问的数据移动到头部
4. 容量满时淘汰尾部数据

---

## 2. 数据结构选择

使用：

1. `std::list` 保存访问顺序
2. `std::unordered_map` 快速定位节点

链表头部表示最近使用，尾部表示最久未使用。

---

## 3. 实现

```cpp
#include <list>
#include <unordered_map>

class LRUCache {
public:
    explicit LRUCache(int capacity) : capacity_(capacity) {}

    int get(int key) {
        auto it = map_.find(key);
        if (it == map_.end()) {
            return -1;
        }

        cache_.splice(cache_.begin(), cache_, it->second);
        return it->second->second;
    }

    void put(int key, int value) {
        auto it = map_.find(key);
        if (it != map_.end()) {
            it->second->second = value;
            cache_.splice(cache_.begin(), cache_, it->second);
            return;
        }

        if (cache_.size() == capacity_) {
            int old_key = cache_.back().first;
            cache_.pop_back();
            map_.erase(old_key);
        }

        cache_.push_front({key, value});
        map_[key] = cache_.begin();
    }

private:
    int capacity_;
    std::list<std::pair<int, int>> cache_;
    std::unordered_map<int, std::list<std::pair<int, int>>::iterator> map_;
};
```

---

## 4. 为什么用 list？

`list` 支持 O(1) 删除和移动节点。

`splice` 可以把已有节点移动到链表头部，不需要重新分配节点。

---

## 5. 面试回答

LRU 通常用哈希表加双向链表实现。哈希表负责 O(1) 查找 key 对应的链表节点，双向链表负责维护访问顺序。每次访问或更新节点，都把节点移动到头部；容量满时删除尾部节点。
