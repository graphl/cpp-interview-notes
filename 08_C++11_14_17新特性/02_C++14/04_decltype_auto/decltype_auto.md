# C++14：`decltype(auto)`

`decltype(auto)` 使用 `decltype` 规则推导类型，可以保留表达式的引用和 `const` 属性。

```cpp
int value = 10;

auto get_value() { return value; }             // int
decltype(auto) get_ref() { return (value); }   // int&
```

括号会影响 `decltype`：对未加括号的变量名得到声明类型，对一般表达式则根据值类别得到 `T&`、`T&&` 或 `T`。

最大风险是意外返回悬空引用：

```cpp
decltype(auto) bad() {
    int local = 0;
    return (local);  // 返回 int&，函数结束后悬空
}
```
