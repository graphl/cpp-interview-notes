# C++14：泛型 Lambda

C++14 允许 Lambda 形参使用 `auto`，编译器会为闭包类型生成函数调用运算符模板。

```cpp
auto add = [](auto a, auto b) {
    return a + b;
};

auto i = add(1, 2);       // int
auto d = add(1.5, 2.0);   // double
```

它适合编写与类型无关的局部操作。C++11 已支持 Lambda，但形参类型必须明确；泛型 Lambda 从 C++14 开始支持。

面试速答：泛型 Lambda 的本质是闭包类拥有一个模板化的 `operator()`，并不是把 Lambda 本身变成普通函数模板。
