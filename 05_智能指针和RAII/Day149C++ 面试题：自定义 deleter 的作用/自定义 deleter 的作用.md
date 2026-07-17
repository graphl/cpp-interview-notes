# C++ 面试题：自定义 deleter 的作用

## 1. 核心结论

自定义 deleter 用来指定智能指针释放资源时的清理方式。

它不仅能释放 `new` 出来的对象，也能管理文件、socket、C 接口资源等。

---

## 2. shared_ptr 自定义 deleter

```cpp
std::shared_ptr<FILE> fp(std::fopen("a.txt", "r"), [](FILE* f) {
    if (f) {
        std::fclose(f);
    }
});
```

当最后一个 `shared_ptr` 销毁时，会调用自定义 deleter。

---

## 3. unique_ptr 自定义 deleter

```cpp
using FilePtr = std::unique_ptr<FILE, decltype(&std::fclose)>;

FilePtr fp(std::fopen("a.txt", "r"), &std::fclose);
```

---

## 4. 使用场景

1. 管理 `FILE*`
2. 管理 socket
3. 管理第三方库资源
4. 对象需要特殊释放函数
5. 数组或内存池回收

---

## 5. 面试回答

自定义 deleter 可以让智能指针在释放资源时执行指定清理逻辑。它常用于管理非 `new/delete` 资源，比如 `FILE*` 需要 `fclose`，socket 需要 close，第三方库对象可能有专门的释放函数。这样可以把这些资源也纳入 RAII 管理。
