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
    // 使用 position & (Capacity - 1) 代替取模，因此容量必须为 2 的幂。
    static_assert(Capacity >= 2,
                  "capacity must be at least 2");
    static_assert((Capacity & (Capacity - 1)) == 0,
                  "capacity must be a power of two");

    // 线程抢到槽位后不能再通过回滚把票号还回去，所以对象操作不能抛异常。
    static_assert(std::is_nothrow_move_constructible<T>::value,
                  "T must be nothrow move constructible");
    static_assert(std::is_nothrow_move_assignable<T>::value,
                  "T must be nothrow move assignable");
    static_assert(std::is_nothrow_destructible<T>::value,
                  "T must be nothrow destructible");

    struct Cell {
        // 槽位序号同时表示：
        // 1. 该槽位属于环形数组的第几轮；
        // 2. 当前是可写、可读，还是仍被另一侧占用。
        std::atomic<std::size_t> sequence;

        // 只预留 T 所需的大小和对齐，不自动构造 T。
        // 生产者抢到槽位后 placement new，消费者读取后手动析构。
        typename std::aligned_storage<
            sizeof(T), alignof(T)>::type storage;
    };

public:
    BoundedMPMCQueue() noexcept {
        for (std::size_t i = 0; i < Capacity; ++i) {
            // 初始逻辑位置 i 对应的槽位可由生产者写入。
            // relaxed 足够：构造完成后队列还没有发布给其他线程。
            cells_[i].sequence.store(
                i, std::memory_order_relaxed);
        }
    }

    // 队列包含原子状态和原始存储，不允许复制。
    BoundedMPMCQueue(const BoundedMPMCQueue&) = delete;
    BoundedMPMCQueue& operator=(
        const BoundedMPMCQueue&) = delete;

    ~BoundedMPMCQueue() {
        // 教学版要求销毁前停止所有线程并排空队列。
        // 两个位置相等只用于检查调用约定；析构本身不负责并发清理。
        assert(enqueue_position_.load(
                   std::memory_order_relaxed) ==
               dequeue_position_.load(
                   std::memory_order_relaxed));
    }

    bool try_enqueue(T value) noexcept {
        // 最终由 CAS 成功的线程独占该 cell。
        Cell* cell = nullptr;

        // enqueue_position_ 是生产者的全局“取票号”位置。
        std::size_t position =
            enqueue_position_.load(std::memory_order_relaxed);

        for (;;) {
            // Capacity 为 2 的幂时，按位与等价于 position % Capacity。
            cell = &cells_[position & mask_];

            // acquire 与消费者释放槽位时的 release 配对：
            // 看到可写序号后，才能安全地在 storage 中构造下一轮对象。
            const std::size_t sequence =
                cell->sequence.load(std::memory_order_acquire);

            // 对生产者而言：
            // difference == 0：该槽位正好属于当前 position，可以竞争。
            // difference < 0：槽位仍停留在旧状态，消费者尚未释放。
            // difference > 0：其他生产者已推进位置，应刷新票号重试。
            const std::intptr_t difference =
                static_cast<std::intptr_t>(sequence) -
                static_cast<std::intptr_t>(position);

            if (difference == 0) {
                // 抢占 [position, position + 1) 这张生产票。
                // compare_exchange_weak 允许伪失败，因此放在循环中使用。
                // 失败时，position 会被自动改写为当前真实值，直接用于下轮重试。
                if (enqueue_position_.compare_exchange_weak(
                        position, position + 1,
                        // 全局位置只负责分配唯一票号，不负责发布 T。
                        std::memory_order_relaxed,
                        std::memory_order_relaxed)) {
                    break;
                }
            } else if (difference < 0) {
                // 当前逻辑位置对应的槽位仍未被消费者归还，队列已满。
                return false;
            } else {
                // 当前 position 已过期，重新读取最新生产位置。
                position = enqueue_position_.load(
                    std::memory_order_relaxed);
            }
        }

        // 此时当前线程独占 cell，在原始存储上构造 T。
        new (&cell->storage) T(std::move(value));

        // position + 1 表示对象已经构造完成，可由对应消费者读取。
        // release 保证 T 的构造写入先于消费者看到这个序号。
        cell->sequence.store(
            position + 1, std::memory_order_release);
        return true;
    }

    bool try_dequeue(T& output) noexcept {
        // 最终由 CAS 成功的线程独占该 cell 中的对象。
        Cell* cell = nullptr;

        // dequeue_position_ 是消费者的全局“取票号”位置。
        std::size_t position =
            dequeue_position_.load(std::memory_order_relaxed);

        for (;;) {
            cell = &cells_[position & mask_];

            // acquire 与生产者发布对象时的 release 配对：
            // 看到可读序号后，才能读取完整构造的 T。
            const std::size_t sequence =
                cell->sequence.load(std::memory_order_acquire);

            // 生产者写完 position 对应对象后会把序号设为 position + 1，
            // 因此消费者以 position + 1 作为期望值。
            const std::intptr_t difference =
                static_cast<std::intptr_t>(sequence) -
                static_cast<std::intptr_t>(position + 1);

            if (difference == 0) {
                // 抢占 [position, position + 1) 这张消费票。
                // CAS 失败时 position 同样会被更新为当前真实值。
                if (dequeue_position_.compare_exchange_weak(
                        position, position + 1,
                        // 消费位置只负责分票，对象可见性由 sequence 保证。
                        std::memory_order_relaxed,
                        std::memory_order_relaxed)) {
                    break;
                }
            } else if (difference < 0) {
                // 生产者还没有发布当前逻辑位置对应的对象，队列为空。
                return false;
            } else {
                // 其他消费者已推进位置，刷新消费票号后继续竞争。
                position = dequeue_position_.load(
                    std::memory_order_relaxed);
            }
        }

        // storage 中的 T 已经由生产者构造，可把原始地址解释为 T*。
        T* value = reinterpret_cast<T*>(&cell->storage);

        // 把元素移交给调用方，然后显式结束槽位内对象的生命周期。
        output = std::move(*value);
        value->~T();

        // position + Capacity 表示该物理槽位已交给下一轮生产者。
        // release 保证析构完成先于下一轮生产者复用 storage。
        cell->sequence.store(
            position + Capacity, std::memory_order_release);
        return true;
    }

    bool position_atomics_are_lock_free() const noexcept {
        // C++ 只保证 atomic 接口语义，不保证所有平台都用无锁指令实现。
        return enqueue_position_.is_lock_free() &&
               dequeue_position_.is_lock_free();
    }

private:
    // Capacity 为 2 的幂，因此 mask_ 可用于快速映射物理槽位。
    static constexpr std::size_t mask_ = Capacity - 1;

    // 固定容量的物理槽位；逻辑 position 会不断递增并循环映射到这里。
    std::array<Cell, Capacity> cells_;

    // 生产者和消费者分别竞争不同的全局位置。
    // 分开对齐用于降低两个热点原子落入同一缓存行造成的伪共享概率。
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

### 容量为 4 的具体例子

假设 `Capacity = 4`，初始状态如下：

```text
物理槽位 index       0    1    2    3
初始 sequence        0    1    2    3
首次生产 position    0    1    2    3
```

以物理槽位 `cell[0]` 为例，它会依次服务逻辑位置 `0`、`4`、`8` 等生产者。

#### 第一轮：生产者写入位置 0

```text
position   = 0
index      = position & (Capacity - 1) = 0
sequence   = 0
difference = sequence - position = 0
```

`difference == 0`，表示 `cell[0]` 正在等待位置 0 的生产者，可以写入。生产者构造对象后发布：

```text
cell[0].sequence = position + 1 = 1
```

此时 `sequence == position + 1`，表示对象已经构造完成，位置 0 的消费者可以读取。

#### 消费者读取位置 0

消费者期望：

```text
sequence == position + 1
sequence == 1
```

读取并析构对象后，消费者归还槽位：

```text
cell[0].sequence = position + Capacity
                 = 0 + 4
                 = 4
```

`sequence == 4` 表示第一轮已经结束，`cell[0]` 可以交给逻辑位置 4 的生产者。

#### 第二轮：生产者写入位置 4

```text
position   = 4
index      = 4 & 3 = 0
sequence   = 4
difference = sequence - position = 0
```

生产者再次写入 `cell[0]`，完成后发布：

```text
cell[0].sequence = position + 1 = 5
```

位置 4 的消费者读取完成后再写入：

```text
cell[0].sequence = position + Capacity
                 = 4 + 4
                 = 8
```

因此 `cell[0]` 的完整序号变化为：

```text
sequence = 0  -> 位置 0 的生产者可写
sequence = 1  -> 位置 0 的消费者可读
sequence = 4  -> 位置 4 的生产者可写
sequence = 5  -> 位置 4 的消费者可读
sequence = 8  -> 位置 8 的生产者可写
```

再看队列已满的情况。假设四个槽位都已经写入，但消费者还没有读取：

```text
enqueue_position = 4

物理槽位 index    0    1    2    3
sequence          1    2    3    4
```

新生产者的 `position = 4`，它映射到 `cell[0]`，但该槽位仍为：

```text
sequence   = 1
position   = 4
difference = 1 - 4 = -3
```

`difference < 0` 表示 `cell[0]` 还停留在上一轮的“可读”状态，消费者尚未将它更新为 4，因此生产者不能覆盖旧对象，队列当前视图下已满。

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
