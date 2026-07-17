## C++ 标准库里的 RAII 锁家族（重点表）

| RAII 锁                    | 对应 mutex          | 特点           |
| -------------------------- | ------------------- | -------------- |
| `std::lock_guard`          | mutex               | 最轻量，最常用 |
| `std::unique_lock`         | mutex / timed_mutex | 最灵活         |
| `std::shared_lock`         | shared_mutex        | 读锁           |
| `std::scoped_lock` (C++17) | 多 mutex            | 防死锁         |

#  std::lock_guard

## 一、什么是 RAII 锁？（一句话）

> **构造函数加锁，析构函数解锁**

```
{
    std::lock_guard<std::mutex> lock(mtx);
    // 临界区
} // 离开作用域 → 自动 unlock
```

