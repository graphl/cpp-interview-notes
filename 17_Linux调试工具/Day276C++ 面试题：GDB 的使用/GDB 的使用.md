# C++ 面试题：GDB 的使用

## 1. 面试主要考什么？

GDB 面试题不是只考命令背诵，而是看你能不能用调试器定位真实问题。

面试官想听到：

1. 如何编译可调试程序
2. 如何设置断点和单步执行
3. 如何查看调用栈
4. 如何查看变量、内存、寄存器
5. 如何调试 core dump
6. 如何调试多线程程序
7. 如何调试动态库和崩溃问题
8. 如何从现象一步步缩小问题范围

核心一句话：

> GDB 是 Linux 下常用的源码级和汇编级调试工具，可以通过断点、单步、栈回溯、变量查看、内存检查、多线程切换和 core dump 分析来定位程序运行时问题。

---

## 2. 如何编译方便 GDB 调试？

常用编译选项：

```bash
g++ -g -O0 main.cpp -o app
```

含义：

1. `-g`：生成调试信息
2. `-O0`：关闭优化，避免变量被优化掉、代码顺序变化太大
3. `-Wall -Wextra`：打开常见警告

如果是线上问题，可能不能完全关闭优化，可以用：

```bash
g++ -g -O2 main.cpp -o app
```

面试回答：

> 调试时一般要带 `-g` 生成符号信息，开发阶段可以用 `-O0` 降低优化干扰。如果是线上程序，可能保留 `-O2`，但要确保二进制和符号文件匹配。

### 2.1 为什么需要 `-g`？

`-g` 的作用是让编译器在目标文件和可执行文件里生成调试信息。

这些调试信息会告诉 GDB：

1. 机器指令对应哪一个源文件、哪一行代码
2. 函数名、变量名、类型名是什么
3. 局部变量、函数参数在栈上、寄存器里还是被优化掉了
4. 结构体、类、模板实例的类型布局
5. inline 函数、宏、作用域等源码级信息

没有 `-g`，CPU 仍然能执行程序，但 GDB 不知道很多源码级语义。

可以这样理解：

```text
程序运行依赖的是机器指令；
GDB 源码级调试依赖的是调试信息。
```

所以 `-g` 不是让程序“能运行”，而是让 GDB “能看懂源码和变量”。

---

### 2.2 不加 `-g` 为什么也可以调试？

不加 `-g` 也可以调试，因为可执行文件里仍然有机器指令，通常也还有一部分符号信息。

GDB 仍然可以做这些事：

```gdb
run
bt
info registers
x/10i $pc
disassemble
b *0x401000
info files
info proc mappings
```

也就是说，不加 `-g` 时仍然可以：

1. 启动程序
2. attach 进程
3. 查看寄存器
4. 查看内存
5. 查看汇编
6. 按地址下断点
7. 根据函数符号下断点，前提是符号没被 strip
8. 分析 core dump 的崩溃地址和调用栈

但是会少很多源码级能力：

1. 不能准确显示源代码行
2. 不能方便查看局部变量名
3. 不能方便查看结构体字段和类型
4. 调用栈可能只有函数地址或少量函数名
5. `bt full` 信息会很少
6. 很难直接判断变量值为什么错

面试回答：

> 不加 `-g` 也能调，因为 GDB 可以基于机器指令、寄存器、内存和符号表做汇编级调试。但没有 `-g` 时缺少源码行号、变量名、类型和作用域信息，所以只能更多依赖地址、反汇编和寄存器，调试效率会低很多。

---

### 2.3 `-g` 到底多了什么？

`-g` 通常会增加 DWARF 调试信息。

可以用这些命令观察：

```bash
readelf -S app | grep debug
readelf --debug-dump=info app
objdump --dwarf=info app
```

常见调试段：

```text
.debug_info       类型、变量、函数等核心调试信息
.debug_line       源码行号和机器地址的对应关系
.debug_str        调试字符串表
.debug_abbrev     DWARF 缩写表
.debug_frame      栈回溯相关信息
```

有了这些信息，GDB 才能做到：

```gdb
b file.cpp:20
list
p local_var
p obj.member
ptype obj
info locals
info args
disassemble /m function
```

核心区别：

```text
不加 -g：
  GDB 主要看到地址、寄存器、汇编、少量符号。

加了 -g：
  GDB 能把地址映射回源码、变量、类型、行号和作用域。
```

---

### 2.4 `-g`、符号表、strip 有什么关系？

这里要区分两类信息：

```text
符号表：
  函数名、全局变量名等链接和符号解析相关信息。

调试信息：
  源码行号、局部变量、类型、作用域等 GDB 调试信息。
```

不加 `-g`，程序可能仍然有 `.symtab` 或 `.dynsym`，所以 GDB 可能还能看到函数名。

如果执行了 strip：

```bash
strip app
```

会删除很多符号和调试信息。

这时 GDB 可能只能看到：

```text
地址
寄存器
汇编
动态符号中的少量函数名
```

线上常见做法是：

```bash
g++ -g -O2 main.cpp -o app
objcopy --only-keep-debug app app.debug
strip --strip-debug app
objcopy --add-gnu-debuglink=app.debug app
```

含义：

```text
线上部署较小的 stripped 二进制；
调试时保留单独的 debug symbol 文件；
分析 core dump 时让 GDB 加载匹配的符号文件。
```

面试里要强调：

> 调试符号文件必须和线上二进制严格匹配，否则行号、调用栈和变量信息可能是错的。

---

### 2.5 `-g` 和 `-O0` 是一回事吗？

不是。

| 选项 | 作用 |
|---|---|
| `-g` | 生成调试信息 |
| `-O0` | 关闭优化 |
| `-O2` | 开启优化 |

可以有这些组合：

```bash
g++ -g -O0 main.cpp -o app
g++ -g -O2 main.cpp -o app
g++ -O0 main.cpp -o app
g++ -O2 main.cpp -o app
```

区别：

```text
-g -O0：
  最适合开发调试，源码行和变量最直观。

-g -O2：
  适合线上符号调试，但可能出现变量 optimized out、函数 inline、代码顺序变化。

不加 -g：
  仍可汇编级调试，但源码级信息不足。
```

遇到：

```text
<optimized out>
```

通常说明变量被编译器优化掉了，或者当前位置已经无法还原这个变量。

---

## 3. GDB 基本启动方式

调试可执行程序：

```gdb
gdb ./app
run
```

带参数运行：

```gdb
gdb --args ./app arg1 arg2
run
```

附加到正在运行的进程：

```bash
gdb -p <pid>
```

调试 core dump：

```bash
gdb ./app core
```

---

## 4. 断点怎么用？

常用命令：

```gdb
break main
b Foo::bar
b file.cpp:20
b *0x400123
info breakpoints
delete 1
disable 1
enable 1
continue
```

条件断点：

```gdb
b file.cpp:30 if count == 100
```

临时断点：

```gdb
tbreak main
```

面试回答：

> 断点可以按函数名、文件行号、地址设置。遇到循环或偶发问题时，可以用条件断点减少无效停顿。调试没有符号的程序时，也可以对地址下断点。

---

## 5. 单步调试怎么用？

常用命令：

```gdb
next        # 单步执行，不进入函数
step        # 单步执行，进入函数
finish      # 执行到当前函数返回
continue    # 继续运行
until       # 运行到指定位置或跳出循环
```

区别：

| 命令 | 含义 |
|---|---|
| `next` | 执行下一行，不进入函数 |
| `step` | 执行下一行，会进入函数 |
| `finish` | 执行到当前函数返回 |
| `continue` | 继续运行到下一个断点 |

---

## 6. 如何查看调用栈？

常用命令：

```gdb
bt
bt full
frame 0
frame 1
up
down
info args
info locals
```

含义：

1. `bt`：查看调用栈
2. `bt full`：查看调用栈和局部变量
3. `frame n`：切换到第 n 层栈帧
4. `info args`：查看函数参数
5. `info locals`：查看局部变量

面试回答：

> 崩溃时我一般先用 `bt` 看调用栈，定位崩溃发生在哪个函数；再切到对应 `frame`，用 `info args` 和 `info locals` 看参数和局部变量是否异常。

---

## 7. 如何查看变量？

常用命令：

```gdb
print var
p var
p *ptr
p array[0]
p obj.member
display var
undisplay 1
set var count = 10
```

如果变量被优化掉，可能看到：

```text
<optimized out>
```

这时要确认编译优化级别和调试符号。

---

## 8. 如何查看内存？

常用命令：

```gdb
x/16xb ptr    # 按字节查看 16 个
x/16xw ptr    # 按 4 字节查看 16 个
x/8gx ptr     # 按 8 字节查看 8 个
x/s ptr       # 按字符串查看
x/10i $pc     # 查看当前 PC 附近 10 条指令
```

格式说明：

```text
x/NFU ADDRESS

N: 数量
F: 格式，x 十六进制，d 十进制，s 字符串，i 指令
U: 单位，b 字节，h 2 字节，w 4 字节，g 8 字节
```

适合场景：

1. 判断指针是否野指针
2. 查看字符串内容
3. 查看数组或结构体内存
4. 查看函数指针、虚表指针
5. 查看当前汇编指令

---

## 9. 如何查看寄存器和反汇编？

常用命令：

```gdb
info registers
p/x $pc
p/x $sp
p/x $fp
x/10i $pc
disassemble
disassemble /m main
```

常见寄存器：

| 架构 | PC | SP | 返回值 |
|---|---|---|---|
| x86_64 | `rip` | `rsp` | `rax` |
| ARM64 | `pc` | `sp` | `x0` |

面试回答：

> 如果源码级信息不够，比如程序崩在动态库、野指针或栈破坏场景，我会看寄存器、当前 PC 附近的汇编，以及栈上的内存内容。

---

## 10. 如何使用 watchpoint？

watchpoint 用来观察某个变量或内存地址什么时候被修改。

```gdb
watch var
watch *ptr
rwatch var
awatch var
info watchpoints
```

区别：

| 命令 | 含义 |
|---|---|
| `watch` | 写时停住 |
| `rwatch` | 读时停住 |
| `awatch` | 读或写都停住 |

典型场景：

1. 变量被莫名其妙改掉
2. 内存被踩
3. 对象状态在某个地方变坏
4. 查找谁修改了某个指针

---

## 11. 如何调试 core dump？

打开 core：

```bash
ulimit -c unlimited
```

运行程序产生 core 后：

```bash
gdb ./app core
```

进入 GDB 后：

```gdb
bt
bt full
info threads
thread apply all bt
frame 0
info locals
info args
```

排查思路：

```text
先看崩溃信号
  -> 看崩溃线程
  -> 看调用栈
  -> 看崩溃位置
  -> 看参数和局部变量
  -> 判断是空指针、野指针、越界、重复释放还是栈破坏
```

面试回答：

> core dump 是程序崩溃时的现场快照。分析 core 时，我会用对应版本的可执行文件和 core 文件打开，先 `bt` 看崩溃栈，再 `thread apply all bt` 看所有线程，定位崩溃线程和调用路径，然后查看局部变量、参数和内存内容。

---

## 12. 如何调试多线程程序？

常用命令：

```gdb
info threads
thread 2
bt
thread apply all bt
set scheduler-locking on
set scheduler-locking off
```

含义：

1. `info threads`：查看所有线程
2. `thread n`：切换到第 n 个线程
3. `thread apply all bt`：打印所有线程调用栈
4. `scheduler-locking on`：单步时只让当前线程运行

常见排查：

1. 死锁：所有线程停在哪些锁上
2. 卡死：主线程是否阻塞在 IO、锁、条件变量
3. 崩溃：哪个线程触发 SIGSEGV
4. 线程池：工作线程是否都阻塞在队列等待

面试回答：

> 多线程问题我会先 `info threads` 看线程列表，再用 `thread apply all bt` 打印所有线程栈。如果怀疑死锁，就看多个线程是否互相卡在 mutex 或 condition_variable 上。如果单步调试时不想其他线程干扰，可以打开 `set scheduler-locking on`。

---

## 13. 如何调试动态库问题？

常用命令：

```gdb
info sharedlibrary
set solib-search-path ./lib
break shared_func
start
info files
info proc mappings
```

排查点：

1. 动态库是否加载
2. 符号是否存在
3. 调试符号是否匹配
4. 运行时加载的库是不是预期版本
5. `LD_LIBRARY_PATH` 是否正确

如果要看程序映射：

```gdb
info proc mappings
```

---

## 14. 如何调试段错误？

常见流程：

```gdb
run
bt
frame 0
info args
info locals
p ptr
x/16gx ptr
```

常见原因：

1. 空指针
2. 野指针
3. 数组越界
4. use-after-free
5. double free
6. 栈溢出
7. 函数指针或虚表被破坏

面试回答：

> 调试段错误时，我会先看崩溃位置和调用栈，再看当前函数参数和局部变量。如果是指针问题，就打印指针值并查看对应内存。如果栈不完整，可能是栈破坏、越界写或优化影响，需要结合反汇编和内存检查继续分析。

---

## 15. 如何调试程序启动阶段？

如果想从第一条指令开始看：

```gdb
starti
info files
x/10i $pc
b main
continue
```

常用于理解：

1. `_start`
2. libc 启动流程
3. main 之前发生了什么
4. 动态链接器如何加载
5. PLT/GOT 懒绑定

动态链接相关命令：

```gdb
info files
maintenance info sections
info proc mappings
```

---

## 16. GDB 常见命令速查

| 目的 | 命令 |
|---|---|
| 启动程序 | `run` |
| 设置断点 | `b main` |
| 继续运行 | `c` |
| 单步不进函数 | `n` |
| 单步进函数 | `s` |
| 函数运行到返回 | `finish` |
| 查看栈 | `bt` |
| 查看变量 | `p var` |
| 查看局部变量 | `info locals` |
| 查看参数 | `info args` |
| 查看线程 | `info threads` |
| 切换线程 | `thread n` |
| 查看内存 | `x/16gx addr` |
| 查看寄存器 | `info registers` |
| 查看汇编 | `disassemble /m func` |
| 查看动态库 | `info sharedlibrary` |
| 查看进程映射 | `info proc mappings` |

---

## 17. 常见错误回答

1. 只会说 `gdb ./app`，不会分析流程
2. 不知道编译时要加 `-g`
3. 以为不加 `-g` 就完全不能调试
4. 分不清 `-g`、符号表、strip、`-O0` 的区别
5. 不会看调用栈
6. 不知道 core dump 怎么调
7. 多线程问题不会看所有线程栈
8. 不知道 watchpoint 用来查内存被谁修改
9. 遇到 `<optimized out>` 不知道和优化有关
10. 不知道线上符号文件要和二进制匹配

---

## 18. 面试回答模板

可以这样回答：

> 我平时使用 GDB 主要按问题类型来定位。开发调试时会用 `-g -O0` 编译，这样 GDB 能看到源码行号、变量名、类型和调用栈；不加 `-g` 也可以调试，但更多是基于地址、寄存器和反汇编。普通逻辑问题会用 `break`、`next`、`step`、`print` 单步看变量变化；崩溃问题会先看 core dump，用 `bt` 和 `bt full` 定位调用栈，再看参数、局部变量和内存；多线程问题会用 `info threads` 和 `thread apply all bt` 看所有线程卡在哪里；如果怀疑变量被意外修改，会用 `watch` 观察写入点。GDB 的核心不是背命令，而是保留现场、定位路径、验证假设。

---

## 19. 最终背诵版

GDB 的本质是：

```text
在程序运行或崩溃现场中，
通过断点、单步、栈、变量、内存、寄存器和线程信息，
还原程序执行路径并定位错误原因。
```

面试中一定要补一句：

```text
调试前要保证二进制和调试符号匹配；
崩溃先看调用栈，多线程先看所有线程栈，内存异常可以用 watchpoint 和 x 命令继续追。
```

关于 `-g` 要记住：

```text
-g 不是让程序能运行，而是让 GDB 能看懂源码、变量、类型和行号；
不加 -g 仍能做汇编级调试，但源码级调试能力会明显变弱。
```
