# 七、promise 生命周期相关（配合理解）

### promise 销毁但未 set_value

```
std::promise<int> p;
auto f = p.get_future();
// p 被销毁
f.get(); // 抛 std::future_error (broken_promise)
```

📌 shared state 仍存在
 📌 状态变为 ready（异常）

------

# 八、完整“生命周期状态表”

| 状态      | valid | 能 wait | 能 get |
| --------- | ----- | ------- | ------ |
| 默认构造  | false | ❌       | ❌      |
| 已绑定    | true  | ✅       | ✅      |
| 已 ready  | true  | ✅       | ✅      |
| 已 get    | false | ❌       | ❌      |
| move 后源 | false | ❌       | ❌      |

------

# 九、工程级使用原则（非常重要）

1️⃣ **future 必须有 owner**
 2️⃣ **get 只能调用一次**
 3️⃣ **检查 valid 防止 UB**
 4️⃣ **async 必须保存 future**
 5️⃣ **需要多次消费 → shared_future**

------

# 十、面试级总结（背这个）

> `std::future` 的生命周期围绕 shared state；
>  创建后 valid 为 true；
>  调用 get、move、share 后失效；
>  来自 async 的 future 在析构时可能阻塞；
>  正确管理生命周期是并发安全的关键。