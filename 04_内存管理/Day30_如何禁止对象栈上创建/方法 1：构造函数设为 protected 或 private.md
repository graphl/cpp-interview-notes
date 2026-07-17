# 方法 1：构造函数设为 `protected` 或 `private`

```
#include <iostream>
using namespace std;

class HeapOnly {
protected:
    HeapOnly() { cout << "Constructor\n"; }
    ~HeapOnly() { cout << "Destructor\n"; }
public:
    static HeapOnly* create() {
        return new HeapOnly();
    }
};

int main() {
    // HeapOnly h; // ❌ 编译错误：构造函数是 protected
    HeapOnly* p = HeapOnly::create(); // ✅ 只能通过 new 创建
    delete p;
}
```

栈上分配需要**直接调用构造函数**，而 `protected/private` 阻止了外部这种调用。

通过静态工厂函数 `create()` 在类内部 `new`，即可强制走堆分配。