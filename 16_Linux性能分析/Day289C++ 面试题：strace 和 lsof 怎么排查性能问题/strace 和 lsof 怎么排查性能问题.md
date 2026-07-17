# C++ 面试题：strace 和 lsof 怎么排查性能问题

## 1. 这道题考什么？

`strace` 看系统调用。
`lsof` 看进程打开了哪些文件、socket、pipe 等资源。

它们适合排查：

1. 系统调用耗时
2. open/read/write/connect 卡住
3. fd 泄漏
4. 文件或 socket 没关闭
5. 程序频繁访问不存在的文件

---

## 2. strace 怎么用？

跟踪程序：

```bash
strace ./app
```

跟踪进程：

```bash
strace -p <pid>
```

统计系统调用耗时：

```bash
strace -c -p <pid>
```

带时间：

```bash
strace -tt -T -p <pid>
```

跟踪子进程/线程：

```bash
strace -f -p <pid>
```

只看某类调用：

```bash
strace -e trace=file ./app
strace -e trace=network ./app
```

---

## 3. strace 看什么？

常见异常：

| 现象 | 可能问题 |
|---|---|
| 大量 `openat ENOENT` | 反复查找不存在的文件 |
| `read`/`write` 很慢 | IO 慢或阻塞 |
| `connect` 慢 | 网络连接慢 |
| `futex` 很多 | 锁竞争或条件变量等待 |
| `epoll_wait` 很久 | 等待事件，可能正常 |
| `stat` 很多 | 路径查找或配置扫描频繁 |

---

## 4. lsof 怎么用？

查看进程打开的文件：

```bash
lsof -p <pid>
```

查看端口：

```bash
lsof -i :8080
```

查看某文件被谁打开：

```bash
lsof /path/file
```

统计 fd 数：

```bash
ls /proc/<pid>/fd | wc -l
lsof -p <pid> | wc -l
```

---

## 5. 面试回答模板

> `strace` 用来看进程的系统调用路径，适合排查程序卡在 open、read、write、connect、futex 还是 epoll_wait。比如 `strace -tt -T -p pid` 可以看到每次系统调用耗时，`strace -c` 可以统计系统调用占比。`lsof` 用来看进程打开了哪些文件、socket、pipe，适合排查 fd 泄漏和端口占用。性能分析时，如果 CPU 不高但程序慢，我会用 strace 看是不是系统调用阻塞，再用 lsof 或 `/proc/<pid>/fd` 看资源是否泄漏。

