

## `unique_lock` 的成员函数（必会）

### 🔹 1. `lock()`

```
lock.lock();   // 阻塞
```

------

### 🔹 2. `try_lock()`

```
if (lock.try_lock()) {
    // success
}
```

------

### 🔹 3. `try_lock_for() / try_lock_until()`

```
lock.try_lock_for(5ms);
lock.try_lock_until(tp);
```

（仅当 mutex 支持 timed）

🔹 4. release



```
std::unique_lock<std::mutex> lock(mtx);
// 临界区
do_work();
// 放弃管理权（但还锁着）
std::mutex* pm = lock.release();
// ⚠️ 必须手动 unlock
pm->unlock();
```

