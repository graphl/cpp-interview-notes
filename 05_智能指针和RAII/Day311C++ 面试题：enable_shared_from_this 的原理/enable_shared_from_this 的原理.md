# C++ 面试题：enable_shared_from_this 的原理

## 1. 为什么不能直接 shared_ptr(this)

```cpp
struct Session {
    std::shared_ptr<Session> self() {
        return std::shared_ptr<Session>(this); // 错误
    }
};
```

外部如果已经有一个 `shared_ptr<Session>`，上面的代码会为同一裸指针创建第二个控制块：

```text
控制块 A ----> 同一个 Session 对象 <---- 控制块 B
```

两个强引用计数会分别归零并分别删除同一对象，导致 double free。

## 2. 正确用法

```cpp
#include <memory>

class Session : public std::enable_shared_from_this<Session> {
public:
    std::shared_ptr<Session> self() {
        return shared_from_this();
    }
};

auto session = std::make_shared<Session>();
auto same_owner = session->self();
```

`same_owner` 和 `session` 共享同一个控制块。

## 3. 常见实现原理

`enable_shared_from_this<T>` 内部可理解为保存了一个指向自己的 `weak_ptr<T>`：

```text
第一个 shared_ptr<T> 接管对象
  -> 检测 T 是否继承 enable_shared_from_this<T>
  -> 用当前控制块初始化对象内部的 weak_this

shared_from_this()
  -> 从 weak_this 构造 shared_ptr
  -> 强引用计数加一，但不创建新控制块
```

具体成员名称和初始化方法属于标准库实现细节，但共享原控制块是核心语义。

## 4. 常见错误

### 在构造函数里调用 shared_from_this

```cpp
Session::Session() {
    auto p = shared_from_this(); // 通常抛 std::bad_weak_ptr
}
```

构造函数执行时，外层 `shared_ptr` 往往还没完成接管，内部弱引用尚未绑定控制块。应在工厂函数完成 `shared_ptr` 创建后再调用初始化逻辑。

### 对象不是由 shared_ptr 管理

栈对象或普通 `new` 得到的对象没有对应控制块，调用 `shared_from_this()` 同样失败。

### 异步回调无意延长生命周期

捕获 `shared_from_this()` 会让任务持有对象；需要允许对象提前销毁时，可以捕获 C++17 的 `weak_from_this()`，执行时再 `lock()`。

## 5. 面试口述版

enable_shared_from_this 用于让对象安全取得共享自身的 shared_ptr。它内部维护一个绑定原控制块的弱引用，shared_from_this 从该弱引用创建新的 shared_ptr，所以不会产生第二个控制块。它不能在对象尚未被 shared_ptr 接管时使用，构造函数内调用通常会抛 bad_weak_ptr。
