### 🔥 标准规定的真实过程（构造 Derived 时）

假设：

```
class Base {
public:
    Base() { foo(); }
    virtual void foo() { cout << "Base foo\n"; }
};

class Derived : public Base {
public:
    Derived() { foo(); }
    virtual void foo() { cout << "Derived foo\n"; }
};
```

 **vptr 切换过程**是这样的：

| 阶段                              | 正在执行哪个构造函数 | vptr 指向哪张虚表 | 调用 `foo()` 结果 |
| --------------------------------- | -------------------- | ----------------- | ----------------- |
| ① 进入 `Base()`                   | Base                 | Base 的虚表       | Base::foo         |
| ② 退出 `Base()`、进入 `Derived()` | Derived              | Derived 的虚表    | Derived::foo      |
| ③ 完全构造好                      | Derived              | Derived 的虚表    | Derived::foo      |