**接口类（Interface Class）**
 一种特殊的抽象类，所有函数都是纯虚函数。相当于 Java 的 interface。

```
struct IShape {
    virtual void draw() = 0;
    virtual ~IShape() {}
};
```

**特点**：

- 完全用于定义“规范/契约”。
- 不包含任何状态（成员变量）。
- 每个派生类必须实现所有函数。