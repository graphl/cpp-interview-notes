# C++ 面试题：从 epoll 就绪到业务回调的数据流

## 1. 这个流程解决什么问题

高并发服务需要让少量线程管理大量连接。`epoll` 负责通知“哪些文件描述符现在可能执行 IO 而不阻塞”，应用仍要完成 accept、recv、协议解析、业务处理、send 和连接回收。

## 2. 数据流向

```text
网卡收到以太网帧
  -> 驱动/NAPI 把数据交给内核网络栈
  -> IP/TCP 校验、排序、重组
  -> 数据进入 socket 接收队列
  -> socket 状态变化触发 epoll 就绪
  -> epoll_wait 返回 fd/用户标识
  -> 非阻塞 recv 拷贝到用户态读缓冲
  -> 协议解码得到完整消息
  -> 业务处理产生响应
  -> 写入用户态发送缓冲
  -> send 尽可能提交到 socket 发送缓冲
  -> 内核协议栈和网卡发出数据
```

epoll 返回的是就绪事件，不携带业务数据。真正的数据仍通过 `accept/recv/send` 等系统调用移动。

## 3. 典型控制流

```text
event_loop()
  -> epoll_wait()
  -> handle_event(connection)
       -> handle_read()
            -> recv_until_EAGAIN()
            -> decode_frames()
            -> dispatch_business()
       -> handle_write()
            -> flush_output_until_EAGAIN()
       -> update_interest()
       -> close_if_needed()
```

ET 模式下必须使用非阻塞 fd，并持续读/写到 `EAGAIN`，否则已经留在 socket 队列中的数据可能不再产生新的边沿通知。LT 模式会在条件持续成立时重复报告，逻辑更宽容但可能产生更多唤醒。

## 4. 核心数据结构

```text
Connection
作用：保存一个连接跨事件的状态
关键字段：fd、read_buffer、write_buffer、decode_state、closing、generation
生命周期：accept 后创建；错误、超时或双方完成关闭后释放

EventLoop
作用：拥有 epoll fd，并在固定线程中分发 IO 事件
关键字段：epoll_fd、连接表、待执行任务队列、唤醒 fd

ProtocolDecoder
作用：把 TCP 字节流恢复成完整业务消息
关键字段：当前帧长度、解析位置、最大消息限制
```

关系：

```text
EventLoop
  └── connection_table[fd/generation]
        └── Connection
              ├── read_buffer -> ProtocolDecoder
              └── write_buffer
```

不能只用 fd 识别长生命周期异步任务：fd 关闭后可能被系统快速复用。可以使用对象生命周期管理、generation 或稳定连接 ID 防止旧任务误操作新连接。

## 5. 背压和半关闭

- `send` 返回 `EAGAIN` 时，把剩余数据留在用户态缓冲并监听可写事件。
- 写缓冲持续增长意味着下游慢，必须设置高水位、暂停读取、丢弃任务或断开连接。
- `recv == 0` 表示对端关闭发送方向；本端是否立即关闭取决于协议和剩余响应。
- 错误路径要统一撤销 epoll 注册、停止定时器、取消任务并最终只关闭一次 fd。

## 6. 最小验证

```bash
strace -f -e trace=epoll_wait,accept4,recvfrom,sendto ./server
ss -tinp
```

预期能看到 epoll 事件与非阻塞读写交替；当客户端故意停止读取时，发送缓冲和 TCP 队列逐渐积压，最终 `send` 返回 `EAGAIN`。

## 7. 面试口述版

epoll 只报告 IO 就绪，数据仍从 socket 队列经 recv 进入用户态缓冲。事件循环根据连接状态执行读到 EAGAIN、协议拆包、业务分发和发送缓冲刷新。ET 必须配合非阻塞 IO 并排空当前就绪条件；工程上还要处理 fd 复用、连接生命周期、半关闭和写侧背压。
