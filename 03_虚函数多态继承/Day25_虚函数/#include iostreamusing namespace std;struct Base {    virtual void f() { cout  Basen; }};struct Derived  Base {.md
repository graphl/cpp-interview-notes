```
#include <iostream>
using namespace std;
struct Base {
    virtual void f() { cout << "Base\n"; }
};
struct Derived : Base {
    void f() override { cout << "Derived\n"; }
};
int main() {
    Base* b = new Derived;
    b->f();
    delete b;
}
```

> **问题**：输出什么？delete 时是否安全？为什么？
>
> **答**：输出 Derived， delete时，不安全，会导致派生类部分的析构函数不被调用，从而造成内存泄漏或资源泄漏。

```
#include <iostream>
using namespace std;
struct A {
    virtual void f() { cout << "A\n"; }
};
struct B : A {
    void f() & override { cout << "B &\n"; }
    void f() && override { cout << "B &&\n"; }
};
int main() {
    B b;
    b.f();
    B{}.f();
}
```

>  **问题**：输出结果？为什么会区分左值和右值版本的虚函数？
> **为什么虚函数会区分？**
>
> - 从 **C++11** 开始，函数签名的一部分包括**成员函数的引用限定符**（`&`、`&&`）。
> - 这意味着 `virtual void f() &` 和 `virtual void f() &&` 是两个完全不同的虚函数槽位，它们在虚表中是分开的。
> - 当对象是左值时，编译器只会在**左值版本的虚表槽**中查找实现；当是右值时，就用右值版本的虚表槽。