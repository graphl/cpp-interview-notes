# C++ 面试题：RTTI、dynamic_cast 和 typeid

## 1. RTTI 解决什么问题

运行时类型识别（RTTI）用于在只持有基类引用或指针时，查询对象的动态类型，或者安全地转换到派生类/兄弟类。

```cpp
struct Base {
    virtual ~Base() = default;
};

struct Derived : Base {
    void work() {}
};

void run(Base* base) {
    if (auto* derived = dynamic_cast<Derived*>(base)) {
        derived->work();
    }
}
```

## 2. dynamic_cast 的结果

```text
指针转换失败    -> 返回 nullptr
引用转换失败    -> 抛出 std::bad_cast
向上转换        -> 通常可在编译期完成
向下/交叉转换   -> 需要检查对象的动态类型和继承关系
```

运行时检查通常要求源类型是多态类型，也就是至少包含一个虚函数。常见 ABI 会把类型信息与虚表相关联，但 RTTI 的具体存储位置不是 C++ 标准规定的对象布局。

## 3. typeid 的静态和动态行为

```cpp
#include <iostream>
#include <typeinfo>

void inspect(Base& object) {
    if (typeid(object) == typeid(Derived)) {
        std::cout << "dynamic type is Derived\n";
    }
}
```

当表达式是多态类型的左值时，`typeid(expression)` 查询动态类型；其他情况下通常反映表达式的静态类型。对解引用后的空多态指针使用 `typeid(*ptr)` 会抛出 `std::bad_typeid`。

## 4. 一次向下转换的概念流程

```text
Base* 静态类型
  -> 读取对象关联的运行时类型信息
  -> 检查完整对象中是否存在可访问且唯一的 Derived 子对象
  -> 必要时调整指针偏移
  -> 成功返回 Derived*，失败返回 nullptr
```

多继承下转换结果可能需要调整地址，因此 `dynamic_cast` 不只是检查一个类型编号。

## 5. 什么时候不应依赖 RTTI

如果代码不断通过 `dynamic_cast` 判断派生类型后执行不同分支，可能说明基类接口缺少合适的虚函数，或者更适合使用 `variant`/访问者模式。RTTI 适合插件边界、安全向下转换和确实需要类型查询的场景，不应代替正常的多态设计。

## 6. 面试口述版

RTTI 让程序在运行时识别多态对象的动态类型。dynamic_cast 可以安全完成向下转换和交叉转换，指针失败返回空，引用失败抛 bad_cast；多继承时还可能调整指针。typeid 可以查询类型信息，但具体 RTTI 与虚表布局属于 ABI 实现细节。
