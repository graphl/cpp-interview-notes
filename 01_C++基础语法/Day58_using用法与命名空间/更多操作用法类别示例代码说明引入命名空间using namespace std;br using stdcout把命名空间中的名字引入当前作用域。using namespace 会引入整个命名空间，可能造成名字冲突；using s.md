| 用法类别                        | 示例代码                                                     | 说明                                                         |
| ------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **引入命名空间**                | using namespace std;<br />using std::cout                    | 把命名空间中的名字引入当前作用域。`using namespace` 会引入整个命名空间，可能造成名字冲突；`using std::cout` 只引入某个符号，更安全。 |
| **类型别名**                    | using uint = unsigned int                                    | 类似 `typedef`，更直观。                                     |
| **模板别名**                    | template<class T><br />using vec = std::vector<T>;<br>vec<int> v; | 允许为模板定义别名，`typedef` 不支持。                       |
| **继承时解除隐藏 / 改变可见性** | struct Base { void f(int){}; protected: int x; };<br>struct Derived: Base {<br>  using Base::f; // 避免函数被隐藏<br>  using Base::x; // 改变访问权限 (protected→public)<br>};<br> | 派生类中 `using` 可让基类同名函数在子类中可见，或者改变成员的访问权限。 |
| **别名模板参数 (C++11+)**       | template<typename T><br />using Ptr = T*;<br>Ptr<int> p; // int*<br> | 提高泛型代码可读性。                                         |
| **函数指针/类型简化**           | using Func = void(*)(int);<br>Func f = nullptr;<br>          | 让复杂函数指针更易读。                                       |
| **与 Concepts 结合 (C++20)**    | cpp<br>template<typename T><br>concept Integral = std::is_integral_v<T>;<br>using Int = int;<br> | 本质还是别名，但常与 Concepts 搭配使用。                     |