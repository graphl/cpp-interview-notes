# C++ 面试题：top、pidstat、vmstat 怎么分析性能

## 1. 这道题考什么？

这三个工具适合做性能排查第一层粗查。

| 工具 | 作用 |
|---|---|
| `top` | 看进程和线程整体状态 |
| `pidstat` | 按进程统计 CPU、内存、IO、上下文切换 |
| `vmstat` | 看系统级 CPU、内存、IO、调度 |

---

## 2. top 怎么看？

常用命令：

```bash
top
top -H -p <pid>
```

重点：

1. CPU 高的是哪个进程
2. 线程级 CPU 是否集中在某个 tid
3. load average 是否异常
4. `%us`、`%sy`、`%wa` 是否异常
5. 内存是否持续上涨

判断：

| 现象 | 可能原因 |
|---|---|
| `%us` 高 | 用户态计算多 |
| `%sy` 高 | 系统调用、网络、IO、内核路径重 |
| `%wa` 高 | IO 等待 |
| load 高但 CPU 不高 | 可能 IO 等待或不可中断睡眠 |

---

## 3. pidstat 怎么看？

CPU：

```bash
pidstat -u -p <pid> 1
```

内存：

```bash
pidstat -r -p <pid> 1
```

IO：

```bash
pidstat -d -p <pid> 1
```

上下文切换：

```bash
pidstat -w -p <pid> 1
```

线程级：

```bash
pidstat -t -u -p <pid> 1
```

---

## 4. vmstat 怎么看？

命令：

```bash
vmstat 1
```

重点字段：

| 字段 | 含义 |
|---|---|
| `r` | 可运行队列长度 |
| `b` | 不可中断睡眠任务数 |
| `si/so` | swap in/out |
| `us` | 用户态 CPU |
| `sy` | 内核态 CPU |
| `wa` | IO wait |
| `cs` | 上下文切换 |
| `in` | 中断 |

判断：

1. `r` 长期大于 CPU 核数：CPU 竞争明显
2. `b` 高：可能 IO 或内核等待
3. `wa` 高：IO 瓶颈
4. `cs` 高：上下文切换频繁
5. `si/so` 高：swap 压力大

---

## 5. 面试回答模板

> 我会先用 `top` 判断整体情况，看 CPU、load、内存和线程热点；如果要看某个进程的细节，用 `pidstat` 分别看 CPU、内存、IO 和上下文切换；如果要看系统整体压力，用 `vmstat` 看 run queue、IO wait、swap、context switch 和 interrupt。它们负责第一层分类，确定是 CPU、IO、内存还是调度问题，再决定是否用 perf、iostat、gdb 等工具深入。

