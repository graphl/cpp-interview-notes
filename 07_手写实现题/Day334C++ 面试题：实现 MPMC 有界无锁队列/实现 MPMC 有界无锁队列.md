# C++ 面试题：实现 MPMC 有界无锁队列

## 1. 为什么 SPSC 实现不能直接扩展

SPSC 中只有一个生产者修改尾位置、一个消费者修改头位置，不需要竞争槽位。MPMC 允许多个生产者和多个消费者并发操作，因此必须解决：

1. 多个生产者如何唯一占有一个写位置。
2. 多个消费者如何唯一占有一个读位置。
3. 环形槽位绕回后，如何区分“本轮可用”和“上一轮尚未消费”。

下面使用“全局位置 CAS + 每槽序号”的经典有界环形队列方案。

## 2. C++11 教学实现

```cpp
#include <array>
#include <atomic>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <new>
#include <type_traits>
#include <utility>

template <typename T, std::size_t Capacity>
class BoundedMPMCQueue {
    static_assert(Capacity >= 2,
                  "capacity must be at least 2");
    static_assert((Capacity & (Capacity - 1)) == 0,
                  "capacity must be a power of two");
    static_assert(std::is_nothrow_move_constructible<T>::value,
                  "T must be nothrow move constructible");
    static_assert(std::is_nothrow_move_assignable<T>::value,
                  "T must be nothrow move assignable");
    static_assert(std::is_nothrow_destructible<T>::value,
                  "T must be nothrow destructible");

    struct Cell {
        std::atomic<std::size_t> sequence;
        typename std::aligned_storage<
            sizeof(T), alignof(T)>::type storage;
    };

public:
    BoundedMPMCQueue() noexcept {
        for (std::size_t i = 0; i < Capacity; ++i) {
            cells_[i].sequence.store(
                i, std::memory_order_relaxed);
        }
    }

    BoundedMPMCQueue(const BoundedMPMCQueue&) = delete;
    BoundedMPMCQueue& operator=(
        const BoundedMPMCQueue&) = delete;

    ~BoundedMPMCQueue() {
        // 教学版要求销毁前停止所有线程并排空队列。
        assert(enqueue_position_.load(
                   std::memory_order_relaxed) ==
               dequeue_position_.load(
                   std::memory_order_relaxed));
    }

    bool try_enqueue(T value) noexcept {
        Cell* cell = nullptr;
        std::size_t position =
            enqueue_position_.load(std::memory_order_relaxed);

        for (;;) {
            cell = &cells_[position & mask_];
            const std::size_t sequence =
                cell->sequence.load(std::memory_order_acquire);
            const std::intptr_t difference =
                static_cast<std::intptr_t>(sequence) -
                static_cast<std::intptr_t>(position);

            if (difference == 0) {
                if (enqueue_position_.compare_exchange_weak(
                        position, position + 1,
                        std::memory_order_relaxed,
                        std::memory_order_relaxed)) {
                    break;
                }
            } else if (difference < 0) {
                return false;
            } else {
                position = enqueue_position_.load(
                    std::memory_order_relaxed);
            }
        }

        new (&cell->storage) T(std::move(value));
        cell->sequence.store(
            position + 1, std::memory_order_release);
        return true;
    }

    bool try_dequeue(T& output) noexcept {
        Cell* cell = nullptr;
        std::size_t position =
            dequeue_position_.load(std::memory_order_relaxed);

        for (;;) {
            cell = &cells_[position & mask_];
            const std::size_t sequence =
                cell->sequence.load(std::memory_order_acquire);
            const std::intptr_t difference =
                static_cast<std::intptr_t>(sequence) -
                static_cast<std::intptr_t>(position + 1);

            if (difference == 0) {
                if (dequeue_position_.compare_exchange_weak(
                        position, position + 1,
                        std::memory_order_relaxed,
                        std::memory_order_relaxed)) {
                    break;
                }
            } else if (difference < 0) {
                return false;
            } else {
                position = dequeue_position_.load(
                    std::memory_order_relaxed);
            }
        }

        T* value = reinterpret_cast<T*>(&cell->storage);
        output = std::move(*value);
        value->~T();

        cell->sequence.store(
            position + Capacity, std::memory_order_release);
        return true;
    }

    bool position_atomics_are_lock_free() const noexcept {
        return enqueue_position_.is_lock_free() &&
               dequeue_position_.is_lock_free();
    }

private:
    static constexpr std::size_t mask_ = Capacity - 1;

    std::array<Cell, Capacity> cells_;

    alignas(64) std::atomic<std::size_t>
        enqueue_position_{0};
    alignas(64) std::atomic<std::size_t>
        dequeue_position_{0};
};
```

## 3. 每槽序号如何区分状态

假设生产者要处理逻辑位置 `position`：

```text
sequence == position
-> 槽位属于当前生产轮次，可以写

sequence < position
-> 消费者还没有释放该槽，队列可能已满

写入完成后 sequence = position + 1
-> 发布给消费者
```

消费者读取完成后写入 `position + Capacity`，把槽位交给环形数组的下一轮生产者。序号同时承担“轮次”和“发布状态”的作用。

## 4. 内存序

1. 生产者构造对象后，用 release 发布 `sequence`。
2. 消费者用 acquire 观察该序号，从而看见完整对象。
3. 消费者析构对象后，用 release 发布槽位可复用状态。
4. 下一轮生产者用 acquire 观察该状态，确认旧对象生命周期已经结束。
5. 全局位置只用于分配唯一票号，不承担对象发布，因此 CAS 可以使用 relaxed。

## 5. lock-free 不等于 wait-free

竞争线程可能反复 CAS 失败，因此单个线程不能保证在有限步内完成；该算法不是 wait-free。

另外，C++ 的 `std::atomic<std::size_t>` 是否真正 lock-free 取决于平台。只有相关原子类型在目标平台无锁时，才能把整体称为底层无锁实现。

## 6. 教学实现的约束

1. 容量固定且必须是 2 的幂，不能动态扩容。
2. 队列满或空时立即返回，不负责阻塞、重试或退避。
3. 为避免占有槽位后抛异常，本实现要求 `T` 的移动构造、移动赋值和析构均为 `noexcept`。
4. `try_dequeue(T&)` 要求调用方提供可移动赋值的对象。
5. 析构前必须停止生产者和消费者，并排空队列。
6. `alignas(64)` 只是常见的伪共享优化，缓存行大小与平台相关。
7. 极端长时间运行时还要分析无符号位置计数回绕；生产代码应结合目标位宽和生命周期验证。

## 7. 与链式 MPMC 的区别

该队列是固定容量数组，槽位不会被释放给内存分配器，因此不需要 Hazard Pointer 来保护节点地址。链式无锁队列会动态删除节点，必须额外解决“线程仍在读取、另一个线程已经释放节点”的安全回收问题。

## 8. 面试口述版

MPMC 有界队列用两个原子位置给生产者和消费者分配唯一票号，再用每个槽位的序号表示它属于哪一轮以及当前可写还是可读。对象写完和析构完都通过 release 发布状态，另一侧用 acquire 获取。CAS 只负责抢位置，可以用 relaxed。算法在支持无锁原子的目标平台上是 lock-free，但不是 wait-free，并且非平凡对象需要明确异常和析构约束。
