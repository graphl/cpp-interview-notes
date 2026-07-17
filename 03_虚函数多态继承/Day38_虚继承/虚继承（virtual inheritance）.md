# 虚继承（**virtual inheritance**）

> 是 C++ 里为了解决 **多继承时的菱形继承问题（diamond problem）** 而引入的机制。

## 菱形继承问题

假设有以下继承结构：

```
class A {
public:
    int value;
};

class B : public A {};
class C : public A {};
class D : public B, public C {};
```

此时 `D` 会同时继承两份 `A`：

- 一份来自 `B`
- 一份来自 `C`

所以在 `D` 中存在两份 `value`，对 `d.value` 的访问会产生**二义性**。