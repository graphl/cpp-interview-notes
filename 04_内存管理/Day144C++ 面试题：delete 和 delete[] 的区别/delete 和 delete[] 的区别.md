# C++ 面试题：delete 和 delete[] 的区别

## 1. 核心结论

`delete` 用来释放单个对象。

`delete[]` 用来释放对象数组。

二者必须和 `new`、`new[]` 正确配对。

---

## 2. 示例

```cpp
int* p = new int(10);
delete p;
```

```cpp
int* arr = new int[10];
delete[] arr;
```

---

## 3. 对象数组

```cpp
class A {
public:
    ~A() {}
};

A* arr = new A[10];
delete[] arr;  // 调用 10 次析构函数
```

`delete[]` 会正确析构数组中的每个对象。

---

## 4. 错误配对

```cpp
int* arr = new int[10];
delete arr;  // 错误
```

这是未定义行为。

---

## 5. 面试回答

`delete` 用于释放单个对象，`delete[]` 用于释放对象数组。对于对象数组，`delete[]` 会调用每个元素的析构函数。`new` 必须配 `delete`，`new[]` 必须配 `delete[]`，混用会导致未定义行为。
