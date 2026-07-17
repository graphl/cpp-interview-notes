# C++ 面试题：iostat 和 sar 怎么分析 IO 和历史性能

## 1. 这道题考什么？

`iostat` 主要看磁盘 IO。
`sar` 可以看历史 CPU、内存、IO、网络等系统性能数据。

---

## 2. iostat 怎么用？

常用命令：

```bash
iostat -xz 1
```

重点字段：

| 字段 | 含义 |
|---|---|
| `r/s`、`w/s` | 每秒读写次数 |
| `rkB/s`、`wkB/s` | 每秒读写带宽 |
| `await` | IO 平均等待时间 |
| `r_await`、`w_await` | 读/写等待时间 |
| `%util` | 设备忙碌比例 |

判断：

| 现象 | 可能原因 |
|---|---|
| `%util` 接近 100% | 设备接近满负载 |
| `await` 高 | IO 延迟高 |
| `r/s/w/s` 高但带宽低 | 小 IO 很多 |
| 带宽高但 await 低 | 大顺序 IO，可能正常 |

---

## 3. sar 怎么用？

CPU：

```bash
sar -u 1
```

内存：

```bash
sar -r 1
```

IO：

```bash
sar -d 1
```

网络：

```bash
sar -n DEV 1
sar -n TCP,ETCP 1
```

历史数据：

```bash
sar -u -f /var/log/sa/saXX
```

---

## 4. 常见 IO 问题

1. 日志同步刷盘太频繁
2. 小随机 IO 太多
3. 数据库或日志和业务共用磁盘
4. page cache 回写导致抖动
5. 存储设备本身到达上限
6. 文件系统或块层异常

---

## 5. 面试回答模板

> 分析 IO 性能时，我会用 `iostat -xz 1` 看设备层指标，重点看 `%util`、`await`、读写 IOPS 和带宽。如果 `%util` 接近 100% 且 await 高，说明设备可能已经成为瓶颈；如果 IOPS 高但带宽低，可能是小随机 IO 多。`sar` 更适合看历史趋势，比如 CPU、IO、网络在问题发生时是否异常。确认 IO 瓶颈后，再结合应用日志、pidstat -d、文件系统和业务访问模式分析。

