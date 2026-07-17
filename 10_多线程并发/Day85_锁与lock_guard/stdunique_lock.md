# std::unique_lock

| unique_lock 构造方式          | 需要 mutex 支持  |
| ----------------------------- | ---------------- |
| `unique_lock(m)`              | lock             |
| `unique_lock(m, defer_lock)`  | 无               |
| `unique_lock(m, try_to_lock)` | try_lock         |
| `unique_lock(m, adopt_lock)`  | 无               |
| `unique_lock(m, time_point)`  | ⭐ try_lock_until |
| `unique_lock(m, duration)`    | ⭐ try_lock_for   |


