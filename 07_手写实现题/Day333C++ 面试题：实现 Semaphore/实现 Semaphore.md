# C++ 面试题：实现计数信号量

## 1. 它与互斥锁有什么不同

互斥锁表达“同一时刻只允许一个所有者”，计数信号量表达“还有多少份资源可用”。初始化计数为 `N`，最多可以有 `N` 个线程同时成功获取资源。

C++20 提供 `std::counting_semaphore`。下面实现的是可在更早标准中使用的互斥锁加条件变量教学版。

## 2. 带关闭语义的实现

```cpp
#include <condition_variable>
#include <cstddef>
#include <limits>
#include <mutex>
#include <stdexcept>

class CountingSemaphore {
public:
    explicit CountingSemaphore(std::size_t initial = 0)
        : count_(initial) {}

    CountingSemaphore(const CountingSemaphore&) = delete;
    CountingSemaphore& operator=(const CountingSemaphore&) = delete;

    bool acquire() {
        std::unique_lock<std::mutex> lock(mutex_);
        condition_.wait(lock, [this] {
            return closed_ || count_ > 0;
        });

        if (count_ == 0) {
            return false;
        }
        --count_;
        return true;
    }

    bool try_acquire() {
        std::lock_guard<std::mutex> lock(mutex_);
        if (count_ == 0) {
            return false;
        }
        --count_;
        return true;
    }

    bool release(std::size_t permits = 1) {
        if (permits == 0) {
            return true;
        }

        {
            std::lock_guard<std::mutex> lock(mutex_);
            if (closed_) {
                return false;
            }
            if (permits >
                std::numeric_limits<std::size_t>::max() - count_) {
                throw std::overflow_error("semaphore overflow");
            }
            count_ += permits;
        }

        if (permits == 1) {
            condition_.notify_one();
        } else {
            condition_.notify_all();
        }
        return true;
    }

    void close() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            closed_ = true;
        }
        condition_.notify_all();
    }

private:
    std::mutex mutex_;
    std::condition_variable condition_;
    std::size_t count_ = 0;
    bool closed_ = false;
};
```

## 3. 关闭协议

`close()` 后：

1. 已经存在的许可仍可被获取。
2. 许可耗尽后，`acquire()` 返回 `false`。
3. 所有正在等待的线程都会被唤醒。
4. `release()` 不再接受新许可。

这种语义适合线程池、连接池和有界队列退出。工程代码也可以选择“关闭后立即拒绝获取”，但必须把协议写清楚。

## 4. 为什么 wait 必须使用谓词

条件变量允许虚假唤醒，而且多个线程被唤醒后会重新竞争互斥锁。谓词必须在锁保护下重新检查 `closed_ || count_ > 0`，不能假设被唤醒就一定有资源。

## 5. 复杂度和边界

1. 获取和释放的共享状态修改是 `O(1)`。
2. 线程等待和唤醒由操作系统调度，不能承诺严格 FIFO。
3. `notify_all()` 可能产生惊群；一次释放一个许可时使用 `notify_one()`。
4. 析构前必须确保没有线程仍在调用对象。
5. 标准 `counting_semaphore` 没有这里的 `close()` 接口。

## 6. 面试口述版

计数信号量维护一个受互斥锁保护的资源计数。获取时等待计数大于零，再把计数减一；释放时增加计数并唤醒等待者。条件变量必须使用谓词处理虚假唤醒。工程实现还要定义关闭、溢出、公平性以及对象析构前如何停止等待线程。
