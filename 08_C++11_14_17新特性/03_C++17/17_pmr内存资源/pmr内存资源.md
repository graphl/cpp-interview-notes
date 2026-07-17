# C++17：`std::pmr` 多态内存资源

`std::pmr` 将容器类型与具体内存分配策略解耦，通过运行期多态的 `memory_resource` 管理内存。

```cpp
std::byte buffer[1024];
std::pmr::monotonic_buffer_resource resource(buffer, sizeof buffer);
std::pmr::vector<int> values(&resource);
```

常见资源包括单调资源和同步/非同步池资源。它适合批量短生命周期对象、减少堆分配或控制内存来源。

注意资源生命周期必须覆盖使用它的容器；释放单个对象不一定立即把内存归还给上游资源。
