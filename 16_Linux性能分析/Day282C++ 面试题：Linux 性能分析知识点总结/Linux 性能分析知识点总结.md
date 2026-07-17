# C++ 面试题：Linux 性能分析知识点总结

## 1. 面试主要考什么？

性能分析不是一上来就背工具，而是先判断瓶颈类型，再选择证据。

面试官想听到：

1. 如何定义性能指标
2. 如何区分 CPU、内存、IO、网络、锁、调度瓶颈
3. 如何从粗粒度工具逐步深入
4. 如何使用 `top`、`pidstat`、`vmstat`、`iostat`、`perf`
5. 如何看 `/proc`、`/sys`、`dmesg`
6. 如何分析多线程锁竞争和上下文切换
7. 如何用火焰图或 perf 找热点
8. 如何根据证据提出优化方案

核心一句话：

> 性能分析的本质是先明确指标，再分类瓶颈，用工具收集证据，最后针对证据优化，而不是凭感觉改代码。

---

## 2. 性能分析先问什么？

开始分析前，先问清楚：

1. 慢在哪里：启动慢、请求慢、吞吐低、CPU 高、内存涨、卡顿、丢帧
2. 指标是什么：延迟、吞吐、QPS、FPS、CPU%、内存、IOPS、带宽、抖动
3. 什么时候出现：启动后、运行一段时间后、高并发时、特定输入时
4. 最近改了什么：代码、内核、驱动、配置、编译参数、硬件、数据量
5. 是否可复现：稳定复现还是偶发
6. 影响范围：单进程、整机、某个线程、某个设备、某个请求路径

性能排查基本流程：

```text
定义指标
  -> 复现问题
  -> 粗粒度观察
  -> 判断瓶颈类型
  -> 选择专项工具
  -> 定位热点
  -> 小实验验证
  -> 再优化
```

---

## 3. 常见瓶颈分类

| 类型 | 典型现象 | 常用工具 |
|---|---|---|
| CPU 瓶颈 | CPU 使用率高，响应慢 | `top`、`pidstat`、`perf` |
| 内存压力 | RSS 涨、OOM、频繁缺页 | `/proc/meminfo`、`vmstat`、`smaps` |
| IO 瓶颈 | iowait 高，读写慢 | `iostat`、`pidstat -d` |
| 网络瓶颈 | 丢包、重传、延迟高 | `ss`、`sar -n`、`ethtool` |
| 锁竞争 | 多线程卡住，上下文切换多 | `perf`、`gdb`、`ftrace` |
| 调度延迟 | 线程醒了但迟迟不运行 | `perf sched`、`trace-cmd` |
| 中断异常 | IRQ 高、中断风暴 | `/proc/interrupts`、`perf top` |
| cache/DDR 瓶颈 | CPU 不满但性能差 | `perf stat`、SoC 计数器 |
| 频繁分配 | malloc/free 开销大、碎片 | `perf`、heap profiler |
| 数据拷贝 | CPU 高、带宽高 | `perf`、火焰图、代码审计 |

---

## 4. 第一层：快速粗查工具

### top

```bash
top
top -H -p <pid>
```

看什么：

1. 哪个进程 CPU 高
2. 哪个线程 CPU 高
3. load 是否异常
4. 内存是否上涨
5. 是否有大量僵尸进程

### pidstat

```bash
pidstat -u -p <pid> 1
pidstat -r -p <pid> 1
pidstat -d -p <pid> 1
pidstat -w -p <pid> 1
```

含义：

| 命令 | 作用 |
|---|---|
| `pidstat -u` | 看 CPU |
| `pidstat -r` | 看内存和缺页 |
| `pidstat -d` | 看进程 IO |
| `pidstat -w` | 看上下文切换 |

### vmstat

```bash
vmstat 1
```

重点字段：

```text
r    可运行队列长度
b    不可中断睡眠任务
si   swap in
so   swap out
us   用户态 CPU
sy   内核态 CPU
id   空闲
wa   IO wait
cs   上下文切换
in   中断
```

### iostat

```bash
iostat -xz 1
```

看什么：

1. `%util` 是否接近 100%
2. `await` 是否很高
3. 读写吞吐是否达到设备上限
4. IO 是否集中在某个磁盘

---

## 5. 第二层：CPU 热点分析

CPU 高时，先判断是用户态高还是内核态高。

```bash
top
pidstat -u -p <pid> 1
```

如果用户态高：

```bash
perf top -p <pid>
perf record -g -p <pid> -- sleep 10
perf report
```

如果想看整体统计：

```bash
perf stat -p <pid> -- sleep 10
```

常见指标：

```text
cycles          CPU 周期
instructions    指令数
IPC             每周期执行指令数
cache-misses    cache miss
branch-misses   分支预测失败
context-switches 上下文切换
page-faults     缺页
```

判断：

1. 某个函数占比高：算法热点或循环热点
2. `copy_user`、`memcpy` 高：数据拷贝多
3. `malloc/free` 高：频繁分配释放
4. 锁相关函数高：锁竞争
5. 内核函数高：系统调用、网络、IO、驱动路径重

---

## 6. 第三层：火焰图

火焰图用于看调用栈热点。

常见流程：

```bash
perf record -F 99 -g -p <pid> -- sleep 30
perf script > out.perf
stackcollapse-perf.pl out.perf > out.folded
flamegraph.pl out.folded > flame.svg
```

怎么看：

1. 横向越宽，消耗 CPU 越多
2. 越靠上，越接近当前执行热点
3. 宽函数不一定是 bug，但一定是优化候选点
4. 先优化最宽、最频繁、最靠近业务路径的热点

面试回答：

> 火焰图不是看时间顺序，而是看采样调用栈的聚合宽度。宽的地方表示 CPU 消耗多，适合定位热点函数和调用路径。

---

## 7. 内存性能分析

常见现象：

1. 内存持续上涨
2. OOM
3. 缺页多
4. swap 频繁
5. page cache 被误判为泄漏
6. 频繁 malloc/free 导致 CPU 高

常用命令：

```bash
cat /proc/meminfo
cat /proc/<pid>/status | grep Vm
cat /proc/<pid>/smaps_rollup
cat /proc/<pid>/maps
vmstat 1
pidstat -r -p <pid> 1
```

重点区分：

```text
RSS       进程实际驻留内存
VmSize    虚拟地址空间
Anon      匿名内存，常见于堆和匿名 mmap
File      文件映射和 page cache
Shmem     共享内存
Pss       按比例分摊后的内存
```

判断流程：

```text
内存涨
  -> 看 RSS 是否涨
  -> 看 anon/file/shmem 谁在涨
  -> 看 maps 是否出现大量 mmap
  -> 看线程数是否增长
  -> 再用 heap profiler 或 ASan 定位
```

---

## 8. IO 性能分析

常见现象：

1. 请求延迟高
2. `wa` 高
3. 磁盘 `%util` 高
4. 日志刷盘导致卡顿
5. 随机 IO 太多
6. fsync 太频繁

常用命令：

```bash
iostat -xz 1
pidstat -d -p <pid> 1
vmstat 1
df -h
du -sh *
```

重点字段：

```text
iostat:
  r/s, w/s       每秒读写次数
  rkB/s, wkB/s   每秒读写带宽
  await          平均等待时间
  %util          设备忙碌程度

vmstat:
  wa             IO wait
```

常见优化：

1. 批量写
2. 减少同步刷盘
3. 顺序 IO 替代随机 IO
4. 异步日志
5. 调整缓存策略
6. 减少临时文件

---

## 9. 网络性能分析

常见现象：

1. 连接数高
2. 延迟高
3. 吞吐低
4. 丢包或重传
5. `TIME_WAIT` 很多
6. accept 或 connect 失败

常用命令：

```bash
ss -antp
ss -s
sar -n DEV 1
sar -n TCP,ETCP 1
cat /proc/net/snmp
cat /proc/net/netstat
ethtool -S eth0
```

排查：

```text
吞吐低
  -> 看网卡 rx/tx
  -> 看 TCP 重传
  -> 看 socket 队列
  -> 看应用线程是否及时读写
```

常见优化：

1. 调整 socket buffer
2. 使用 epoll
3. 减少小包
4. 批量发送
5. 避免阻塞业务线程
6. 检查网卡错误和丢包

---

## 10. 多线程和锁竞争分析

常见现象：

1. CPU 不高但吞吐低
2. 线程很多但都在等待
3. 上下文切换高
4. 延迟抖动明显
5. 偶发卡死

常用命令：

```bash
top -H -p <pid>
pidstat -w -p <pid> 1
gdb -p <pid>
```

GDB 中：

```gdb
info threads
thread apply all bt
```

判断：

1. 很多线程卡在同一把锁：锁竞争
2. 卡在 `pthread_cond_wait`：等待条件变量
3. 卡在 `epoll_wait`：等待 IO 事件
4. 卡在 `futex`：用户态锁或条件变量进入内核等待

进一步工具：

```bash
perf record -g -p <pid> -- sleep 10
perf report
perf sched record -- sleep 10
perf sched latency
```

---

## 11. 调度延迟和上下文切换

上下文切换过多会导致 CPU 时间浪费在调度上。

观察：

```bash
vmstat 1
pidstat -w -p <pid> 1
cat /proc/<pid>/status | grep ctxt
```

字段：

```text
voluntary_ctxt_switches      主动切换，常见于等待 IO、锁、条件变量
nonvoluntary_ctxt_switches   被动切换，常见于 CPU 竞争被抢占
```

常见原因：

1. 线程数过多
2. 锁竞争
3. 频繁唤醒
4. 小任务切得太碎
5. IO 阻塞频繁
6. 定时器太密集

---

## 12. cache 和内存带宽问题

常见现象：

1. CPU 使用率不满，但性能上不去
2. IPC 低
3. cache miss 高
4. 多核扩展性差
5. 多线程共享数据导致 cache line 抖动

常用命令：

```bash
perf stat -e cycles,instructions,cache-references,cache-misses -p <pid> -- sleep 10
perf stat -e branch-misses,branches -p <pid> -- sleep 10
```

常见原因：

1. 数据结构局部性差
2. 随机访问多
3. false sharing
4. 大量跨核共享写
5. 内存拷贝过多
6. DDR 带宽达到瓶颈

优化方向：

1. 改善数据布局
2. 减少随机访问
3. cache line 对齐
4. 分片减少共享写
5. 减少 memcpy
6. 批处理

---

## 13. 嵌入式 Linux 性能分析重点

嵌入式场景除了 CPU，还要关注：

1. DDR 带宽
2. DMA/cache 一致性
3. 中断频率
4. 驱动线程调度
5. thermal throttling 降频
6. 电源管理
7. 硬件加速模块是否生效
8. 数据在模块之间是否反复拷贝

典型媒体链路：

```text
Sensor
  -> ISP
  -> VPSS
  -> VENC
  -> DDR
  -> App
  -> Network/Storage
```

排查思路：

```text
先看每个阶段输入输出帧率
  -> 看队列是否堆积
  -> 看 DDR 带宽
  -> 看中断和线程调度
  -> 看是否有多余 memcpy
  -> 看硬件编码/缩放是否启用
```

---

## 14. 性能优化常见方向

| 问题 | 优化方向 |
|---|---|
| 算法复杂度高 | 换算法、减少重复计算 |
| CPU 热点集中 | 优化热点函数、SIMD、减少分支 |
| 锁竞争 | 降低锁粒度、分片、无锁队列 |
| IO 慢 | 批量 IO、异步 IO、减少 fsync |
| 内存涨 | 修泄漏、复用对象、减少 mmap |
| cache miss 高 | 改数据布局、提高局部性 |
| 拷贝多 | 零拷贝、move、DMA buffer |
| 线程太多 | 控制线程池大小、减少唤醒 |
| 网络慢 | 批量发送、减少小包、调 socket buffer |

---

## 15. 性能分析常见误区

1. 看到 CPU 高就直接优化代码，不看热点
2. 看到内存高就说内存泄漏，不区分 page cache
3. 只看平均延迟，不看 P99/P999
4. 只看进程 CPU，不看线程 CPU
5. 只看用户态，不看内核态
6. 没有基准数据就说优化有效
7. 一次改很多地方，无法判断哪个改动有效
8. 在线上直接使用高开销 tracing
9. 忽略编译优化参数和符号是否匹配
10. 优化前没有可复现 workload

---

## 16. 面试回答模板

可以这样回答：

> 我做性能分析不会一上来就改代码，而是先明确指标，比如延迟、吞吐、CPU、内存、IO 或抖动。然后用 `top`、`pidstat`、`vmstat`、`iostat` 做粗粒度判断，先分清是 CPU、内存、IO、网络、锁竞争还是调度问题。CPU 热点用 `perf record/report` 或火焰图看调用栈；内存问题看 `/proc/meminfo`、`smaps_rollup`；IO 问题看 `iostat` 和 `pidstat -d`；多线程卡顿看 `top -H`、`thread apply all bt` 和上下文切换。最后根据证据做小实验验证优化效果，而不是凭感觉优化。

---

## 17. 最终背诵版

性能分析的本质是：

```text
定义指标
  -> 分类瓶颈
  -> 收集证据
  -> 定位热点
  -> 实验验证
  -> 再做优化
```

重点记：

```text
CPU 看 top/pidstat/perf；
内存看 meminfo/smaps/vmstat；
IO 看 iostat/pidstat -d；
网络看 ss/sar/ethtool；
线程锁看 top -H/gdb/perf sched；
设备和中断看 dmesg、/proc/interrupts、/sys。
```
