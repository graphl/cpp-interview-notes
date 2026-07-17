# 04 异常路径或提前 return 泄漏

## 1. 类型定义

异常路径泄漏是指正常流程会释放资源，但错误分支、异常、提前 `return`、`break`、`continue` 导致释放代码没有执行。

这种问题在 C 风格资源管理和复杂函数中很常见。

---

## 2. 典型现象

```text
正常测试不容易复现
错误输入或异常场景下内存上涨
压测失败请求越多，内存增长越明显
代码里有多个 return 路径
```

---

## 3. 典型代码

```cpp
bool process(bool error) {
    char* buf = new char[1024];

    if (error) {
        return false; // 泄漏
    }

    delete[] buf;
    return true;
}
```

异常场景：

```cpp
void process() {
    char* buf = new char[1024];

    may_throw();

    delete[] buf;
}
```

如果 `may_throw()` 抛异常，`delete[] buf` 不会执行。

---

## 4. 排查方法

1. 检查函数是否有多个出口
2. 检查 `new/malloc/open/lock` 后是否所有路径都释放
3. 使用 ASan 覆盖异常路径
4. 对错误路径做单元测试
5. 重点看 `return false`、`goto fail`、`throw` 前后的资源释放

搜索：

```bash
rg "new |malloc|return|throw"
```

---

## 5. 修复方式

使用 RAII：

```cpp
bool process(bool error) {
    std::vector<char> buf(1024);

    if (error) {
        return false;
    }

    return true;
}
```

智能指针：

```cpp
bool process(bool error) {
    auto buf = std::make_unique<char[]>(1024);

    if (error) {
        return false;
    }

    return true;
}
```

锁资源：

```cpp
std::lock_guard<std::mutex> lock(mtx);
```

---

## 6. 面试总结

异常路径泄漏的本质是资源释放依赖手写流程。C++ 中应该用 RAII 让资源释放绑定到对象析构，这样不管正常返回、提前返回还是异常退出，都能自动释放。
