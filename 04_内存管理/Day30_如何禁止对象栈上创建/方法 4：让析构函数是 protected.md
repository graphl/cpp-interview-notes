#### **方法 4：让析构函数是 `protected`**

这种方法也常见：

```
class HeapOnly {
protected:
    ~HeapOnly() = default; // 栈对象会在作用域结束时自动调用析构 → 编译错误
public:
    HeapOnly() = default;
};

int main() {
    // HeapOnly h;  // ❌ 编译错误：析构是 protected
    HeapOnly* p = new HeapOnly(); // ✅
    delete p; // ✅ 通过指针 delete 时，类内部可以访问析构
}
```

- 栈对象离开作用域需要调用析构函数，但外部不能访问 protected 析构，所以无法栈分配。
- `new` + `delete` 是可以的，因为 `delete` 会在类内部的作用域中访问析构。