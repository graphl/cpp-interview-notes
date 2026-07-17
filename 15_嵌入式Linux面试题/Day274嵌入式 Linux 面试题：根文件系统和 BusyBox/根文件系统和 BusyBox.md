# 嵌入式 Linux 面试题：根文件系统和 BusyBox

## 1. 面试主要考什么？

根文件系统 rootfs 是用户空间运行的基础。
内核起来以后，如果没有 rootfs，就无法启动用户程序。

面试官想听到：

1. rootfs 里有什么
2. `/sbin/init` 的作用
3. BusyBox 是什么
4. initramfs 和真实 rootfs
5. 动态库和解释器
6. VFS 挂载失败怎么排查

---

## 2. 数据流

```text
Kernel
  -> 挂载 rootfs
  -> 查找 /sbin/init
  -> 启动 init
  -> 执行启动脚本
  -> 挂载 proc/sys/dev
  -> 启动应用程序
```

---

## 3. rootfs 常见目录

```text
/bin
/sbin
/etc
/lib
/dev
/proc
/sys
/tmp
/usr
/mnt
```

最小 rootfs 至少要有：

1. init 程序
2. 基本 shell
3. 必要动态库或静态链接程序
4. 设备节点
5. `/etc/inittab` 或启动脚本

---

## 4. BusyBox 是什么？

BusyBox 把很多常见 Linux 命令集合到一个可执行文件里。

例如：

```text
ls -> busybox
cp -> busybox
sh -> busybox
mount -> busybox
ifconfig -> busybox
```

嵌入式系统空间有限，所以常用 BusyBox 构建最小用户空间。

---

## 5. 常见启动参数

```text
root=/dev/mmcblk0p2 rootfstype=ext4 rw
root=/dev/nfs nfsroot=192.168.1.10:/nfs/rootfs ip=dhcp
console=ttyS0,115200
init=/linuxrc
```

---

## 6. 调试方法

如果 panic：

```text
Kernel panic - not syncing: VFS: Unable to mount root fs
```

排查：

```text
cat /proc/cmdline
ls -l /sbin/init
ls -l /lib/ld-linux*
ldd ./app
mount -t proc proc /proc
mount -t sysfs sysfs /sys
```

---

## 7. 常见坑

1. `root=` 设备写错
2. 内核没打开对应文件系统支持
3. rootfs 缺少 `/sbin/init`
4. init 没有执行权限
5. 动态链接器缺失
6. `/dev/console` 不存在
7. proc、sysfs、devtmpfs 没挂载

---

## 8. 面试回答

rootfs 是 Linux 用户空间的基础，里面包含可执行程序、动态库、配置文件和设备节点。内核启动后会根据 `bootargs` 挂载 rootfs，然后启动 `/sbin/init` 或指定的 init 程序。BusyBox 是嵌入式 Linux 常用的用户空间工具集合，它把很多命令集成在一个二进制里，适合构建小型 rootfs。如果系统启动失败，我会先检查 `root=` 参数、文件系统类型、内核配置、`/sbin/init`、动态库和 `/dev/console`。
