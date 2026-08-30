# C++14：`std::make_unique`

`std::make_unique` 创建对象并返回对应的 `unique_ptr`：

```cpp
auto object = std::make_unique<Widget>(1, "worker");
auto array = std::make_unique<int[]>(100);
```

它避免显式使用 `new`，类型只需书写一次，并使对象创建后立即进入 RAII 管理。

版本辨析：

```text
std::unique_ptr、std::make_shared：C++11
std::make_unique：                C++14
```

对于需要自定义删除器的 `unique_ptr`，通常仍需显式构造智能指针。

## 使用方法

```cpp
#include <iostream>
#include <memory>
#include <utility>

struct Device {
    explicit Device(int id) : id(id) {}
    void start() const { std::cout << "start " << id << '\n'; }
    int id;
};

void consume(std::unique_ptr<Device> device) {
    device->start();
}

int main() {
    auto device = std::make_unique<Device>(7); // 创建并初始化对象
    device->start();                           // 通过 -> 调用成员函数

    consume(std::move(device));                // 转移所有权
    if (!device) std::cout << "ownership moved\n";

    auto samples = std::make_unique<int[]>(4); // 动态数组
    samples[0] = 42;
} // 未转移的 unique_ptr 在离开作用域时自动释放资源
```

`unique_ptr` 不可拷贝，只能移动。函数只借用对象时传 `Device&` 或 `Device*`；函数接管所有权时才按值接收 `unique_ptr<Device>`。不要用 `release()` 代替正常析构，除非马上把裸指针交给另一个所有者。
