# C++ 面试题：/dev 目录和设备节点如何排查问题

## 1. 面试主要考什么？

`/dev` 是用户态访问设备的入口。

面试官想听到：

1. `/dev` 下面是什么
2. 字符设备和块设备节点怎么看
3. 主设备号和次设备号是什么
4. `/dev`、`/sys`、驱动之间是什么关系
5. 设备节点不存在怎么排查
6. 权限不够、open 失败、设备忙怎么排查
7. `mknod`、udev、devtmpfs 的关系

核心一句话：

> `/dev` 存放设备节点，用户程序通过 open/read/write/ioctl/mmap 访问这些节点，最终进入内核对应设备驱动。

---

## 2. /dev 是什么？

`/dev` 里不是普通业务文件，而是设备节点。

常见类型：

```text
字符设备：tty、串口、gpiochip、i2c、input、video
块设备：磁盘、分区、eMMC、SD 卡
伪设备：null、zero、random、urandom
```

查看：

```bash
ls -l /dev
```

示例：

```text
crw-rw---- 1 root dialout 4, 64 ttyS0
brw-rw---- 1 root disk   179, 0 mmcblk0
```

开头字符含义：

```text
c  字符设备
b  块设备
-  普通文件
d  目录
```

---

## 3. 主设备号和次设备号

示例：

```text
crw-rw---- 1 root dialout 4, 64 ttyS0
```

其中：

```text
4   主设备号 major
64  次设备号 minor
```

含义：

1. 主设备号通常表示一类驱动
2. 次设备号通常表示这个驱动管理的某个具体设备
3. 内核通过设备号找到对应的 file_operations

查看主设备号：

```bash
cat /proc/devices
```

---

## 4. /dev、/sys、驱动的关系

可以这样理解：

```text
驱动注册设备
  -> 内核设备模型生成 /sys 信息
  -> devtmpfs/udev 创建设备节点 /dev/xxx
  -> 用户程序 open("/dev/xxx")
  -> VFS
  -> 驱动 file_operations
```

关系：

```text
/sys
  -> 说明设备在内核里是否存在、是否绑定驱动

/dev
  -> 用户态实际打开的设备入口
```

所以：

```text
/sys 有设备，不一定 /dev 一定有节点；
/dev 有节点，也不代表设备一定正常工作。
```

---

## 5. 用户程序如何访问 /dev？

典型调用链：

```text
open("/dev/demo")
  -> VFS
  -> demo_open()

read(fd)
  -> VFS
  -> demo_read()

write(fd)
  -> VFS
  -> demo_write()

ioctl(fd)
  -> VFS
  -> demo_ioctl()
```

驱动里对应：

```cpp
static const struct file_operations fops = {
    .owner = THIS_MODULE,
    .open = demo_open,
    .read = demo_read,
    .write = demo_write,
    .unlocked_ioctl = demo_ioctl,
};
```

---

## 6. 设备节点不存在怎么查？

流程：

```text
1. /sys 里设备是否存在
2. 驱动是否 probe 成功
3. 驱动是否调用 device_create
4. devtmpfs 是否挂载
5. udev/mdev 是否运行
6. 是否需要手动 mknod
```

命令：

```bash
ls /sys/class
ls /sys/bus/platform/devices
dmesg | grep -i probe
dmesg | grep -i devtmpfs
mount | grep devtmpfs
cat /proc/devices
```

手动创建设备节点：

```bash
mknod /dev/demo c <major> <minor>
chmod 666 /dev/demo
```

注意：

```text
mknod 只是创建设备节点；
如果内核里没有对应设备号和驱动，打开仍然会失败。
```

---

## 7. open 设备失败怎么查？

常见错误：

```text
No such file or directory
Permission denied
No such device
Device or resource busy
Input/output error
```

排查：

```bash
ls -l /dev/xxx
stat /dev/xxx
cat /proc/devices
dmesg | tail
strace ./app
```

错误含义：

| 错误 | 常见原因 |
|---|---|
| `ENOENT` | 设备节点不存在 |
| `EACCES` | 权限不够 |
| `ENODEV` | 设备号没有对应驱动或设备不存在 |
| `EBUSY` | 设备被占用 |
| `EIO` | 底层硬件或驱动 IO 错误 |

---

## 8. 权限问题怎么查？

查看权限：

```bash
ls -l /dev/ttyS0
id
groups
```

常见解决：

```bash
chmod 666 /dev/ttyS0
chown root:dialout /dev/ttyS0
usermod -aG dialout <user>
```

注意：

```text
chmod 666 适合临时调试；
正式系统应该通过 udev 规则或权限组管理。
```

---

## 9. 常见 /dev 节点

```text
/dev/null       丢弃写入，读取返回 EOF
/dev/zero       读取返回 0
/dev/random     随机数，可能阻塞
/dev/urandom    随机数，通常不阻塞
/dev/tty        当前控制终端
/dev/ttyS0      串口
/dev/i2c-0      I2C adapter
/dev/spidev0.0  SPI 设备
/dev/input/*    输入设备
/dev/video0     V4L2 视频设备
/dev/mmcblk0    eMMC/SD 块设备
```

---

## 10. /dev 和嵌入式调试

嵌入式 Linux 常见问题：

1. 串口没有 `/dev/ttySx`
2. I2C 没有 `/dev/i2c-x`
3. SPI 没有 `/dev/spidevX.Y`
4. 摄像头没有 `/dev/video0`
5. input 没有 `/dev/input/eventX`
6. 块设备没有 `/dev/mmcblk0`

排查顺序：

```text
设备树 status 是否 okay
  -> pinctrl/clock/reset 是否正确
  -> 驱动是否 probe
  -> /sys/class 是否出现设备
  -> /dev 是否出现节点
  -> 用户程序权限是否足够
```

---

## 11. udev、mdev、devtmpfs

概念：

| 机制 | 作用 |
|---|---|
| devtmpfs | 内核自动维护基本 `/dev` 设备节点 |
| udev | 用户态设备管理，处理热插拔、命名、权限 |
| mdev | BusyBox 提供的轻量 udev 替代 |
| mknod | 手动创建设备节点 |

嵌入式系统中常见：

```text
devtmpfs + mdev
```

或：

```text
devtmpfs + udev
```

---

## 12. 常见错误回答

1. 认为 `/dev/xxx` 是普通文件
2. 不知道 `c` 和 `b` 分别表示字符设备、块设备
3. 不知道主设备号和次设备号
4. 设备节点不存在时只会手动 mknod，不查驱动是否注册
5. 不知道 `/dev` 和 `/sys` 的区别
6. 不会用 `strace` 看 open 失败原因
7. 权限问题只会 chmod，不知道用户组和 udev 规则

---

## 13. 面试回答模板

可以这样回答：

> `/dev` 是用户态访问设备的入口，里面主要是字符设备和块设备节点。用户程序对 `/dev/xxx` 调用 `open/read/write/ioctl`，最终会经过 VFS 调到驱动的 `file_operations`。排查设备节点问题时，我会先 `ls -l /dev/xxx` 看节点类型、权限、主次设备号，再看 `/proc/devices` 确认设备号是否注册。如果节点不存在，要继续看 `/sys` 中设备是否创建、驱动是否 probe、devtmpfs 或 udev 是否工作。`mknod` 只能创建设备节点，不能替代真正的驱动注册。

---

## 14. 最终背诵版

`/dev` 的本质是：

```text
用户态访问内核设备驱动的入口。
```

重点记：

```text
ls -l /dev/xxx      看类型、权限、主次设备号
cat /proc/devices   看设备号是否注册
/sys/class          看设备类别是否出现
/sys/bus            看设备是否绑定驱动
strace ./app        看 open/ioctl 失败原因
```
