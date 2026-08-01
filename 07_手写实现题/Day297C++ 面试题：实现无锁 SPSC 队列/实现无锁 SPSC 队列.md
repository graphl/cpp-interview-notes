# C++ 面试题：实现无锁 SPSC 队列

## 1. 考点

SPSC（Single Producer Single Consumer）队列只允许一个生产者线程和一个消费者线程。这个约束让环形队列可以不使用互斥锁。

面试主要考：

1. 原子变量
2. acquire/release 内存序
3. 环形数组
4. 缓存行竞争
5. 无锁算法的适用边界

---

## 2. 固定容量实现

下面预留一个槽位区分空和满，因此有效容量是 `Capacity - 1`。

```cpp
#include <array>
#include <atomic>
#include <cstddef>
#include <optional>
#include <utility>

template <typename T, size_t Capacity>
class SpscQueue {
    static_assert(Capacity >= 2, "Capacity must be at least 2");

public:
    bool push(T value) {
        const size_t tail = tail_.load(std::memory_order_relaxed);
        const size_t next = increment(tail);

        if (next == head_.load(std::memory_order_acquire)) {
            return false; // 满
        }

        buffer_[tail].emplace(std::move(value));
        tail_.store(next, std::memory_order_release);
        return true;
    }

    bool pop(T& value) {
        const size_t head = head_.load(std::memory_order_relaxed);

        if (head == tail_.load(std::memory_order_acquire)) {
            return false; // 空
        }

        value = std::move(*buffer_[head]);
        buffer_[head].reset();
        head_.store(increment(head), std::memory_order_release);
        return true;
    }

    static constexpr size_t capacity() noexcept {
        return Capacity - 1;
    }

private:
    static constexpr size_t increment(size_t index) noexcept {
        return (index + 1) % Capacity;
    }

    std::array<std::optional<T>, Capacity> buffer_{};
    alignas(64) std::atomic<size_t> head_{0}; // 主要由消费者写
    alignas(64) std::atomic<size_t> tail_{0}; // 主要由生产者写
};            若59
```

---

## 3. 内存序为什么这样写？

生产者先构造 `buffer_[tail]`，再用 release 发布新 `tail`；消费者用 acquire 看到新 `tail` 后，也必须看到此前完成的元素构造。

消费者先读取并销毁元素，再用 release 发布新 `head`；生产者 acquire 读取 `head` 后，才可以安全复用该槽位。

每个线程读取自己负责写的下标时可以用 relaxed，因为不需要借此同步另一个线程的数据。

---

## 4. 为什么它不是通用无锁队列？

这个实现依赖：

1. 只有一个线程调用 `push`
2. 只有一个线程调用 `pop`
3. 队列销毁前生产者和消费者都已停止

多个生产者可能同时占用同一尾槽，多个消费者也可能重复取同一元素。MPMC 队列需要 CAS、每槽序号或链式节点回收机制，不能直接套用本实现。

---

## 5. 性能和注意点

1. `push`、`pop` 是 O(1)，操作不会阻塞
2. 失败时立即返回，调用方可重试、退避或丢弃
3. `alignas(64)` 用于降低头尾下标之间的伪共享，但缓存行大小与平台相关
4. `optional` 简化对象生命周期管理，但极致性能实现常使用原始对齐存储
5. “无锁”不等于“没有同步”，原子操作和内存序仍不可缺少

---

## 6. 面试回答

SPSC 队列基于固定环形数组，生产者独占写尾下标，消费者独占写头下标，因此不需要 CAS 抢占位置。生产者构造元素后用 release 发布尾下标，消费者用 acquire 读取；消费者释放槽位后同样用 release 发布头下标。它读写 O(1) 且不阻塞，但只适用于单生产者、单消费者。
