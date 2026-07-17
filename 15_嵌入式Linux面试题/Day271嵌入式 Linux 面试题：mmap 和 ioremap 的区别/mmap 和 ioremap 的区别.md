# 嵌入式 Linux 面试题：mmap 和 ioremap 的区别

## 1. 面试主要考什么？

`ioremap` 和 `mmap` 都和地址映射有关，但发生的位置和目的不同。

面试官想听到：

1. 物理地址、内核虚拟地址、用户虚拟地址
2. `ioremap` 用于内核访问 MMIO 寄存器
3. `mmap` 用于把内核对象或设备内存映射到用户态
4. `remap_pfn_range`
5. cache 属性和内存屏障

---

## 2. 地址关系

```text
外设寄存器物理地址
  -> ioremap()
  -> 内核虚拟地址
  -> readl()/writel()
```

```text
设备内存或 DMA buffer
  -> 驱动 mmap()
  -> remap_pfn_range()
  -> 用户进程虚拟地址
  -> 用户态直接访问
```

---

## 3. ioremap 是什么？

`ioremap` 把外设寄存器的物理地址映射成内核可以访问的虚拟地址。

典型流程：

```cpp
res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
base = devm_ioremap_resource(&pdev->dev, res);
value = readl(base + REG_STATUS);
writel(value, base + REG_CTRL);
```

注意：访问 MMIO 寄存器推荐使用 `readl/writel`，不要直接解引用普通指针。

---

## 4. mmap 是什么？

`mmap` 是用户态系统调用。
驱动可以实现 `file_operations.mmap`，把设备内存或 DMA buffer 映射到用户空间。

简化逻辑：

```cpp
static int demo_mmap(struct file* file, struct vm_area_struct* vma) {
    unsigned long pfn = phys_addr >> PAGE_SHIFT;
    unsigned long size = vma->vm_end - vma->vm_start;

    return remap_pfn_range(vma, vma->vm_start, pfn, size, vma->vm_page_prot);
}
```

---

## 5. 对比

| 项目 | ioremap | mmap |
|---|---|---|
| 使用者 | 内核驱动 | 用户进程调用，驱动实现 |
| 目的 | 内核访问外设寄存器 | 用户态访问映射内存 |
| 输入 | 物理地址 | 文件描述符和偏移 |
| 输出 | 内核虚拟地址 | 用户虚拟地址 |
| 常见接口 | `ioremap`、`devm_ioremap_resource` | `mmap`、`remap_pfn_range` |

---

## 6. 调试方法

命令：

```text
cat /proc/iomem
cat /proc/<pid>/maps
dmesg | grep -i mmap
devmem 0xaddr
```

---

## 7. 常见坑

1. 把 `ioremap` 和 `mmap` 混为一谈
2. 用普通指针直接访问 MMIO
3. 映射大小不是页对齐
4. cache 属性不对，导致设备和 CPU 看到的数据不一致
5. 用户态映射寄存器时没有权限控制，带来安全风险

---

## 8. 面试回答

`ioremap` 是驱动在内核态使用的接口，用来把外设寄存器物理地址映射成内核虚拟地址，然后通过 `readl/writel` 访问。`mmap` 是用户态系统调用，驱动实现 `mmap` 回调后，可以把设备内存、DMA buffer 或其他内核对象映射到用户进程地址空间。简单说，`ioremap` 解决内核访问硬件的问题，`mmap` 解决用户态直接访问某段映射内存的问题。
