# 嵌入式 Linux 面试题：I2C、SPI、UART 的区别

## 1. 面试主要考什么？

这道题考的是常见低速外设总线的通信方式、线数、速率、寻址和 Linux 驱动模型。

面试官想听到：

1. I2C 两线、多从机、地址寻址
2. SPI 四线、片选、全双工、速度高
3. UART 异步串口、点对点、波特率
4. Linux 中对应的 adapter、client、master、slave、tty
5. 调试工具

---

## 2. 对比

| 总线 | 线数 | 通信方式 | 寻址方式 | 特点 |
|---|---:|---|---|---|
| I2C | SCL、SDA | 半双工 | 设备地址 | 省线，适合传感器、EEPROM |
| SPI | SCLK、MOSI、MISO、CS | 全双工 | 片选 | 速度快，适合 Flash、屏幕 |
| UART | TX、RX | 全双工异步 | 无总线地址 | 简单，常用于调试串口 |

---

## 3. 数据流

I2C：

```text
应用程序
  -> i2c-dev
  -> i2c_adapter
  -> I2C 控制器
  -> SCL/SDA
  -> I2C slave
```

SPI：

```text
应用程序或内核驱动
  -> spi_device
  -> spi_master
  -> SPI 控制器
  -> SCLK/MOSI/MISO/CS
  -> SPI slave
```

UART：

```text
应用程序
  -> tty
  -> uart driver
  -> UART 控制器
  -> TX/RX
  -> 对端设备
```

---

## 4. Linux 里怎么看？

```text
ls /dev/i2c-*
i2cdetect -y 0
i2cget -y 0 0x50 0x00
ls /dev/spidev*
ls /dev/ttyS* /dev/ttyUSB*
stty -F /dev/ttyS0
```

设备树中常见字段：

```text
I2C: reg = <0x50>
SPI: reg = <0>          // 片选号
UART: current-speed = <115200>
```

---

## 5. 常见追问

### I2C 为什么需要上拉电阻？

I2C 常见是开漏输出，设备只能主动拉低，释放后靠上拉电阻拉高。

### SPI 为什么速度比 I2C 高？

SPI 线更多，没有复杂地址仲裁，通常由主机通过片选直接选择设备，可以全双工传输。

### UART 为什么要配置波特率？

UART 没有时钟线，收发双方必须约定波特率、数据位、停止位和校验位。

---

## 6. 常见坑

1. I2C 地址 7 位和 8 位混淆
2. I2C 上拉电阻不合适
3. SPI mode 0/1/2/3 配错
4. SPI 片选极性配错
5. UART 波特率或流控配置错
6. pinctrl 没配置，外设引脚没复用出来

---

## 7. 面试回答

I2C 是两线总线，通过设备地址区分从设备，省引脚，适合传感器、EEPROM 这类低速设备。SPI 通常是四线，通过片选选择设备，支持全双工，速度更高，常用于 Flash、屏幕、ADC。UART 是异步串口，没有时钟线，双方通过波特率和帧格式约定通信，常用于调试和模块通信。在 Linux 中，I2C 重点看 adapter 和 client，SPI 重点看 master 和 device，UART 通常走 tty 子系统。
