# perf stat 异常指标分析

发现某项指标异常后，不要立即采集所有事件，而应只选择对应方向的事件继续缩小范围。

```text
整体指标
   ↓
找到异常方向
   ↓
选择对应事件
   ↓
提出原因假设
   ↓
通过对照实验验证
```

## 1. IPC 较低

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

## 2. branch miss 较高

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

## 3. 怀疑 L1、L2 或 LLC Cache

```bash
perf list | grep -Ei 'L1|L2|LLC|cache|mem_load'
```

重点对比：

- 顺序访问与随机访问；
- 小工作集与大工作集；
- 优化前与优化后；
- 单线程与多线程。

预期现象：随机访问或工作集超过 Cache 容量后，Cache miss 增加、IPC 下降、运行时间上升。

## 4. 怀疑 TLB

```bash
perf list | grep -Ei 'dtlb|itlb|tlb'
```

TLB miss 常见于：

- 工作集很大；
- 内存访问跨度较大；
- 随机访问大量不同页面；
- 页表层级较深；
- 没有使用大页且地址分布离散。

## 5. 怀疑 CPU 前端取指

```bash
perf list | grep -Ei 'frontend|icache|idq|fetch|decode'
```

可能原因包括指令缓存未命中、代码体积过大、复杂控制流以及译码供给不足。

## 6. 怀疑 CPU 后端或内存等待

```bash
perf list | grep -Ei 'backend|stall|memory|bound|cycle_activity'
```

可能原因包括数据缓存未命中、DRAM 延迟、执行端口竞争、长依赖链或者 Store Buffer 等资源受限。

## 7. page fault 较高

需要区分次缺页和主缺页：

```bash
perf stat -e page-faults,minor-faults,major-faults ./program
```

- `minor-faults`：通常不需要从磁盘读取，例如首次建立匿名页映射；
- `major-faults`：需要从磁盘或后备存储读取，代价通常更高。

首次运行与后续运行可能受到 Page Cache、按需分配和文件缓存的影响，因此要明确实验使用冷缓存还是热缓存条件。

## 8. context switch 或 CPU migration 较高

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

## 9. 异常方向速查

| 现象 | 优先检查 | 下一步 |
|---|---|---|
| IPC 低、branch miss 高 | 分支结构与分支预测 | 查找分支专用事件 |
| IPC 低、cache miss 高 | Cache、TLB、DRAM | 区分缓存层级和访问模式 |
| page fault 高 | 内存映射、Page Cache、Swap | 区分 minor 和 major |
| context switch 高 | 线程、锁、阻塞、唤醒 | 使用 `perf sched` |
| CPU migration 高 | 亲和性与负载均衡 | 使用 `taskset` 对照 |
| 上述指标都不高但 IPC 低 | 前端、后端、数据依赖 | 使用微架构专用事件 |

