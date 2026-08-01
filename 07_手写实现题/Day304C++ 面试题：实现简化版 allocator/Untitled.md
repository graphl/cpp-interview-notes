## 5. 教学实现还缺什么

1. over-aligned 类型的显式对齐分配处理。
2. 有状态 allocator 的资源身份和传播规则。
3. 内存池、线程本地缓存和大小分级。
4. C++17 `std::pmr::memory_resource` 的运行时多态资源模型。
5. 完整标准版本兼容性与所有 allocator requirements。