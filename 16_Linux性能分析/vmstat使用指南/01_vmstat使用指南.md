# vmstat 使用指南

相关内容：[设备中不存在 vmstat 时如何查看这些信息](02_设备中不存在vmstat时如何查看这些信息.md)。

`vmstat` 用于观察系统级的进程调度、内存、Swap、块设备 I/O、中断、上下文切换和 CPU 状态。它适合做性能排查的第一层粗查，帮助判断问题主要属于 CPU、内存、I/O、调度还是虚拟化资源竞争。

```text
系统出现变慢、卡顿或延迟
          ↓
vmstat 判断压力方向
          ↓
使用对应工具继续定位到设备或进程
```

## 1. 最常用的命令

```bash
# 每 1 秒采样一次，持续输出
vmstat 1

# 每 1 秒采样一次，共输出 10 次
vmstat 1 10

# 跳过第一行的“开机以来平均值”
vmstat -y 1 10

# 添加时间戳并使用宽格式
vmstat -t -w 1

# 推荐用于现场观察
vmstat -y -t -w 1
```

命令格式：

```text
vmstat [选项] [采样间隔秒数 [采样次数]]
```

如果指定了采样间隔但没有指定次数，`vmstat` 会持续输出，按 `Ctrl+C` 结束。

## 2. 第一行陷阱

`vmstat` 的第一行比较特殊：

- 部分字段是从系统启动到现在的平均值；
- 进程数和内存字段仍反映当前状态；
- 从第二行开始，数据才对应指定的采样周期。

因此分析实时问题时，可以忽略第一行，或者使用：

```bash
vmstat -y 1
```

> 较旧版本的 `vmstat` 可能不支持 `-y`，此时手动忽略第一行即可。

## 3. 默认输出结构

```text
procs -----------memory---------- ---swap-- -----io---- -system-- -------cpu-------
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 2  0      0 512000  32000 900000    0    0    10    25  800 1500 20  5 74  1  0
```

可以把输出分为六组：

| 分组 | 字段 | 主要判断内容 |
|---|---|---|
| `procs` | `r`、`b` | CPU 排队和阻塞任务 |
| `memory` | `swpd`、`free`、`buff`、`cache` | 物理内存和缓存状态 |
| `swap` | `si`、`so` | 当前是否频繁换页 |
| `io` | `bi`、`bo` | 块设备读写吞吐 |
| `system` | `in`、`cs` | 中断和上下文切换 |
| `cpu` | `us`、`sy`、`id`、`wa`、`st` | CPU 时间分布 |

## 4. procs：运行和阻塞任务

| 字段 | 含义 | 判断重点 |
|---|---|---|
| `r` | 正在运行或等待 CPU 的任务数 | 持续大于逻辑 CPU 数时，可能存在 CPU 竞争 |
| `b` | 阻塞等待 I/O 完成的任务数 | 持续不为 0 时，检查磁盘、网络存储或设备 I/O |

查看逻辑 CPU 数量：

```bash
nproc
```

不能只看到某一秒 `r` 较高就断定 CPU 不足。更可靠的证据组合是：

```text
r 持续大于逻辑 CPU 数
+ id 接近 0
+ us 或 sy 较高
= CPU 可能已经饱和
```

## 5. memory：物理内存状态

| 字段 | 含义 |
|---|---|
| `swpd` | 已经使用的 Swap 空间 |
| `free` | 当前完全空闲的物理内存 |
| `buff` | Buffer 使用的内存 |
| `cache` | Page Cache 等缓存使用的内存 |
| `active` | 活跃内存，使用 `vmstat -a` 显示 |
| `inact` | 非活跃内存，使用 `vmstat -a` 显示 |

不要只根据 `free` 很低判断内存不足。Linux 会主动使用空闲内存作为文件缓存，应重点结合：

- `si`、`so` 是否持续增加；
- `/proc/meminfo` 中的 `MemAvailable`；
- Memory PSI 是否持续出现压力；
- 是否发生直接内存回收或 OOM。

继续检查：

```bash
free -h
cat /proc/meminfo
cat /proc/pressure/memory
```

## 6. swap：换入和换出

| 字段 | 含义 |
|---|---|
| `si` | 每秒从 Swap 换入内存的数据量 |
| `so` | 每秒从内存换出到 Swap 的数据量 |

判断时要区分 `swpd` 和 `si/so`：

```text
swpd > 0，但 si/so 长期为 0
```

表示系统使用过 Swap，但当前不一定存在换页压力。

```text
si/so 持续较高
+ b 或 wa 上升
+ 系统响应变慢
= 可能发生内存压力或换页抖动
```

## 7. io：块设备吞吐

| 字段 | 含义 |
|---|---|
| `bi` | 每秒从块设备读取的 KiB |
| `bo` | 每秒写入块设备的 KiB |

`bi/bo` 高只说明 I/O 流量大，不等于设备已经成为瓶颈。需要结合 `b`、`wa`、设备延迟和队列长度判断。

继续检查：

```bash
iostat -xz 1
pidstat -d 1
```

## 8. system：中断和上下文切换

| 字段 | 含义 |
|---|---|
| `in` | 每秒中断次数，包括时钟中断 |
| `cs` | 每秒上下文切换次数 |

`in` 或 `cs` 没有适用于所有机器的固定异常阈值，应该与同一机器的正常基线比较。

`in` 明显升高可能与以下情况有关：

- 网卡包量增加；
- 设备中断风暴；
- 高频定时器；
- 驱动异常。

`cs` 明显升高可能与以下情况有关：

- 线程数量过多；
- 锁竞争；
- 大量短任务；
- 频繁睡眠和唤醒；
- 生产者与消费者切换过于频繁。

继续检查：

```bash
cat /proc/interrupts
pidstat -w 1
mpstat -P ALL 1
perf sched timehist
```

## 9. cpu：CPU 时间分布

| 字段 | 含义 | 常见方向 |
|---|---|---|
| `us` | 用户态 CPU 时间占比 | 业务计算、算法代码 |
| `sy` | 内核态 CPU 时间占比 | 系统调用、网络、驱动、内存管理 |
| `id` | CPU 空闲时间占比 | 越低表示 CPU 越忙 |
| `wa` | CPU 等待 I/O 的时间占比 | 关注存储或其他 I/O 延迟 |
| `st` | 虚拟机被宿主机抢走的 CPU 时间占比 | 关注宿主机资源争抢 |
| `gu` | CPU 运行 KVM Guest 的时间占比 | 主要用于虚拟化宿主机 |

`wa` 较高表示采样期间 CPU 没有可运行任务，同时系统存在未完成的 I/O；它是继续调查 I/O 的线索，但不能单独证明某块磁盘就是瓶颈。

## 10. 常见异常组合

| 现象组合 | 可能方向 | 下一步 |
|---|---|---|
| `r` 高、`us` 高、`id` 低 | 用户态计算压力 | `pidstat -u`、`perf stat`、`perf record` |
| `r` 高、`sy` 高、`id` 低 | 内核路径开销 | `pidstat`、`perf`、`ftrace` |
| `b` 高、`wa` 高、`bi/bo` 活跃 | I/O 等待 | `iostat -xz`、`pidstat -d` |
| `si/so` 持续较高、`wa` 上升 | 内存压力或换页抖动 | `free`、Memory PSI、`sar -B` |
| `cs` 高、`sy` 高 | 调度、锁或频繁唤醒 | `pidstat -w`、`perf sched` |
| `in` 高、`sy` 高 | 中断或驱动压力 | `/proc/interrupts`、`mpstat -I` |
| `st` 高 | 虚拟机被宿主机抢占 | 检查宿主机负载和 vCPU 配额 |

## 11. 实际排查顺序

运行：

```bash
vmstat -y -t -w 1
```

按照下面的顺序观察：

1. 看 `r` 和 `id`：CPU 是否饱和；
2. 看 `b` 和 `wa`：是否存在 I/O 等待；
3. 看 `si` 和 `so`：是否正在频繁换页；
4. 看 `us` 和 `sy`：压力主要在用户态还是内核态；
5. 看 `in` 和 `cs`：是否存在中断或调度异常；
6. 看 `st`：虚拟机是否被宿主机抢占；
7. 使用专用工具定位到具体设备、进程、线程或函数。

```text
vmstat 发现方向
       ├── CPU     → mpstat、pidstat、perf
       ├── 磁盘 I/O → iostat、pidstat -d
       ├── 内存     → free、/proc/meminfo、PSI、sar -B
       ├── 调度     → pidstat -w、perf sched、ftrace
       └── 中断     → /proc/interrupts、mpstat -I
```

## 12. 其他常用选项

| 命令 | 用途 |
|---|---|
| `vmstat -a 1` | 显示 active 和 inactive 内存 |
| `vmstat -s` | 显示内存及事件累计统计 |
| `vmstat -d` | 显示磁盘详细统计 |
| `vmstat -D` | 显示磁盘汇总统计 |
| `vmstat -p <分区>` | 显示指定分区统计 |
| `vmstat -m` | 显示 Slab 信息，可能需要更高权限 |
| `vmstat -S M 1` | 将内存字段切换为 MiB 单位 |
| `vmstat -t 1` | 在每行后追加时间戳 |
| `vmstat -w 1` | 使用宽格式，避免大数值错位 |
| `vmstat -n 1` | 表头只显示一次 |
| `vmstat -y 1` | 不显示开机以来平均值的第一行 |

`-S` 只影响内存和 Swap 等字段的显示单位，不改变 `bi/bo` 字段的单位。

## 13. vmstat 的边界

`vmstat` 只能反映整机总体状态，不能直接回答：

- 哪个进程占用 CPU；
- 哪个线程发生频繁切换；
- 哪块磁盘延迟最高；
- 哪个函数产生 Cache miss；
- 哪条调用路径消耗时间最多。

因此它的定位是：

```text
vmstat 负责分类瓶颈
专用工具负责定位根因
```

## 14. 快速记忆

日常先记住下面七个字段：

```text
r      CPU 是否排队
b      是否有任务阻塞
si/so  是否正在频繁换页
wa     是否存在 I/O 等待
cs     是否频繁上下文切换
st     虚拟机是否被抢 CPU
```

核心原则：不要孤立地看单个瞬时值，要观察持续趋势、异常组合，并与正常业务基线进行比较。
