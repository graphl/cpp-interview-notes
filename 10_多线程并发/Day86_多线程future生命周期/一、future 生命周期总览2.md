# 三、阶段 2：使用中（valid == true）

### 可以做什么？

| 操作         | 结果           |
| ------------ | -------------- |
| `wait()`     | 等             |
| `wait_for()` | 等             |
| `get()`      | 取（只能一次） |
| `valid()`    | true           |

### 不能做什么？

- 不能复制
- 不能多次 get

------

# 四、阶段 3：失效（valid == false）

future **失效的 4 种情况（必背）**

## 1️⃣ 调用 `get()`

```
auto f = std::async([]{ return 1; });
f.get();
f.valid(); // false
```

📌 **get 会消费 shared state**

------

## 2️⃣ 被 move 走

```
std::future<int> f1 = std::async(...);
std::future<int> f2 = std::move(f1);

f1.valid(); // false
f2.valid(); // true
```

------

## 3️⃣ 调用 `share()`

```
auto f = std::async(...);
auto sf = f.share();

f.valid();  // false
sf.valid(); // true
```

------

## 4️⃣ 默认构造（从一开始就无效）

```
std::future<int> f;
f.valid(); // false
```

------

> 