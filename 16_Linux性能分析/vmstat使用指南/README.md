# vmstat 使用指南

本专题用于学习 `vmstat` 的字段含义、异常组合，以及裁剪版或嵌入式设备没有 `vmstat` 时的替代排查方法。

## 文档导航

1. [vmstat 使用指南](01_vmstat使用指南.md)
   - 常用命令与第一行陷阱；
   - CPU、内存、Swap、I/O、调度字段；
   - 常见异常组合与后续定位工具。

2. [设备中不存在 vmstat 时如何查看这些信息](02_设备中不存在vmstat时如何查看这些信息.md)
   - 检查 BusyBox 是否内置 `vmstat`；
   - 使用 `/proc` 获取同类内核计数；
   - 将 `vmstat` 字段映射到 `/proc/stat`、`/proc/meminfo`、`/proc/vmstat` 和 `/proc/diskstats`；
   - 在最小化系统中进行连续采样；
   - 安装或编译 `vmstat` 的方法。

## 推荐顺序

```text
先掌握 vmstat 输出
        ↓
理解每个字段来自哪类内核计数
        ↓
设备没有 vmstat 时直接读取 /proc
        ↓
根据异常方向切换到专用工具
```
