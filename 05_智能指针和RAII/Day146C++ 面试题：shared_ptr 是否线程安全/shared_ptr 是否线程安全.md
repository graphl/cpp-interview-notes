# C++ 面试题：shared_ptr 是否线程安全

## 1. 核心结论

`shared_ptr` 的引用计数操作通常是线程安全的。

但多个线程同时读写同一个 `shared_ptr` 对象本身，不一定线程安全。

---

## 2. 安全的情况

不同 `shared_ptr` 对象共享同一个控制块时，各自拷贝、析构通常是安全的。

```cpp
auto p = std::make_shared<int>(10);

std::thread t1([p] {});
std::thread t2([p] {});
```

这里多个线程持有的是不同的 `shared_ptr` 副本。

---

## 3. 不安全的情况

多个线程同时修改同一个 `shared_ptr` 变量：

```cpp
std::shared_ptr<int> p = std::make_shared<int>(10);

// 线程 1
p.reset();

// 线程 2
p = std::make_shared<int>(20);
```

这需要加锁或使用原子操作。

---

## 4. 被管理对象不自动线程安全

```cpp
auto p = std::make_shared<int>(0);
```

`shared_ptr` 管理的是生命周期，不会让 `*p` 的读写自动线程安全。

---

## 5. 面试回答

`shared_ptr` 的控制块引用计数增减通常是线程安全的，因此不同 `shared_ptr` 副本在多个线程中拷贝析构是安全的。但如果多个线程同时修改同一个 `shared_ptr` 对象本身，需要同步。另外，`shared_ptr` 不保证被管理对象的访问线程安全。
