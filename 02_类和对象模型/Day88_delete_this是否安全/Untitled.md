## 9. 常见应用场景

`delete this` 常见于自管理生命周期的对象，例如：

1. 引用计数对象
2. COM 风格对象的 `Release()`
3. 某些事件回调对象执行完后自销毁
4. 框架内部封装的异步任务对象

示例：

```cpp
class Task {
public:
    void run() {
        // 执行任务
        delete this;
    }
};

int main() {
    Task* task = new Task;
    task->run();
}
```

这种写法要求调用者非常清楚：`run()` 之后对象已经不存在。

所以它对接口设计要求很高，否则很容易误用。

---

## 10. 更推荐的做法

现代 C++ 中更推荐使用智能指针管理生命周期。

### 使用 `std::unique_ptr`

```cpp
#include <memory>

class A {
public:
    void work() {}
};

int main() {
    std::unique_ptr<A> p = std::make_unique<A>();
    p->work();
}
```

`unique_ptr` 离开作用域时会自动释放对象，不需要对象自己 `delete this`。

### 使用 `std::shared_ptr`

```cpp
#include <memory>

class A : public std::enable_shared_from_this<A> {
public:
    std::shared_ptr<A> getSelf() {
        return shared_from_this();
    }
};
```

如果对象需要共享所有权，应使用 `shared_ptr`，而不是让对象自己删除自己。

---

## 11. 面试回答模板

可以这样回答：

> `delete this` 在 C++ 中语法合法，但不一定安全。只有当对象是通过 `new` 创建的，并且删除之后不再访问该对象，也不会被重复释放时，才是安全的。它不能用于栈对象、全局对象、成员对象，否则会产生未定义行为。执行 `delete this` 后，`this` 指针和外部保存的对象指针都会变成悬空指针，所以不能再调用成员函数或访问成员变量。实际开发中更推荐使用 RAII 和智能指针管理对象生命周期。

---

## 12. 总结

| 问题                                  | 答案                             |
| ------------------------------------- | -------------------------------- |
| `delete this` 语法合法吗？            | 合法                             |
| 一定安全吗？                          | 不一定                           |
| 栈对象能 `delete this` 吗？           | 不能                             |
| `new` 出来的对象能 `delete this` 吗？ | 满足条件时可以                   |
| 删除后还能访问成员吗？                | 不能                             |
| 外部指针会自动变成 `nullptr` 吗？     | 不会                             |
| 推荐日常使用吗？                      | 不推荐                           |
| 更好的方式是什么？                    | RAII、`unique_ptr`、`shared_ptr` |

最终记忆：

> `delete this` 可以用，但必须保证对象来自堆，并且删除后对象彻底不再被使用。它是合法但危险的生命周期自管理手段。