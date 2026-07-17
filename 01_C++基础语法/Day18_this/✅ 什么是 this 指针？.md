# ✅ 什么是 `this` 指针？

在 **C++ 的非静态成员函数** 中，`this` 是一个 **隐式指针参数**，指向调用该成员函数的对象本身。

```
class Person {
public:
    void showName() {
        std::cout << this->name << std::endl;
    }
private:
    std::string name = "Alice";
};
```

上面的 `this->name` 实际是指向当前调用 `showName()` 的对象的 `name` 成员。

# ❓为什么存在 `this` 指针？

因为 **类的成员函数对多个对象共享**，编译器需要一种方式区分“哪个对象在调用这个函数”，这就是 `this` 指针的作用。

```
Person p1, p2;
p1.showName();  // this == &p1
p2.showName();  // this == &p2
```

如果没有 `this`，成员函数内部就无法访问“当前对象”的成员变量。