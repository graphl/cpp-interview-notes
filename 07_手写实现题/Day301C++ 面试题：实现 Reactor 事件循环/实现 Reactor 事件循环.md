# C++ 面试题：实现 Reactor 事件循环

## 1. 考点

Reactor 使用 IO 多路复用等待多个文件描述符就绪，再把事件分发给对应回调。Linux 下常用 `epoll` 实现。

面试主要考：

1. `epoll_create1`、`epoll_ctl`、`epoll_wait`
2. 事件注册与分发
3. 非阻塞 IO
4. LT 和 ET 模式
5. 跨线程唤醒
6. 文件描述符生命周期

---

## 2. 最小可用实现

```cpp
#include <atomic>
#include <cerrno>
#include <cstdint>
#include <functional>
#include <stdexcept>
#include <system_error>
#include <unordered_map>
#include <utility>
#include <vector>

#include <sys/epoll.h>
#include <sys/eventfd.h>
#include <unistd.h>

class Reactor {
public:
    using Callback = std::function<void(uint32_t)>;

    Reactor() {
        epoll_fd_ = ::epoll_create1(EPOLL_CLOEXEC);
        if (epoll_fd_ < 0) throw_system_error("epoll_create1");

        wake_fd_ = ::eventfd(0, EFD_NONBLOCK | EFD_CLOEXEC);
        if (wake_fd_ < 0) {
            int error = errno;
            ::close(epoll_fd_);
            throw std::system_error(error, std::generic_category(), "eventfd");
        }

        try {
            add(wake_fd_, EPOLLIN, [this](uint32_t) { drain_wakeup(); });
        } catch (...) {
            ::close(wake_fd_);
            ::close(epoll_fd_);
            wake_fd_ = -1;
            epoll_fd_ = -1;
            throw;
        }
    }

    ~Reactor() {
        if (wake_fd_ >= 0) ::close(wake_fd_);
        if (epoll_fd_ >= 0) ::close(epoll_fd_);
    }

    Reactor(const Reactor&) = delete;
    Reactor& operator=(const Reactor&) = delete;

    void add(int fd, uint32_t events, Callback callback) {
        auto [it, inserted] = callbacks_.emplace(fd, std::move(callback));
        if (!inserted) {
            throw std::invalid_argument("fd is already registered");
        }

        epoll_event event{};
        event.events = events;
        event.data.fd = fd;
        if (::epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, fd, &event) < 0) {
            callbacks_.erase(it);
            throw_system_error("epoll_ctl ADD");
        }
    }

    void modify(int fd, uint32_t events) {
        epoll_event event{};
        event.events = events;
        event.data.fd = fd;
        if (::epoll_ctl(epoll_fd_, EPOLL_CTL_MOD, fd, &event) < 0) {
            throw_system_error("epoll_ctl MOD");
        }
    }

    void remove(int fd) {
        // Linux 2.6.9 之后 DEL 可以传 nullptr。
        if (::epoll_ctl(epoll_fd_, EPOLL_CTL_DEL, fd, nullptr) < 0 &&
            errno != ENOENT && errno != EBADF) {
            throw_system_error("epoll_ctl DEL");
        }
        callbacks_.erase(fd);
    }

    void run() {
        stopped_.store(false, std::memory_order_relaxed);
        std::vector<epoll_event> events(64);

        while (!stopped_.load(std::memory_order_acquire)) {
            int count = ::epoll_wait(epoll_fd_, events.data(),
                                     static_cast<int>(events.size()), -1);
            if (count < 0) {
                if (errno == EINTR) continue;
                throw_system_error("epoll_wait");
            }

            for (int i = 0; i < count; ++i) {
                int fd = events[i].data.fd;
                auto it = callbacks_.find(fd);
                if (it != callbacks_.end()) {
                    Callback callback = it->second;
                    callback(events[i].events);
                }
            }
        }
    }

    void stop() noexcept {
        stopped_.store(true, std::memory_order_release);
        uint64_t one = 1;
        // 非阻塞 eventfd 已满时可以忽略，已有唤醒值足以使 epoll 返回。
        (void)::write(wake_fd_, &one, sizeof(one));
    }

private:
    [[noreturn]] static void throw_system_error(const char* operation) {
        throw std::system_error(errno, std::generic_category(), operation);
    }

    void drain_wakeup() noexcept {
        uint64_t value;
        while (::read(wake_fd_, &value, sizeof(value)) > 0) {}
    }

    int epoll_fd_ = -1;
    int wake_fd_ = -1;
    std::unordered_map<int, Callback> callbacks_;
    std::atomic<bool> stopped_{false};
};
```

---

## 3. 事件处理流程

```text
注册 fd 和关注事件
        ↓
epoll_wait 阻塞等待
        ↓
取得就绪事件列表
        ↓
根据 fd 查找回调并执行
        ↓
继续等待下一批事件
```

`eventfd` 用来唤醒阻塞在 `epoll_wait` 的事件循环，使其他线程调用 `stop()` 后能够及时退出。

---

## 4. LT 和 ET

1. LT：只要 fd 仍满足条件，后续 `epoll_wait` 还会继续报告，代码更容易写对
2. ET：只在状态变化时通知，必须使用非阻塞 fd，并一直读或写到返回 `EAGAIN`

面试时如果实现 ET 读回调，不能只调用一次 `read`，否则剩余数据可能长期得不到处理。

---

## 5. 生产版本还需要解决什么？

1. Reactor 默认不拥有业务 fd，关闭与移除顺序要明确
2. 所有注册修改最好在事件循环线程完成；跨线程操作应进入任务队列再通过 `eventfd` 唤醒
3. 回调中删除自身时要避免迭代器或回调对象失效，因此示例先复制回调
4. 处理 `EPOLLERR`、`EPOLLHUP`、半关闭和写缓冲积压
5. 回调不能长时间阻塞，耗时任务应交给工作线程
6. 异常不能直接穿透并终止整个事件循环

---

## 6. 面试回答

Reactor 先向 epoll 注册文件描述符和关注事件，然后在 `epoll_wait` 中等待就绪事件，返回后按 fd 分发给对应回调。业务 fd 通常设置为非阻塞，ET 模式下必须一直处理到 `EAGAIN`。跨线程停止或投递任务可以使用 `eventfd` 唤醒事件循环，文件描述符所有权、回调耗时和错误事件处理是生产实现的重点。
