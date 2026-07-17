# delete this 是否安全？

## 1. 先给结论

`delete this` 语法上是允许的，但只有在非常严格的条件下才是安全的。

一句话总结：

> 只有当对象确实是通过 `new` 创建，并且执行 `delete this` 之后不再访问该对象时，才可能是安全的。

也就是说，`delete this` 本身不是一定错误，但它非常危险，实际开发中不推荐随便使用。

---

## 2. `delete this` 做了什么？

在成员函数中，`this` 指针指向当前对象。

```cpp
class A {
public:
    void destroy() {
        delete this;
    }
};
```

调用：

```cpp
A* p = new A;
p->destroy();
```

执行 `delete this` 时，相当于：

```cpp
delete p;
```

它会做两件事：

1. 调用当前对象的析构函数
2. 释放对象占用的堆内存

---

## 3. 什么情况下是安全的？

必须同时满足下面几个条件：

| 条件 | 说明 |
|---|---|
| 对象必须由 `new` 创建 | 不能是栈对象、全局对象、成员对象 |
| 对象只能被删除一次 | 否则会 double free |
| `delete this` 后不能再访问成员变量或成员函数 | 此时 `this` 已经悬空 |
| 外部不能再继续使用原来的对象指针 | 原指针已经变成悬空指针 |
| 析构函数访问权限和多态删除要正确 | 通过基类删除时析构函数应为 virtual |

安全示例：

```cpp
class RefCounted {
public:
    void release() {
        if (--ref_count_ == 0) {
            delete this;
        }
    }

private:
    int ref_count_ = 1;
};

int main() {
    RefCounted* p = new RefCounted;
    p->release();

    // p 已经失效，不能再使用
    p = nullptr;
}
```

这个例子里，对象由 `new` 创建，并且 `release()` 后不再访问对象，所以符合基本安全条件。

---

## 4. 危险情况一：对象在栈上

```cpp
class A {
public:
    void destroy() {
        delete this;
    }
};

int main() {
    A a;
    a.destroy();   // 错误
}
```

`a` 是栈对象，不是通过 `new` 创建的。

`delete this` 会尝试释放一块不属于堆分配器管理的内存，结果是未定义行为。

可能出现的问题：

1. 程序崩溃
2. 堆管理结构被破坏
3. 表面不崩，但后续随机出错

---

