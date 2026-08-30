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

## 路径初始化与常用调用

```cpp
#include <filesystem>
#include <iostream>
#include <system_error>

namespace fs = std::filesystem;

int main() {
    fs::path root{"data"};                    // 初始化路径
    fs::path file = root / "config.json";     // 使用 / 拼接路径

    std::error_code ec;
    fs::create_directories(root, ec);
    if (ec) {
        std::cerr << ec.message() << '\n';
        return 1;
    }

    std::cout << file.filename() << ' ' << file.extension() << '\n';
    std::cout << std::boolalpha << fs::exists(file, ec) << '\n';

    for (const fs::directory_entry& entry : fs::directory_iterator(root, ec))
        std::cout << entry.path() << '\n';
}
```

路径查询包括 `filename()`、`stem()`、`extension()`、`parent_path()` 和 `lexically_normal()`；文件操作包括 `copy()`、`rename()`、`remove()`。库函数会改变真实文件系统，删除、覆盖和重命名前必须确认目标路径。
