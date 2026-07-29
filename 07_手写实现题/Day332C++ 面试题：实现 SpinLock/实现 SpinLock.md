# C++ 面试题：实现 SpinLock

## 1. 自旋锁解决什么问题

自旋锁获取失败时不睡眠，而是在用户态反复尝试。它适合临界区非常短、竞争较轻，并且线程不会长时间被抢占的场景。

如果临界区较长，自旋会持续占用 CPU，此时互斥锁通常更合适。

## 2. C++11 最小实现

```cpp
#include <atomic>
#include <thread>

class SpinLock {
public:
    SpinLock() noexcept = default;
    SpinLock(const SpinLock&) = delete;
    SpinLock& operator=(const SpinLock&) = delete;

    void lock() noexcept {
        unsigned int attempts = 0;

        while (flag_.test_and_set(std::memory_order_acquire)) {
            ++attempts;
            if (attempts >= 64) {
                attempts = 0;
                std::this_thread::yield();
            }
        }
    }

    bool try_lock() noexcept {
        return !flag_.test_and_set(std::memory_order_acquire);
    }

    void unlock() noexcept {
        flag_.clear(std::memory_order_release);
    }

private:
    std::atomic_flag flag_ = ATOMIC_FLAG_INIT;
};
```

它满足 `BasicLockable` 的接口要求，因此可以交给 `std::lock_guard<SpinLock>` 管理，避免异常或提前返回时忘记解锁。

## 3. 为什么使用 acquire/release

成功加锁的 acquire 保证当前线程能看到前一个持锁线程在解锁前完成的写入；解锁的 release 把临界区中的写入发布给下一个成功加锁的线程。

失败的 `test_and_set` 仍然会产生写竞争。C++20 可以先用 `atomic_flag::test(relaxed)` 只读观察，减少缓存行反复失效；C++11 版本没有这个接口。

## 4. 工程边界

1. 该实现不保证公平，某个线程可能长期饥饿。
2. `yield()` 只是调度提示，不是严格的退避策略。
3. 持锁线程被抢占时，其他线程会空耗 CPU。
4. 不能在持锁期间执行阻塞 IO、长循环或未知耗时回调。
5. 信号处理、中断上下文和内核自旋锁还有额外约束，不能直接套用这个用户态实现。

## 5. 面试口述版

用 `atomic_flag::test_and_set(acquire)` 竞争锁，返回 `false` 的线程成功获得所有权；解锁时用 `clear(release)`。自旋避免了短临界区中的睡眠和唤醒开销，但竞争激烈或持锁时间长时会浪费 CPU，而且简单实现没有公平性保证。
