# 06 mmap 或第三方库泄漏

## 1. 类型定义

有些内存不来自普通 heap，而是来自 `mmap`、共享内存、图像库、音视频库、数据库客户端库、GPU/驱动接口或第三方 C 库。

这类问题可能表现为 RSS 上涨，但 heap 不明显增长。

---

## 2. 典型现象

```text
VmRSS 持续上涨
[heap] 增长不明显
smaps 中某些 mmap 区域增长
业务使用图像、音视频、数据库、共享内存等外部库
Valgrind 不一定能完整定位
```

---

## 3. 典型代码

`mmap` 泄漏：

```cpp
void func(int fd) {
    void* p = mmap(nullptr, 4096, PROT_READ, MAP_PRIVATE, fd, 0);
    if (p == MAP_FAILED) {
        return;
    }

    // 忘记 munmap(p, 4096)
}
```

第三方库对象未释放：

```cpp
Image* img = image_load("a.jpg");
// 忘记 image_free(img)
```

---

## 4. 排查方法

查看内存映射：

```bash
pmap -x <pid>
cat /proc/<pid>/maps
cat /proc/<pid>/smaps
```

重点看：

```text
Anonymous
File-backed mapping
Shared memory
Private_Dirty
Rss
```

跟踪 mmap/munmap：

```bash
strace -f -e trace=mmap,munmap,mremap ./app
```

如果是第三方库：

1. 查库文档里的释放函数
2. 检查 init/destroy 是否成对
3. 检查 create/free 是否成对
4. 检查引用计数 API 是否 release
5. 看库是否有自己的 debug allocator 或 memory stats

---

## 5. 修复方式

`mmap` 用 RAII 封装：

```cpp
class MmapRegion {
public:
    MmapRegion(void* addr, size_t len) : addr_(addr), len_(len) {}
    ~MmapRegion() {
        if (addr_ != MAP_FAILED && addr_ != nullptr) {
            munmap(addr_, len_);
        }
    }

    MmapRegion(const MmapRegion&) = delete;
    MmapRegion& operator=(const MmapRegion&) = delete;

private:
    void* addr_;
    size_t len_;
};
```

第三方库对象用自定义 deleter：

```cpp
using ImagePtr = std::unique_ptr<Image, decltype(&image_free)>;

ImagePtr img(image_load("a.jpg"), image_free);
```

---

## 6. 面试总结

如果 RSS 上涨但 heap 不明显，要考虑 mmap、共享内存或第三方库泄漏。排查时重点看 `/proc/<pid>/smaps` 和 `pmap`，修复时用 RAII 或 `unique_ptr` 自定义 deleter 管理外部资源。
