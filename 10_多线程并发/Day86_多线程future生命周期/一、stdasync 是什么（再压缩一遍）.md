## 一、`std::async` 是什么（再压缩一遍）

> **`std::async` 用来启动一个异步任务，并返回一个 `std::future` 获取结果。**

你可以把它理解成：

```
std::async
= 自动创建线程
+ 自动管理 promise
+ 返回 future
+ 自动传播异常
+ RAII 管理
```

------

## 二、最基本 & 正确的使用方式（推荐）

```
#include <future>
#include <iostream>

int work() {
    return 42;
}

int main() {
    std::future<int> fut =
        std::async(std::launch::async, work);

    std::cout << fut.get() << std::endl;
}
```

**关键点：**

- ✔ 显式写 `std::launch::async`
- ✔ 保存返回的 `future`
- ✔ 用 `get()` 取结果

------

## 三、使用 lambda（90% 场景）

```
auto fut = std::async(std::launch::async, [] {
    std::this_thread::sleep_for(std::chrono::seconds(1));
    return 100;
});

std::cout << fut.get();
```

------

## 四、传参方式（值 / 引用）

### 1️⃣ 传值（安全）

```
void f(int x, std::string s);

auto fut = std::async(std::launch::async, f, 10, "abc");
```

------

### 2️⃣ 传引用（⚠️ 必须保证生命周期）

```
void inc(int& x) { ++x; }

int v = 0;
auto fut = std::async(std::launch::async, inc, std::ref(v));
fut.get();
```

------

## 五、launch 策略（非常重要）

### 1️⃣ `std::launch::async`（强烈推荐）

```
std::async(std::launch::async, task);
```

- 一定新线程
- 真并发
- 析构 future 会 **join**

------

### 2️⃣ `std::launch::deferred`

```
std::async(std::launch::deferred, task);
```

- 不创建线程
- `get()` 时在当前线程执行

```
fut.get(); // 此处才运行
```

------

### 3️⃣ 默认策略（⚠️ 不推荐）

```
std::async(task); // async | deferred
```

- 行为不确定
- 可能不并发

📌 **工程代码应避免**

------

## 六、异常处理（必须知道）

```
auto fut = std::async(std::launch::async, [] {
    throw std::runtime_error("error");
});

try {
    fut.get();   // 这里抛异常
} catch (const std::exception& e) {
    std::cout << e.what();
}
```

------

## 七、async 的“析构阻塞”坑（高频）

### ❌ 错误示例

```
void foo() {
    std::async(std::launch::async, [] {
        std::this_thread::sleep_for(5s);
    });
} // 这里阻塞 5 秒
```

### 原因

- 返回的 `future` 是临时对象
- 析构时等待任务完成（隐式 join）

------

### ✅ 正确写法

```
auto fut = std::async(std::launch::async, task);
// 或者存进容器
```

------

## 八、多个 async 并发执行

```
auto f1 = std::async(std::launch::async, task1);
auto f2 = std::async(std::launch::async, task2);

f1.get();
f2.get();
```

------

## 九、什么时候 **不该** 用 async

❌ 频繁创建短任务
 ❌ 想用线程池
 ❌ 需要取消任务
 ❌ 精细控制线程数量

👉 async ≠ 线程池

------

## 十、async vs thread（快速对照）

| 对比   | async | thread |
| ------ | ----- | ------ |
| 返回值 | ✅     | ❌      |
| 异常   | 自动  | 手动   |
| join   | 自动  | 手动   |
| 易用性 | ⭐⭐⭐⭐  | ⭐⭐     |
| 控制力 | ⭐⭐    | ⭐⭐⭐⭐   |

------

## 十一、工程级使用准则（总结）

**记住这 5 条就够了：**

1️⃣ **总是显式写 `std::launch::async`**
 2️⃣ **保存 future，避免析构阻塞**
 3️⃣ **不要用默认策略**
 4️⃣ **任务粒度不要太小**
 5️⃣ **多消费者用 `shared_future`**

------

## 十二、面试级总结（背这个）

> `std::async` 启动异步任务并返回 future；
>  `launch::async` 强制新线程，`launch::deferred` 延迟执行；
>  默认策略不确定；
>  future 析构可能阻塞；
>  异常在 `get()` 时传播。