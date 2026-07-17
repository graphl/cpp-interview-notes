# Linux 调试工具

这个专题用于整理 Linux/C++ 调试相关面试题和实战排查方法。

## 1. 当前已有内容

1. Day276：GDB 的使用
2. Day277：gdbserver 远程调试

## 2. 推荐整理顺序

建议从源码级调试开始，再扩展到线上排查：

```text
GDB
  -> gdbserver
  -> core dump
  -> pstack
  -> strace
  -> lsof
  -> addr2line / objdump / readelf
  -> dmesg / journalctl
```

## 3. 后续可追加主题

1. core dump 如何分析崩溃现场
2. pstack 如何排查线程卡死
3. strace 如何排查系统调用问题
4. lsof 如何排查 fd 泄漏
5. addr2line 如何根据崩溃地址定位代码
6. objdump 如何看反汇编
7. readelf 如何看符号表和段信息
8. dmesg 如何看内核错误
9. journalctl 如何看系统日志
10. ASan/TSan/UBSan 如何定位内存和并发错误

## 4. 回答框架

调试类题目建议按这个顺序回答：

```text
先保留现场
  -> 判断问题类型
  -> 选择调试工具
  -> 看调用栈、变量、内存、线程
  -> 验证假设
  -> 定位根因
```

不要只背命令，要说明每个命令用来验证什么。
