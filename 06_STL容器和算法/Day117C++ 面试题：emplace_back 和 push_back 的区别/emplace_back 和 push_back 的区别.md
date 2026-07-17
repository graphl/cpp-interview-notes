# C++ 面试题：emplace_back 和 push_back 的区别

## 1. 核心结论

`push_back` 是把一个已经存在的对象放入容器。

`emplace_back` 是在容器尾部直接构造对象。

---

## 2. 示例

```cpp
#include <string>
#include <vector>

std::vector<std::string> v;

v.push_back(std::string("hello"));
v.emplace_back("world");
```

`emplace_back("world")` 可以直接用参数在容器内部构造 `std::string`。

---

## 3. 对比表

| 对比点 | `push_back` | `emplace_back` |
|---|---|---|
| 参数 | 对象 | 构造对象所需参数 |
| 构造位置 | 先构造临时对象，再放入容器 | 容器内部原地构造 |
| 可能开销 | 可能拷贝或移动 | 通常减少一次拷贝或移动 |
| 可读性 | 直观 | 需要理解构造参数 |

---

## 4. 注意点

`emplace_back` 不一定永远更快。

如果传入的本来就是同类型对象：

```cpp
std::string s = "hello";
v.emplace_back(s);
```

这仍然会拷贝。

---

## 5. 面试回答

`push_back` 接收一个已经构造好的对象，然后拷贝或移动进容器；`emplace_back` 接收构造参数，在容器内部原地构造对象，可能减少临时对象和拷贝移动开销。对于复杂对象，`emplace_back` 通常更高效，但不是任何场景都必然更快。
