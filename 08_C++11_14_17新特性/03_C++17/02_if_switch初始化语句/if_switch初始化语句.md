# C++17：`if` 和 `switch` 初始化语句

C++17 允许在条件判断前初始化变量：

```cpp
if (auto it = table.find(key); it != table.end()) {
    use(it->second);
}
```

初始化语句和条件之间使用分号。变量的作用域覆盖 `if`、所有 `else if` 和 `else` 分支，但不会泄漏到语句之后。

这个特性适合查找、加锁和状态查询，可以缩小变量作用域。它仍是运行期分支，不要与 `if constexpr` 混淆。
