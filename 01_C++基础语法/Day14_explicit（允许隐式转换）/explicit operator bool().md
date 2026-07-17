# explicit operator bool()

```
// 没有 explicit（允许隐式转换）
class MyWrapper {
public:
    operator bool() const {
        return true;
    }
};

int main() {
    MyWrapper w;
    bool b = w;     // ✅ 隐式转换
}

// 使用 explicit（更安全）
class MyWrapper {
public:
    explicit operator bool() const {
        return true;
    }
};

int main() {
    MyWrapper w;
    bool b = w;      // ❌ 编译错误
    bool b2 = static_cast<bool>(w);  // ✅ 显式转换
    if (w) {}        // ✅ 可以用于 if 判断
}
/// /while/switch 允许使用
/// switch 使用    explicit operator int();

```

