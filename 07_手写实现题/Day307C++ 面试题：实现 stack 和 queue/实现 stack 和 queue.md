# C++ 面试题：实现 stack 和 queue

## 1. 它们为什么叫容器适配器

`stack` 和 `queue` 通常不直接管理底层存储，而是限制另一个顺序容器的接口：

```text
stack：只暴露后端的 push_back、pop_back、back
queue：暴露后端的 push_back、pop_front、front、back
```

## 2. 最小实现

```cpp
#include <cassert>
#include <cstddef>
#include <deque>
#include <utility>

template <typename T, typename Container = std::deque<T>>
class Stack {
public:
    void push(T value) {
        container_.push_back(std::move(value));
    }

    void pop() {
        assert(!empty());
        container_.pop_back();
    }

    T& top() {
        assert(!empty());
        return container_.back();
    }

    bool empty() const noexcept { return container_.empty(); }
    std::size_t size() const noexcept { return container_.size(); }

private:
    Container container_;
};

template <typename T, typename Container = std::deque<T>>
class Queue {
public:
    void push(T value) {
        container_.push_back(std::move(value));
    }

    void pop() {
        assert(!empty());
        container_.pop_front();
    }

    T& front() {
        assert(!empty());
        return container_.front();
    }

    T& back() {
        assert(!empty());
        return container_.back();
    }

    bool empty() const noexcept { return container_.empty(); }
    std::size_t size() const noexcept { return container_.size(); }

private:
    Container container_;
};
```

## 3. 为什么 queue 默认不使用 vector

普通 vector 的 `pop_front()` 需要把后续元素整体前移，为 `O(n)`；deque 的头尾插入删除通常为摊销 `O(1)`。stack 只操作尾部，可以使用 vector、deque 等支持 `back/push_back/pop_back` 的容器。

## 4. 面试口述版

stack 和 queue 是容器适配器，不负责规定具体存储结构，而是在底层容器上限制接口。stack 只操作同一端，queue 从尾部加入、头部移除。底层容器必须提供适配器所需操作及对应复杂度，因此 queue 通常默认使用 deque 而不是 vector。
