# const 和 引用 成员必须初始化

```
struct Foo {
    const int ci; 
    int& ref; 
    Foo(int v) : ci(v), ref(x) {} // ✅ 必须在初始化列表中
    int x = 42;
};
```

如果你在构造函数体内写 `ci = v;` 会直接编译错误。