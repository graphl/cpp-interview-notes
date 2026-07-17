# C++ 面试题：/sys 文件系统如何排查设备和驱动问题

## 1. 面试主要考什么？

`/sys` 是 sysfs，主要展示 Linux 内核设备模型。

面试官想听到：

1. `/sys` 和 `/proc` 的区别
2. `/sys/bus`、`/sys/class`、`/sys/devices` 分别看什么
3. 如何判断设备是否创建
4. 如何判断设备是否绑定驱动
5. 如何查看模块参数
6. 如何排查驱动没有 probe
7. 如何查看网络、块设备、tty、GPIO 等设备状态

核心一句话：

> `/sys` 主要用于观察和配置内核对象，尤其是设备、驱动、总线、class、模块参数和电源管理信息。

---

## 2. /sys 是什么？

`/sys` 是 sysfs，按照内核对象关系组织。

可以这样理解：

```text
/sys
  -> 设备模型
  -> 总线
  -> 驱动
  -> 设备类别
  -> 模块参数
  -> 电源管理
```

和 `/proc` 的区别：

| 路径 | 重点 |
|---|---|
| `/proc` | 进程状态、系统运行统计 |
| `/sys` | 设备模型、驱动、总线、内核对象 |

---

## 3. /sys 常用入口

```bash
ls /sys/bus
ls /sys/class
ls /sys/devices
ls /sys/module
ls /sys/kernel
```

含义：

| 路径 | 作用 |
|---|---|
| `/sys/bus` | 按总线查看设备和驱动 |
| `/sys/class` | 按设备类别查看 |
| `/sys/devices` | 按真实设备层级查看 |
| `/sys/module` | 查看已加载模块和模块参数 |
| `/sys/kernel` | 查看内核功能，如 debug、tracing |

---

## 4. /sys/bus：按总线看设备和驱动

常见命令：

```bash
ls /sys/bus/platform/devices
ls /sys/bus/platform/drivers

ls /sys/bus/i2c/devices
ls /sys/bus/i2c/drivers

ls /sys/bus/spi/devices
ls /sys/bus/spi/drivers

ls /sys/bus/usb/devices
ls /sys/bus/pci/devices
```

排查流程：

```text
设备不工作
  -> 先看 /sys/bus/<bus>/devices 里有没有设备
  -> 再看 /sys/bus/<bus>/drivers 里有没有驱动
  -> 再看设备有没有绑定 driver
  -> 再看 dmesg 中 probe 是否失败
```

---

## 5. 判断设备是否绑定驱动

查看设备是否有 driver 链接：

```bash
readlink /sys/bus/platform/devices/<dev>/driver
```

如果没有 `driver` 链接，说明设备没有绑定驱动。

也可以看驱动目录：

```bash
ls /sys/bus/platform/drivers/<driver>
```

一般能看到绑定到该驱动的设备名。

面试回答：

> 如果设备没有进入 probe，我会先看 `/sys/bus/<bus>/devices` 下设备是否存在，再看 `/sys/bus/<bus>/drivers` 下驱动是否存在。设备目录下如果没有 `driver` 符号链接，说明设备没有成功绑定驱动，下一步查 compatible、id_table、内核配置和 dmesg。

---

## 6. bind 和 unbind

手动解绑：

```bash
echo <dev> > /sys/bus/platform/drivers/<driver>/unbind
```

手动绑定：

```bash
echo <dev> > /sys/bus/platform/drivers/<driver>/bind
```

用途：

1. 重新触发 probe
2. 验证 remove 路径
3. 临时切换驱动绑定
4. 调试驱动资源释放

注意：

```text
bind/unbind 会影响真实设备运行；
生产环境和关键设备上要谨慎。
```

---

## 7. /sys/class：按类别看设备

常见入口：

```bash
ls /sys/class/net
ls /sys/class/block
ls /sys/class/tty
ls /sys/class/gpio
ls /sys/class/input
ls /sys/class/leds
ls /sys/class/pwm
```

特点：

```text
/sys/class 更适合从用户使用视角查设备；
/sys/devices 更适合从硬件层级查设备。
```

---

## 8. 查看网络设备

```bash
ls /sys/class/net
cat /sys/class/net/eth0/operstate
cat /sys/class/net/eth0/carrier
cat /sys/class/net/eth0/address
cat /sys/class/net/eth0/statistics/rx_packets
cat /sys/class/net/eth0/statistics/tx_packets
cat /sys/class/net/eth0/statistics/rx_errors
cat /sys/class/net/eth0/statistics/tx_errors
```

判断：

1. `operstate` 是否 up
2. `carrier` 是否为 1
3. rx/tx 包是否增长
4. error/drop 是否增长

---

## 9. 查看块设备

```bash
ls /sys/class/block
cat /sys/class/block/mmcblk0/size
cat /sys/class/block/mmcblk0/queue/scheduler
cat /sys/class/block/mmcblk0/stat
```

用途：

1. 查看磁盘、eMMC、SD 卡是否识别
2. 查看队列调度器
3. 查看块设备统计
4. 排查 IO 错误和性能问题

通常还要结合：

```bash
dmesg | grep -i mmc
dmesg | grep -i "I/O error"
```

---

## 10. 查看 tty/串口设备

```bash
ls /sys/class/tty
dmesg | grep -i tty
```

常见问题：

1. 串口设备节点没有出现
2. 设备树 status 没打开
3. pinctrl 配置错
4. 波特率配置错
5. console 参数写错

相关启动参数：

```text
console=ttyS0,115200
```

---

## 11. 查看模块和模块参数

```bash
ls /sys/module
ls /sys/module/<module>/parameters
cat /sys/module/<module>/parameters/<param>
```

用途：

1. 判断模块是否加载
2. 查看模块参数是否生效
3. 调整驱动调试开关
4. 确认运行时配置

也可以配合：

```bash
lsmod
modinfo <module>
```

---

## 12. /sys/kernel

常见入口：

```bash
ls /sys/kernel
ls /sys/kernel/debug
ls /sys/kernel/tracing
```

说明：

1. `/sys/kernel/debug` 通常需要挂载 debugfs
2. `/sys/kernel/tracing` 用于 ftrace
3. 这些工具比普通 sysfs 更偏深入内核调试

挂载 debugfs：

```bash
mount -t debugfs none /sys/kernel/debug
```

---

## 13. 设备没有 probe 怎么查？

流程：

```text
1. dmesg 看是否有 probe failed
2. /sys/bus/<bus>/devices 看设备是否创建
3. /sys/bus/<bus>/drivers 看驱动是否注册
4. 设备目录下看是否有 driver 链接
5. 检查设备树 compatible/status/reg/interrupts
6. 检查内核配置是否编进内核或模块是否加载
```

常用命令：

```bash
dmesg | grep -i probe
ls /sys/bus/platform/devices
ls /sys/bus/platform/drivers
readlink /sys/bus/platform/devices/<dev>/driver
```

---

## 14. 常见错误回答

1. 把 `/sys` 当成普通磁盘目录
2. 不知道 `/sys/bus` 能看设备和驱动绑定
3. 不知道设备目录下的 `driver` 链接代表绑定关系
4. 驱动没 probe 只看代码，不看 sysfs 和 dmesg
5. 不知道 `/sys/class/net` 可以看网卡状态和统计
6. 随便写 bind/unbind，没意识到会影响设备

---

## 15. 面试回答模板

可以这样回答：

> `/sys` 是 Linux 的 sysfs，主要展示内核设备模型。我一般用 `/sys/bus` 看总线下的 devices 和 drivers，用 `/sys/class` 从设备类别角度看 net、block、tty 等设备，用 `/sys/devices` 看真实设备层级。如果设备驱动没有 probe，我会先看设备是否出现在 `/sys/bus/<bus>/devices`，驱动是否出现在 `/sys/bus/<bus>/drivers`，设备目录下有没有 `driver` 链接。再结合 dmesg 检查 probe 失败原因、设备树 compatible、status、clock、reset、pinctrl 等配置。

---

## 16. 最终背诵版

`/sys` 的本质是：

```text
看内核设备模型和驱动绑定关系。
```

重点记：

```text
/sys/bus       总线、设备、驱动
/sys/class     按类别看设备
/sys/devices   真实设备层级
/sys/module    模块和模块参数
/sys/kernel    内核调试和 tracing 入口
```
