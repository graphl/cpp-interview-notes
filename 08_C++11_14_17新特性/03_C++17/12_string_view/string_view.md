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
