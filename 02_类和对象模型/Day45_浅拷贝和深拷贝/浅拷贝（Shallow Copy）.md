## 浅拷贝（Shallow Copy）

**定义**：对象拷贝时，只复制成员变量的值。

如果成员里有指针，只会拷贝指针本身（地址），不会复制指针指向的数据。

**结果**：两个对象指向同一块内存。释放时可能会 **重复释放 (double free)**。

```
#include <iostream>
#include <cstring>
using namespace std;

class Shallow {
public:
    char* data;

    Shallow(const char* str) {
        data = new char[strlen(str) + 1];
        strcpy(data, str);
    }

    // 默认拷贝构造函数：浅拷贝
    // Shallow(const Shallow& other) { this->data = other.data; }

    ~Shallow() {
        delete[] data;
    }
};

int main() {
    Shallow a("hello");
    Shallow b = a; // 浅拷贝

    cout << a.data << endl; // hello
    cout << b.data << endl; // hello

    // 程序结束时，a和b都会调用析构函数 -> 两次delete同一块内存 -> 崩溃
}

```

