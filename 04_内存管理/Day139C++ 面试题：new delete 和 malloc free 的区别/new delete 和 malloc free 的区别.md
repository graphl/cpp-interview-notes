# C++ 面试题：new/delete 和 malloc/free 的区别

## 1. 核心结论

`new/delete` 是 C++ 运算符。

`malloc/free` 是 C 标准库函数。

---

## 2. 对比表

| 对比 | `new/delete` | `malloc/free` |
|---|---|---|
| 类型 | 运算符 | 库函数 |
| 是否调用构造/析构 | 是 | 否 |
| 返回类型 | 具体类型指针 | `void*` |
| 失败行为 | 抛出 `std::bad_alloc` | 返回 `nullptr` |
| 大小计算 | 自动计算 | 需要手动传字节数 |
| 可重载 | 可以 | 不可以 |

---

## 3. 示例

```cpp
int* p1 = new int(10);
delete p1;
```

```cpp
int* p2 = static_cast<int*>(std::malloc(sizeof(int)));
std::free(p2);
```

---

## 4. 对象场景

```cpp
class A {
public:
    A() {}
    ~A() {}
};

A* p = new A;     // 调用构造函数
delete p;         // 调用析构函数
```

`malloc` 只分配内存，不会调用构造函数。

---

## 5. 面试回答

`new` 会分配内存并调用构造函数，`delete` 会调用析构函数并释放内存；`malloc` 只分配原始内存，`free` 只释放内存，不会调用构造和析构。C++ 中管理对象应使用 `new/delete`，更推荐使用智能指针和 RAII。
