# C++17：`std::filesystem`

`<filesystem>` 提供跨平台路径表示和文件系统操作：

```cpp
namespace fs = std::filesystem;

for (const auto& entry : fs::directory_iterator(".")) {
    std::cout << entry.path() << '\n';
}
```

常用能力包括 `path`、`exists`、`file_size`、`create_directories`、`copy`、`rename` 和目录迭代。

多数操作既有抛异常版本，也有接收 `std::error_code` 的非抛异常重载。工程中还需考虑权限、符号链接、路径编码和检查后再操作产生的 TOCTOU 竞争。
