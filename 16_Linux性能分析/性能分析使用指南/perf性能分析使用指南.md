# perf 性能分析使用指南

`perf` 的事件很多，不需要从一开始就学习完整的 `perf list`。推荐按照“通用指标 → 异常方向 → 专用事件 → 热点与实验”的顺序学习和排查。

## 文档导航

### 1. [perf stat 核心指标与十个事件](01_perf_stat核心指标与十个事件.md)

先学习日常最常用的十个事件：

```text
task-clock
cycles
instructions
branches
branch-misses
cache-references
cache-misses
page-faults
context-switches
cpu-migrations
```

这篇还包括 IPC、Cache miss rate、Branch miss rate，以及 `minor-faults` 和 `major-faults` 的区别。

### 2. [perf stat 异常指标分析](02_perf_stat异常指标分析.md)

根据第一轮结果继续深入：

- IPC 低；
- Branch miss 高；
- Cache miss 高；
- TLB miss；
- CPU 前端或后端停顿；
- Page fault、上下文切换或 CPU 迁移过多。

### 3. [perf 专用事件与 perf list](03_perf专用事件与perf_list.md)

介绍 Intel、AMD、ARM 等不同 CPU 的专用 PMU 事件，以及如何按关键词查询本机支持的事件、识别事件不支持和事件复用。

### 4. [perf 排查流程与实验方法](04_perf排查流程与实验方法.md)

串联完整排查闭环：

```text
perf stat 查看整体指标
          ↓
perf record/report 定位热点
          ↓
按异常方向选择专用事件
          ↓
单变量对照实验
          ↓
验证运行时间和指标是否同时改善
```

## 推荐阅读顺序

```text
01 核心指标与十个事件
        ↓
02 异常指标分析
        ↓
03 专用事件与 perf list
        ↓
04 排查流程与实验方法
```

如果只是日常使用，掌握第 1 篇和第 4 篇即可；遇到具体微架构问题时，再查第 2 篇和第 3 篇。
