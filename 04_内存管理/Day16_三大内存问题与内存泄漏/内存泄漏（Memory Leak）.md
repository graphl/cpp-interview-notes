# 内存泄漏（Memory Leak）

**分配的内存未释放**，程序失去对其引用，造成资源泄露。

```
void leak() {
    int* p = new int[100];
    // 没有 delete[] p; → 内存泄漏
}
```

###  结果：

- 长时间运行程序内存不断增长，最终崩溃或性能下降

### 防范建议：

- 用智能指针：`std::unique_ptr`, `std::shared_ptr`
- 手动 `delete` 配对每次 `new`
- 使用工具：Valgrind、ASan（地址消毒器）