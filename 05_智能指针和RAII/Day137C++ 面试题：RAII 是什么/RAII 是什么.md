# C++ 面试题：RAII 是什么

## 1. 核心结论

RAII 是 Resource Acquisition Is Initialization。

意思是：资源获取即初始化，用对象生命周期管理资源生命周期。

---

## 2. 基本思想

在构造函数中获取资源，在析构函数中释放资源。

```cpp
class File {
public:
    File(const char* path) {
        fp_ = std::fopen(path, "r");
    }

    ~File() {
        if (fp_) {
            std::fclose(fp_);
        }
    }

private:
    FILE* fp_;
};
```

对象离开作用域时，析构函数自动执行，资源自动释放。

---

## 3. 常见 RAII 类型

| 类型 | 管理资源 |
|---|---|
| `std::unique_ptr` | 堆对象 |
| `std::shared_ptr` | 共享堆对象 |
| `std::lock_guard` | 互斥锁 |
| `std::fstream` | 文件句柄 |
| `std::vector` | 动态内存 |

---

## 4. RAII 的优势

1. 自动释放资源
2. 异常安全
3. 避免内存泄漏
4. 让资源所有权清晰

---

## 5. 面试回答

RAII 是 C++ 中非常重要的资源管理思想。它通过对象生命周期管理资源生命周期，在构造函数中获取资源，在析构函数中释放资源。这样即使函数提前返回或发生异常，局部对象析构时也能自动释放资源。
