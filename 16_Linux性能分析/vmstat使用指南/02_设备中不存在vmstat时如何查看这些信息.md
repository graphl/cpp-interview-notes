# 设备中不存在 vmstat 时如何查看这些信息

`vmstat` 本身不是内核功能，而是读取 `/proc` 中内核计数并进行格式化、差值计算的用户态工具。设备上没有 `vmstat` 时，只要 `/proc` 可用，仍然可以取得大部分同类信息。

```text
vmstat 不存在
    ↓
先检查 BusyBox 是否包含 applet
    ↓
没有 applet 时直接读取 /proc
    ↓
对累计计数做两次采样并求差值
    ↓
根据异常方向继续定位
```

## 1. 先确认是不是真的没有 vmstat

```bash
command -v vmstat
which vmstat 2>/dev/null
```

很多嵌入式设备使用 BusyBox，虽然没有单独的 `/usr/bin/vmstat`，但 BusyBox 可能已经包含该 applet：

```bash
busybox --list | grep -w vmstat
busybox vmstat 1
```

也可以检查常见路径：

```bash
ls -l /bin/vmstat /usr/bin/vmstat /sbin/vmstat /usr/sbin/vmstat 2>/dev/null
```

如果 `busybox vmstat 1` 可以运行，就不需要额外安装工具。

## 2. vmstat 字段与内核接口的对应关系

| vmstat 字段 | 可替代的数据源 | 说明 |
|---|---|---|
| `r` | `/proc/stat` 的 `procs_running`、`/proc/loadavg` | 当前可运行任务数量 |
| `b` | `/proc/stat` 的 `procs_blocked` | 当前等待 I/O 的阻塞任务数量 |
| `swpd` | `/proc/meminfo` | `SwapTotal - SwapFree` |
| `free` | `/proc/meminfo` 的 `MemFree` | 完全空闲的物理内存 |
| `buff` | `/proc/meminfo` 的 `Buffers` | Buffer 使用量 |
| `cache` | `/proc/meminfo` | 主要参考 `Cached`、`SReclaimable` 等字段 |
| `si`、`so` | `/proc/vmstat` 的 `pswpin`、`pswpout` | 累计换入、换出页数，需要采样求差值 |
| `bi`、`bo` | `/proc/diskstats` | 累计读写扇区数，需要采样求差值 |
| `in` | `/proc/stat` 的 `intr`、`/proc/interrupts` | 总中断及各 IRQ 中断次数 |
| `cs` | `/proc/stat` 的 `ctxt` | 累计上下文切换次数 |
| `us/sy/id/wa/st` | `/proc/stat` 第一行 `cpu` | 累计 CPU 时间，需要采样求差值并计算比例 |

## 3. 查看运行队列和阻塞任务

```bash
grep -E '^(procs_running|procs_blocked)' /proc/stat
cat /proc/loadavg
```

典型输出：

```text
procs_running 2
procs_blocked 0
0.20 0.15 0.10 2/126 4321
```

含义：

- `procs_running` 近似对应 `vmstat` 的 `r`；
- `procs_blocked` 近似对应 `vmstat` 的 `b`；
- `/proc/loadavg` 第四项 `2/126` 表示当前可运行任务数与任务总数。

判断逻辑：

```text
procs_running 持续大于逻辑 CPU 数
+ CPU idle 很低
= 可能存在 CPU 排队
```

查看 CPU 数量：

```bash
grep -c '^processor' /proc/cpuinfo
```

## 4. 查看物理内存和 Swap

```bash
grep -E '^(MemTotal|MemFree|MemAvailable|Buffers|Cached|SReclaimable|SwapTotal|SwapFree):' /proc/meminfo
```

重点字段：

| 字段 | 含义 |
|---|---|
| `MemAvailable` | 内核估算的不发生明显换页时可供新程序使用的内存 |
| `MemFree` | 完全空闲的物理内存 |
| `Buffers` | 块设备 Buffer 使用量 |
| `Cached` | 文件页缓存等可回收缓存 |
| `SReclaimable` | 可回收的 Slab 内存 |
| `SwapTotal` | Swap 总量 |
| `SwapFree` | 剩余 Swap |

计算已经使用的 Swap：

```text
swpd = SwapTotal - SwapFree
```

不要只看到 `MemFree` 很低就判断内存不足，应同时查看 `MemAvailable`、换页活动和 Memory PSI。

如果内核支持 PSI：

```bash
cat /proc/pressure/memory
```

## 5. 查看 Swap 换入和换出

```bash
grep -E '^(pswpin|pswpout) ' /proc/vmstat
```

- `pswpin`：系统启动以来累计换入的页数；
- `pswpout`：系统启动以来累计换出的页数。

这些是累计值，不能直接当作 `vmstat` 中每秒的 `si/so`。需要间隔采样：

```text
si = (第二次 pswpin  - 第一次 pswpin)  × 页面大小 / 采样秒数
so = (第二次 pswpout - 第一次 pswpout) × 页面大小 / 采样秒数
```

查看系统页面大小：

```bash
getconf PAGESIZE
```

最小化设备没有 `getconf` 时，常见页面大小为 4096 字节，但不应直接假设；可以检查内核配置、架构文档或由小型程序调用 `sysconf(_SC_PAGESIZE)` 获取。

## 6. 查看 CPU 使用情况

```bash
head -n 1 /proc/stat
```

典型输出：

```text
cpu  1200 20 300 8000 40 10 30 0 0 0
```

字段顺序：

```text
cpu user nice system idle iowait irq softirq steal guest guest_nice
```

这些数值是从系统启动以来累计的 CPU 时间。要得到 `us/sy/id/wa/st` 百分比，需要读取两次并计算差值：

```text
Δtotal = Δuser + Δnice + Δsystem + Δidle + Δiowait
       + Δirq + Δsoftirq + Δsteal

us = (Δuser + Δnice) / Δtotal × 100%
sy = (Δsystem + Δirq + Δsoftirq) / Δtotal × 100%
id = Δidle / Δtotal × 100%
wa = Δiowait / Δtotal × 100%
st = Δsteal / Δtotal × 100%
```

`guest` 已包含在 `user` 中，`guest_nice` 已包含在 `nice` 中，计算总时间时不要再次相加，否则会重复统计。

如果系统有 `top`，最简单的替代方法是：

```bash
top -b -n 1
```

BusyBox `top` 支持的参数可能与 procps-ng 不同，可以先执行：

```bash
busybox top --help
```

## 7. 查看块设备 I/O

```bash
cat /proc/diskstats
```

为了减少输出，可以按设备名过滤：

```bash
grep -E ' (sda|mmcblk0|nvme0n1) ' /proc/diskstats
```

`/proc/diskstats` 包含累计完成的读写次数、读写扇区、I/O 耗时和当前正在处理的 I/O 数量。要得到类似 `bi/bo` 的每秒速率，也需要两次采样求差值：

```text
读取速率 = Δ读取扇区数 × 512 / 采样秒数
写入速率 = Δ写入扇区数 × 512 / 采样秒数
```

`/proc/diskstats` 中的扇区计数通常按内核接口定义的 512 字节单位统计，不等同于设备实际物理扇区大小。

如果系统有对应工具，优先使用：

```bash
iostat -xz 1
```

## 8. 查看中断

查看所有中断的累计总数：

```bash
grep '^intr ' /proc/stat
```

查看各个 IRQ 在不同 CPU 上的次数：

```bash
cat /proc/interrupts
```

连续观察：

```bash
while true; do
    date
    cat /proc/interrupts
    sleep 1
done
```

如果某个 IRQ 的计数异常快速增长，继续确认它对应的网卡、存储、定时器或其他外设，并检查驱动状态。

## 9. 查看上下文切换

```bash
grep '^ctxt ' /proc/stat
```

`ctxt` 是系统启动以来的累计上下文切换次数。每秒速率为：

```text
cs/s = (第二次 ctxt - 第一次 ctxt) / 采样秒数
```

如果系统有 `pidstat`，可以继续定位到进程：

```bash
pidstat -w 1
```

没有 `pidstat` 时，可以查看单个进程的调度状态：

```bash
cat /proc/<PID>/status
cat /proc/<PID>/sched
```

在 `/proc/<PID>/status` 中重点查看：

```text
voluntary_ctxt_switches
nonvoluntary_ctxt_switches
```

## 10. 最小化设备的一次性快照

下面的命令只依赖常见 Shell、`cat`、`grep` 和 `date`：

```bash
date

echo '[run queue]'
grep -E '^(procs_running|procs_blocked)' /proc/stat

echo '[cpu]'
head -n 1 /proc/stat

echo '[memory]'
grep -E '^(MemTotal|MemFree|MemAvailable|Buffers|Cached|SwapTotal|SwapFree):' /proc/meminfo

echo '[swap io]'
grep -E '^(pswpin|pswpout) ' /proc/vmstat

echo '[system]'
grep -E '^(intr|ctxt) ' /proc/stat
```

连续观察原始计数变化：

```bash
while true; do
    date
    grep -E '^(cpu |intr |ctxt |procs_running|procs_blocked)' /proc/stat
    grep -E '^(MemFree|MemAvailable|SwapFree):' /proc/meminfo
    grep -E '^(pswpin|pswpout) ' /proc/vmstat
    sleep 1
done
```

这个循环显示的是原始累计值。除当前状态字段外，判断速率时要观察相邻两次数据的差值。

## 11. PSI：直接观察资源压力

较新的内核可能支持 Pressure Stall Information：

```bash
cat /proc/pressure/cpu
cat /proc/pressure/memory
cat /proc/pressure/io
```

PSI 反映任务因为 CPU、内存或 I/O 资源不足而停顿的时间比例。它不能逐项替代 `vmstat`，但对判断“系统是否真的因某类资源产生延迟”非常有用。

如果目录不存在，可能是内核版本较旧或没有启用相关配置。

## 12. /proc 不存在或字段缺失

先检查 `/proc` 是否挂载：

```bash
mount | grep ' on /proc '
```

如果设备内核支持 procfs，但尚未挂载，可以使用：

```bash
mount -t proc proc /proc
```

如果 `/proc` 中缺少某些接口，可能与以下情况有关：

- 内核没有启用 `CONFIG_PROC_FS`；
- 裁剪掉了 VM 事件或 PSI 等配置；
- 容器限制了可见的 procfs 内容；
- `/proc` 使用了限制性挂载选项；
- 系统并非 Linux，而是 RTOS 或厂商自定义系统。

此时需要检查内核配置：

```bash
zcat /proc/config.gz 2>/dev/null | grep -E 'CONFIG_PROC_FS|CONFIG_VM_EVENT_COUNTERS|CONFIG_PSI'
```

如果 `/proc/config.gz` 不存在，就检查构建目录中的内核 `.config`。

## 13. 安装或编译 vmstat

完整发行版中，`vmstat` 通常属于 `procps` 或 `procps-ng` 软件包：

```bash
# Debian / Ubuntu
apt install procps

# RHEL / CentOS / Fedora
dnf install procps-ng

# Alpine Linux
apk add procps
```

嵌入式系统可以选择：

1. 在 BusyBox 配置中启用 `vmstat` applet；
2. 交叉编译 procps-ng；
3. 只部署所需的静态或动态依赖；
4. 不安装工具，直接使用 `/proc` 和设备自带监控接口。

部署前应考虑根文件系统空间、动态库依赖、目标架构、权限和许可证要求。

## 14. 最实用的替代排查流程

```text
1. /proc/stat
   看 procs_running、procs_blocked 和 CPU 累计时间
              ↓
2. /proc/meminfo + /proc/vmstat
   看 MemAvailable、Swap 和换页活动
              ↓
3. /proc/diskstats
   看块设备读写与 I/O 状态
              ↓
4. /proc/interrupts + ctxt
   看中断和上下文切换
              ↓
5. /proc/pressure/*
   确认 CPU、内存或 I/O 是否造成实际停顿
```

核心原则：`/proc` 中很多值是系统启动以来的累计计数。要模拟 `vmstat 1`，必须按固定间隔采样两次，用差值除以采样时间，而不是直接把累计值解释成每秒速率。
