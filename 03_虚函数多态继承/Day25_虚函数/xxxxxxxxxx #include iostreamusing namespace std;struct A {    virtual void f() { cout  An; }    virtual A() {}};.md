```
#include <iostream>
using namespace std;
struct A {
    virtual void f() { cout << "A\n"; }
    virtual ~A() {}
};
struct B : A {
    B() { f(); }
    void f() override { cout << "B\n"; }
};
int main() {
    B b;
}
```

> **问题**：输出什么？为什么构造函数中调用虚函数没调用派生类版本？
> 原因: **调用当前正在构造的类的版本**，不会调用子类的版本。
> 原因是：构造父类时，子类对象部分尚未初始化，`vptr` 指向的是父类的虚表。

