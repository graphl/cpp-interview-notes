# C++ 面试题：/proc 文件系统如何排查问题

## 1. 面试主要考什么？

`/proc` 是 Linux 暴露内核运行状态和进程状态的虚拟文件系统。

面试官想听到：

1. `/proc` 不是普通磁盘文件
2. `/proc/<pid>` 可以查看进程状态
3. `/proc/<pid>/fd` 可以排查文件描述符泄漏
4. `/proc/<pid>/maps`、`smaps` 可以查看地址空间和内存
5. `/proc/interrupts` 可以查看中断
6. `/proc/meminfo`、`/proc/stat`、`/proc/loadavg` 可以看系统状态
7. `/proc/sys` 可以查看和修改内核参数

核心一句话：

> `/proc` 主要用来观察系统和进程的运行时状态，是 Linux 排查 CPU、内存、线程、fd、信号、中断等问题的第一入口。

---

## 2. /proc 是什么？

`/proc` 是 procfs，里面的内容大多由内核动态生成。

特点：

1. 不占真实磁盘空间
2. 反映当前内核和进程状态
3. 大量文件是只读状态信息
4. `/proc/sys` 下部分节点可以写，用于调整内核参数

可以这样理解：

```text
/proc
  -> 当前系统运行状态
  -> 当前进程运行状态
  -> 内核统计信息
  -> 部分内核参数
```

---

## 3. 查看进程基本状态

常用命令：

```bash
cat /proc/<pid>/status
cat /proc/<pid>/cmdline
cat /proc/<pid>/limits
cat /proc/<pid>/environ
```

重点字段：

```text
Name       进程名
State      进程状态
Threads    线程数量
VmSize     虚拟地址空间大小
VmRSS      实际驻留内存
FDSize     文件描述符表大小
SigBlk     被屏蔽的信号
SigIgn     被忽略的信号
SigCgt     被捕获的信号
```

排查场景：

1. 进程是否还活着
2. 线程数量是否异常
3. 内存是否上涨
4. 资源限制是否太小
5. 信号是否被屏蔽或忽略

---

## 4. 查看线程状态

线程入口：

```bash
ls /proc/<pid>/task
cat /proc/<pid>/task/<tid>/status
cat /proc/<pid>/task/<tid>/stack
```

说明：

```text
/proc/<pid>/task
  -> 进程下所有线程

/proc/<pid>/task/<tid>/status
  -> 单个线程状态

/proc/<pid>/task/<tid>/stack
  -> 线程内核态调用栈
```

常见流程：

```bash
top -H -p <pid>
```

找到高 CPU 的线程 tid 后：

```bash
cat /proc/<pid>/task/<tid>/status
cat /proc/<pid>/task/<tid>/stack
```

注意：

```text
/proc/<pid>/task/<tid>/stack 只能看到内核态栈；
用户态栈要用 gdb、pstack、core dump 等工具。
```

---

## 5. 查看文件描述符泄漏

常用命令：

```bash
ls /proc/<pid>/fd
ls /proc/<pid>/fd | wc -l
ls -l /proc/<pid>/fd
readlink /proc/<pid>/fd/3
cat /proc/<pid>/fdinfo/3
cat /proc/<pid>/limits | grep "open files"
```

排查场景：

```text
Too many open files
accept failed
open failed
socket 创建失败
```

判断方法：

1. fd 数量是否持续上涨
2. fd 指向的是 socket、pipe、eventfd、timerfd 还是普通文件
3. `limits` 里的 open files 是否太小
4. 是否有连接关闭后 fd 没释放

面试回答：

> 怀疑 fd 泄漏时，我会先看 `/proc/<pid>/fd` 数量，再用 `readlink` 看 fd 指向什么资源。如果大量 socket、pipe 或 eventfd 持续增长，就说明程序可能没有正确 close。再结合 `/proc/<pid>/limits` 看 open files 限制。

---

## 6. 查看进程内存

系统整体内存：

```bash
cat /proc/meminfo
```

进程内存：

```bash
cat /proc/<pid>/status | grep Vm
cat /proc/<pid>/maps
cat /proc/<pid>/smaps
cat /proc/<pid>/smaps_rollup
```

重点字段：

```text
VmSize    虚拟内存
VmRSS     实际物理内存
RssAnon   匿名页，常见于堆、栈、匿名 mmap
RssFile   文件映射页
RssShmem  共享内存页
Pss       按比例分摊后的内存
```

排查思路：

```text
内存持续上涨
  -> 看 VmRSS 是否上涨
  -> 看 smaps_rollup
  -> 区分 anon/file/shmem
  -> 看 maps 中 heap、stack、anon mmap 是否增加
```

常见误区：

```text
看到系统 used 内存高，不一定是内存泄漏；
Linux 会用空闲内存做 page cache。
```

---

## 7. 查看地址空间 maps

命令：

```bash
cat /proc/<pid>/maps
```

用途：

1. 查看主程序和动态库映射
2. 查看堆、栈、匿名 mmap
3. 判断崩溃地址属于哪个模块
4. 排查动态库版本问题
5. 排查 mmap 是否泄漏

典型映射：

```text
[heap]
[stack]
/lib/libc.so.6
/app
anonymous mapping
```

面试回答：

> 如果程序崩溃地址是一个虚拟地址，我会用 `/proc/<pid>/maps` 判断这个地址属于主程序、动态库、堆、栈还是匿名映射，再结合 GDB 或 addr2line 定位。

---

## 8. 查看 CPU、负载、调度

系统负载：

```bash
cat /proc/loadavg
```

CPU 统计：

```bash
cat /proc/stat
```

进程调度信息：

```bash
cat /proc/<pid>/sched
cat /proc/<pid>/status | grep ctxt
```

重点字段：

```text
voluntary_ctxt_switches      主动上下文切换
nonvoluntary_ctxt_switches   被动上下文切换
```

判断：

1. 主动切换多：可能频繁等待锁、IO、条件变量
2. 被动切换多：可能 CPU 竞争激烈，被调度器抢占
3. load 高但 CPU 不高：可能大量任务卡在不可中断睡眠或 IO 等待

---

## 9. 查看中断

命令：

```bash
cat /proc/interrupts
cat /proc/irq/<irq>/smp_affinity
```

用途：

1. 判断设备是否产生中断
2. 判断 IRQ 是否持续增长
3. 排查中断风暴
4. 查看中断是否集中在某个 CPU
5. 排查网卡、存储、GPIO、串口等设备问题

常见判断：

```text
设备没有响应，IRQ 不增长
  -> 可能硬件没产生中断
  -> 设备树中断配置错
  -> 驱动没有 request_irq

某个 IRQ 计数疯狂增长
  -> 可能中断风暴
  -> 可能驱动没有正确清中断
```

---

## 10. /proc/sys 查看内核参数

常用命令：

```bash
cat /proc/sys/kernel/pid_max
cat /proc/sys/kernel/threads-max
cat /proc/sys/fs/file-max
cat /proc/sys/net/ipv4/ip_local_port_range
cat /proc/sys/vm/swappiness
```

等价命令：

```bash
sysctl kernel.pid_max
sysctl fs.file-max
sysctl net.ipv4.ip_local_port_range
```

注意：

```text
/proc/sys 下很多节点可以写；
写入会改变内核行为，生产环境要谨慎。
```

---

## 11. 典型问题怎么查

### 11.1 进程 CPU 高

```bash
top -H -p <pid>
cat /proc/<pid>/task/<tid>/status
cat /proc/<pid>/sched
```

下一步通常用：

```text
gdb
perf
pstack
```

### 11.2 内存持续上涨

```bash
cat /proc/<pid>/status | grep Vm
cat /proc/<pid>/smaps_rollup
cat /proc/<pid>/maps
cat /proc/meminfo
```

### 11.3 fd 泄漏

```bash
ls /proc/<pid>/fd | wc -l
ls -l /proc/<pid>/fd
cat /proc/<pid>/limits | grep "open files"
```

### 11.4 中断不触发

```bash
cat /proc/interrupts
dmesg | grep -i irq
```

---

## 12. 常见错误回答

1. 只知道 `top`，不知道 `/proc/<pid>`
2. 不知道 `/proc/<pid>/fd` 可以查 fd 泄漏
3. 不知道 `/proc/<pid>/maps` 可以判断地址归属
4. 看到内存高就直接说内存泄漏
5. 不知道 `/proc/interrupts` 可以看中断
6. 随便修改 `/proc/sys` 参数

---

## 13. 面试回答模板

可以这样回答：

> `/proc` 是 Linux 暴露进程和内核运行状态的虚拟文件系统。我排查问题时，会先看 `/proc/<pid>/status` 了解进程状态、线程数、内存和信号；怀疑 fd 泄漏看 `/proc/<pid>/fd`；怀疑内存问题看 `/proc/meminfo`、`/proc/<pid>/smaps_rollup` 和 `maps`；怀疑线程或 CPU 问题看 `/proc/<pid>/task` 和调度统计；设备中断问题看 `/proc/interrupts`。如果涉及内核参数，会看 `/proc/sys`，但生产环境不会随便改。

---

## 14. 最终背诵版

`/proc` 的本质是：

```text
看系统和进程的运行时状态。
```

重点记：

```text
/proc/<pid>/status      进程状态
/proc/<pid>/task        线程
/proc/<pid>/fd          文件描述符
/proc/<pid>/maps        地址空间
/proc/<pid>/smaps       内存详情
/proc/meminfo           系统内存
/proc/interrupts        中断
/proc/sys               内核参数
```
