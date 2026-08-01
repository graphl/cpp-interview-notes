# C++ 面试题：core dump 如何还原崩溃现场

## 1. core dump 保存了什么

进程收到会产生 core 的致命信号时，内核或用户态 coredump 处理器可以保存当时的虚拟内存映射、线程寄存器和部分内存内容。调试器再把地址与原二进制、调试符号和共享库对应起来。

```text
崩溃信号
  -> 内核冻结并收集进程状态
  -> 按 core_pattern 写文件或交给 systemd-coredump
  -> gdb 加载 executable + core
  -> 根据寄存器恢复每个线程的栈帧
  -> 根据 DWARF/符号表映射到函数、文件和行号
```

## 2. 生成前检查

```bash
ulimit -c
cat /proc/sys/kernel/core_pattern
cat /proc/$PID/limits | grep -i core
```

systemd 环境可使用：

```bash
coredumpctl list
coredumpctl info <PID-or-exe>
coredumpctl debug <PID-or-exe>
```

必须保存与崩溃进程完全匹配的可执行文件、共享库和调试符号。仅有 core 文件但二进制版本不匹配，栈和变量解释可能错误。

## 3. GDB 调查顺序

```bash
gdb /path/to/executable /path/to/core
```

```gdb
set pagination off
info files
info sharedlibrary
info threads
thread apply all bt full
frame 0
info args
info locals
info registers
x/16i $pc-16
disassemble /m
```

建议先保存所有线程栈，再聚焦崩溃线程。死锁或内存破坏的真正原因可能在其他线程，不能只看 `frame 0`。

## 4. 从现象到根因

```text
信号和 fault address
  -> 崩溃指令正在读/写什么
  -> 寄存器中的对象地址是否合理
  -> 当前栈帧参数和局部变量
  -> 对象由谁创建、何时释放
  -> 其他线程是否正在修改或释放它
  -> 日志、构建版本、sanitizer 或复现实验验证
```

`SIGSEGV` 的崩溃点经常只是损坏最终被使用的位置。越界写可能早已发生，因此需要结合 ASan、watchpoint、硬件 trace 或最小复现继续追根。

## 5. 优化构建的限制

- 内联会让多个源码调用关系折叠。
- 尾调用优化可能消除栈帧。
- 变量可能显示为 `<optimized out>`。
- frame pointer 省略和栈损坏会降低回溯质量。

生产构建建议保留独立调试符号和 build-id；在可接受时使用 `-g` 与 `-fno-omit-frame-pointer` 改善观测性，但仍需评估性能和产物策略。

## 6. 面试口述版

core dump 是进程崩溃时线程寄存器、内存映射和部分内存的快照。分析时必须使用完全匹配的二进制、共享库和调试符号，先保存所有线程栈，再从崩溃指令、寄存器、参数和对象生命周期反推原因。崩溃点不一定是内存被破坏的位置，必要时要用 sanitizer 或复现实验继续验证。
