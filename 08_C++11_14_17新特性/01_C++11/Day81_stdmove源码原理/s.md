## 🔹std::move 的真正源码（简化版）

```
template<class T>
remove_reference_t<T>&& move(T&& t) noexcept {
    return static_cast<remove_reference_t<T>&&>(t);
}
```

⚠ 可以看到：

- 没有资源复制
- 没有释放内存
- 单纯 `static_cast` → 右值引用