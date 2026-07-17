## 回调函数（Callback Function）

- **定义**：回调函数就是你自己写的、传给系统的函数。等事件发生时，系统就会“回过头来”调用它。
- **作用**：由用户实现，系统在适当的时机调用，完成用户需要的处理逻辑。



```
// 用户自己写的函数 —— 回调函数
void myHandler(int eventType) {
    std::cout << "Event type = " << eventType << std::endl;
}

int main() {
    // 注册，把回调函数传给库
    registerEventHandler(myHandler);

    // 系统以后触发事件时，会自动调用 myHandler
}

```

