# const 总结

| 用法位置               | 含义                             | 示例代码                                                     |
| ---------------------- | -------------------------------- | ------------------------------------------------------------ |
| `const int a = 10;`    | 常量，值不可修改                 | `a = 5; // ❌ 错误`                                           |
| `const int* p`         | 指向常量的指针（指针可变）       | `*p = 2; // ❌ p++ ✔`                                         |
| `int* const p`         | 常指针（值可变，地址不可变）     | `*p = 2; ✔ p++ // ❌`                                         |
| `const int* const p`   | 指向常量的常指针                 | `*p = 2; ❌ p++ // ❌`                                         |
| `void func() const;`   | const 成员函数（不能改成员变量） | class B {<br/>public:<br/>    void func() const { x = 0; }  // ❌ const 成员函数返回引用<br/>private:<br/>    int x = 100;<br/>}; |
| `const int& ref = x;`  | 引用常量，不能通过引用修改原值   | `ref = 3; // ❌`                                              |
| `int func(const int);` | 参数是常量，防止被修改           | `x = 4; // ❌ inside func`                                    |
| `const class T;`       | 声明一个类是常量类型（少见）     | 主要用于接口                                                 |

