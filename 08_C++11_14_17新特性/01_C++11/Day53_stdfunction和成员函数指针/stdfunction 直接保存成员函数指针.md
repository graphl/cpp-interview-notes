**静态成员函数**

```
struct Foo {
    static void bar(int x) { std::cout << x << std::endl; }
};
std::function<void(int)> f = Foo::bar;
f(20);
```

**非静态成员函数（绑定对象）std::bind**

```
Foo obj;
std::function<void(int)> f = std::bind(&Foo::bar, &obj, std::placeholders::_1);
f(30);
```

- `&Foo::show` → 成员函数指针
- `&obj` → 绑定到具体对象
- `std::placeholders::_1` → 占位符，表示调用时再传参数

**非静态成员函数直接保存成员函数指针**

```
#include <functional>
#include <iostream>
using namespace std;

struct Foo {
    void show(int x) { cout << "Foo::show " << x << endl; }
};

int main() {
    std::function<void(Foo&, int)> f = &Foo::show; 
    Foo obj;
    f(obj, 100); // 必须传对象引用 + 参数
}
```

👉 这种写法相当于 **把对象实例作为第一个参数传进去**。

