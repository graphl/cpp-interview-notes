# C++17：`std::from_chars` 和 `std::to_chars`

`<charconv>` 提供数字与字符序列之间的低开销转换：

```cpp
int value = 0;
std::string_view text = "123";

auto [ptr, ec] = std::from_chars(
    text.data(), text.data() + text.size(), value);
```

它不依赖区域设置、不分配内存，也不通过异常报告普通解析失败，而是返回指针和 `std::errc`。

必须检查 `ec`，并根据需求确认 `ptr` 是否到达输入末尾，否则 `"123abc"` 可能被当成成功解析前缀。

## 字符串转数字

```cpp
#include <charconv>
#include <iostream>
#include <string_view>
#include <system_error>

bool parse_int(std::string_view text, int& output) {
    const char* begin = text.data();
    const char* end = begin + text.size();
    auto result = std::from_chars(begin, end, output);
    return result.ec == std::errc{} && result.ptr == end;
}

int main() {
    int value = 0;
    if (parse_int("123", value)) std::cout << value << '\n';
}
```

## 数字转字符

```cpp
#include <charconv>
#include <iostream>
#include <system_error>

int main() {
    char buffer[32];
    auto result = std::to_chars(buffer, buffer + sizeof buffer, 255, 16);
    if (result.ec == std::errc{})
        std::cout.write(buffer, result.ptr - buffer); // 输出 ff
}
```

`to_chars` 不会自动添加 `\0`，返回的 `ptr` 指向已写数据末尾。C++17 的整数转换支持最稳定；浮点重载在较老标准库实现中可能不完整，应结合实际工具链验证。
