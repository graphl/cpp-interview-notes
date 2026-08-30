# perf 排查流程与实验方法

性能分析的目标不是收集尽可能多的事件，而是形成“测量、解释、验证”的闭环。

```text
查看整体指标
    ↓
定位热点函数
    ↓
根据异常选择事件
    ↓
设计单变量实验
    ↓
验证优化是否有效
```

## 1. 查看总览

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

如果默认输出不够，可使用十个核心事件：

```bash
perf stat -r 5 \
  -e task-clock,cycles,instructions,\
branches,branch-misses,\
cache-references,cache-misses,\
page-faults,context-switches,cpu-migrations \
  ./program
```

## 2. 定位热点函数

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

## 3. 根据异常方向选择事件

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

## 4. 设计对照实验

每次尽量只改变一个因素，例如：

- 顺序访问改为随机访问；
- 缩小或扩大工作集；
- 固定 CPU 与不固定 CPU；
- 单线程与多线程；
- 优化前与优化后。

建议记录：

只有当指标变化与运行时间变化能够相互印证时，才能更有把握地建立因果关系。

## 5. 常见注意事项

1. **保持实验环境一致**：使用相同输入、编译参数、CPU 频率策略和后台负载。
2. **不要只测一次**：短程序尤其容易受调度和频率变化影响，建议使用 `-r` 重复测量。
3. **关注事件复用**：一次采集过多事件时，有限的硬件计数器会被轮流使用，结果可能产生额外误差。
4. **先比较再判断**：IPC、Cache miss rate 没有适用于所有程序的固定阈值，对照实验通常比绝对数值更重要。
5. **注意权限限制**：若出现权限错误，检查 `/proc/sys/kernel/perf_event_paranoid`，不要为了方便直接长期关闭系统保护。
6. **注意符号和调用栈**：缺少调试符号、二进制被剥离或省略帧指针，都可能影响 `perf report` 的可读性。
7. **统计相关不等于因果**：某个事件与耗时同时升高，只能形成假设，还需要通过单变量实验验证。

## 6. 最终闭环

```text
measure：用 perf stat 或 perf record 收集证据
   ↓
interpret：根据事件、热点和调用路径提出瓶颈假设
   ↓
experiment：只改变一个因素进行对照实验
   ↓
verify：同时检查运行时间和相关指标是否改善
```

