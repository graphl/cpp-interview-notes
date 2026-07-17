# C++ 面试题：如何通过 /proc 和 /sys 查看错误信息

## 1. 面试主要考什么？

这道题主要考 Linux 问题排查能力。

面试官想听到：

1. `/proc` 和 `/sys` 分别是什么
2. 如何查看进程状态、线程、内存、文件描述符
3. 如何查看 CPU、中断、负载、调度信息
4. 如何查看内核参数和系统资源
5. 如何查看设备、驱动、总线、模块信息
6. 如何根据现象选择排查入口

核心一句话：

> `/proc` 更偏运行时状态和进程/内核统计信息，`/sys` 更偏设备模型、驱动、总线、电源、参数等内核对象的层次化视图。

---

## 2. /proc 和 /sys 的区别

| 路径 | 主要用途 | 典型内容 |
|---|---|---|
| `/proc` | 查看进程和内核运行状态 | 进程、内存、CPU、中断、文件描述符、网络统计 |
| `/sys` | 查看和配置内核对象 | 设备、驱动、总线、class、电源、模块参数 |

可以这样理解：

```text
/proc
  -> 系统当前运行状态
  -> 进程视角
  -> 内核统计信息

/sys
  -> 内核设备模型
  -> 驱动视角
  -> 设备和总线关系
```

---

## 3. 排查问题的通用顺序

遇到 Linux 程序异常时，可以先按这个顺序看：

```text
现象分类
  -> 进程是否还活着
  -> CPU 是否异常
  -> 内存是否异常
  -> 文件描述符是否泄漏
  -> 线程是否卡住
  -> IO/网络/中断是否异常
  -> 设备或驱动是否异常
```

对应入口：

```text
进程状态     -> /proc/<pid>/status
线程状态     -> /proc/<pid>/task/
内存使用     -> /proc/meminfo, /proc/<pid>/smaps
文件描述符   -> /proc/<pid>/fd
CPU/负载     -> /proc/loadavg, /proc/stat
中断         -> /proc/interrupts
设备/驱动    -> /sys/bus, /sys/class, /sys/devices
内核参数     -> /proc/sys
```

---

## 4. 查看进程状态

常用命令：

```bash
cat /proc/<pid>/status
cat /proc/<pid>/cmdline
cat /proc/<pid>/environ
cat /proc/<pid>/limits
```

重点字段：

```text
Name        进程名
State       进程状态
Threads     线程数量
VmRSS       实际驻留内存
VmSize      虚拟地址空间大小
FDSize      文件描述符表大小
SigBlk      被屏蔽的信号
SigIgn      被忽略的信号
SigCgt      被捕获的信号
```

面试回答：

> 如果一个进程异常，我会先看 `/proc/<pid>/status`，确认进程状态、线程数、内存占用和信号处理情况，再看 `cmdline` 确认启动参数，`limits` 确认文件描述符、core 文件大小等资源限制。

---

## 5. 查看线程信息

每个线程在 `/proc/<pid>/task/` 下都有一个目录。

```bash
ls /proc/<pid>/task
cat /proc/<pid>/task/<tid>/status
cat /proc/<pid>/task/<tid>/stack
```

常见用途：

1. 查看线程数量是否异常增长
2. 判断某个线程是否卡住
3. 查看内核态调用栈
4. 配合 `top -H -p <pid>` 找高 CPU 线程

流程：

```text
top -H -p <pid>
  -> 找到高 CPU 的 tid
  -> printf "%x\n" <tid>
  -> gdb 里匹配线程
  -> 或查看 /proc/<pid>/task/<tid>/status
```

注意：

```text
/proc/<pid>/task/<tid>/stack 只能看到内核态栈；
用户态栈通常要用 gdb、pstack 或 core dump 看。
```

---

## 6. 查看文件描述符泄漏

常用命令：

```bash
ls -l /proc/<pid>/fd
ls /proc/<pid>/fd | wc -l
cat /proc/<pid>/limits | grep "open files"
```

查看 fd 详情：

```bash
readlink /proc/<pid>/fd/3
cat /proc/<pid>/fdinfo/3
```

典型现象：

```text
Too many open files
accept failed
open failed
socket 创建失败
```

排查重点：

1. fd 数量是否持续增长
2. 是否有大量 socket 没关闭
3. 是否有文件、pipe、eventfd、timerfd 泄漏
4. `ulimit -n` 是否太小

面试回答：

> 如果怀疑文件描述符泄漏，我会看 `/proc/<pid>/fd` 统计 fd 数量，再用 `readlink` 看每个 fd 指向文件、socket 还是 pipe。再结合 `/proc/<pid>/limits` 看 open files 上限，判断是资源限制太小还是程序忘记关闭 fd。

---

## 7. 查看进程内存

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
VmSize   虚拟内存大小
VmRSS    实际驻留物理内存
RssAnon  匿名页，通常和堆、栈、匿名 mmap 有关
RssFile  文件映射页
RssShmem 共享内存页
Pss      按比例分摊后的实际内存
```

排查思路：

```text
内存持续上涨
  -> 看 VmRSS 是否上涨
  -> 看 smaps_rollup
  -> 区分 anon/file/shmem
  -> 看 maps 中 heap、anon mmap、动态库映射
```

常见问题：

1. 堆内存泄漏
2. mmap 没释放
3. 线程太多导致栈内存增加
4. page cache 增长被误认为内存泄漏
5. 共享内存未释放

---

## 8. 查看进程地址空间

```bash
cat /proc/<pid>/maps
```

典型内容：

```text
00400000-00452000 r-xp ... /app
00652000-00653000 rw-p ... /app
7f... r-xp ... /lib/libc.so.6
7f... rw-p ... [heap]
7f... rw-p ... [stack]
```

用途：

1. 查看动态库是否加载
2. 查看堆、栈、匿名映射
3. 判断地址属于哪个模块
4. 配合崩溃地址定位 so
5. 查看 mmap 是否持续增加

面试回答：

> 如果程序崩溃地址在某个范围内，可以用 `/proc/<pid>/maps` 判断这个地址属于主程序、动态库、堆、栈还是匿名映射。这对定位野指针、函数指针错误、动态库版本问题很有用。

---

## 9. 查看 CPU、负载和上下文切换

系统负载：

```bash
cat /proc/loadavg
```

CPU 统计：

```bash
cat /proc/stat
```

进程调度统计：

```bash
cat /proc/<pid>/sched
cat /proc/<pid>/stat
```

进程状态：

```bash
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
3. load 高但 CPU 不高：可能大量线程处于不可中断睡眠或 IO 等待

---

## 10. 查看中断信息

```bash
cat /proc/interrupts
```

用途：

1. 查看某个 IRQ 是否持续增长
2. 判断设备是否产生中断
3. 判断中断是否集中在某个 CPU
4. 排查中断风暴
5. 排查网卡、存储、GPIO、串口等设备问题

常见现象：

```text
某个 IRQ 计数疯狂增长
  -> 可能中断风暴

设备没响应，IRQ 不增长
  -> 可能硬件没产生中断、设备树中断配置错、驱动没 request_irq
```

相关 sysfs：

```bash
cat /proc/irq/<irq>/smp_affinity
echo 2 > /proc/irq/<irq>/smp_affinity
```

---

## 11. 查看内核日志和错误信息

虽然不在 `/proc` 或 `/sys` 下，但排查一定要结合：

```bash
dmesg
dmesg -T
journalctl -k
```

常见关键词：

```text
segfault
Out of memory
oom-killer
BUG
Oops
panic
hung task
RCU stall
watchdog
I/O error
reset
timeout
probe failed
```

结合 `/proc` 和 `/sys` 的方式：

```text
dmesg 看到 OOM
  -> /proc/meminfo
  -> /proc/<pid>/status
  -> /proc/<pid>/smaps_rollup

dmesg 看到 probe failed
  -> /sys/bus
  -> /sys/class
  -> /sys/devices
  -> /proc/interrupts
```

---

## 12. /proc/sys：查看和调整内核参数

`/proc/sys` 对应很多 `sysctl` 参数。

常见路径：

```bash
cat /proc/sys/kernel/pid_max
cat /proc/sys/kernel/threads-max
cat /proc/sys/fs/file-max
cat /proc/sys/net/ipv4/tcp_tw_reuse
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
写之前必须明确影响范围，生产环境不能随便改。
```

---

## 13. /sys 查看设备和驱动

常用入口：

```bash
ls /sys/bus
ls /sys/class
ls /sys/devices
ls /sys/module
```

含义：

| 路径 | 作用 |
|---|---|
| `/sys/bus` | 按总线查看设备和驱动 |
| `/sys/class` | 按设备类别查看，如 net、tty、gpio、block |
| `/sys/devices` | 设备层级树 |
| `/sys/module` | 已加载模块和模块参数 |
| `/sys/kernel` | 内核功能，如 debug、tracing |

---

## 14. 查看 platform/I2C/SPI/USB 等设备

platform：

```bash
ls /sys/bus/platform/devices
ls /sys/bus/platform/drivers
```

I2C：

```bash
ls /sys/bus/i2c/devices
ls /sys/bus/i2c/drivers
```

SPI：

```bash
ls /sys/bus/spi/devices
ls /sys/bus/spi/drivers
```

USB：

```bash
ls /sys/bus/usb/devices
lsusb
```

排查思路：

```text
设备没有工作
  -> /sys/bus/.../devices 是否存在
  -> /sys/bus/.../drivers 是否有驱动
  -> 设备是否 bind 到驱动
  -> dmesg 是否有 probe failed
```

---

## 15. 查看驱动绑定关系

设备目录下通常有：

```bash
readlink /sys/bus/platform/devices/<dev>/driver
```

如果没有 `driver` 链接，说明设备没有绑定驱动。

手动解绑和绑定：

```bash
echo <dev> > /sys/bus/platform/drivers/<driver>/unbind
echo <dev> > /sys/bus/platform/drivers/<driver>/bind
```

注意：

```text
bind/unbind 会影响真实设备运行；
生产环境要谨慎使用。
```

面试回答：

> 如果设备驱动没有 probe，我会先看 `/sys/bus/<bus>/devices` 下设备是否存在，再看 `/sys/bus/<bus>/drivers` 下驱动是否存在，并检查设备目录下有没有 `driver` 链接。如果设备存在但没有绑定驱动，通常要检查设备树 compatible、驱动匹配表和内核配置。

---

## 16. 查看模块参数

```bash
ls /sys/module
ls /sys/module/<module>/parameters
cat /sys/module/<module>/parameters/<param>
```

用途：

1. 查看模块是否加载
2. 查看模块参数
3. 调试驱动行为
4. 确认参数是否生效

也可以用：

```bash
lsmod
modinfo <module>
```

---

## 17. 查看块设备、网络设备、tty

块设备：

```bash
ls /sys/class/block
cat /sys/class/block/mmcblk0/size
cat /sys/class/block/mmcblk0/queue/scheduler
```

网络设备：

```bash
ls /sys/class/net
cat /sys/class/net/eth0/operstate
cat /sys/class/net/eth0/carrier
cat /sys/class/net/eth0/statistics/rx_errors
cat /sys/class/net/eth0/statistics/tx_errors
```

串口：

```bash
ls /sys/class/tty
dmesg | grep -i tty
```

---

## 18. 典型问题怎么查

### 18.1 进程 CPU 很高

```bash
top -H -p <pid>
cat /proc/<pid>/task/<tid>/status
cat /proc/<pid>/sched
```

下一步：

```text
用 gdb attach 或 perf 看热点函数。
```

### 18.2 进程内存一直涨

```bash
cat /proc/<pid>/status | grep Vm
cat /proc/<pid>/smaps_rollup
cat /proc/<pid>/maps
cat /proc/meminfo
```

判断是：

1. 堆涨
2. mmap 涨
3. 线程栈涨
4. page cache 涨
5. 共享内存涨

### 18.3 文件描述符泄漏

```bash
ls /proc/<pid>/fd | wc -l
ls -l /proc/<pid>/fd
cat /proc/<pid>/limits | grep "open files"
```

### 18.4 设备驱动没有 probe

```bash
dmesg | grep -i probe
ls /sys/bus/platform/devices
ls /sys/bus/platform/drivers
readlink /sys/bus/platform/devices/<dev>/driver
```

### 18.5 中断没有触发

```bash
cat /proc/interrupts
cat /proc/irq/<irq>/smp_affinity
dmesg | grep -i irq
```

---

## 19. 常见错误回答

1. 只会说 `top`，不会看 `/proc/<pid>`
2. 把 `/proc` 和 `/sys` 混为一谈
3. 不知道 `/proc/<pid>/fd` 可以查 fd 泄漏
4. 不知道 `/proc/<pid>/maps` 可以判断地址属于哪个模块
5. 不知道 `/proc/interrupts` 可以看中断是否触发
6. 不知道 `/sys/bus` 可以看设备和驱动绑定关系
7. 看到内存占用高就说内存泄漏，不区分 RSS、page cache、mmap、shared memory
8. 随便写 `/proc/sys` 或 `/sys` 节点，没意识到会改变内核运行状态

---

## 20. 面试回答模板

可以这样回答：

> 我排查 Linux 问题时，会先用 `/proc` 看运行状态，用 `/sys` 看设备和驱动关系。比如进程异常先看 `/proc/<pid>/status`、`cmdline`、`limits`；怀疑 fd 泄漏看 `/proc/<pid>/fd`；怀疑内存问题看 `/proc/meminfo`、`/proc/<pid>/smaps_rollup` 和 `maps`；怀疑多线程卡住看 `/proc/<pid>/task`。如果是设备或驱动问题，我会看 `/sys/bus`、`/sys/class`、`/sys/devices`，确认设备是否创建、驱动是否存在、是否成功绑定。中断问题会结合 `/proc/interrupts`，内核错误还要结合 `dmesg`。

---

## 21. 最终背诵版

`/proc` 和 `/sys` 的本质是：

```text
/proc 看运行状态；
/sys 看内核对象。
```

面试中一定要补一句：

```text
排查问题要先分类：
进程看 /proc/<pid>，
内存看 /proc/meminfo 和 smaps，
fd 看 /proc/<pid>/fd，
中断看 /proc/interrupts，
设备驱动看 /sys/bus、/sys/class、/sys/devices。
```
