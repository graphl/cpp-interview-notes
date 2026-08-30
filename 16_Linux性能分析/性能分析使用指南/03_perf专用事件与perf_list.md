# perf 专用事件与 perf list

通用事件只能帮助判断大方向。进入微架构分析后，需要查询当前 CPU 实际支持的 PMU 事件。

## 1. CPU 型号专用事件

下面是一些常见的微架构事件示例：

```text
mem_load_retired.l1_miss
l2_rqsts.miss
cycle_activity.stalls_mem_any
uops_retired.retire_slots
```

它们适合分析具体缓存层级、内存等待和流水线状态，但不同 CPU 支持的名称和含义可能不同：

```text
Intel 事件 != AMD 事件 != ARM 事件
```

因此不需要死记事件名称。应当先确认 CPU 型号，再从本机支持的事件中查找：

```bash
lscpu
perf list
```

## 2. perf list 的作用

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

不同 `perf` 版本的分类过滤行为可能不同。如果分类命令没有得到预期结果，直接使用关键词过滤。

## 3. 按问题查找事件

```bash
# 分支预测
perf list | grep -Ei 'branch|br_misp'

# L1、L2、LLC 和内存加载
perf list | grep -Ei 'L1|L2|LLC|cache|mem_load'

# TLB
perf list | grep -Ei 'dtlb|itlb|tlb'

# CPU 前端
perf list | grep -Ei 'frontend|icache|idq|fetch|decode'

# CPU 后端和内存等待
perf list | grep -Ei 'backend|stall|memory|bound|cycle_activity'
```

核心方法：

```text
先通过通用事件确定异常方向
              ↓
使用 perf list 搜索本机事件
              ↓
选择少量事件进行测量
              ↓
结合热点和对照实验验证
```

## 4. 事件不支持和事件复用

如果事件不受支持，`perf stat` 可能显示：

```text
<not supported>
```

常见原因包括：

- 当前 CPU 没有该事件；
- 事件名称属于其他微架构；
- 内核或 `perf` 版本不支持；
- 虚拟机没有暴露对应 PMU；
- 系统权限限制访问硬件计数器。

硬件 PMU 计数器数量有限。一次采集过多事件时，`perf` 会轮流调度事件，即事件复用。输出中可能显示事件实际运行时间的比例；比例偏低时，统计误差可能增大。

因此应尽量按方向分组采集：

```text
第一组：cycles + instructions
第二组：branches + branch-misses
第三组：Cache 或 TLB 专用事件
第四组：前端或后端停顿事件
```

## 5. 使用原则

1. 先确认 CPU 型号和本机事件支持情况。
2. 不直接照抄其他 CPU 上的事件名称。
3. 一次只采集与当前假设有关的少量事件。
4. 关注事件复用比例和测量误差。
5. 事件计数只能形成证据，需要结合热点和对照实验建立因果关系。

