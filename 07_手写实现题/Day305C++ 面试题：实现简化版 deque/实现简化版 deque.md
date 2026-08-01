# C++ 面试题：实现简化版 deque

## 1. deque 为什么不是一整块连续内存

`deque` 需要同时支持头尾扩展。如果像 vector 一样只有一整块连续内存，头部插入要搬移全部元素。常见实现使用“中央映射表 + 多个固定大小的数据块”：

```text
map
+----+----+----+----+
|  * |  * |  * |  * |
+--|-+--|-+--|-+--|-+
   v    v    v    v
 [block][block][block][block]
```

元素在单个 block 内连续，但整个 deque 不保证全局连续。随机访问先做除法找到 block，再取余找到块内位置。

## 2. 教学实现

下面用 `std::optional` 表示块内尚未构造或已经构造的元素，突出分段索引。为了缩短代码，中央映射表使用 vector；真实 deque 会在映射表两端预留空间，避免每次头部扩展都移动块指针。

```cpp
#include <array>
#include <cassert>
#include <cstddef>
#include <memory>
#include <optional>
#include <utility>
#include <vector>

template <typename T, std::size_t BlockSize = 8>
class SegmentedDeque {
private:
    using Block = std::array<std::optional<T>, BlockSize>;

public:
    SegmentedDeque() {
        static_assert(BlockSize > 0, "BlockSize must be positive");
        blocks_.push_back(std::make_unique<Block>());
        start_offset_ = BlockSize / 2;
    }

    void push_back(T value) {
        const auto [block, offset] = locate(size_);
        ensure_back_block(block);
        (*blocks_[block])[offset].emplace(std::move(value));
        ++size_;
    }

    void push_front(T value) {
        if (start_offset_ == 0) {
            if (start_block_ == 0) {
                // 教学版在头部插入块指针为 O(块数)。
                blocks_.insert(blocks_.begin(), std::make_unique<Block>());
                ++start_block_; // 原有块整体右移一格
            }
            --start_block_;
            start_offset_ = BlockSize;
        }

        --start_offset_;
        (*blocks_[start_block_])[start_offset_].emplace(std::move(value));
        ++size_;
    }

    void pop_back() {
        assert(size_ > 0);
        const auto [block, offset] = locate(size_ - 1);
        (*blocks_[block])[offset].reset();
        --size_;
    }

    void pop_front() {
        assert(size_ > 0);
        (*blocks_[start_block_])[start_offset_].reset();
        --size_;
        ++start_offset_;

        if (start_offset_ == BlockSize) {
            start_offset_ = 0;
            ++start_block_;
        }
    }

    T& operator[](std::size_t index) {
        assert(index < size_);
        const auto [block, offset] = locate(index);
        return *(*blocks_[block])[offset];
    }

    std::size_t size() const noexcept {
        return size_;
    }

private:
    std::pair<std::size_t, std::size_t>
    locate(std::size_t logical_index) const {
        const std::size_t linear = start_offset_ + logical_index;
        return {
            start_block_ + linear / BlockSize,
            linear % BlockSize
        };
    }

    void ensure_back_block(std::size_t block_index) {
        while (block_index >= blocks_.size()) {
            blocks_.push_back(std::make_unique<Block>());
        }
    }

    std::vector<std::unique_ptr<Block>> blocks_;
    std::size_t start_block_ = 0;
    std::size_t start_offset_ = 0;
    std::size_t size_ = 0;
};
```

## 3. 复杂度和迭代器

- 随机访问通过两级索引完成，复杂度为 `O(1)`，但常数通常高于 vector。
- 真实 deque 在头尾插入/删除通常为摊销 `O(1)`。
- 中间插入仍可能移动较短一侧的元素，为 `O(n)`。
- deque 的迭代器通常需要保存块指针和块内位置，比普通指针复杂。
- 扩展映射表时，迭代器可能失效；引用是否失效要结合具体操作和标准保证判断。

## 4. 教学实现边界

该实现没有回收空 block，也没有为中央映射表预留两端空间，因此头部新增 block 可能是 `O(块数)`；它用于展示分段寻址，不是完整标准容器。

## 5. 面试口述版

deque 通常由中央映射表指向多个固定大小的数据块。元素不全局连续，随机访问用逻辑下标除以块大小定位数据块，再取余定位块内元素。分段结构让头尾扩展不必搬移全部元素，但迭代器更复杂，缓存局部性通常弱于 vector。
