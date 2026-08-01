# C++ 面试题：实现 Bitmap

## 1. Bitmap 为什么节省空间

如果只需要记录“编号是否出现”，用一个字节甚至一个整数保存一个状态都很浪费。Bitmap 用一个二进制位表示一个状态：

```text
bit 0 -> 编号 0 是否存在
bit 1 -> 编号 1 是否存在
...
```

保存 `n` 个状态大约只需要 `n / 8` 字节。它常用于去重、权限集合、布隆过滤器底层存储和大规模布尔标记。

## 2. 教学实现

```cpp
#include <cstddef>
#include <cstdint>
#include <stdexcept>
#include <vector>

class Bitmap {
    static constexpr std::size_t bits_per_word = 64;

public:
    explicit Bitmap(std::size_t bit_count)
        : words_((bit_count + bits_per_word - 1) /
                 bits_per_word),
          bit_count_(bit_count) {}

    void set(std::size_t bit) {
        check(bit);
        words_[word_index(bit)] |= mask(bit);
    }

    void reset(std::size_t bit) {
        check(bit);
        words_[word_index(bit)] &= ~mask(bit);
    }

    void flip(std::size_t bit) {
        check(bit);
        words_[word_index(bit)] ^= mask(bit);
    }

    bool test(std::size_t bit) const {
        check(bit);
        return (words_[word_index(bit)] & mask(bit)) != 0;
    }

    std::size_t size() const noexcept {
        return bit_count_;
    }

    std::size_t count() const noexcept {
        std::size_t result = 0;
        for (std::uint64_t word : words_) {
            while (word != 0) {
                word &= word - 1;
                ++result;
            }
        }
        return result;
    }

private:
    static std::size_t word_index(std::size_t bit) noexcept {
        return bit / bits_per_word;
    }

    static std::uint64_t mask(std::size_t bit) noexcept {
        return std::uint64_t{1} << (bit % bits_per_word);
    }

    void check(std::size_t bit) const {
        if (bit >= bit_count_) {
            throw std::out_of_range("Bitmap bit index");
        }
    }

    std::vector<std::uint64_t> words_;
    std::size_t bit_count_;
};
```

定位一个 bit 需要两个值：

```text
word 下标 = bit / 64
word 内偏移 = bit % 64
mask = 1ULL << 偏移
```

显式使用 `uint64_t{1}` 很重要。如果写成普通 `1 << offset`，左操作数可能只有 32 位，大位移会产生错误或未定义行为。

## 3. count 为什么使用 word &= word - 1

`word - 1` 会把最低位的 `1` 变成 `0`，并改变它右侧的位。与原值按位与后，恰好清除最低位的一个 `1`：

```text
word &= word - 1
```

循环次数等于置位数量。C++20 也可以使用 `<bit>` 中的 `std::popcount`。

## 4. 复杂度和边界

- `set`、`reset`、`flip`、`test` 都是 `O(1)`；
- `count` 当前实现与机器字数量和置位数量有关；
- 空 Bitmap 合法，但任何位访问都会越界；
- 最后一个机器字可能有未使用的高位，本实现从不设置这些位；
- 并发修改同一个机器字会产生数据竞争，线程安全版本需要原子机器字或分片锁；
- Bitmap 只能表示有限且已知范围的非负编号。

## 5. 面试口述版

Bitmap 用一个 bit 表示一个编号状态。先用除法定位 64 位机器字，再用取模定位字内偏移，通过 OR、AND 和 XOR 实现设置、清除和翻转。单点操作是 `O(1)`，空间约为 `n/8` 字节。需要注意移位操作数宽度、越界以及多个线程修改同一机器字的数据竞争。
