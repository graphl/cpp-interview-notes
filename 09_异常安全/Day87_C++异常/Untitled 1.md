## 13. catch(...) 的作用是什么？

`catch(...)` 可以捕获任意类型的异常。

```cpp
try {
    throw 1;
} catch (...) {
    std::cout << "catch any exception" << std::endl;
}
```

注意：

- 通常放在所有 `catch` 的最后。
- 它不知道异常的具体类型。
- 可以用于兜底处理、日志记录、资源清理。

## 14. 异常和错误码有什么区别？

异常适合处理不常发生、会打断正常流程的错误；错误码适合可预期、频繁发生的状态判断。

异常优点：

- 正常逻辑和错误处理分离。
- 可以跨多层调用传播错误。
- 构造函数失败时更自然。

异常缺点：

- 控制流不如返回值直观。
- 不适合高频路径。
- 需要注意异常安全。

错误码优点：

- 流程显式。
- 性能和控制更可预测。
- 常用于系统调用、嵌入式、底层接口。

## 15. 面试代码题：下面代码输出什么？

```cpp
#include <iostream>
#include <stdexcept>

class A {
public:
    A() {
        std::cout << "A()" << std::endl;
    }

    ~A() {
        std::cout << "~A()" << std::endl;
    }
};

void func() {
    A a;
    throw std::runtime_error("error");
    std::cout << "after throw" << std::endl;
}

int main() {
    try {
        func();
    } catch (const std::exception& e) {
        std::cout << e.what() << std::endl;
    }
}
```

**答案：**

```text
A()
~A()
error
```

解释：

- `func()` 中先构造对象 `a`。
- `throw` 后，`after throw` 不会执行。
- 异常传播前发生栈展开，调用 `a` 的析构函数。
- `main()` 中的 `catch` 捕获异常并打印 `error`。

## 16. 面试代码题：下面代码有什么问题？

```cpp
class Base {
public:
    virtual ~Base() {}
};

class Derived : public Base {};

try {
    throw Derived();
} catch (Base e) {
}
```

问题是 `catch (Base e)` 按值捕获，会发生对象切片，`Derived` 的派生类部分会丢失。

应该改成：

```cpp
catch (const Base& e) {
}
```

## 17. 面试代码题：下面代码为什么危险？

```cpp
class A {
public:
    ~A() {
        throw std::runtime_error("destructor error");
    }
};
```

析构函数抛异常很危险。

如果对象在正常流程中析构，异常可能还能被捕获；但如果对象是在栈展开过程中析构，此时已经有一个异常正在传播，再抛出第二个异常会导致程序调用 `std::terminate()`。

建议：

```cpp
~A() noexcept {
    try {
        // cleanup
    } catch (...) {
        // log only
    }
}
```

## 18. 高频总结

面试回答时可以抓住这几句话：

1. 异常通过 `throw` 抛出，通过 `try-catch` 捕获。
2. 异常传播时会发生栈展开，局部对象会自动析构。
3. `catch` 推荐使用 `const T&`，避免拷贝和对象切片。
4. 构造函数可以抛异常，析构函数不应该让异常逃出。
5. `noexcept` 表示函数承诺不抛异常，异常逃出会终止程序。
6. RAII 是写异常安全 C++ 代码的关键。
7. `throw;` 是重新抛出当前异常，`throw e;` 可能造成切片。
8. 标准库异常一般继承自 `std::exception`，可以通过 `what()` 查看错误信息。