# 函数重载（overload）与虚函数混用时

重载决议（overload resolution）在编译期完成，只会在静态类型范围内找候选函数。

```
struct Base { virtual void f(int) { cout << "Base int\n"; } };
struct Derived : Base {
    void f(double) { cout << "Derived double\n"; } // 不是重写，而是隐藏
};
int main() {
    Derived d;
    Base* p = &d;
    p->f(1.0); // 会调用 Base::f(int)，不是 Derived::f(double)
}

```

你的 `p->f(1.0)` 为什么调用 Base::f(int)

这里分两步：

1. **静态类型检查**：`p` 是 `Base*`，所以编译器只会在 `Base` 的成员列表里查找函数签名。`Derived::f(double)` 不在基类接口中，根本不会考虑。
2. **重载匹配**：`Base` 里只有 `f(int)`，`1.0` 可以转换成 `int`，所以匹配 `Base::f(int)`。
3. **动态绑定**：`f(int)` 是虚函数，本来可以动态绑定到派生类版本，但派生类根本没重写它，所以最终还是调用 `Base::f(int)`。