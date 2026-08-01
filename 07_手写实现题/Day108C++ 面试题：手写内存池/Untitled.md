# 简化版

```
#include <cstddef>
#include <cstdlib>

class MemoryPool {
public:
    MemoryPool(size_t block_size, size_t block_count)
        : block_size_(block_size), block_count_(block_count) {
        if (block_size_ < sizeof(Node)) {
            block_size_ = sizeof(Node);
        }

        memory_ = static_cast<char*>(std::malloc(block_size_ * block_count_));
        free_list_ = nullptr;

        for (size_t i = 0; i < block_count_; ++i) {
            Node* node = reinterpret_cast<Node*>(memory_ + i * block_size_);
            node->next = free_list_;
            free_list_ = node;
        }
    }

    ~MemoryPool() {
        std::free(memory_);
    }

    void* allocate() {
        if (!free_list_) {
            return nullptr;
        }

        Node* node = free_list_;
        free_list_ = free_list_->next;
        return node;
    }

    void deallocate(void* p) {
        if (!p) {
            return;
        }

        Node* node = static_cast<Node*>(p);
        node->next = free_list_;
        free_list_ = node;
    }

private:
    struct Node {
        Node* next;
    };

    size_t block_size_;
    size_t block_count_;
    char* memory_;
    Node* free_list_;
};
```

