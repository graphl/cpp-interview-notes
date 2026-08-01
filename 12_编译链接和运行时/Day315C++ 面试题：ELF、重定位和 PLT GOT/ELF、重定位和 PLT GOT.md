# C++ 面试题：ELF、重定位和 PLT/GOT

## 1. 这个机制解决什么问题

编译一个源文件时，编译器不知道外部函数最终会被加载到哪个虚拟地址。目标文件先保存符号和重定位需求，链接器及动态加载器再把“对某个符号的引用”绑定到实际地址。

## 2. section 和 segment 不要混淆

```text
section：链接视角，组织代码、数据、符号和重定位信息
segment：装载视角，告诉内核哪些文件范围映射到进程地址空间，以及权限是什么
```

多个 section 可以被装入同一个 `PT_LOAD` segment。运行程序时内核主要读取 program headers，而不是按 section 逐个映射。

常见内容：

| 名称 | 作用 |
|---|---|
| `.text` | 机器指令 |
| `.rodata` | 只读常量 |
| `.data/.bss` | 已初始化/零初始化全局数据 |
| `.dynsym/.dynstr` | 动态符号及字符串 |
| `.rela.dyn/.rela.plt` | 动态重定位记录 |
| `.plt` | 外部函数调用跳板 |
| `.got/.got.plt` | 运行时地址槽位 |
| `.dynamic` | 依赖库、重定位表位置等动态标签 |

## 3. 进程启动时的数据流

```text
execve
  -> 内核读取 ELF header 和 program headers
  -> 映射主程序的 PT_LOAD segments
  -> 把控制权交给 ELF interpreter（通常是 ld.so）
  -> ld.so 建立已加载对象链表
  -> 装载依赖库
  -> 处理必要重定位和符号查找
  -> 执行初始化函数
  -> 进入程序启动代码，最终调用 main
```

实际解释器路径可通过 `readelf -l` 的 `INTERP` 项确认。

## 4. 一次延迟绑定调用

以常见 x86-64 ELF 的经典 lazy binding 模型为例：

```text
call puts@plt
  -> .plt 跳板间接读取 puts 对应 GOT 槽
  -> 第一次调用时槽位仍指向解析路径
  -> 进入 ld.so resolver
  -> 根据重定位项和 link_map 查找 puts
  -> 把 libc 中 puts 的地址写回 GOT 槽
  -> 跳转到真实 puts

后续调用
  -> puts@plt
  -> GOT 已保存真实地址
  -> 直接跳到 libc puts
```

是否启用 lazy binding、PLT 的具体指令形态、`.rela.plt` 名称以及 GOT 是否可写，受架构、链接选项、PIE 和 RELRO 影响。`-Wl,-z,now` 通常要求启动阶段完成相关绑定；full RELRO 会进一步收紧 GOT 写权限。

## 5. 验证命令

```bash
readelf -hW ./app                  # ELF 类型、架构、入口
readelf -lW ./app                  # program headers、INTERP、segments
readelf -SW ./app                  # sections
readelf -dW ./app                  # NEEDED、PLTGOT、BIND_NOW 等动态标签
readelf -rW ./app                  # 重定位项
objdump -d -M intel -j .plt ./app  # PLT 反汇编，section 名依平台而异
objdump -R ./app                   # 动态重定位概览
```

运行时还可以查看：

```bash
cat /proc/$PID/maps
LD_DEBUG=libs,bindings ./app
```

`LD_DEBUG` 输出较多，适合最小实验，不建议直接用于高负载生产进程。

## 6. 面试口述版

ELF section 服务于链接，segment 服务于装载。外部符号地址未知时，目标文件记录重定位项；动态加载器装载依赖库后根据符号表完成地址绑定。经典 lazy binding 中，第一次函数调用经过 PLT、GOT 和 ld.so 解析器，解析结果写回 GOT，后续调用便可直接跳到真实函数。具体布局必须结合架构、PIE、RELRO 和绑定选项验证。
