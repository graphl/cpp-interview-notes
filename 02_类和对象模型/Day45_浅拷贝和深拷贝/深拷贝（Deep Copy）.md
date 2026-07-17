## 深拷贝（Deep Copy）

**定义**：不仅复制指针，还要复制指针指向的数据，保证新对象有自己独立的内存。

**结果**：对象互不干扰，释放时安全。

```
#include <iostream>
#include <cstring>
using namespace std;

class Deep {
public:
    char* data;

    Deep(const char* str) {
        data = new char[strlen(str) + 1];
        strcpy(data, str);
    }

    // 深拷贝构造函数
    Deep(const Deep& other) {
        data = new char[strlen(other.data) + 1];
        strcpy(data, other.data);
    }

    ~Deep() {
        delete[] data;
    }
};

int main() {
    Deep a("world");
    Deep b = a; // 深拷贝

    cout << a.data << endl; // world
    cout << b.data << endl; // world

    b.data[0] = 'W';
    cout << a.data << endl; // world
    cout << b.data << endl; // World （互不影响）
}

```

