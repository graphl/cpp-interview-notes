# 方法 1：将 `operator new` 和 `operator delete` 设为 `private`

```
#include <iostream>
using namespace std;

class StackOnly {
public:
    StackOnly() { cout << "Constructor\n"; }
    ~StackOnly() { cout << "Destructor\n"; }

private:
    // 禁止堆分配
    void* operator new(size_t) = delete;
    void operator delete(void*) = delete;
};

int main() {
    StackOnly a;     // ✅ 栈上 OK
    // StackOnly* p = new StackOnly(); // ❌ 编译错误：operator new 被删除
}

```

