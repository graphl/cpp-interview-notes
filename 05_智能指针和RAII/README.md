# C++ 智能指针与 RAII

RAII 的核心是把“必须成对出现的获取和释放”变成一个对象的不变量。智能指针只是 RAII 管理动态对象的一组常用工具，不等于 RAII 的全部。

## 推荐学习顺序

```text
资源所有权与 RAII
  -> unique_ptr 独占所有权
  -> shared_ptr 控制块与强引用
  -> weak_ptr 与弱引用
  -> 循环引用、deleter、make_shared
  -> 并发与异常安全边界
```

## 必会问题

1. `unique_ptr` 为什么不可复制但可以移动？
2. `shared_ptr` 对象和控制块的生命周期为什么不同？
3. `weak_ptr::lock()` 需要解决什么并发窗口？
4. 循环引用为什么让强引用计数无法归零？
5. `make_shared` 的单次分配有什么收益，又可能延迟释放哪块内存？
6. “不同 shared_ptr 实例可并发操作”与“被管理对象线程安全”有什么区别？

## 待补重点

`enable_shared_from_this`、别名构造函数、数组特化、状态型删除器，以及原子 `shared_ptr` 的使用边界。
