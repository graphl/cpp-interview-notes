#  缓冲区溢出（Buffer Overflow）

写入超过数组/内存块边界的数据，导致**覆盖其他内存区域**。

```
char buf[5];
strcpy(buf, "123456");  // 溢出，6字节写入5字节空间
```

### 防范建议：

- 使用 `std::array`, `std::vector`, `std::string`
- 使用安全函数，如 `strncpy`, `snprintf`
- 开启编译器防护（如 Stack Protector）