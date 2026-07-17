# C++ 面试题：erase-remove 惯用法

## 1. 核心结论

`std::remove` 不会真正删除容器元素，只是把不需要删除的元素移动到前面。

真正缩小容器需要配合 `erase`。

---

## 2. 删除 vector 中的指定元素

```cpp
#include <algorithm>
#include <vector>

std::vector<int> v = {1, 2, 3, 2, 4};

v.erase(std::remove(v.begin(), v.end(), 2), v.end());
```

结果：

```text
1 3 4
```

---

## 3. remove 做了什么？

```cpp
auto new_end = std::remove(v.begin(), v.end(), 2);
```

它返回新的逻辑结尾。

`new_end` 后面的元素仍然存在，只是值未定义为有意义内容。

---

## 4. 条件删除

```cpp
v.erase(std::remove_if(v.begin(), v.end(), [](int x) {
    return x % 2 == 0;
}), v.end());
```

---

## 5. 面试回答

`remove` 是算法，不知道容器本身，所以不能真正删除元素。它只是把不删除的元素往前移动，并返回新的逻辑结尾。要真正改变容器大小，需要再调用容器的 `erase`，这就是 erase-remove 惯用法。
