# C++ 面试题：手写 string 类

## 1. 面试考点

手写 `string` 类，本质考的是 C++ 对象资源管理。

核心考点：

1. 构造函数
2. 析构函数
3. 拷贝构造函数
4. 拷贝赋值运算符
5. 移动构造函数
6. 移动赋值运算符
7. 深拷贝和浅拷贝
8. 自赋值问题
9. 异常安全

如果类中有裸指针资源，通常要遵守“三/五法则”。

---

## 2. 简化版 string 类实现

```cpp
#include <cstring>
#include <utility>

class String {
public:
    String(const char* str = "") {
        if (str == nullptr) {
            str = "";
        }

        size_ = std::strlen(str);
        data_ = new char[size_ + 1];
        std::strcpy(data_, str);
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

    size_t size() const {
        return size_;
    }

    char& operator[](size_t index) {
        return data_[index];
    }

    const char& operator[](size_t index) const {
        return data_[index];
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

## 3. 为什么必须深拷贝？

如果直接复制指针，就是浅拷贝：

```cpp
data_ = other.data_;
```

这样两个对象会指向同一块堆内存。

问题：

1. 一个对象析构后，另一个对象的指针变成悬空指针
2. 两个对象析构时会重复释放同一块内存
3. 修改一个对象可能影响另一个对象

所以拷贝构造必须重新申请内存，再复制字符串内容。

---

## 4. 拷贝赋值为什么要处理自赋值？

错误写法：

```cpp
String& operator=(const String& other) {
    delete[] data_;
    size_ = other.size_;
    data_ = new char[size_ + 1];
    std::strcpy(data_, other.data_);
    return *this;
}
```

如果出现：

```cpp
s = s;
```

`delete[] data_` 会先把自己的字符串释放掉，此时 `other.data_` 也指向同一块已经释放的内存。

所以要判断：

```cpp
if (this != &other)
```

或者使用 copy-swap 写法。

