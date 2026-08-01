# C++ 面试题：实现简化版 malloc 和 free

## 1. 这道题真正考什么

`malloc` 管理的是一段没有对象类型的原始字节存储。一个最小教学实现需要回答：空闲块放在哪里、如何满足对齐、怎样切分大块、释放后怎样合并相邻块。

真实分配器还会向操作系统申请页、维护多个大小级别、处理多线程和安全加固。下面只在固定缓冲区上演示核心数据结构。

## 2. 内存布局

```text
Block 头部                       返回给调用者的区域
+-----------------------------+-----------------------+
| size | free | prev | next   | aligned payload ...   |
+-----------------------------+-----------------------+
^
块的起始地址
```

所有块按物理地址组成双向链表。这样释放一个块后，可以直接检查前后物理相邻块并合并。

## 3. 教学实现

```cpp
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <new>

template <std::size_t Capacity>
class FixedArena {
private:
    struct Block {
        std::size_t size; // payload 可用字节数
        bool free;
        Block* prev;
        Block* next;
    };

    static constexpr std::size_t kAlign = alignof(std::max_align_t);

    static constexpr std::size_t align_up(std::size_t n) {
        return (n + kAlign - 1) / kAlign * kAlign;
    }

    static constexpr std::size_t kHeaderSize = align_up(sizeof(Block));

public:
    FixedArena() {
        static_assert(Capacity > kHeaderSize, "arena is too small");

        // 在固定缓冲区开头建立第一个 Block 对象。
        head_ = ::new (static_cast<void*>(storage_))
            Block{Capacity - kHeaderSize, true, nullptr, nullptr};
    }

    void* allocate(std::size_t bytes) {
        if (bytes == 0) {
            return nullptr;
        }

        const std::size_t required = align_up(bytes);

        // first-fit：找到第一个足够大的空闲块。
        for (Block* block = head_; block; block = block->next) {
            if (!block->free || block->size < required) {
                continue;
            }

            split_if_needed(block, required);
            block->free = false;
            return payload(block);
        }

        return nullptr;
    }

    void deallocate(void* ptr) {
        if (!ptr) {
            return;
        }

        // 教学版约定 ptr 必须由当前 arena 返回，且不能重复释放。
        Block* block = header(ptr);
        assert(!block->free);
        block->free = true;

        // 先向后合并，再尝试并入前一个空闲块。
        merge_with_next(block);
        if (block->prev && block->prev->free) {
            merge_with_next(block->prev);
        }
    }

private:
    static void* payload(Block* block) {
        return reinterpret_cast<std::byte*>(block) + kHeaderSize;
    }

    static Block* header(void* ptr) {
        return reinterpret_cast<Block*>(
            static_cast<std::byte*>(ptr) - kHeaderSize);
    }

    static void split_if_needed(Block* block, std::size_t required) {
        // 剩余空间至少还能放下一个块头和一个对齐单位时才切分。
        if (block->size < required + kHeaderSize + kAlign) {
            return;
        }

        auto* new_address = static_cast<std::byte*>(payload(block)) + required;
        Block* rest = ::new (static_cast<void*>(new_address)) Block{
            block->size - required - kHeaderSize,
            true,
            block,
            block->next
        };

        if (rest->next) {
            rest->next->prev = rest;
        }
        block->next = rest;
        block->size = required;
    }

    static void merge_with_next(Block* block) {
        Block* next = block->next;
        if (!next || !next->free) {
            return;
        }

        block->size += kHeaderSize + next->size;
        block->next = next->next;
        if (block->next) {
            block->next->prev = block;
        }
    }

    alignas(std::max_align_t) std::byte storage_[Capacity];
    Block* head_ = nullptr;
};
```

## 4. 一次分配和释放的数据流

```text
allocate(24)
  -> 向上对齐 required
  -> 遍历空闲链表
  -> 大块切成“已用块 + 剩余空闲块”
  -> 返回块头之后的 payload

deallocate(ptr)
  -> ptr 向前找到块头
  -> 标记为空闲
  -> 与后块合并
  -> 再与前块合并
```

## 5. 复杂度和边界

- first-fit 查找最坏为 `O(n)`，`n` 是块数量。
- 合并相邻块为 `O(1)`，因为块头保存了前后指针。
- 该实现不是线程安全的，也不检查越界写、非法指针和重复释放。
- 固定 arena 耗尽后返回 `nullptr`，不会自动向操作系统申请新页。
- 块头本身和无法切分的小尾部都会产生额外空间成本。

## 6. 面试口述版

简化分配器可以在一段对齐的固定内存上维护物理有序的空闲块链表。分配时采用 first-fit 找到足够大的块，必要时切分；释放时通过 payload 前面的块头恢复元数据，并合并相邻空闲块减少外部碎片。真实 malloc 还要处理页申请、大小分级、多线程缓存和安全检查。
