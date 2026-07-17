# 一、future 生命周期总览

```
创建 shared state
        │
        ▼
future.valid() == true
        │
  ┌─────┴──────────┐
  │                │
wait / wait_for    get()
  │                │
  │          消费 shared state
  │                │
  └──────────► future.valid() == false
                        │
                        ▼
                   析构 future
```

------

# 二、阶段 1：创建（shared state 诞生）

future **只有在绑定 shared state 后才“活着”**。

### 创建方式

| 方式                         | 是否创建 shared state |
| ---------------------------- | --------------------- |
| `std::async`                 | ✅                     |
| `promise.get_future()`       | ✅                     |
| `packaged_task.get_future()` | ✅                     |
| 默认构造 `std::future`       | ❌                     |

```
std::future<int> f;        // 无状态
auto f2 = std::async(...); // 有状态
```
