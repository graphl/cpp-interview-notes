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
