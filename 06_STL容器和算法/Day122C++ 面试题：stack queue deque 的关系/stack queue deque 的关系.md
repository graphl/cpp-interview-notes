# C++ 面试题：stack queue deque 的关系

## 1. 核心结论

`stack` 和 `queue` 是容器适配器，不是独立的底层容器。

它们默认底层容器通常是 `deque`。

---

## 2. stack

`stack` 是后进先出。

```cpp
std::stack<int> st;
st.push(1);
st.push(2);
st.top();  // 2
st.pop();
```

常用操作：

| 操作 | 含义 |
|---|---|
| `push` | 入栈 |
| `pop` | 出栈 |
| `top` | 访问栈顶 |

---

## 3. queue

`queue` 是先进先出。

```cpp
std::queue<int> q;
q.push(1);
q.push(2);
q.front();  // 1
q.pop();
```

---

## 4. deque

`deque` 是双端队列，可以直接操作头尾。

```cpp
std::deque<int> dq;
dq.push_front(1);
dq.push_back(2);
dq.pop_front();
dq.pop_back();
```

---

## 5. 面试回答

`stack`、`queue` 是容器适配器，它们封装底层容器，只暴露特定接口。`stack` 默认用 `deque` 实现后进先出，`queue` 默认用 `deque` 实现先进先出。`deque` 本身是双端队列，支持头尾高效插入删除。
