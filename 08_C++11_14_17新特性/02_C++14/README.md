# C++14 专题索引

| 序号 | 专题 | 核心问题 |
|---:|---|---|
| 00 | C++14 总览 | C++14 的定位、完整特性清单和版本辨析 |
| 01 | 泛型 Lambda | `auto` 形参和模板化调用运算符 |
| 02 | Lambda 初始化捕获 | 移动捕获和闭包成员初始化 |
| 03 | 函数返回类型推导 | 普通函数如何使用 `auto` 推导返回类型 |
| 04 | `decltype(auto)` | 如何保留引用与 `const` 属性 |
| 05 | `constexpr` 增强 | 循环、分支和局部变量如何参与常量计算 |
| 06 | 变量模板 | 编译期变量如何模板化 |
| 07 | 二进制字面量 | 使用 `0b` 表示二进制整数 |
| 08 | 数字分隔符 | 使用单引号提高数字可读性 |
| 09 | `make_unique` | 安全、简洁地创建独占智能指针 |
| 10 | `integer_sequence` | 如何生成编译期整数下标序列 |
| 11 | `std::exchange` | 替换值并返回旧值 |
| 12 | 共享锁 | `shared_timed_mutex` 与 `shared_lock` |

推荐顺序：

```text
泛型 Lambda -> 初始化捕获
-> 返回类型推导 -> decltype(auto)
-> constexpr -> 变量模板
-> make_unique -> integer_sequence
-> exchange -> 共享锁
```
