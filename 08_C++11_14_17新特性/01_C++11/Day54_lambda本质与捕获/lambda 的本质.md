## lambda 的本质

一个 lambda 例如：

```
auto f = [](int x) { return x + 1; };
```

编译器会把它转化成类似的类：

```
struct __Lambda_1 {
    int operator()(int x) const {
        return x + 1;
    }
};
auto f = __Lambda_1{};
```

👉 所以 **lambda 是一个语法糖，本质是一个匿名函数对象（functor）**。