## 用 lambda 捕获对象

更现代的写法是直接用 lambda 捕获对象：

```
#include <functional>
#include <iostream>
using namespace std;

struct Foo {
    void show(int x) { cout << "Foo::show " << x << endl; }
};

int main() {
    Foo obj;

    std::function<void(int)> f = [&obj](int x) { obj.show(x); };

    f(300); // 输出: Foo::show 300
}
```

这种写法更直观，C++11 之后一般优先用 lambda。