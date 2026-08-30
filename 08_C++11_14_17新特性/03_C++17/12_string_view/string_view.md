# C++17：`std::string_view`

`string_view` 是对连续字符序列的非拥有只读视图，通常只保存指针和长度。

```cpp
void parse(std::string_view text);

parse("hello");
parse(std::string{"world"});
```

它可以减少字符串复制和临时分配，但不管理底层字符的生命周期：

```cpp
std::string_view bad() {
    return std::string("temporary"); // 返回悬空视图
}
```

另外，`string_view::data()` 指向的数据不保证以 `\0` 结尾，不能无条件传给要求 C 字符串的接口。

## 初始化、传参与查询

```cpp
#include <iostream>
#include <string>
#include <string_view>

std::string_view trim_prefix(std::string_view text) {
    while (!text.empty() && text.front() == ' ')
        text.remove_prefix(1);               // 只移动视图，不修改原字符串
    return text;
}

void print(std::string_view text) {
    std::cout.write(text.data(), static_cast<std::streamsize>(text.size()));
    std::cout << '\n';
}

int main() {
    std::string storage = "  hello world";
    std::string_view view{storage};           // 指向 storage 的字符区间
    view = trim_prefix(view);                 // 函数调用并接收子视图
    print(view.substr(0, 5));

    storage += "!";                           // 可能重分配，旧 view 可能悬空
}
```

常用接口有 `size()`、`empty()`、`substr()`、`find()`、`remove_prefix()` 和 `remove_suffix()`。它不拥有内存，适合作为同步函数的只读参数；需要长期保存时通常复制为 `std::string`。
