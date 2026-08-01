# C++ 面试题：实现 Trie 字典树

## 1. Trie 适合什么场景

Trie 按字符逐层保存字符串。多个单词共享相同前缀，因此适合：

- 前缀搜索；
- 自动补全；
- 词典匹配；
- 路由或关键字过滤。

查找时间主要与字符串长度有关，而不是字典中单词数量。代价是节点数量可能很大。

下面的教学版本只接受小写英文字母。

## 2. 教学实现

```cpp
#include <array>
#include <cstddef>
#include <memory>
#include <stdexcept>
#include <string_view>

class Trie {
    struct Node {
        bool terminal = false;
        std::array<std::unique_ptr<Node>, 26> children{};
    };

public:
    void insert(std::string_view word) {
        Node* current = &root_;
        for (char ch : word) {
            const std::size_t i = index(ch);
            if (!current->children[i]) {
                current->children[i] = std::make_unique<Node>();
            }
            current = current->children[i].get();
        }
        current->terminal = true;
    }

    bool contains(std::string_view word) const {
        const Node* node = find_prefix(word);
        return node && node->terminal;
    }

    bool starts_with(std::string_view prefix) const {
        return find_prefix(prefix) != nullptr;
    }

    bool erase(std::string_view word) {
        bool removed = false;
        erase(root_, word, 0, removed);
        return removed;
    }

private:
    static std::size_t index(char ch) {
        if (ch < 'a' || ch > 'z') {
            throw std::invalid_argument("Trie accepts only a-z");
        }
        return static_cast<std::size_t>(ch - 'a');
    }

    const Node* find_prefix(std::string_view text) const {
        const Node* current = &root_;
        for (char ch : text) {
            const std::size_t i = index(ch);
            if (!current->children[i]) {
                return nullptr;
            }
            current = current->children[i].get();
        }
        return current;
    }

    static bool has_children(const Node& node) {
        for (const auto& child : node.children) {
            if (child) {
                return true;
            }
        }
        return false;
    }

    static bool erase(Node& node,
                      std::string_view word,
                      std::size_t depth,
                      bool& removed) {
        if (depth == word.size()) {
            if (!node.terminal) {
                return false;
            }
            node.terminal = false;
            removed = true;
            return !has_children(node);
        }

        const std::size_t i = index(word[depth]);
        if (!node.children[i]) {
            return false;
        }
        if (erase(*node.children[i], word, depth + 1, removed)) {
            node.children[i].reset();
        }
        return !node.terminal && !has_children(node);
    }

    Node root_;
};
```

删除时不能看到单词结束就一路释放节点，因为节点可能仍是其他单词的前缀。例如删除 `app` 不能破坏 `apple`。

## 3. 复杂度和空间取舍

设字符串长度为 `L`：

- 插入、完整查找和前缀查找都是 `O(L)`；
- 删除需要检查孩子，固定 26 字符表时仍可看作 `O(L)`；
- 当前节点固定保存 26 个指针，查询快但稀疏时浪费空间；
- 字符集较大时可改用 `unordered_map<char, unique_ptr<Node>>`，用额外哈希成本换空间。

## 4. 边界和生产版本

1. 要明确空字符串是否允许作为一个单词。
2. 大小写、UTF-8 和任意字节需要不同的字符映射策略。
3. 递归删除深度等于字符串长度，超长 key 可能造成栈过深。
4. 并发读写需要外部同步或不可变快照。
5. 压缩 Trie 或 Radix Tree 可以合并只有一个孩子的连续节点。

## 5. 面试口述版

Trie 把字符串拆成字符路径，共享公共前缀。查找复杂度与 key 长度有关。节点可以使用固定数组获得稳定的字符访问成本，也可以用哈希表节省稀疏节点空间。删除时只有在节点不是单词结尾且没有孩子时才能回收，避免破坏其他共享前缀。
