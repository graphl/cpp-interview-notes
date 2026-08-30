# C++17：`if` 和 `switch` 初始化语句

C++17 允许在条件判断前初始化变量：

```cpp
if (auto it = table.find(key); it != table.end()) {
    use(it->second);
}
```

初始化语句和条件之间使用分号。变量的作用域覆盖 `if`、所有 `else if` 和 `else` 分支，但不会泄漏到语句之后。

这个特性适合查找、加锁和状态查询，可以缩小变量作用域。它仍是运行期分支，不要与 `if constexpr` 混淆。

## 使用方法

```cpp
#include <iostream>
#include <map>
#include <string>

int main() {
    std::map<int, std::string> table{{1, "ready"}};

    if (auto it = table.find(1); it != table.end()) {
        std::cout << it->second << '\n';
    } else {
        // it 在 else 中仍然有效
        std::cout << "missing\n";
    }

    switch (int status = 2; status) {
    case 0: std::cout << "idle\n"; break;
    case 2: std::cout << "running\n"; break;
    default: break;
    }
}
```

语法是 `if (初始化语句; 条件)` 或 `switch (初始化语句; 条件)`。特别适合迭代器查找、解析结果和带锁判断；初始化变量会在整个条件语句结束时销毁。
