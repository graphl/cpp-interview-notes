# Linux 性能分析

这个专题用于整理 Linux/C++ 后台和嵌入式 Linux 性能分析相关面试题。

## 1. 当前已有内容

1. Day282：Linux 性能分析知识点总结
2. Day283：perf 性能分析怎么用
3. Day284：perf stat 指标怎么看
4. Day285：perf record 和 report 如何定位热点
5. Day286：火焰图怎么看
6. Day287：top、pidstat、vmstat 怎么分析性能
7. Day288：iostat 和 sar 怎么分析 IO 和历史性能
8. Day289：strace 和 lsof 怎么排查性能问题

## 2. 推荐整理顺序

建议先建立整体框架，再按工具和问题类型拆分：

```text
性能分析总览
  -> perf
  -> 火焰图
  -> top / pidstat / vmstat
  -> iostat / sar
  -> strace / lsof
  -> gdb / pstack
  -> ftrace / trace-cmd
  -> bpftrace
```

## 3. 后续可追加主题

1. `pstack` 和 `gdb` 如何排查线程卡死
2. `ftrace` 和 `trace-cmd` 如何分析内核延迟
3. `bpftrace` 如何做动态追踪
4. 多线程锁竞争如何分析
5. cache miss 和 false sharing 如何分析
6. 嵌入式 Linux 中 DDR、DMA、IRQ 性能问题如何分析
7. `perf c2c` 如何分析 cache line 竞争
8. 压测指标 QPS、P99、吞吐、抖动怎么看

## 4. 回答框架

性能分析题建议按这个顺序回答：

```text
先明确指标
  -> 再分类瓶颈
  -> 选择低成本工具
  -> 收集证据
  -> 定位热点
  -> 小实验验证
  -> 最后优化
```

不要一上来就说“用 perf”。面试里更重要的是说明为什么选这个工具、看哪个指标、指标异常意味着什么。
