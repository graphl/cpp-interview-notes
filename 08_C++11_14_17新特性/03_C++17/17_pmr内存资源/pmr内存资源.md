# C++17：`std::pmr` 多态内存资源

`std::pmr` 将容器类型与具体内存分配策略解耦，通过运行期多态的 `memory_resource` 管理内存。

```cpp
std::byte buffer[1024];
std::pmr::monotonic_buffer_resource resource(buffer, sizeof buffer);
std::pmr::vector<int> values(&resource);
```

常见资源包括单调资源和同步/非同步池资源。它适合批量短生命周期对象、减少堆分配或控制内存来源。

注意资源生命周期必须覆盖使用它的容器；释放单个对象不一定立即把内存归还给上游资源。

## 初始化与容器调用

```cpp
#include <array>
#include <cstddef>
#include <iostream>
#include <memory_resource>
#include <string>
#include <string_view>
#include <vector>

int main() {
    std::array<std::byte, 1024> buffer{};
    std::pmr::monotonic_buffer_resource resource{
        buffer.data(), buffer.size(), std::pmr::null_memory_resource()};

    std::pmr::vector<std::pmr::string> names{&resource};
    names.emplace_back("camera");
    names.emplace_back("sensor");

    for (std::string_view name : names)
        std::cout << name << '\n';

    names.clear();     // 销毁元素；单调资源通常不回收单次分配
    resource.release();// 一次性释放该资源持有的全部内存
}
```

构造 PMR 容器时传入 `memory_resource*`。单调资源适合整批创建、整批销毁；池资源适合大量相似大小的分配。资源必须比所有使用它的容器及其元素活得更久，跨资源移动或交换容器前还要确认分配器传播规则。
