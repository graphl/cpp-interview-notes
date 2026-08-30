# C++14 新特性总览

C++14 是对 C++11 的增量完善，重点是让 Lambda、类型推导、`constexpr`、模板编程和资源管理更易用。下面按“作用 + 最小示例”快速总结；更完整的用法和易错点见各专题。

> 编译示例：`g++ -std=c++14 demo.cpp`。共享锁示例在 Linux 上通常还需要加 `-pthread`。

## 1. 泛型 Lambda

Lambda 的形参可以写成 `auto`。编译器会为闭包类型生成模板化的 `operator()`，因此同一个 Lambda 可以处理多种类型。

```cpp
auto add = [](auto a, auto b) {
    return a + b;
};

auto i = add(1, 2);       // int：3
auto d = add(1.5, 2.0);   // double：3.5
```

详见：[泛型 Lambda](./01_泛型Lambda/泛型Lambda.md)

## 2. Lambda 初始化捕获

可以在捕获列表中创建并初始化闭包成员，常用于改名捕获和移动捕获。C++11 有 Lambda，但初始化捕获从 C++14 才开始支持。

```cpp
#include <memory>
#include <utility>

auto ptr = std::make_unique<int>(42);
auto get = [owned = std::move(ptr)] {
    return *owned;
};

// get() == 42；ptr 的所有权已经转入闭包
```

详见：[Lambda 初始化捕获](./02_Lambda初始化捕获/Lambda初始化捕获.md)

## 3. 普通函数返回类型推导

普通函数可以直接用 `auto` 推导返回类型。若有多条 `return`，它们推导出的类型必须一致。

```cpp
auto square(int value) {
    return value * value;  // 返回类型推导为 int
}

auto choose(bool flag) {
    if (flag) return 1;
    return 2;              // 两个分支都是 int
}
```

`auto` 通常按值推导，会丢弃引用和顶层 `const`。

详见：[函数返回类型推导](./03_函数返回类型推导/函数返回类型推导.md)

## 4. `decltype(auto)`

`decltype(auto)` 按 `decltype` 的规则推导，可以保留表达式的引用和 `const` 属性，适合需要原样返回表达式类型的包装函数。

```cpp
int value = 10;

auto get_value() {
    return value;          // int
}

decltype(auto) get_ref() {
    return (value);        // int&，括号使表达式按左值推导
}

get_ref() = 20;            // 修改全局 value
```

注意：若返回局部变量的引用，会产生悬空引用。

详见：[`decltype(auto)`](./04_decltype_auto/decltype_auto.md)

## 5. `constexpr` 增强

C++14 放宽了 `constexpr` 函数体限制，允许使用局部变量、循环和条件分支等语句。

```cpp
constexpr int factorial(int n) {
    int result = 1;
    for (int i = 2; i <= n; ++i) {
        result *= i;
    }
    return result;
}

static_assert(factorial(5) == 120, "wrong result");
```

`constexpr` 函数并不保证每次都在编译期执行；只有进入常量表达式上下文并满足条件时，才必须在编译期求值。

详见：[`constexpr` 增强](./05_constexpr增强/constexpr增强.md)

## 6. 变量模板

变量也可以模板化，从而为不同类型提供一组变量或编译期常量。

```cpp
template <typename T>
constexpr T pi = static_cast<T>(3.1415926535897932385L);

float  f = pi<float>;
double d = pi<double>;
```

C++17 的 `std::is_same_v<T, U>` 等 `_v` 写法就是变量模板的典型应用。

详见：[变量模板](./06_变量模板/变量模板.md)

## 7. 二进制字面量

整数可以使用 `0b` 或 `0B` 前缀直接写成二进制，适合表达寄存器位和标志位。

```cpp
unsigned read  = 0b0001;
unsigned write = 0b0010;
unsigned mask  = read | write;  // 0b0011
```

详见：[二进制字面量](./07_二进制字面量/二进制字面量.md)

## 8. 数字分隔符

数字字面量中可以插入单引号，提高可读性；分隔符不影响数值和类型。

```cpp
int population = 1'000'000;
unsigned mask  = 0b1111'0000;
double pi      = 3.141'592'6;
```

详见：[数字分隔符](./08_数字分隔符/数字分隔符.md)

## 9. `std::make_unique`

`std::make_unique` 创建对象并立即交给 `unique_ptr` 管理，可以避免显式书写 `new`。

```cpp
#include <memory>

auto value = std::make_unique<int>(42);
auto array = std::make_unique<int[]>(10);

array[0] = *value;
```

版本辨析：`std::unique_ptr` 和 `std::make_shared` 属于 C++11，`std::make_unique` 属于 C++14。

详见：[`std::make_unique`](./09_make_unique/make_unique.md)

## 10. `std::integer_sequence`

`std::integer_sequence` 用类型表示编译期整数序列；最常见的用途是生成元组下标并展开参数包。

```cpp
#include <iostream>
#include <tuple>
#include <utility>

template <typename Tuple, std::size_t... I>
void print(const Tuple& tuple, std::index_sequence<I...>) {
    using expand = int[];
    (void)expand{0, ((void)(std::cout << std::get<I>(tuple) << ' '), 0)...};
}

int main() {
    auto data = std::make_tuple(7, 3.5, "C++14");
    print(data, std::make_index_sequence<3>{});  // 生成 0、1、2
}
```

C++14 常借助初始化列表展开参数包；C++17 可以使用更简洁的折叠表达式。

详见：[`std::integer_sequence`](./10_integer_sequence/integer_sequence.md)

## 11. `std::exchange`

`std::exchange(object, new_value)` 先保存旧值，再用新值替换对象，最后返回旧值。

```cpp
#include <utility>

int value = 10;
int old = std::exchange(value, 0);

// old == 10，value == 0
```

它常用于移动构造和“取走后复位”操作，但只是普通赋值，不是线程安全的原子交换。

详见：[`std::exchange`](./11_std_exchange/std_exchange.md)

## 12. 共享锁

C++14 引入 `std::shared_timed_mutex` 和 `std::shared_lock`，允许多个读线程同时持有共享锁，而写线程使用独占锁。

```cpp
#include <mutex>
#include <shared_mutex>

std::shared_timed_mutex mutex;
int value = 0;

int read_value() {
    std::shared_lock<std::shared_timed_mutex> lock(mutex);
    return value;
}

void write_value(int new_value) {
    std::unique_lock<std::shared_timed_mutex> lock(mutex);
    value = new_value;
}
```

版本辨析：`std::shared_timed_mutex` 属于 C++14，名字更短的 `std::shared_mutex` 属于 C++17。

详见：[共享锁](./12_共享锁/共享锁.md)

## 面试速答

> C++14 是对 C++11 的完善。语言层面主要增加了泛型 Lambda、Lambda 初始化捕获、普通函数返回类型推导、`decltype(auto)`、更宽松的 `constexpr`、变量模板、二进制字面量和数字分隔符；标准库层面常考 `make_unique`、`integer_sequence`、`exchange` 和共享锁。

## 推荐学习顺序

```text
泛型 Lambda -> 初始化捕获
-> 返回类型推导 -> decltype(auto)
-> constexpr -> 变量模板
-> 二进制字面量 -> 数字分隔符
-> make_unique -> integer_sequence
-> exchange -> 共享锁
```
