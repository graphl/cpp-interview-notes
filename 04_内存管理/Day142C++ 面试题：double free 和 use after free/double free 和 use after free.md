# C++ 面试题：double free 和 use after free

## 1. 核心结论

`double free` 是同一块内存被释放两次。

`use after free` 是内存释放后继续使用。

两者都是严重的内存错误。

---

## 2. double free 示例

```cpp
int* p = new int(10);
delete p;
delete p;  // 错误，重复释放
```

---

## 3. use after free 示例

```cpp
int* p = new int(10);
delete p;

std::cout << *p << std::endl;  // 错误，释放后使用
```

---

## 4. 如何避免？

1. 释放后置 `nullptr`
2. 明确资源所有权
3. 避免多个裸指针管理同一资源
4. 使用智能指针
5. 使用 AddressSanitizer 排查

```cpp
delete p;
p = nullptr;
```

---

## 5. 面试回答

`double free` 是同一块动态内存释放两次，可能破坏堆管理结构；`use after free` 是内存释放后仍然访问，属于悬空指针访问。它们都属于未定义行为。实际开发中应使用 RAII 和智能指针减少这类问题。
