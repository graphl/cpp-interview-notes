# C++ 面试题：weak_ptr 的作用

## 1. 核心结论

`weak_ptr` 是对 `shared_ptr` 管理对象的弱引用。

它不增加强引用计数，不拥有对象。

---

## 2. 主要作用

1. 解决 `shared_ptr` 循环引用
2. 安全观察对象是否还存在
3. 缓存、观察者模式中避免延长对象生命周期

---

## 3. 使用 lock 获取对象

```cpp
std::weak_ptr<int> wp;

{
    auto sp = std::make_shared<int>(10);
    wp = sp;
}

if (auto p = wp.lock()) {
    // 对象还存在
} else {
    // 对象已经释放
}
```

---

## 4. expired

```cpp
if (wp.expired()) {
    // 对象已经不存在
}
```

但实际使用对象时，更推荐 `lock()`，因为它能在对象存在时得到一个临时 `shared_ptr`。

---

## 5. 面试回答

`weak_ptr` 不拥有对象，也不会增加 `shared_ptr` 的强引用计数。它常用于解决循环引用，也可以安全判断对象是否还存在。使用时通过 `lock()` 尝试获取 `shared_ptr`，如果获取成功说明对象仍然有效。
