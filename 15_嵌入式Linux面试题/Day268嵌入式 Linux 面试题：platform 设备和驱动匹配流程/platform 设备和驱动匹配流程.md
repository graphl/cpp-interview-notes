# 嵌入式 Linux 面试题：platform 设备和驱动匹配流程

## 1. 面试主要考什么？

platform 总线用于管理 SoC 内部那些不能被自动枚举发现的设备。

面试官想听到：

1. 为什么需要 platform 总线
2. platform_device 和 platform_driver
3. 设备树如何生成 platform_device
4. `compatible` 如何匹配
5. `probe` 和 `remove` 做什么
6. 资源如何获取和释放

---

## 2. 数据流

```text
设备树节点
  -> of_platform_populate()
  -> platform_device
  -> platform_bus_type
  -> platform_driver
  -> of_match_table 匹配
  -> probe()
```

---

## 3. 驱动骨架

```cpp
static const struct of_device_id demo_of_match[] = {
    { .compatible = "vendor,demo" },
    { }
};
MODULE_DEVICE_TABLE(of, demo_of_match);

static int demo_probe(struct platform_device* pdev) {
    struct resource* res;
    void __iomem* base;
    int irq;

    res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
    base = devm_ioremap_resource(&pdev->dev, res);
    if (IS_ERR(base)) {
        return PTR_ERR(base);
    }

    irq = platform_get_irq(pdev, 0);
    if (irq < 0) {
        return irq;
    }

    return 0;
}

static int demo_remove(struct platform_device* pdev) {
    return 0;
}

static struct platform_driver demo_driver = {
    .probe = demo_probe,
    .remove = demo_remove,
    .driver = {
        .name = "demo",
        .of_match_table = demo_of_match,
    },
};

module_platform_driver(demo_driver);
```

---

## 4. 控制流

```text
module_platform_driver()
  -> platform_driver_register()
  -> driver_register()
  -> bus_add_driver()
  -> driver_attach()
  -> bus_for_each_dev()
  -> platform_match()
  -> really_probe()
  -> demo_probe()
```

---

## 5. probe 里通常做什么？

1. 获取寄存器资源
2. `ioremap` 映射寄存器
3. 获取 IRQ
4. 获取 clock、reset、regulator、GPIO
5. 初始化硬件
6. 注册字符设备、input 设备、netdev 或其他子系统设备
7. 保存私有数据 `platform_set_drvdata`

---

## 6. 调试方法

命令：

```text
ls /sys/bus/platform/devices
ls /sys/bus/platform/drivers
dmesg | grep -i probe
dmesg | grep -i "vendor,demo"
cat /sys/bus/platform/devices/xxx/uevent
```

如果驱动没进 `probe`，优先查：

1. 设备树节点是否存在
2. `status` 是否为 `okay`
3. `compatible` 是否完全一致
4. 驱动是否成功加载
5. 内核配置是否打开

---

## 7. 常见坑

1. `compatible` 拼错
2. 忘记 `MODULE_DEVICE_TABLE`
3. `probe` 里资源申请失败但没打印错误
4. `remove` 里释放顺序不对
5. 没用 `devm_`，错误路径资源泄漏
6. pinctrl、clock、reset 没处理，导致访问寄存器无效

---

## 8. 面试回答

platform 总线主要用于 SoC 内部无法自动枚举的设备。设备树描述硬件节点，内核解析后创建 `platform_device`，驱动通过 `platform_driver` 注册到 platform 总线。匹配时主要看设备树节点的 `compatible` 和驱动的 `of_match_table` 是否一致，匹配成功后调用 `probe`。`probe` 里一般获取寄存器、中断、时钟、GPIO 等资源，完成硬件初始化并注册到对应内核子系统。调试时重点看 `/sys/bus/platform`、设备树节点和 `dmesg` 的 probe 日志。
