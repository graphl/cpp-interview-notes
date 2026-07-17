`sizeof(Empty)` 通常是 1，但 **编译器可以做优化**（如：不放在数组里时可能优化掉）。

多继承中，空基类可能被优化为 0（叫做 **空基类优化 EBO**），见下方例子。

class A {}; // 空类
class B {}; // 空类
class C : public A, public B {};  // 多继承

int main() {
    std::cout << sizeof(C); // 可能输出 1（优化后）
}