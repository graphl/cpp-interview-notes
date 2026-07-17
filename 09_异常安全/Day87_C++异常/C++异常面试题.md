# Day87 C++ 异常面试题

## 1. C++ 异常机制的基本流程是什么？

C++ 异常处理主要由 `throw`、`try`、`catch` 三部分组成。

```cpp
try {
    throw std::runtime_error("error");
} catch (const std::exception& e) {
    std::cout << e.what() << std::endl;
}
```

执行流程：

1. `throw` 抛出异常对象。
2. 程序停止当前正常执行路径。
3. 从当前作用域开始向外查找匹配的 `catch`。
4. 查找过程中会进行栈展开。
5. 找到匹配的 `catch` 后进入异常处理逻辑。
6. 如果一直找不到匹配的 `catch`，程序调用 `std::terminate()` 终止。

## 2. 什么是栈展开？

**栈展开是指异常抛出后，程序沿着函数调用栈向外寻找匹配的 `catch`，在*退出每一层作用域时，会自动调用已经构造完成的局部对象的析构函数***。

```cpp
class A {
public:
    ~A() {
        std::cout << "~A()" << std::endl;
    }
};

void func() {
    A a;
    throw std::runtime_error("error");
}
```

当 `func()` 抛出异常时，局部对象 `a` 会被正确析构。

核心点：

- 栈展开保证局部对象能自动释放资源。
- 这是 RAII 能和异常机制良好配合的基础。
- 只会析构已经构造完成的对象。

## 3. 为什么 catch 通常要使用引用捕获？

推荐使用：

```cpp
catch (const std::exception& e)
```

原因：

1. 避免异常对象拷贝，提高效率。
2. 避免对象切片(**把一个派生类对象赋值给基类对象时，派生类多出来的部分会被"切掉"（slice），只保留基类部分**)
3. 可以通过基类引用捕获派生类异常。
4. `const` 表示不会修改异常对象。

错误示例：

```cpp
catch (std::exception e)
```

如果抛出的是 `std::runtime_error`，按值捕获会发生对象切片，只保留基类部分。

## 4. catch 的匹配顺序有什么要求？

**答：**

`catch` 会按照从上到下的顺序匹配，因此派生类异常应该写在基类异常前面。

```cpp
try {
    throw std::runtime_error("runtime error");
} catch (const std::runtime_error& e) {
    std::cout << "runtime_error" << std::endl;
} catch (const std::exception& e) {
    std::cout << "exception" << std::endl;
}
```

如果把 `std::exception` 放在前面，派生类异常会先被基类捕获，后面的 `std::runtime_error` 分支就没有机会执行。

## 5. 构造函数可以抛异常吗？

可以，而且构造函数失败时，抛异常是常见做法。

原因：

- 构造函数没有返回值，不能通过返回错误码表示失败。
- 抛异常可以阻止一个无效对象被创建出来。

注意点：

- 如果构造函数抛异常，当前对象不会被认为构造成功。
- 当前类的析构函数不会被调用。
- 已经构造完成的成员变量和基类子对象会被自动析构。

```cpp
class Test {
public:
    Test() {
        throw std::runtime_error("construct failed");
    }

    ~Test() {
        std::cout << "~Test()" << std::endl;
    }
};
```

上面代码中，如果构造函数抛异常，`~Test()` 不会被调用。

## 6. 析构函数可以抛异常吗？

语法上可以，但强烈不推荐。

原因：

- 析构函数常常在栈展开过程中被调用。
- 如果栈展开时析构函数又抛出异常，就会出现双异常。
- 双异常会导致 `std::terminate()`，程序直接终止。

推荐做法：

```cpp
class File {
public:
    ~File() noexcept {
        try {
            close();
        } catch (...) {
            // 记录日志，吞掉异常
        }
    }

    void close() {
        // 可能失败的资源释放逻辑
    }
};
```

C++11 之后，析构函数默认通常被视为 `noexcept`，所以析构函数里更应该避免异常逃出。
