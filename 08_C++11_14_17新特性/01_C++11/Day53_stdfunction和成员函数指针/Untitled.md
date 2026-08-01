# std::function、成员函数指针与对象绑定

## 1. 为什么成员函数指针不能当普通函数指针用

非静态成员函数执行时需要一个对象作为隐含的 `this` 参数，因此下面两种类型不同：

```cpp
void (*normal)(int);       // 普通函数指针
void (Foo::*member)(int);  // Foo 的成员函数指针
```

成员函数指针只描述“调用 Foo 的哪个成员函数”，还没有说明“在哪个 Foo 对象上调用”。

## 2. 三种调用方式

```cpp
#include <functional>
#include <iostream>

struct Foo {
    void show(int value) {
        std::cout << value << '\n';
    }
};

int main() {
    Foo object;
    void (Foo::*member)(int) = &Foo::show;

    // 方式一：使用成员函数指针语法。
    (object.*member)(10);

    // 方式二：std::function 把对象作为第一个显式参数。
    std::function<void(Foo&, int)> direct = &Foo::show;
    direct(object, 20);

    // 方式三：lambda 捕获对象，得到普通的一元可调用对象。
    std::function<void(int)> bound = [&object](int value) {
        object.show(value);
    };
    bound(30);
}
```

## 3. 生命周期是最容易忽略的问题

```cpp
std::function<void(int)> make_callback() {
    Foo local;
    return [&local](int value) { local.show(value); }; // 错误
}
```

函数返回后 `local` 已销毁，回调中保存的引用悬空。可选方案包括：

1. 按值捕获一个可复制对象。
2. 由外部保证被引用对象比回调活得更久。
3. 捕获 `shared_ptr` 延长生命周期。
4. 捕获 `weak_ptr`，调用前先 `lock()`，避免无意延长生命周期。

## 4. std::function 的成本

`std::function<R(Args...)>` 使用类型擦除保存不同类型的可调用对象。调用通常存在一层间接访问；较大的捕获对象还可能触发堆分配。具体是否使用小对象优化属于标准库实现细节。

如果调用目标类型在编译期已知且性能敏感，可以优先使用模板参数或直接保存 lambda 类型；需要统一存储异构回调时，再使用 `std::function`。

## 5. 面试口述版

非静态成员函数指针还缺少调用对象，因为成员函数需要隐含的 this。可以使用 `object.*member` 直接调用，也可以让 `std::function` 把对象作为第一个参数，或者通过 lambda 捕获对象完成绑定。真正的工程风险通常不是语法，而是回调保存的对象引用是否仍然有效，以及类型擦除和可能的堆分配成本。
