# C++ 面试题：perf stat 指标怎么看

## 1. 这道题考什么？

`perf stat` 用来收集性能计数器统计值，适合做性能分析的第一步。

它主要回答：

```text
程序到底用了多少 CPU？
CPU 执行效率怎么样？
是不是 cache miss、分支预测、缺页、上下文切换、CPU 迁移导致慢？
```

注意：

```text
perf stat 的“参数”分两类：
1. 命令选项：-e、-p、-a、-C、-I、-r 等
2. 性能事件：cycles、instructions、cache-misses、sched:sched_switch 等
```

完整事件列表不是固定的，和 CPU、PMU、内核版本、perf 版本有关。

完整事件要在目标机器上看：

```bash
perf list
```

完整命令选项看：

```bash
perf stat -h
man perf-stat
```

---

## 2. perf stat 最常用命令

运行并统计一个程序：

```bash
perf stat ./app
```

统计已有进程：

```bash
perf stat -p <pid> -- sleep 10
```

统计整个系统：

```bash
perf stat -a -- sleep 10
```

指定事件：

```bash
perf stat -e cycles,instructions,cache-misses,branch-misses ./app
```

每秒输出一次：

```bash
perf stat -I 1000 -p <pid>
```

重复多次取平均：

```bash
perf stat -r 5 ./app
```

---

## 3. perf stat 命令选项总览

### 3.1 选择事件

| 选项 | 作用 | 示例 |
|---|---|---|
| `-e, --event` | 指定事件 | `-e cycles,instructions` |
| `-M, --metrics` | 指定 metric 或 metric group | `-M IPC` |
| `--topdown` | 输出 CPU TopDown 指标 | `perf stat --topdown ./app` |
| `-d, --detailed` | 输出更详细指标，可重复 | `-d`、`-d -d`、`-d -d -d` |

`-e` 可以指定：

1. 符号事件名：`cycles`
2. raw PMU 事件：`r1a8`
3. PMU 格式事件：`cpu/event=0xa8,umask=0x1/`
4. tracepoint：`sched:sched_switch`
5. 带 modifier 的事件：`cycles:u`、`cycles:k`

---

### 3.2 选择统计对象

| 选项 | 作用 | 示例 |
|---|---|---|
| `-p, --pid` | 统计指定进程 | `-p 1234` |
| `-t, --tid` | 统计指定线程 | `-t 1234` |
| `-a, --all-cpus` | 统计所有 CPU，系统级采样 | `-a -- sleep 10` |
| `-C, --cpu` | 统计指定 CPU | `-a -C 0-3` |
| `-G, --cgroup` | 统计指定 cgroup | `-G docker/xxx` |
| `--for-each-cgroup` | 对多个 cgroup 展开统计 | `--for-each-cgroup name` |
| `-b, --bpf-prog` | 统计 BPF 程序 | `--bpf-prog <id>` |

选择建议：

```text
看单个进程：-p
看单个线程：-t
看整机：-a
看某几个 CPU：-a -C
看容器：-G 或 --for-each-cgroup
```

---

### 3.3 控制输出粒度

| 选项 | 作用 | 示例 |
|---|---|---|
| `-A, --no-aggr` | 不聚合 CPU/PMU 计数 | `-A -a` |
| `--per-thread` | 按线程聚合 | `--per-thread -p <pid>` |
| `--per-core` | 按物理核心聚合 | `--per-core -a` |
| `--per-socket` | 按 socket 聚合 | `--per-socket -a` |
| `--per-node` | 按 NUMA node 聚合 | `--per-node -a` |
| `--per-die` | 按 die 聚合 | `--per-die -a` |
| `--per-cluster` | 按 cluster 聚合 | `--per-cluster -a` |
| `--per-cache` | 按 cache 实例聚合 | `--per-cache=L3 -a` |

常见用途：

```text
怀疑 CPU 核间不均衡：--per-core
怀疑 NUMA 不均衡：--per-node
怀疑多 socket 不均衡：--per-socket
怀疑 L3 cache 维度问题：--per-cache=L3
```

---

### 3.4 控制时间和重复

| 选项 | 作用 | 示例 |
|---|---|---|
| `-I, --interval-print` | 按间隔输出增量 | `-I 1000` |
| `--interval-count` | 限制 interval 输出次数 | `--interval-count 5` |
| `--interval-clear` | 每次 interval 清屏 | `--interval-clear` |
| `--timeout` | 到时间自动停止 | `--timeout 10000` |
| `-r, --repeat` | 重复执行并输出平均和方差 | `-r 5` |
| `-D, --delay` | 延迟开始统计 | `-D 5000` |
| `--pre` | 统计前执行命令 | `--pre 'sync'` |
| `--post` | 统计后执行命令 | `--post 'date'` |

示例：

```bash
perf stat -I 1000 -e cycles,instructions -p <pid>
perf stat -r 10 ./app
perf stat -D 5000 -p <pid> -- sleep 20
```

---

### 3.5 控制输出格式

| 选项 | 作用 | 示例 |
|---|---|---|
| `-o, --output` | 输出到文件 | `-o stat.txt` |
| `--append` | 追加输出 | `--append -o stat.txt` |
| `--log-fd` | 输出到指定 fd | `--log-fd 3` |
| `-x, --field-separator` | CSV 风格输出 | `-x ';'` |
| `--table` | repeat 时表格输出 | `--table -r 5` |
| `--metric-only` | 只输出计算后的 metric | `--metric-only` |
| `--summary` | interval 模式输出汇总 | `--summary -I 1000` |
| `--no-csv-summary` | CSV 模式不输出 summary 列 | `--no-csv-summary` |
| `-B, --big-num` | 大数字使用分隔符 | 默认常开 |
| `--no-big-num` | 不使用大数字分隔符 | `--no-big-num` |
| `-v, --verbose` | 输出更详细错误/信息 | `-v` |
| `--quiet` | 不打印普通输出和警告 | `--quiet` |

适合脚本处理：

```bash
perf stat -x ';' -e cycles,instructions ./app 2> stat.csv
```

---

### 3.6 记录和回放 stat 数据

`perf stat` 也有 record/report 子命令：

```bash
perf stat record -o stat.data -- ./app
perf stat report -i stat.data
```

用途：

```text
先在目标机器记录统计数据；
后续再拿出来分析或归档。
```

---

### 3.7 权限、空间和事件控制

| 选项 | 作用 |
|---|---|
| `--all-user` | 事件只统计用户态 |
| `--all-kernel` | 事件只统计内核态 |
| `-i, --no-inherit` | 子任务不继承计数器 |
| `--no-scale` | 不对 multiplex 计数做缩放 |
| `-n, --null` | 空运行，不启动计数器 |
| `--no-affinity` | 不调整调度 CPU affinity |
| `--control` | 用 fifo/fd 控制统计启停 |
| `--bpf-counters` | 使用 BPF 聚合计数器 |
| `--bpf-attr-map` | 指定 BPF pinned map 路径 |

常用例子：

```bash
perf stat -e cycles:u,instructions:u ./app
perf stat -e cycles:k,instructions:k -a -- sleep 10
```

---

## 4. perf 事件类型总览

完整事件用：

```bash
perf list
```

常见分类：

```text
hw           硬件事件
sw           软件事件
cache        硬件 cache 事件
tracepoint   内核 tracepoint
pmu          PMU 专有事件
sdt          静态探针
metric       组合指标
metricgroup  指标组
```

可以按分类看：

```bash
perf list hw
perf list sw
perf list cache
perf list tracepoint
perf list metric
perf list metricgroup
```

---

## 5. 常见硬件事件 hw

| 事件 | 含义 | 用途 |
|---|---|---|
| `cycles` / `cpu-cycles` | CPU 周期 | 判断 CPU 消耗 |
| `instructions` | 指令数 | 和 cycles 计算 IPC |
| `branches` | 分支指令数 | 分支密度 |
| `branch-misses` | 分支预测失败 | 分支是否稳定 |
| `cache-references` | cache 访问 | 计算 miss rate |
| `cache-misses` | cache miss | 数据局部性 |
| `bus-cycles` | 总线周期 | 总线压力，平台相关 |
| `stalled-cycles-frontend` | 前端停顿 | 取指/译码瓶颈 |
| `stalled-cycles-backend` | 后端停顿 | 执行/内存瓶颈 |
| `ref-cycles` | 参考周期 | 不受频率变化影响的周期参考 |

常用组合：

```bash
perf stat -e cycles,instructions,branches,branch-misses,cache-references,cache-misses ./app
```

---

## 6. 常见软件事件 sw

| 事件 | 含义 | 用途 |
|---|---|---|
| `cpu-clock` | CPU clock 软件计数 | CPU 时间 |
| `task-clock` | 任务运行时间 | CPU 利用率 |
| `page-faults` | 缺页总数 | 内存行为 |
| `minor-faults` | minor fault | 页表建立/首次访问 |
| `major-faults` | major fault | 需要磁盘 IO 的缺页 |
| `context-switches` | 上下文切换 | 调度/阻塞 |
| `cpu-migrations` | CPU 迁移 | cache/调度稳定性 |
| `alignment-faults` | 对齐错误 | 架构相关 |
| `emulation-faults` | 指令仿真错误 | 架构相关 |
| `dummy` | dummy event | 工具内部/测试 |
| `bpf-output` | BPF 输出事件 | BPF 相关 |

常用组合：

```bash
perf stat -e task-clock,context-switches,cpu-migrations,page-faults,minor-faults,major-faults ./app
```

---

## 7. 常见 cache 事件

cache 事件通常有三元组：

```text
cache 类型 : 操作 : 结果
```

例子：

```bash
perf stat -e L1-dcache-loads,L1-dcache-load-misses ./app
perf stat -e LLC-loads,LLC-load-misses ./app
perf stat -e dTLB-loads,dTLB-load-misses ./app
```

常见类型：

| 类型 | 含义 |
|---|---|
| `L1-dcache` | L1 数据 cache |
| `L1-icache` | L1 指令 cache |
| `LLC` | Last Level Cache |
| `dTLB` | 数据 TLB |
| `iTLB` | 指令 TLB |
| `branch` | 分支预测相关 |
| `node` | NUMA node 相关，平台相关 |

常见操作：

```text
load
store
prefetch
```

常见结果：

```text
access
miss
```

常用事件：

| 事件 | 用途 |
|---|---|
| `L1-dcache-load-misses` | L1 数据读取 miss |
| `L1-icache-load-misses` | 指令 cache miss |
| `LLC-load-misses` | 末级 cache 读取 miss |
| `dTLB-load-misses` | 数据 TLB miss |
| `iTLB-load-misses` | 指令 TLB miss |

---

## 8. tracepoint 事件

tracepoint 是内核静态跟踪点。

查看：

```bash
perf list tracepoint
```

常见类型：

```text
sched:*
syscalls:*
irq:*
timer:*
block:*
net:*
kmem:*
workqueue:*
```

常用例子：

```bash
perf stat -e sched:sched_switch -a -- sleep 10
perf stat -e syscalls:sys_enter_read,syscalls:sys_enter_write -p <pid> -- sleep 10
perf stat -e irq:irq_handler_entry,irq:irq_handler_exit -a -- sleep 10
```

用途：

| tracepoint | 用途 |
|---|---|
| `sched:sched_switch` | 上下文切换 |
| `sched:sched_wakeup` | 线程唤醒 |
| `syscalls:*` | 系统调用次数 |
| `irq:*` | 中断处理 |
| `block:*` | 块 IO 路径 |
| `kmem:*` | 内核内存分配 |

---

## 9. PMU、raw event 和平台相关事件

有些事件不是通用名称，而是 CPU 或 SoC PMU 专有。

查看 PMU：

```bash
ls /sys/bus/event_source/devices
```

查看 PMU 参数格式：

```bash
ls /sys/bus/event_source/devices/cpu/format
cat /sys/bus/event_source/devices/cpu/format/event
```

raw event 示例：

```bash
perf stat -e r1a8 -a -- sleep 1
```

PMU 格式示例：

```bash
perf stat -e cpu/event=0xa8,umask=0x1/ -a -- sleep 1
```

注意：

```text
raw event 必须查 CPU 厂商手册或 perf list 输出；
不同 CPU 上同一个 raw 编码可能含义不同。
```

---

## 10. event modifier 怎么用？

事件后面可以加冒号 modifier。

常见 modifier：

| modifier | 含义 |
|---|---|
| `u` | 只统计用户态 |
| `k` | 只统计内核态 |
| `h` | hypervisor |
| `G` | guest |
| `H` | host |
| `I` | non idle |
| `p` | precise level |
| `P` | 最大 precise level |
| `D` | pin event 到 PMU |
| `W` | weak group |
| `e` | exclusive |

示例：

```bash
perf stat -e cycles:u,instructions:u ./app
perf stat -e cycles:k,instructions:k -a -- sleep 10
perf stat -e cpu-cycles:p ./app
```

面试里最常用的是：

```text
:u 只看用户态
:k 只看内核态
```

---

## 11. event group 怎么用？

事件组用于让多个事件尽量同时调度，减少 multiplex 带来的误差。

示例：

```bash
perf stat -e '{cycles,instructions,cache-misses}' ./app
```

注意：

```text
硬件计数器数量有限；
事件太多时 perf 会 multiplex；
部分计数会被缩放，精度可能下降。
```

如果看到事件运行时间比例较低，要警惕误差。

---

## 12. perf stat 默认输出指标

不同 perf 版本和平台可能略有差异，常见默认包括：

```text
task-clock
context-switches
cpu-migrations
page-faults
cycles
instructions
branches
branch-misses
```

有的平台还会显示：

```text
cache-references
cache-misses
```

因此不要死背默认事件全集。
需要明确时用：

```bash
perf stat -v ./app
```

或显式指定：

```bash
perf stat -e task-clock,context-switches,cpu-migrations,page-faults,cycles,instructions,branches,branch-misses ./app
```

---

## 13. 核心指标怎么解释？

### 13.1 task-clock

`task-clock` 是任务实际占用 CPU 的总时间。

```text
task-clock / elapsed time = 平均用了几个 CPU
```

例子：

```text
40,000 ms task-clock
10 s elapsed
```

说明平均使用约 4 个 CPU。

判断：

| 现象 | 说明 |
|---|---|
| task-clock 远小于 elapsed | 大部分时间在等待 |
| task-clock 接近 elapsed | 单核 CPU-bound |
| task-clock 是 elapsed 多倍 | 多线程使用多个 CPU |

---

### 13.2 cycles、instructions、IPC

```text
IPC = instructions / cycles
```

经验判断：

| IPC | 含义 |
|---:|---|
| > 2 | 通常较好 |
| 1 - 2 | 常见，需要结合业务 |
| < 1 | 可能有 cache miss、分支、锁、内存等待 |
| < 0.5 | 需要重点排查 stall |

注意：

```text
IPC 没有绝对标准；
必须和同平台、同 workload、优化前后对比。
```

---

### 13.3 cache miss rate

```text
cache miss rate = cache-misses / cache-references
```

经验判断：

| cache miss rate | 含义 |
|---:|---|
| < 1% | 通常较好 |
| 1% - 5% | 常见范围 |
| 5% - 10% | 可能有局部性问题 |
| > 10% | 通常需要重点查 |

常见原因：

1. 随机访问
2. 链表、树、哈希表跳转多
3. 工作集超过 cache
4. false sharing
5. 跨核共享写

---

### 13.4 branch miss rate

```text
branch miss rate = branch-misses / branches
```

经验判断：

| branch miss rate | 含义 |
|---:|---|
| < 1% | 通常较好 |
| 1% - 5% | 常见 |
| 5% - 10% | 可能分支不稳定 |
| > 10% | 需要重点查 |

---

### 13.5 context-switches

上下文切换高可能说明：

1. 线程太多
2. 锁竞争
3. IO 阻塞
4. 条件变量等待频繁
5. 小任务切得太碎

判断：

| 现象 | 说明 |
|---|---|
| CPU 高、context-switches 低 | 纯计算热点 |
| CPU 不高、context-switches 高 | 可能频繁阻塞/唤醒 |
| 延迟抖动、context-switches 高 | 调度和锁竞争要重点看 |

---

### 13.6 page-faults

| 类型 | 含义 |
|---|---|
| minor fault | 页表未建立，但数据在内存 |
| major fault | 需要磁盘 IO，代价高 |

判断：

| 现象 | 说明 |
|---|---|
| 启动阶段 minor fault 高 | 常见 |
| 稳态 major fault 高 | 通常不好 |
| page-faults 持续高 | 可能频繁 mmap、内存压力或文件映射 |

---

## 14. 常用事件组合

### 14.1 基础画像

```bash
perf stat -e task-clock,context-switches,cpu-migrations,page-faults,cycles,instructions,branches,branch-misses ./app
```

### 14.2 CPU 执行效率

```bash
perf stat -e cycles,instructions,branches,branch-misses ./app
```

### 14.3 cache 和 TLB

```bash
perf stat -e cache-references,cache-misses,L1-dcache-loads,L1-dcache-load-misses,LLC-loads,LLC-load-misses,dTLB-loads,dTLB-load-misses ./app
```

### 14.4 调度

```bash
perf stat -e context-switches,cpu-migrations,sched:sched_switch,sched:sched_wakeup -p <pid> -- sleep 10
```

### 14.5 缺页

```bash
perf stat -e page-faults,minor-faults,major-faults -p <pid> -- sleep 10
```

### 14.6 用户态和内核态拆分

```bash
perf stat -e cycles:u,instructions:u,cycles:k,instructions:k -p <pid> -- sleep 10
```

### 14.7 TopDown

```bash
perf stat --topdown -p <pid> -- sleep 10
```

TopDown 常见分类：

```text
Frontend Bound   前端取指/译码瓶颈
Backend Bound    后端执行/内存瓶颈
Bad Speculation  分支预测等错误推测浪费
Retiring         有效完成指令
```

---

## 15. 什么样的指标是好，什么样是差？

这些是经验信号，不是绝对阈值。

| 指标 | 较好信号 | 较差信号 |
|---|---|---|
| IPC | > 1，甚至 > 2 | < 0.5 需要查 |
| cache miss rate | < 1% | > 10% 通常要查 |
| branch miss rate | < 1% | > 10% 通常要查 |
| context switches | 与业务模型匹配 | 每秒几十万且延迟高 |
| cpu migrations | 较低 | 持续高且 cache miss 高 |
| major faults | 稳态接近 0 | 持续增长通常不好 |
| task-clock | 与预期 CPU 使用匹配 | CPU 低但延迟高，说明可能在等待 |

最重要原则：

```text
指标要和业务模型、硬件平台、优化前后对比。
不要只看一个绝对数字下结论。
```

---

## 16. 典型例子

### 16.1 CPU 高，但指标健康

```text
IPC = 2.1
cache miss = 0.6%
branch miss = 0.8%
```

判断：

```text
CPU 在有效执行，可能是正常计算热点。
```

下一步：

```bash
perf record -g -p <pid> -- sleep 10
perf report
```

找具体热点函数。

---

### 16.2 IPC 低，cache miss 高

```text
IPC = 0.35
cache miss = 15%
```

判断：

```text
CPU 大量时间可能在等内存。
```

可能原因：

1. 随机访问
2. 数据结构局部性差
3. 工作集太大
4. false sharing

下一步：

```bash
perf record -g -e cache-misses -p <pid> -- sleep 10
perf report
```

---

### 16.3 延迟高，但 task-clock 低

```text
task-clock 远小于 elapsed
context-switches 高
```

判断：

```text
CPU 不是主要瓶颈，程序可能在等待锁、IO、条件变量或网络事件。
```

下一步：

```bash
pidstat -w -p <pid> 1
perf sched record -- sleep 10
perf sched latency
gdb -p <pid>
```

---

## 17. 常见坑

1. 把 `perf stat` 当成热点定位工具，它主要看整体指标
2. 不知道 `-e` 事件和命令选项不是一回事
3. 死背事件全集，不知道要用 `perf list`
4. 事件太多导致 multiplex，结果误差变大
5. 不看 event running 百分比
6. 不区分用户态和内核态
7. 用一次结果下结论，不重复测
8. workload 不稳定，前后对比无意义
9. 把经验阈值当绝对标准
10. 不知道不同 CPU 支持的事件不一样

---

## 18. 面试回答模板

可以这样回答：

> `perf stat` 用来做整体性能画像。它的参数分两类，一类是命令选项，比如 `-e` 指定事件、`-p` 指定进程、`-a` 看全系统、`-I` 周期输出、`-r` 重复统计；另一类是性能事件，比如 `cycles`、`instructions`、`cache-misses`、`branch-misses`、`context-switches`、`page-faults`。完整事件列表和硬件有关，要用 `perf list` 查看。分析时我会先看 `task-clock` 判断 CPU 使用量，再看 IPC、cache miss、branch miss、context switch、page fault 来判断瓶颈方向。`perf stat` 判断方向，`perf record/report` 定位具体热点。

---

## 19. 最终背诵版

`perf stat` 的本质是：

```text
用性能计数器给程序做整体画像。
```

重点记：

```text
-e 选事件
-p 选进程
-t 选线程
-a 看全系统
-C 选 CPU
-I 周期输出
-r 重复测
-d 输出详细指标
-M 输出 metric
```

关键指标：

```text
task-clock 看 CPU 用量
IPC 看执行效率
cache miss 看数据局部性
branch miss 看分支预测
context switch 看调度/锁/阻塞
page fault 看内存压力
cpu migration 看调度稳定性
```

最后一定要说：

```text
perf stat 的事件不是固定全集，完整列表要在目标机器上用 perf list 查看。
```
