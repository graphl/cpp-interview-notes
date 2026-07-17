# C如何调用C++ 成员函数

## 1. 对外暴露 `extern "C"` 的接口函数

在 C++ 里写一个 `extern "C"` 的包装函数，这个函数再去调用 C++ 成员函数。
 C 代码只需要调用包装函数。

## 2. 回调方式（C 调用 C++ 成员函数指针）

如果要在 C 中注册回调，然后回调 C++ 的成员函数，可以用 **静态函数 + `this` 指针** 方案。

```
#include <stdio.h>

class MyClass {
public:
    static void callback(void* ctx, int x) {
        MyClass* self = static_cast<MyClass*>(ctx);
        self->handle(x);
    }

    void handle(int x) {
        printf("C++ handle called with %d\n", x);
    }
};

// C 端需要的函数指针类型
typedef void (*c_callback)(void* ctx, int x);

// 模拟 C 函数：接受函数指针和上下文
void c_function(c_callback cb, void* ctx) {
    cb(ctx, 123);
}

int main() {
    MyClass obj;
    c_function(&MyClass::callback, &obj); // 回调到成员函数
}
```

