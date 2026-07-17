# C++ 面试题：自定义 unordered_map 的 hash 函数

## 1. 核心结论

`unordered_map` 的 key 如果是自定义类型，需要提供：

1. 哈希函数
2. 相等比较函数

---

## 2. 自定义结构体作为 key

```cpp
#include <unordered_map>

struct Point {
    int x;
    int y;

    bool operator==(const Point& other) const {
        return x == other.x && y == other.y;
    }
};

struct PointHash {
    size_t operator()(const Point& p) const {
        return std::hash<int>()(p.x) ^ (std::hash<int>()(p.y) << 1);
    }
};

int main() {
    std::unordered_map<Point, int, PointHash> mp;
    mp[{1, 2}] = 10;
}
```

---

## 3. 自定义 pair 的 hash

```cpp
struct PairHash {
    size_t operator()(const std::pair<int, int>& p) const {
        return std::hash<int>()(p.first) ^
               (std::hash<int>()(p.second) << 1);
    }
};

std::unordered_map<std::pair<int, int>, int, PairHash> mp;
```

---

## 4. 注意点

哈希函数必须满足：

如果两个 key 相等，那么它们的 hash 值必须相等。

```text
a == b  =>  hash(a) == hash(b)
```

反过来不要求成立。

---

## 5. 面试回答

自定义 `unordered_map` 的 key 时，需要提供哈希函数和相等比较。哈希函数通常写成函数对象，重载 `operator()`，然后作为 `unordered_map` 的第三个模板参数传入。同时 key 类型需要支持 `==`，用于哈希冲突时判断两个 key 是否真正相等。
