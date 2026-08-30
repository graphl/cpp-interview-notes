# perf stat 核心指标与十个事件

`perf` 的事件非常多，日常使用不需要记住完整的 `perf list`。第一步应使用少量通用指标判断整体瓶颈方向。

## 1. 通用采集命令

```bash
perf stat -r 5 \
  -e task-clock,cycles,instructions,\
branches,branch-misses,\
cache-references,cache-misses,\
page-faults,context-switches,cpu-migrations \
  ./program
```

`-r 5` 表示重复运行 5 次，可以观察平均值和波动，减少单次测量偶然性的影响。

对于顺序访问与随机访问等对照实验，这组指标通常已经能够给出主要结论。

## 2. 只需要先记住的十个事件

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

可以按四组记忆：

| 分组 | 事件 | 回答的问题 |
|---|---|---|
| CPU 效率 | `task-clock`、`cycles`、`instructions` | 用了多少 CPU 时间？每周期完成多少指令？ |
| 分支 | `branches`、`branch-misses` | 控制流是否难以预测？ |
| Cache | `cache-references`、`cache-misses` | Cache 访问和未命中压力是否增大？ |
| 内存与调度 | `page-faults`、`context-switches`、`cpu-migrations` | 是否存在缺页、频繁调度或跨核迁移？ |

## 3. 三个常用公式

```text
IPC              = instructions / cycles
cache miss rate  = cache-misses / cache-references × 100%
branch miss rate = branch-misses / branches × 100%
```

IPC 越高，通常表示 CPU 每个周期完成的有效指令越多。但这些指标没有脱离具体 CPU 和工作负载的统一好坏阈值，应重点比较同一机器上不同版本或不同访问模式的差异。

> `cache-references` 和 `cache-misses` 是通用硬件事件，具体映射到哪一级 Cache，可能因 CPU、内核和 PMU 实现而异。深入分析时应使用具体微架构事件。

## 4. page-faults 的分类

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

`minor-faults` 数量多不一定意味着性能异常，因为按需分配内存时自然会产生次缺页。`major-faults` 通常代价更高，如果数量持续增加并伴随 I/O 延迟，应进一步检查文件访问、内存压力和 Swap。

