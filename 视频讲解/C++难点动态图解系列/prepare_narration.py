from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


VIDEO_RANGES = [
    (1, 7, "从 malloc 到 vector——内存与对象生命周期"),
    (8, 15, "一次虚函数调用到底发生了什么"),
    (16, 23, "条件变量与内存序——线程如何真正看见彼此"),
    (24, 30, "ELF、PLT/GOT 与第一次动态函数调用"),
    (31, 38, "epoll Reactor——一个网络包如何变成业务回调"),
]


CUSTOM_LEADS = {
    1: "我们先拆掉一个最常见的误解：代码里写了申请内存，并不代表一个对象已经存在。",
    2: "画面从下往上看，C++ 的内存问题可以稳定地分成三层。",
    3: "先进入最底层，只看一段没有类型的连续字节。",
    4: "分配器的核心动作其实只有两个：把大块切开，以及把相邻空闲块重新接回去。",
    5: "现在把原始存储交给 C++ 对象模型，就得到 new 和 delete 的四步时间线。",
    6: "placement new 和 allocator 负责把存储管理与对象生命周期彻底拆开。",
    7: "vector 扩容是前面所有概念的一次综合演练。",
    8: "第二段视频从一个现象开始：同样是 Base 指针，为什么最终会进入不同函数？",
    9: "普通调用和虚调用的差异，在于目标函数能否在编译期直接确定。",
    10: "下面使用常见 ABI 模型观察对象、vptr 和 vtable 的关系。",
    11: "一次虚调用可以沿着对象地址逐步走到最终函数入口。",
    12: "构造和析构阶段看似违反多态，其实是在保护对象生命周期。",
    13: "多继承让一个完整对象中出现多个基类子对象，因此地址本身也成为问题的一部分。",
    14: "虚继承进一步改变布局：重复的虚基类被最派生对象共享。",
    15: "RTTI 和 dynamic_cast 就建立在完整对象及继承关系的运行时检查上。",
    16: "并发部分先从一句关键规则开始：通知不是状态，条件才是状态。",
    17: "任何并发代码都应该先画共享状态和不变量，再讨论用什么 API。",
    18: "condition_variable 的关键不是 wait 这个名字，而是解锁、睡眠和重新加锁的原子衔接。",
    19: "丢失通知和虚假唤醒看起来相反，却由同一条规则解决：永远重新检查谓词。",
    20: "跨线程可见性可以用最典型的发布获取链路来理解。",
    21: "内存序不是越弱越高级，它只是用不同成本表达不同的顺序需求。",
    22: "一个线程池是否可靠，往往不是看它怎么启动，而是看它怎么停止。",
    23: "最后用六个问题检查并发正确性，把锁、条件变量和内存序放回同一张图。",
    24: "动态链接从一个现实约束开始：编译 puts 调用时，我们还不知道 libc 最终加载到哪里。",
    25: "先把源代码一路变成 ELF，看看未知地址是怎样被保留下来的。",
    26: "section 和 segment 经常被混为一谈，但它们服务于完全不同的阶段。",
    27: "程序运行时，execve 到 main 之间还有动态加载器完成的大量工作。",
    28: "第一次 puts 调用是整套机制最值得慢下来看的地方。",
    29: "解析完成后，第二次调用的路径明显缩短；安全选项还会改变绑定时机和写权限。",
    30: "理解 ELF 最可靠的方法不是背图，而是用命令逐层验证。",
    31: "最后一段视频纠正一个常见说法：epoll 返回的是就绪事件，不是业务数据。",
    32: "先沿数据走一遍，从网卡进入内核，最终抵达 socket 接收队列。",
    33: "epoll_wait 返回后，真正承接长期状态的是 Connection 对象，而不是一个孤立的 fd 数字。",
    34: "ET 模式的核心约束是：一次边沿到来后，要把当前可读条件消耗到 EAGAIN。",
    35: "recv 得到的只是 TCP 字节流，业务消息边界必须由协议解码器恢复。",
    36: "写侧也不是一次 send 就结束；慢客户端会形成需要主动处理的背压。",
    37: "正常读写只占连接生命周期的一部分，错误、超时和半关闭最终都必须汇入统一回收路径。",
    38: "当服务变慢或崩溃时，我们再沿相反方向从症状回到证据。",
}


def normalize(sentence: str) -> str:
    sentence = sentence.strip()
    if not sentence:
        return ""
    if sentence[-1] not in "。！？；":
        sentence += "。"
    return sentence


def video_for_slide(number: int) -> tuple[int, int, str]:
    for start, end, title in VIDEO_RANGES:
        if start <= number <= end:
            return start, end, title
    raise ValueError(number)


def main() -> None:
    spec = json.loads((ROOT / "deck_spec.json").read_text(encoding="utf-8"))
    slides = spec["slides"]
    narrations = []
    speech = ["# C++ 难点动态图解系列：中文旁白与演讲备注", ""]

    for idx, slide in enumerate(slides):
        number = slide["number"]
        start, end, video_title = video_for_slide(number)
        points = [normalize(point) for point in slide.get("key_points", []) if point.strip()]
        lead = CUSTOM_LEADS[number]
        body = "".join(points)

        if number == end:
            transition = "这一段到这里形成闭环，建议回到笔记里的代码和命令亲手验证一次。"
        else:
            next_title = slides[idx + 1]["title"]
            transition = f"接下来继续看“{next_title}”。"

        text = lead + body + transition
        narrations.append(
            {
                "slide": number,
                "video_title": video_title,
                "title": slide["title"],
                "text": text,
            }
        )

        speech.extend(
            [
                f"## Slide {number}: {slide['title']}",
                "",
                text,
                "",
                "---",
                "",
                "注意点：",
                f"- 重点：{points[0] if points else slide['title']}",
                "- 画面引导：先看主图，再沿箭头阅读状态变化，最后落到结论。",
                "- 节奏：关键地址、生命周期或线程关系出现时放慢语速。",
                "",
            ]
        )

    (ROOT / "narration.json").write_text(
        json.dumps(narrations, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (ROOT / "speech.md").write_text("\n".join(speech), encoding="utf-8")
    print(f"prepared narration for {len(narrations)} slides")


if __name__ == "__main__":
    main()
