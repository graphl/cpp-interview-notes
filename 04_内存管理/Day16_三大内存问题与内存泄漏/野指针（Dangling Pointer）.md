# 野指针（Dangling Pointer）

```
int* p;        // 未初始化 → 野指针
*p = 10;       // 未定义行为，程序可能崩溃

int* q = new int(5);
delete q;
*q = 6;        // 悬空指针，访问已释放内存
```

指针初始化为 `nullptr`

删除后设置为 `nullptr`

尽量用 `std::unique_ptr` 或 `std::shared_ptr`