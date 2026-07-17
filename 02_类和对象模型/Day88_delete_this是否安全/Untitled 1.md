## 5. 危险情况二：删除后继续访问成员

```cpp
class A {
public:
    void destroy() {
        delete this;
        x = 10;        // 错误：this 已经失效
        print();       // 错误：对象已经被销毁
    }

    void print() {}

private:
    int x = 0;
};
```

`delete this` 执行后，对象生命周期已经结束。

此时再访问成员变量、调用成员函数，都是对悬空指针的访问，属于未定义行为。

---

## 6. 危险情况三：外部指针继续使用

```cpp
class A {
public:
    void destroy() {
        delete this;
    }

    void hello() {}
};

int main() {
    A* p = new A;
    p->destroy();

    p->hello();   // 错误：p 已经是悬空指针
    delete p;     // 错误：重复释放
}
```

`destroy()` 内部已经释放了对象。

外部的 `p` 不会自动变成 `nullptr`，它仍然保存原来的地址，但这块内存已经无效。

## 7. 危险情况四：对象是成员对象

```cpp
class A {
public:
    void destroy() {
        delete this;
    }
};

class B {
public:
    A a;
};

int main() {
    B b;
    b.a.destroy();   // 错误
}
```

`b.a` 是 `B` 对象的一部分，不是单独通过 `new` 分配出来的。

对成员对象执行 `delete this` 会破坏整个对象的内存布局。

---

## 8. 多态场景下要注意虚析构函数

如果通过基类指针触发对象自毁，基类析构函数应该是虚函数。

```cpp
class Base {
public:
    virtual ~Base() = default;

    void destroy() {
        delete this;
    }
};

class Derived : public Base {
public:
    ~Derived() {
        // 释放 Derived 自己的资源
    }
};

int main() {
    Base* p = new Derived;
    p->destroy();
}
```

如果 `Base` 的析构函数不是 `virtual`，通过 `Base*` 删除 `Derived` 对象时，只调用基类析构函数，派生类资源可能无法正确释放。

