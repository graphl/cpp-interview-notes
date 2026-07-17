# 嵌入式 Linux 面试题：DMA 和 cache 一致性

## 1. 面试主要考什么？

DMA 让外设绕过 CPU 直接访问内存。
难点在于：CPU cache 和内存里的数据可能不一致。

面试官想听到：

1. DMA 数据流
2. cache 一致性问题
3. coherent 和 streaming DMA
4. `dma_alloc_coherent`
5. `dma_map_single`
6. cache clean 和 invalidate
7. 方向参数的重要性

---

## 2. 数据流

外设写内存：

```text
Device
  -> DMA controller
  -> DDR
  -> CPU 读取 buffer
```

CPU 写给外设：

```text
CPU
  -> cache
  -> DDR
  -> DMA controller
  -> Device
```

如果 CPU cache 没有同步，设备和 CPU 可能看到不同的数据。

---

## 3. 两类常见 DMA 内存

### coherent DMA

```cpp
cpu_addr = dma_alloc_coherent(dev, size, &dma_handle, GFP_KERNEL);
```

特点：

1. CPU 和设备看到的数据一致
2. 使用简单
3. 可能性能略低
4. 适合描述符、控制块、小块长期共享内存

### streaming DMA

```cpp
dma_addr = dma_map_single(dev, buf, size, DMA_TO_DEVICE);
dma_unmap_single(dev, dma_addr, size, DMA_TO_DEVICE);
```

特点：

1. 适合临时传输
2. 需要 map/unmap
3. 方向必须写对
4. 性能更灵活

---

## 4. cache 一致性怎么理解？

CPU 写数据给设备前：

```text
CPU cache 里有新数据
DDR 里还是旧数据
Device 从 DDR 读到旧数据
```

所以需要 clean，把 cache 写回内存。

设备写数据给 CPU 前：

```text
Device 已经把新数据写到 DDR
CPU cache 里还有旧数据
CPU 读到旧数据
```

所以需要 invalidate，让 CPU 重新从内存读取。

---

## 5. 调试方法

命令和现象：

```text
dmesg | grep -i dma
cat /proc/iomem
cat /sys/kernel/debug/dma_buf/bufinfo
```

常见现象：

1. DMA 传输偶发错误
2. 小数据正常，大数据异常
3. 加 `printk` 后问题消失
4. cache 关闭后问题消失
5. 方向参数改对后问题消失

---

## 6. 常见坑

1. 忘记 `dma_unmap_single`
2. `DMA_TO_DEVICE` 和 `DMA_FROM_DEVICE` 写反
3. 使用普通 `kmalloc` 内存直接给设备 DMA
4. buffer 没满足设备对齐要求
5. 驱动没设置 DMA mask
6. 在设备还没完成 DMA 时 CPU 提前访问 buffer

---

## 7. 面试回答

DMA 是外设不经过 CPU 直接读写内存的机制，可以减少 CPU 拷贝开销。它的关键问题是 cache 一致性：CPU 可能读写的是 cache，而设备读写的是 DDR。CPU 给设备数据前要保证 cache 写回内存，设备给 CPU 数据后要保证 CPU 不再读旧 cache。Linux 里常用 `dma_alloc_coherent` 分配一致性内存，也可以用 `dma_map_single` 做 streaming DMA。面试时一定要强调 DMA 方向、map/unmap、对齐和 cache 同步。
