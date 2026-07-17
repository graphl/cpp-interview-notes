# C++ 面试题：gdbserver 远程调试

## 1. 面试主要考什么？

`gdbserver` 主要用于远程调试，嵌入式 Linux 场景非常常见。

面试官想听到：

1. 为什么需要 `gdbserver`
2. host 和 target 分别运行什么
3. 交叉 GDB 怎么连接目标板
4. 符号文件和目标程序的关系
5. 动态库路径怎么配置
6. 如何 attach 正在运行的进程
7. 常见连接失败、符号不匹配、源码路径不一致问题

核心一句话：

> gdbserver 运行在目标板上负责控制被调试进程，交叉 GDB 运行在开发机上负责加载符号、下断点、查看栈和变量，二者通过网络或串口通信完成远程调试。

---

## 2. 为什么需要 gdbserver？

嵌入式目标板通常有这些限制：

1. CPU 架构和开发机不同
2. 存储空间小，不适合安装完整 GDB
3. 目标板性能弱，交互调试不方便
4. 符号文件很大，不适合放到板子上
5. 开发机上更方便查看源码、符号和调试信息

所以常见模式是：

```text
开发机 host
  -> 运行交叉 gdb
  -> 加载带符号的可执行文件
  -> 连接目标板 gdbserver

目标板 target
  -> 运行 gdbserver
  -> 启动或 attach 目标程序
  -> 接收 gdb 调试命令
```

---

## 3. 基本调试流程

目标板上运行：

```bash
gdbserver :1234 ./app arg1 arg2
```

开发机上运行：

```bash
aarch64-linux-gnu-gdb ./app
```

进入 GDB 后：

```gdb
target remote 192.168.1.100:1234
b main
c
```

数据流：

```text
host gdb
  -> TCP 1234
  -> target gdbserver
  -> 控制目标进程
  -> 返回寄存器、内存、断点、信号等信息
```

---

## 4. host 和 target 上分别放什么？

开发机 host：

```text
带调试符号的 app
源码
交叉 gdb
动态库符号文件
```

目标板 target：

```text
可运行的 app
gdbserver
运行所需动态库
```

注意：

```text
开发机上的 app 用于加载符号；
目标板上的 app 用于真实运行；
两边 app 必须来自同一次编译产物，不能版本不一致。
```

---

## 5. attach 正在运行的进程

目标板上：

```bash
pidof app
gdbserver :1234 --attach <pid>
```

开发机上：

```bash
aarch64-linux-gnu-gdb ./app
```

GDB 中：

```gdb
target remote 192.168.1.100:1234
bt
info threads
```

适合场景：

1. 程序已经启动
2. 问题只在线上运行状态出现
3. 需要看当前卡在哪里
4. 需要排查死锁、卡死、CPU 占用异常

---

## 6. 多线程远程调试

连接后常用命令：

```gdb
info threads
thread apply all bt
thread 2
bt
set scheduler-locking on
```

排查思路：

```text
程序卡死
  -> attach 进程
  -> info threads
  -> thread apply all bt
  -> 看是否卡在 mutex、condition_variable、read、poll、epoll_wait
```

面试回答：

> 使用 gdbserver attach 到目标进程后，多线程调试和本地 GDB 类似，可以用 `info threads` 看所有线程，用 `thread apply all bt` 打印所有线程栈，判断线程是卡在锁、条件变量、IO 还是事件循环里。

---

## 7. 动态库和符号路径怎么处理？

远程调试时，目标板上的库路径和开发机上的库路径往往不同。

常用命令：

```gdb
set sysroot /path/to/rootfs
set solib-search-path /path/to/rootfs/lib:/path/to/rootfs/usr/lib
info sharedlibrary
info proc mappings
```

含义：

1. `set sysroot`：告诉 GDB 目标板根文件系统在开发机上的镜像路径
2. `set solib-search-path`：告诉 GDB 去哪里找动态库符号
3. `info sharedlibrary`：查看动态库是否加载符号
4. `info proc mappings`：查看目标进程地址映射

典型问题：

```text
No symbol table info available
```

可能原因：

1. 没有 `-g`
2. 符号被 strip
3. GDB 找不到对应动态库
4. 开发机符号文件和目标板运行库版本不一致

---

## 8. 源码路径不一致怎么办？

如果编译时源码路径和当前开发机路径不同，GDB 可能找不到源码。

查看编译路径：

```gdb
info sources
```

替换源码路径：

```gdb
set substitute-path /old/build/path /new/source/path
```

例子：

```gdb
set substitute-path /home/build/project G:/Desktop/project
```

---

## 9. 远程调试 core dump 和 gdbserver 的区别

| 场景 | 工具 | 特点 |
|---|---|---|
| 程序已经崩溃 | core dump + gdb | 看崩溃现场，不能继续运行 |
| 程序还在运行 | gdbserver attach | 能看当前状态，也能继续执行 |
| 程序启动即崩 | gdbserver 启动程序 | 可以从 main 前后开始断住 |
| 偶发卡死 | gdbserver attach | 可以看所有线程栈 |

面试回答：

> core dump 是事后分析，gdbserver 是在线远程调试。程序已经崩了就分析 core；程序还活着但卡死、死锁或行为异常，就用 gdbserver attach 上去看线程栈和变量。

---

## 10. 常见命令速查

目标板：

```bash
gdbserver :1234 ./app
gdbserver :1234 ./app arg1 arg2
gdbserver :1234 --attach <pid>
```

开发机：

```bash
aarch64-linux-gnu-gdb ./app
```

GDB：

```gdb
target remote <ip>:1234
set sysroot /path/to/rootfs
set solib-search-path /path/to/lib
b main
c
bt
info threads
thread apply all bt
info sharedlibrary
info proc mappings
detach
quit
```

---

## 11. 常见问题排查

### 11.1 连接不上 gdbserver

检查：

1. 目标板 IP 是否能 ping 通
2. 端口是否被防火墙拦截
3. gdbserver 是否正在监听
4. IP 和端口是否写错
5. 目标程序是否已经退出

命令：

```bash
ps | grep gdbserver
netstat -an | grep 1234
```

### 11.2 架构不匹配

现象：

```text
file format not recognized
```

或连接后寄存器显示异常。

排查：

```bash
file app
readelf -h app
```

要使用目标架构对应的交叉 GDB，例如：

```bash
aarch64-linux-gnu-gdb
arm-linux-gnueabihf-gdb
```

### 11.3 断点不生效

可能原因：

1. 没有调试符号
2. 优化导致代码行变化
3. 下断点的源码和运行程序不是同一版本
4. 动态库还没加载
5. PIE/ASLR 导致地址变化

处理：

```gdb
info files
info sharedlibrary
b function_name
set breakpoint pending on
```

### 11.4 看不到源码

处理：

```gdb
directory /path/to/source
set substitute-path /old/path /new/path
```

---

## 12. 安全注意点

`gdbserver` 不适合直接暴露在公网或生产环境。

原因：

1. 可以控制目标进程
2. 可以读写目标进程内存
3. 可以执行调试命令
4. 可能泄露敏感信息

建议：

1. 只在内网或调试环境使用
2. 调试完成后关闭 gdbserver
3. 必要时通过 SSH 隧道转发端口

SSH 隧道示例：

```bash
ssh -L 1234:127.0.0.1:1234 root@192.168.1.100
```

---

## 13. 常见错误回答

1. 认为 gdbserver 会加载所有调试符号
2. 不知道 host 上也需要对应的带符号二进制
3. 不知道目标板和开发机二进制必须匹配
4. 不知道 `target remote`
5. 不会 attach 正在运行的进程
6. 不知道动态库符号要配置 `sysroot`
7. 不知道源码路径不一致可以用 `set substitute-path`
8. 把 core dump 和 gdbserver 的使用场景混淆

---

## 14. 面试回答模板

可以这样回答：

> `gdbserver` 常用于嵌入式 Linux 远程调试。目标板上运行 `gdbserver`，负责启动或 attach 被调试进程；开发机上运行对应架构的交叉 GDB，加载带调试符号的可执行文件，然后通过 `target remote ip:port` 连接目标板。调试时符号主要在开发机上，目标板只需要能运行程序和 gdbserver。远程调试动态库时，要配置 `set sysroot` 或 `set solib-search-path`，保证 GDB 能找到和目标板一致的库符号。如果程序卡死，可以 attach 后用 `info threads` 和 `thread apply all bt` 看所有线程栈。

---

## 15. 最终背诵版

`gdbserver` 的本质是：

```text
把调试控制放在目标板，
把符号解析和交互操作放在开发机，
通过远程协议完成跨机器、跨架构调试。
```

面试中一定要补一句：

```text
远程调试最关键的是三件事：
交叉 GDB 架构要对、host 符号文件要和 target 程序匹配、动态库和源码路径要配置正确。
```
