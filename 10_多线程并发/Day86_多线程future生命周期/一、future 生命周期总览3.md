# 五、阶段 4：析构（最容易忽略）

### ❗ 重点规则（async 专属）

> 如果 future 来自 `std::async(std::launch::async)`
>  且任务尚未完成
>  那么 **future 的析构会阻塞，直到任务完成**

### 示例（经典坑）

```
void foo() {
    std::async(std::launch::async, [] {
        std::this_thread::sleep_for(5s);
    });
} // ❗ 这里阻塞 5 秒
```

📌 因为：

- 临时 future 析构
- 标准要求隐式 join

------

### 正确做法

```
auto f = std::async(std::launch::async, task);
// 保持 f 活着
```

------

# 六、异常 & 生命周期

### 子线程抛异常

```
auto f = std::async([] {
    throw std::runtime_error("oops");
});
```

- 异常存入 shared state
- future 仍然 valid
- 在 `get()` 时重新抛出

------

> 