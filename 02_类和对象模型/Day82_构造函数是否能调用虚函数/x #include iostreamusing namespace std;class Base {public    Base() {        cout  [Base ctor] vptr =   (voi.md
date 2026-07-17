```
#include <iostream>
using namespace std;

class Base {
public:
    Base() {
        cout << "[Base ctor] vptr = " << *(void**)this << endl;
        foo();
    }
    virtual void foo() { cout << "Base::foo()" << endl; }
};

class Derived : public Base {
public:
    Derived() {
        cout << "[Derived ctor] vptr = " << *(void**)this << endl;
        foo();
    }
    virtual void foo() { cout << "Derived::foo()" << endl; }
};

int main() {
    cout << "---- constructing Derived d ----" << endl;
    Base b;
    Derived d;

    cout << "---- after construction ----" << endl;
    cout << "[d] vptr = " << *(void**)&d << endl;
    cout << "[b] vptr = " << *(void**)&b << endl;
}

```

