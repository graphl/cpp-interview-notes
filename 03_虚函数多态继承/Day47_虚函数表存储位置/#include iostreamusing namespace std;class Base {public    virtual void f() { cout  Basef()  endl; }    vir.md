```
#include <iostream>
using namespace std;

class Base {
public:
    virtual void f() { cout << "Base::f()" << endl; }
    virtual void g() { cout << "Base::g()" << endl; }
};

class Derived : public Base {
public:
    void f() override { cout << "Derived::f()" << endl; }
    void h() { cout << "Derived::h()" << endl; }
};

int main() {
    Base* p = new Derived();
    p->f(); // 调用 Derived::f()
}
```

在 ELF 可执行文件中，你能看到类似符号：

_ZTV5Base      # Base 的虚函数表
_ZTV7Derived   # Derived 的虚函数表
这些符号都在 **只读数据段（.rodata）**。