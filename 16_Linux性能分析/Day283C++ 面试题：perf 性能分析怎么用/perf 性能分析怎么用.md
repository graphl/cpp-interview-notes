# C++ 面试题：perf 性能分析怎么用

## 1. 面试主要考什么？

`perf` 是 Linux 下常用的性能分析工具，主要用来分析 CPU、cache、分支预测、上下文切换、缺页、热点函数等问题。

面试官想听到：

1. `perf stat` 看整体指标
2. `perf record/report` 找热点函数
3. `perf top` 实时看热点
4. `perf sched` 看调度延迟
5. `perf c2c` 看 cache line 竞争
6. 如何解释 cycles、instructions、IPC、cache miss、branch miss
7. 什么指标算好，什么指标可能有问题
8. 如何根据指标提出下一步分析方向

核心一句话：

> `perf` 的作用是用硬件性能计数器和内核采样能力，把“程序慢”拆成 CPU 指令、cache、分支、调度、缺页、锁竞争等可观测证据。

---

## 2. perf 分析的基本流程

不要一上来就 `perf record`。
建议流程：

```text
先定义问题
  -> perf stat 看整体指标
  -> 判断是哪类瓶颈
  -> perf record 采样热点
  -> perf report 看函数和调用栈
  -> 针对热点做实验验证
```

常用命令：

```bash
perf stat ./app
perf stat -p <pid> -- sleep 10
perf record -g ./app
perf record -g -p <pid> -- sleep 10
perf report
perf top -p <pid>
```

---

## 3. perf stat 看什么？

最常用：

```bash
perf stat ./app
```

或观察运行中的进程：

```bash
perf stat -p <pid> -- sleep 10
```

典型输出会包含：

```text
task-clock
context-switches
cpu-migrations
page-faults
cycles
instructions
branches
branch-misses
cache-references
cache-misses
```

这些指标不是单独看，要组合判断。

---

## 4. task-clock 和 CPU 利用率

`task-clock` 表示任务实际在 CPU 上运行的时间总和。

示例：

```text
10,000 msec task-clock
10.0 seconds time elapsed
```

如果是单线程程序：

```text
task-clock 接近 elapsed time
  -> 大约占满 1 个 CPU
```

如果是多线程程序：

```text
40,000 msec task-clock
10.0 seconds elapsed
  -> 平均使用约 4 个 CPU
```

判断：

| 现象 | 说明 |
|---|---|
| task-clock 远小于 elapsed | 程序大部分时间在等待 IO、锁、sleep |
| task-clock 约等于 elapsed | 单核 CPU-bound |
| task-clock 是 elapsed 多倍 | 多线程并行占用多个 CPU |

例子：

```text
程序请求延迟高，但 task-clock 很低
```

说明 CPU 可能不是瓶颈，应该继续查 IO、锁、网络、条件变量等待。

---

## 5. cycles、instructions、IPC

核心指标：

```text
cycles       CPU 周期数
instructions 执行的指令数
IPC          instructions / cycles
```

IPC 表示每个 CPU 周期平均执行多少条指令。

一般理解：

| IPC | 大致含义 |
|---:|---|
| > 2 | 通常比较好，流水线利用率较高 |
| 1 - 2 | 常见水平，需要结合业务判断 |
| < 1 | 可能存在 cache miss、分支失败、内存等待、锁等待 |
| 很低，比如 0.2 | 通常说明 CPU 经常在等内存、IO、锁或 pipeline stall |

注意：

```text
IPC 没有绝对标准，不同 CPU、程序类型差别很大。
要和同机器、同 workload、优化前后的结果对比。
```

例子：

```text
10,000,000,000 cycles
2,000,000,000 instructions
IPC = 0.2
```

可能原因：

1. cache miss 很高
2. 随机内存访问
3. 锁竞争
4. 频繁缺页
5. CPU 等待内存或分支预测失败

下一步：

```bash
perf stat -e cache-references,cache-misses,branches,branch-misses -p <pid> -- sleep 10
```

---

## 6. cache-references 和 cache-misses

命令：

```bash
perf stat -e cache-references,cache-misses -p <pid> -- sleep 10
```

重点看 cache miss rate：

```text
cache miss rate = cache-misses / cache-references
```

经验判断：

| cache miss rate | 可能情况 |
|---:|---|
| < 1% | 通常较好 |
| 1% - 5% | 需要结合场景 |
| 5% - 10% | 可能有数据局部性问题 |
| > 10% | 大概率存在明显内存访问问题 |

注意：

```text
不同硬件、事件定义、程序类型会有差异。
比如大规模数据扫描本来 cache miss 就可能高。
```

常见原因：

1. 数据结构太分散
2. 链表、树、哈希表随机访问多
3. 工作集超过 cache
4. 多线程 false sharing
5. 跨核共享写导致 cache line 抖动
6. 大量 memcpy 或 DDR 带宽瓶颈

优化方向：

1. 数组替代链表
2. 结构体字段重排
3. 提高数据局部性
4. 批处理
5. cache line 对齐
6. 分片减少共享写

---

## 7. branches 和 branch-misses

命令：

```bash
perf stat -e branches,branch-misses -p <pid> -- sleep 10
```

重点看：

```text
branch miss rate = branch-misses / branches
```

经验判断：

| branch miss rate | 可能情况 |
|---:|---|
| < 1% | 通常较好 |
| 1% - 5% | 常见范围 |
| 5% - 10% | 可能分支不稳定 |
| > 10% | 分支预测失败较多，可能影响性能 |

常见原因：

1. 大量随机 if/else
2. 数据分布不可预测
3. 虚函数或间接跳转多
4. 状态机分支复杂
5. 热路径里混入大量冷分支

优化方向：

1. 把热路径和冷路径拆开
2. 减少循环中的复杂分支
3. 使用查表替代多重判断
4. 提高数据分布稳定性
5. 让常见分支更靠前

---

## 8. context-switches 上下文切换

命令：

```bash
perf stat -e context-switches,cpu-migrations -p <pid> -- sleep 10
```

上下文切换高可能说明：

1. 线程太多
2. 锁竞争严重
3. 频繁等待条件变量
4. IO 阻塞频繁
5. 小任务切得太碎
6. 线程反复 wakeup/sleep

经验判断：

| 现象 | 可能问题 |
|---|---|
| context-switches 很低但 CPU 高 | 纯 CPU 计算热点 |
| context-switches 很高且 CPU 不高 | 线程频繁阻塞/唤醒 |
| context-switches 很高且延迟抖动 | 调度开销、锁竞争、线程过多 |

例子：

```text
context-switches 每秒几十万
```

如果业务不是高并发 IO 框架，这通常值得警惕。

下一步：

```bash
pidstat -w -p <pid> 1
perf sched record -- sleep 10
perf sched latency
```

---

## 9. cpu-migrations CPU 迁移

CPU 迁移表示线程从一个 CPU 被调度到另一个 CPU。

迁移过多可能导致：

1. cache 热数据失效
2. NUMA 访问变差
3. 延迟抖动
4. cache miss 增加

经验判断：

| 现象 | 说明 |
|---|---|
| migrations 很少 | 通常较稳定 |
| migrations 持续很高 | 可能调度抖动或线程太多 |
| migrations 高且 cache miss 高 | 可能影响 cache 局部性 |

优化方向：

1. 控制线程数
2. 线程池固定工作线程
3. 必要时设置 CPU affinity
4. NUMA 场景下绑定内存和 CPU

---

## 10. page-faults 缺页

命令：

```bash
perf stat -e page-faults,minor-faults,major-faults -p <pid> -- sleep 10
```

区别：

| 类型 | 含义 |
|---|---|
| minor fault | 页表未建立，但数据已经在内存中 |
| major fault | 需要从磁盘加载，代价高 |

判断：

| 现象 | 可能问题 |
|---|---|
| minor fault 高 | 大量新内存分配、mmap、首次访问 |
| major fault 高 | IO 压力、内存不足、swap、文件映射读盘 |
| page faults 运行初期高 | 可能正常，预热阶段 |
| 长时间 major fault 高 | 通常较差，需要重点查 |

优化方向：

1. 预热内存
2. 减少频繁 mmap/munmap
3. 使用内存池
4. 避免 swap
5. 优化文件访问模式

---

## 11. perf record/report 怎么找热点？

采样当前进程：

```bash
perf record -g -p <pid> -- sleep 10
perf report
```

运行程序并采样：

```bash
perf record -g ./app
perf report
```

参数解释：

| 参数 | 含义 |
|---|---|
| `record` | 采样记录性能数据 |
| `-g` | 记录调用栈 |
| `-p <pid>` | 分析指定进程 |
| `-- sleep 10` | 采样 10 秒 |
| `report` | 查看采样结果 |

看 report 时重点看：

1. 哪些函数占比高
2. 热点在用户态还是内核态
3. 热点函数的调用路径
4. 是否是业务函数、库函数、系统调用或锁函数

常见热点含义：

| 热点 | 可能说明 |
|---|---|
| 业务函数 | 算法或循环热点 |
| `memcpy` | 数据拷贝多 |
| `malloc/free` | 频繁分配释放 |
| `pthread_mutex_lock` / `futex` | 锁竞争 |
| `copy_user` | 用户态/内核态拷贝多 |
| `tcp_sendmsg` / `tcp_recvmsg` | 网络路径开销 |
| `do_syscall` | 系统调用频繁 |

---

## 12. perf top 实时看热点

命令：

```bash
perf top
perf top -p <pid>
```

适合：

1. 线上临时观察
2. CPU 高时快速看热点
3. 不想先生成 perf.data

注意：

```text
perf top 是实时采样；
如果问题是偶发的，可能需要 perf record 留证据。
```

---

## 13. perf stat 常用事件组合

### 13.1 CPU 基础指标

```bash
perf stat -e cycles,instructions,branches,branch-misses -p <pid> -- sleep 10
```

看：

1. IPC
2. 分支失败率
3. CPU 是否真的在执行指令

### 13.2 cache 指标

```bash
perf stat -e cache-references,cache-misses,L1-dcache-loads,L1-dcache-load-misses -p <pid> -- sleep 10
```

看：

1. cache miss rate
2. L1 数据 cache 是否命中差
3. 数据局部性是否有问题

### 13.3 调度指标

```bash
perf stat -e context-switches,cpu-migrations,sched:sched_switch -p <pid> -- sleep 10
```

看：

1. 上下文切换
2. CPU 迁移
3. 调度是否频繁

### 13.4 内存缺页

```bash
perf stat -e page-faults,minor-faults,major-faults -p <pid> -- sleep 10
```

看：

1. 是否频繁缺页
2. 是否有 major fault
3. 是否可能内存压力或 mmap 过多

---

## 14. 例子 1：CPU 高，怎么分析？

现象：

```text
top 显示 app 占用 390% CPU
```

第一步：

```bash
perf stat -p <pid> -- sleep 10
```

如果看到：

```text
40,000 msec task-clock
10.0 seconds elapsed
IPC = 2.3
cache-miss rate = 0.5%
branch-miss rate = 0.8%
```

解释：

```text
程序大约用了 4 个 CPU；
IPC 不低，cache 和 branch 都不错；
更像是正常 CPU 计算热点。
```

下一步：

```bash
perf record -g -p <pid> -- sleep 10
perf report
```

如果热点集中在 `calc_hash()`，优化方向就是算法、循环、SIMD、减少重复计算。

---

## 15. 例子 2：CPU 高但 IPC 很低

指标：

```text
IPC = 0.35
cache-miss rate = 15%
branch-miss rate = 2%
```

解释：

```text
IPC 很低，cache miss 很高；
CPU 很可能大量时间在等内存。
```

可能原因：

1. 随机访问大数组
2. 链表/树遍历
3. 哈希表冲突或访问分散
4. 工作集超过 cache
5. 多线程共享数据导致 cache line 抖动

下一步：

```bash
perf record -g -e cache-misses -p <pid> -- sleep 10
perf report
```

优化方向：

1. 改善数据结构局部性
2. 减少指针跳转
3. 批量处理
4. 分片数据
5. 减少跨线程共享写

---

## 16. 例子 3：延迟高但 CPU 不高

指标：

```text
task-clock 远小于 elapsed
context-switches 很高
major-faults 很低
```

解释：

```text
程序不是一直在 CPU 上跑；
可能频繁等待锁、条件变量、IO 或网络事件。
```

下一步：

```bash
pidstat -w -p <pid> 1
perf sched record -- sleep 10
perf sched latency
gdb -p <pid>
```

GDB 中：

```gdb
thread apply all bt
```

如果很多线程卡在 `pthread_mutex_lock` 或 `futex`，说明锁竞争可能是瓶颈。

---

## 17. 例子 4：内存相关性能差

指标：

```text
major-faults 持续增长
page-faults 很高
RSS 持续上涨
```

解释：

```text
可能存在内存压力、文件映射读盘、swap、频繁 mmap 或内存泄漏。
```

下一步：

```bash
cat /proc/<pid>/smaps_rollup
cat /proc/<pid>/maps
vmstat 1
perf record -g -e page-faults -p <pid> -- sleep 10
```

优化方向：

1. 减少频繁分配
2. 预分配或对象池
3. 避免频繁 mmap/munmap
4. 排查内存泄漏
5. 避免 swap

---

## 18. 好指标和差指标怎么理解？

不要把下面数值当绝对标准，它们是排查时的经验信号。

| 指标 | 较好信号 | 较差信号 |
|---|---|---|
| IPC | > 1 或更高 | < 0.5 需要警惕 |
| cache miss rate | < 1% 通常好 | > 10% 通常要查 |
| branch miss rate | < 1% 通常好 | > 10% 通常要查 |
| context switches | 与业务模型匹配 | 每秒几十万且延迟高 |
| cpu migrations | 较低 | 持续很高且 cache miss 高 |
| major faults | 稳态接近 0 | 持续增长通常不好 |
| task-clock | 和预期 CPU 使用匹配 | CPU 低但延迟高，说明在等待 |

最重要原则：

```text
指标要和业务模型、硬件平台、优化前后对比。
不要只看一个绝对数字下结论。
```

---

## 19. perf 分析常见坑

1. 没有加 `-g` 或没有符号，report 里全是地址
2. 编译优化导致调用栈不完整
3. 没装 frame pointer，调用栈采样不准
4. 采样时间太短，结果不稳定
5. workload 不稳定，前后对比无意义
6. 只看函数占比，不看调用路径
7. 把 cache miss 高直接等同于代码有 bug
8. 忽略用户态和内核态热点区别
9. 在线上长时间高频采样，影响业务
10. 不知道不同 CPU 支持的 perf event 可能不同

建议编译参数：

```bash
g++ -O2 -g -fno-omit-frame-pointer main.cpp -o app
```

说明：

1. `-O2`：接近真实运行性能
2. `-g`：保留符号和源码信息
3. `-fno-omit-frame-pointer`：让调用栈更容易采准

---

## 20. 面试回答模板

可以这样回答：

> 我使用 perf 一般先用 `perf stat` 看整体指标，比如 cycles、instructions、IPC、cache miss、branch miss、context switches、page faults。IPC 低可能说明 CPU 在等待内存、锁或分支失败；cache miss 高说明数据局部性可能差；branch miss 高说明分支预测不稳定；context switch 高可能是锁竞争或线程频繁阻塞。确认瓶颈类型后，再用 `perf record -g` 采样调用栈，用 `perf report` 找热点函数和调用路径。如果热点在业务函数，就优化算法；如果在 memcpy，就减少拷贝；如果在 malloc/free，就考虑对象池；如果在 futex 或 mutex，就分析锁竞争。优化后再用同样 workload 复测指标。

---

## 21. 最终背诵版

`perf` 的分析顺序：

```text
perf stat 看指标
  -> 判断 CPU/cache/branch/sched/page fault
  -> perf record -g 采样
  -> perf report 找热点和调用路径
  -> 针对证据优化
  -> 再复测
```

关键指标：

```text
IPC 低：CPU 可能在等内存、锁、分支或其他 stall
cache miss 高：数据局部性可能差
branch miss 高：分支预测可能差
context switch 高：线程调度或锁竞争可能严重
major fault 高：内存压力或文件映射读盘可能严重
task-clock 低但延迟高：程序可能在等待 IO、锁或事件
```
