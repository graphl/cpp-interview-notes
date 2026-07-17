### RAII（Resource Acquisition Is Initialization）

**概念**

- 一种 C++ 常用的管理资源的惯用法。
- 思想：**把资源的申请和释放绑定到对象的生命周期上**。
- 当对象构造时获取资源（申请内存、打开文件、加锁等），当对象析构时自动释放资源（释放内存、关闭文件、解锁等）。

**优点**

1. **异常安全**：即使抛异常，栈上的局部对象会自动调用析构函数释放资源。
2. **防止资源泄露**：不需要显式调用 `free()` / `close()`，资源由对象自动管理。
3. **代码简洁**：避免写很多 `try/catch` 或 `goto` 来处理清理逻辑。

**典型例子**

```
#include <iostream>
#include <memory>
#include <mutex>
#include <fstream>

void example() {
    std::unique_ptr<int> ptr(new int(10));  // 构造时申请资源
    std::lock_guard<std::mutex> lock(m);    // 构造时加锁
    std::ifstream file("data.txt");         // 构造时打开文件

    // 出作用域时，ptr 会自动 delete，lock 会自动解锁，file 会自动关闭
}
```