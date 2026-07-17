## 可变 lambda

```
int a = 10;
auto f = [a]() mutable { return ++a; };
```

展开成：

```
struct __Lambda_4 {
    int a;
    int operator()() {  // 注意不再是 const
        return ++a;
    }
};
auto f = __Lambda_4{a};
```

👉 `mutable` 让 `operator()` 去掉了 `const`，可以修改捕获的拷贝。

