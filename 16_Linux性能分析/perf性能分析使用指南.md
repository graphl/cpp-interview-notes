# perf 性能分析使用指南

`perf` 的事件非常多，日常使用不需要记住完整的 `perf list`。更有效的方法是先通过少量通用指标判断瓶颈方向，再针对异常方向选择更细的硬件事件。

基本分析路径：

```text
整体指标
   ↓
发现异常方向
   ↓
选择对应事件
   ↓
定位热点函数和调用路径
   ↓
设计对照实验并验证结论
```

## 一、第一层：通用核心指标

日常分析先看下面这些指标：

```bash
perf stat -r 5 \
  -e task-clock,cycles,instructions,\
branches,branch-misses,\
cache-references,cache-misses,\
page-faults,context-switches,cpu-migrations \
  ./program
```

`-r 5` 表示重复运行 5 次，可以观察平均值和波动，减少单次测量偶然性的影响。

| 指标 | 主要判断内容 |
|---|---|
| `task-clock` | 程序实际占用 CPU 的时间 |
| `cycles` | 消耗的 CPU 周期数 |
| `instructions` | 完成的指令数 |
| `cycles` 与 `instructions` | 计算 IPC，判断整体执行效率 |
| `branches` | 执行的分支指令数量 |
| `branch-misses` | 分支预测失败次数 |
| `cache-references` | 硬件缓存访问情况的通用统计 |
| `cache-misses` | 硬件缓存未命中情况的通用统计 |
| `page-faults` | 缺页次数 |
| `context-switches` | 上下文切换次数 |
| `cpu-migrations` | 任务在不同 CPU 核之间迁移的次数 |

对于顺序访问与随机访问等对照实验，这一层通常已经能够给出主要结论。

### 常用计算公式

IPC（Instructions Per Cycle）：

```text
IPC = instructions / cycles
```

IPC 越高，通常表示 CPU 每个周期完成的有效指令越多。但 IPC 没有脱离具体 CPU 和工作负载的统一好坏阈值，应重点比较同一机器上不同版本或不同访问模式的差异。

缓存未命中率：

```text
cache miss rate = cache-misses / cache-references × 100%
```

分支预测失败率：

```text
branch miss rate = branch-misses / branches × 100%
```

> `cache-references` 和 `cache-misses` 是通用硬件事件，具体统计的是哪一级缓存以及如何映射，可能因 CPU、内核和 PMU 实现而异。深入分析时应改用具体微架构事件。

## 二、如何解释第一层结果

### 1. IPC 较低

例如 IPC 明显低于同类实现，或者在对照实验中从较高值下降到小于 1，说明 CPU 流水线中可能存在较多等待。

可能原因包括：

- Cache 或内存访问延迟；
- 分支预测失败；
- 前端取指、译码受阻；
- 指令之间存在较长的数据依赖；
- 锁竞争或调度等待；
- 工作负载本身包含高延迟指令。

继续测量：

```bash
perf stat -r 5 \
  -e cycles,instructions,\
cache-references,cache-misses,\
branches,branch-misses \
  ./program
```

不能只根据 IPC 低就断定是 Cache 问题，必须结合其他事件继续缩小范围。

### 2. branch miss 较高

先计算分支预测失败率，再查找当前 CPU 支持的分支事件：

```bash
perf list | grep -i branch
```

典型原因：

- 数据相关的随机分支；
- 大量不可预测的条件判断；
- 间接跳转目标不稳定；
- 不同输入导致控制流差异较大。

可以尝试将复杂分支改成更易预测的控制流，然后对比运行时间、IPC 和 branch miss rate。

### 3. 怀疑 L1、L2 或 LLC Cache

```bash
perf list | grep -Ei 'L1|L2|LLC|cache|mem_load'
```

重点对比：

- 顺序访问与随机访问；
- 小工作集与大工作集；
- 优化前与优化后；
- 单线程与多线程。

预期现象：随机访问或工作集超过 Cache 容量后，Cache miss 增加、IPC 下降、运行时间上升。

### 4. 怀疑 TLB

```bash
perf list | grep -Ei 'dtlb|itlb|tlb'
```

TLB miss 常见于：

- 工作集很大；
- 内存访问跨度较大；
- 随机访问大量不同页面；
- 页表层级较深；
- 没有使用大页且地址分布离散。

### 5. 怀疑 CPU 前端取指

```bash
perf list | grep -Ei 'frontend|icache|idq|fetch|decode'
```

可能原因包括指令缓存未命中、代码体积过大、复杂控制流以及译码供给不足。

### 6. 怀疑 CPU 后端或内存等待

```bash
perf list | grep -Ei 'backend|stall|memory|bound|cycle_activity'
```

可能原因包括数据缓存未命中、DRAM 延迟、执行端口竞争、长依赖链或者 Store Buffer 等资源受限。

### 7. page fault 较高

需要区分轻微缺页和主要缺页：

```bash
perf stat -e page-faults,minor-faults,major-faults ./program
```

- `minor-faults`：通常不需要从磁盘读取，例如首次建立匿名页映射；
- `major-faults`：需要从磁盘或后备存储读取，代价通常更高。

首次运行与后续运行可能受到 Page Cache、按需分配和文件缓存的影响，因此要明确实验是否需要冷缓存或热缓存条件。

### 8. context switch 或 CPU migration 较高

进一步检查：

```bash
perf stat -e context-switches,cpu-migrations ./program
perf sched record ./program
perf sched timehist
```

常见原因包括：

- 线程数量远大于 CPU 数量；
- 锁竞争与频繁唤醒；
- 任务运行时间过短；
- CPU 亲和性不合理；
- 系统中存在其他干扰负载。

可以结合 `taskset` 固定 CPU 做对照实验：

```bash
taskset -c 2 perf stat -r 5 ./program
```

## 三、第三层：CPU 型号专用事件

下面这些属于 CPU 厂商或具体微架构事件：

```text
mem_load_retired.l1_miss
l2_rqsts.miss
cycle_activity.stalls_mem_any
uops_retired.retire_slots
```

它们适合更深入的微架构分析，但不同 CPU 支持的名称和含义可能不同：

```text
Intel 事件 != AMD 事件 != ARM 事件
```

因此不用死记事件名称，应当先确认 CPU 型号，再从本机支持的事件中查找：

```bash
lscpu
perf list
```

如果事件不受支持，`perf stat` 可能显示 `<not supported>`；如果 PMU 计数器不足，可能发生事件复用，输出中会显示事件实际运行时间的比例。采集事件过多会降低结果精度，所以应尽量按问题分组测量。

## 四、perf list 的使用方法

`perf list` 更像一本当前 CPU 的事件字典，不是必须背完的命令表。

可以尝试按类别查看：

```bash
# 硬件事件
perf list hardware

# 软件事件
perf list software

# 缓存事件
perf list cache

# 跟踪点
perf list tracepoint

# PMU 事件
perf list pmu
```

不同 `perf` 版本的分类过滤行为可能不同。如果分类命令没有得到预期结果，直接使用关键词过滤：

```bash
perf list | grep -Ei 'branch|cache|L1|L2|LLC|tlb|stall|memory'
```

## 五、一套实际排查流程

### 第一步：查看总览

```bash
perf stat -r 5 ./program
```

重点回答：

1. 程序运行多久？多次运行是否稳定？
2. IPC 相比基线是升高还是降低？
3. 分支预测失败率是否明显升高？
4. Cache 未命中率是否明显升高？
5. page fault 是否异常？
6. context switch 和 CPU migration 是否异常？

### 第二步：定位热点函数

```bash
perf record -g ./program
perf report
```

重点回答：

1. 时间主要花在哪个函数？
2. 热点位于用户态还是内核态？
3. 哪条调用路径贡献了主要开销？
4. 热点是否符合原先对瓶颈的猜测？

如果调用栈不完整，可以在编译时保留调试信息和帧指针：

```bash
gcc -O2 -g -fno-omit-frame-pointer program.c -o program
```

### 第三步：根据异常方向选择事件

```text
IPC 低
├── branch miss 高
│   └── 检查分支结构和分支预测事件
├── cache miss 高
│   └── 检查各级 Cache、TLB 和内存访问模式
├── page fault 高
│   └── 检查内存映射、按需分配和文件 I/O
├── context switch 高
│   └── 检查线程数量、锁竞争、唤醒和调度
└── 上述指标都不高
    └── 检查前端、后端、数据依赖和微架构停顿
```

### 第四步：设计对照实验

每次尽量只改变一个因素，例如：

- 顺序访问改为随机访问；
- 缩小或扩大工作集；
- 固定 CPU 与不固定 CPU；
- 单线程与多线程；
- 优化前与优化后。

## 六、只需要先记住的十个事件

```text
task-clock        # 程序实际占用 CPU 的时间；可结合 CPU 数量判断并行程度
cycles            # CPU 周期数；表示程序总共消耗了多少处理器周期
instructions      # 完成执行的指令数；与 cycles 一起计算 IPC
branches          # 执行的分支指令数；作为计算分支预测失败率的分母
branch-misses     # 分支预测失败次数；比例高可能导致流水线清空和重取指
cache-references  # 通用硬件 Cache 访问次数；具体含义会随 CPU/PMU 而变化
cache-misses      # 通用硬件 Cache 未命中次数；与 references 计算未命中率
page-faults       # 缺页总次数；包括 minor faults 和 major faults
context-switches  # 上下文切换次数；过多时关注线程、锁、阻塞和频繁唤醒
cpu-migrations    # 任务迁移到其他 CPU 核的次数；过多可能破坏 Cache 局部性
```

其中，`page-faults` 可以进一步拆成两类：

| 事件 | 中文 | 是否需要存储 I/O | 常见场景 |
|---|---|---|---|
| `minor-faults` | 次缺页／轻微缺页 | 不需要 | 匿名内存首次访问、写时复制、目标页已在 Page Cache 中 |
| `major-faults` | 主缺页／严重缺页 | 需要 | 必须从文件或 Swap 等后备存储读取页面 |

```text
page-faults = minor-faults + major-faults
```

需要区分两者时使用：

```bash
perf stat -e page-faults,minor-faults,major-faults ./program
```

`minor-faults` 数量多不一定意味着性能异常，因为按需分配内存时自然会产生次缺页；`major-faults` 通常代价更高，如果数量持续增加并伴随 I/O 延迟，应进一步检查文件访问、内存压力和 Swap。

可以按下面四组记忆：

| 分组 | 事件 | 回答的问题 |
|---|---|---|
| CPU 效率 | `task-clock`、`cycles`、`instructions` | 用了多少 CPU 时间？每周期完成多少指令？ |
| 分支 | `branches`、`branch-misses` | 控制流是否难以预测？ |
| Cache | `cache-references`、`cache-misses` | Cache 访问和未命中压力是否增大？ |
| 内存与调度 | `page-faults`、`context-switches`、`cpu-migrations` | 是否存在缺页、频繁调度或跨核迁移？ |

再记住三个公式：

```text
IPC              = instructions / cycles
cache miss rate  = cache-misses / cache-references × 100%
branch miss rate = branch-misses / branches × 100%
```

核心原则：先用通用指标发现方向，再查找本机支持的专用事件，最后通过热点分析和对照实验验证结论。

## 七、常见注意事项

1. **保持实验环境一致**：使用相同输入、编译参数、CPU 频率策略和后台负载。
2. **不要只测一次**：短程序尤其容易受调度和频率变化影响，建议使用 `-r` 重复测量。
3. **关注事件复用**：一次采集过多事件时，有限的硬件计数器会被轮流使用，结果可能产生额外误差。
4. **先比较再判断**：IPC、Cache miss rate 没有适用于所有程序的固定阈值，对照实验通常比绝对数值更重要。
5. **注意权限限制**：若出现权限错误，检查 `/proc/sys/kernel/perf_event_paranoid`，不要为了方便直接长期关闭系统保护。
6. **注意符号和调用栈**：缺少调试符号、二进制被剥离或省略帧指针，都可能影响 `perf report` 的可读性。
7. **统计相关不等于因果**：某个事件与耗时同时升高，只能形成假设，还需要通过单变量实验验证。
