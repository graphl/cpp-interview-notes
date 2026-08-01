from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTLINE = ROOT / "outline.md"
SAMPLE = ROOT / "origin_image" / "slide_04.png"


ROLE_LAYOUTS = {
    "封面": "大标题位于左上，中央只放一个强隐喻技术图，留出大量呼吸空间",
    "问题引入": "左侧问题、右侧核心矛盾示意图，用一条手绘箭头建立阅读顺序",
    "概念解释": "中央概念图，周围三到四个短标签，底部一条结论",
    "数据结构": "中央精确结构剖面，字段用稀疏标注线指向对应区域",
    "过程": "从左到右三至四步流程，每步只画一个状态变化",
    "状态变化": "上下或左右 before-after，对变化区域使用浅色强调",
    "时间线": "横向时间轴，四个关键节点和简短动作标签",
    "对比": "左右镜像对比，中间用细线区分，底部收束差异",
    "内存布局": "横向对象内存剖面和少量地址箭头，强调相对位置",
    "调用链": "从调用者到目标函数的单向链路，节点清楚、箭头连续",
    "生命周期时间线": "从构造到析构的横向阶段图，当前有效类型逐步变化",
    "结构变化": "before-after 结构图，突出共享、重复或地址调整",
    "应用": "中央机制图配一个小型使用场景，右下角一句规则",
    "控制流时间线": "双线程泳道或事件时间线，锁、睡眠、唤醒按顺序排列",
    "失败案例对比": "左侧错误时间线、右侧正确时间线，错误用浅桃色标记",
    "跨线程数据流": "生产者和消费者双泳道，release/acquire 之间建立明显连线",
    "决策": "稀疏决策树或三档比较尺，强调选择条件而非大段文字",
    "状态机": "中央状态机，进入、退出和停止路径有明确方向",
    "总结清单": "一个小型总图加六个极短检查词，形成闭环",
    "流程总览": "从左到右的阶段流程，阶段之间用细手绘箭头连接",
    "文件布局": "文件剖面与内存映射上下对应，用颜色区分 section/segment",
    "装载时间线": "execve 到 main 的横向时间线，ld.so 为视觉中心",
    "实验": "左侧命令终端意象，右侧对应可观察证据，不画真实 UI 截图",
    "内核数据流": "从网卡到 socket 队列的纵向数据路径，模块分层明确",
    "数据结构关系": "EventLoop、Connection、缓冲区的层级关系图",
    "协议状态机": "字节流进入缓冲后拆出半包/整包/多包的状态变化",
    "反馈回路": "发送缓冲、高水位和暂停读取构成闭环箭头",
    "失败路径": "正常路径为主线，错误、超时、关闭从侧面汇入统一回收点",
    "案例总结": "症状到证据再到验证的闭环，五个节点形成圆环",
}


def parse_outline() -> list[dict]:
    lines = OUTLINE.read_text(encoding="utf-8").splitlines()
    slides: list[dict] = []
    video_title = ""
    index = 0

    while index < len(lines):
        line = lines[index]
        if line.startswith("# 视频 "):
            video_title = line[2:].strip()
            index += 1
            continue

        scene_match = re.match(r"## Scene \d+：(.+)", line)
        if not scene_match:
            index += 1
            continue

        title = scene_match.group(1).strip()
        index += 1
        points: list[str] = []
        role_text = "概念解释"
        visual = ""

        while index < len(lines) and not lines[index].startswith("## Scene ") and not lines[index].startswith("# 视频 "):
            item = lines[index].strip()
            if item.startswith("- 角色："):
                role_text = item.removeprefix("- 角色：").rstrip("。").strip()
            elif item.startswith("- 视觉想法："):
                visual = item.removeprefix("- 视觉想法：").strip()
            elif item.startswith("- "):
                points.append(item[2:].strip())
            index += 1

        role_parts = [part.strip() for part in re.split(r"[/、]", role_text) if part.strip()]
        primary_role = role_parts[0] if role_parts else "概念解释"
        composition = next(
            (layout for name, layout in ROLE_LAYOUTS.items() if name in role_text),
            ROLE_LAYOUTS["概念解释"],
        )
        if not visual:
            visual = f"围绕“{title}”绘制一个小而精确的技术解释图"

        number = len(slides) + 1
        slides.append(
            {
                "number": number,
                "title": title,
                "role": primary_role,
                "intent": f"在《{video_title}》中解释：{title}",
                "key_points": points[:5],
                "local_context": {
                    "required_background": f"所属视频：{video_title}。本镜头必须独立表达这些事实：" + "；".join(points)
                },
                "layout": {
                    "composition": composition,
                    "relationship_to_previous_slide": "同一视觉身份下使用新的语义布局，不照搬上一页构图",
                },
                "visual_elements": {
                    "main_visual": visual,
                    "supporting_elements": "细手绘箭头、稀疏中文标签、浅色 marker 强调，不使用数字 UI 卡片",
                },
                "constraints": [
                    "只呈现标题和必要短标签，不把 key points 整段抄到画面",
                    "中文必须准确清晰，禁止乱码和伪字",
                    "画面保持大量留白，核心图小而精确",
                    "无页码、无水印、无 logo、无全页边框",
                    "必须是横向 16:9 全画布",
                ],
                **({"sample_approved": True} if number == 4 else {}),
            }
        )

    return slides


def main() -> None:
    slides = parse_outline()
    if len(slides) != 38:
        raise RuntimeError(f"expected 38 slides, got {len(slides)}")
    if not SAMPLE.exists():
        raise FileNotFoundError(SAMPLE)

    spec = {
        "deck_name": "C++难点动态图解系列",
        "language": "Chinese",
        "goal": "把 C++ 与 Linux 中依赖时间、地址和状态变化的难点讲成可跟随的数据流动画视频。",
        "deck_context": {
            "source_summary": "五个短视频依次解释内存与对象生命周期、虚函数动态绑定、条件变量与内存序、ELF 动态链接、epoll Reactor 数据流。",
            "core_claim": "复杂技术概念只有沿数据流、控制流、对象生命周期和失败路径展开，才真正容易理解。",
            "canonical_terms": [
                "原始存储",
                "对象生命周期",
                "vptr/vtable",
                "happens-before",
                "PLT/GOT",
                "epoll 就绪",
            ],
        },
        "selected_image_backend": "built-in image tool",
        "max_concurrent_slides": 3,
        "sample_generation_method": {
            "backend_used": "built-in image tool",
            "tool_name": "image_gen",
            "mode": "generate",
            "prompt_source": "自决策通过的内存块分割与合并样片提示词",
            "size": "16:9 landscape, built-in generated 1672x941",
            "quality": "built-in default high quality",
            "approved_sample_path": str(SAMPLE),
            "input_context_preparation": "parent inspected approved sample with view_image; workers use it as style-only reference",
            "handoff_rule": "Subagents must use this same built-in image tool in generate mode; return a blocker if unavailable.",
        },
        "style": {
            "name": "手绘技术解释风",
            "visual_direction": "clean Chinese hand-drawn technical explainer, near-white paper background, thin sketch lines, light pencil hatching, small precise diagram, restrained pastel markers, lots of whitespace, calm educational tone",
            "color_palette": "near-white #FCFBF7, graphite #2F3437, pale blue #BFD7F1, sage #CFE2D1, peach #F4C7B8, lavender #D8C7EF",
            "typography": "简短准确的中文手写标题和稀疏标签，标题中等偏大，禁止长段正文",
            "texture_and_finish": "干净纸张、轻微铅笔排线、柔和 marker 强调",
        },
        "approved_style_reference": {
            "path": str(SAMPLE),
            "role": "approved sample slide style reference",
            "fidelity": "match palette, line quality, typography mood, whitespace and calm educational tone only; do not copy layout or memory-block content",
        },
        "slides": slides,
    }

    (ROOT / "deck_spec.json").write_text(
        json.dumps(spec, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"prepared {len(slides)} slides")


if __name__ == "__main__":
    main()
