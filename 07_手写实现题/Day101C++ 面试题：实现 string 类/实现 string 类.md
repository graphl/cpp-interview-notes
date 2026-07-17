# C++ 面试题：实现 string 类

## 1. 考点

手写 `string` 类主要考资源管理。

核心点：

1. 深拷贝
2. 析构释放内存
3. 拷贝构造
4. 赋值运算符
5. 移动构造和移动赋值

---

## 2. 简化实现

```cpp
#include <cstring>
#include <utility>

class String {
public:
    String(const char* s = "") {
        size_ = std::strlen(s);
        data_ = new char[size_ + 1];
        std::strcpy(data_, s);
    }

    ~String() {
        delete[] data_;
    }

    String(const String& other) {
        size_ = other.size_;
        data_ = new char[size_ + 1];
        std::strcpy(data_, other.data_);
    }

    String& operator=(const String& other) {
        if (this != &other) {
            String temp(other);
            swap(temp);
        }
        return *this;
    }

    String(String&& other) noexcept
        : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;
        other.size_ = 0;
    }

    String& operator=(String&& other) noexcept {
        if (this != &other) {
            delete[] data_;
            data_ = other.data_;
            size_ = other.size_;
            other.data_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }

    const char* c_str() const {
        return data_ ? data_ : "";
    }

    void swap(String& other) noexcept {
        std::swap(data_, other.data_);
        std::swap(size_, other.size_);
    }

private:
    char* data_;
    size_t size_;
};
```

---

## 3. 为什么赋值用 copy-swap？

优点：

1. 自动处理自赋值
2. 异常安全
3. 代码简洁

---

## 4. 面试回答

手写 `string` 的重点是深拷贝和资源释放。类中有裸指针成员，所以必须自定义析构函数、拷贝构造和拷贝赋值。现代 C++ 还应实现移动构造和移动赋值，避免临时对象拷贝，提高效率。
