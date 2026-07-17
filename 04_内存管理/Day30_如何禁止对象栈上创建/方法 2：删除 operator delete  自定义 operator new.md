#### **方法 2：删除 `operator delete` / 自定义 `operator new`**

- 原理：阻止栈对象析构（不安全方法）
- 缺点：可能导致无法 `delete`，不推荐直接这么干。