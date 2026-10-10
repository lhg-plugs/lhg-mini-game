#!/usr/bin/env python3
"""lhg-mini-game 硬门②（警告级，不拦截）：写游戏 html 文件后做快速体检提醒。

触发：PostToolUse / Write|Edit。只做提醒，永远 exit 0、不拦截写入。
游戏文件写完常忘三件事：viewport meta、触摸事件、结束条件；
这里做一次轻量文本检查，缺了就提醒一句。

逃生方式：LHG_MG_HOOKS_OFF=1（环境变量）可关闭本提醒；
或 /plugin disable lhg-mini-game 停用整个插件。
零第三方依赖。
"""

import json
import os
import re
import sys


def quick_checks(text):
    tips = []
    if not re.search(r'<meta[^>]+name=["\']viewport["\']', text, re.IGNORECASE):
        tips.append("缺 <meta name=\"viewport\">：手机上会缩放错乱")
    if not re.search(r"touchstart|touchmove|touchend|pointerdown", text, re.IGNORECASE):
        tips.append("无 touch*/pointer* 触摸事件：手机上点按会有 300ms 级延迟感")
    code = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    code = re.sub(r"(?m)//[^\n]*", "", code)
    if not re.search(r"gameover|结束|胜利|失败|\bwin\b|\blose\b|通关|时间到", code, re.IGNORECASE):
        tips.append("未检测到结束条件：游戏会永远玩不完")
    return tips


def main() -> int:
    if os.environ.get("LHG_MG_HOOKS_OFF") == "1":
        return 0

    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0

    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "") or ""
    if not file_path:
        return 0
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in (".html", ".htm"):
        return 0
    if not os.path.isfile(file_path):
        return 0

    try:
        with open(file_path, encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError):
        return 0
    if "<canvas" not in text.lower():
        return 0  # 不是游戏文件，不打扰

    tips = quick_checks(text)
    if not tips:
        return 0

    msg = (
        "游戏文件体检提醒（lhg-mini-game）：%s 刚写入，快速检查发现：\n%s\n"
        "完整审计请跑 /lhg-mini-game:mini-game-audit。\n"
        "关闭本提醒：export LHG_MG_HOOKS_OFF=1（当前会话有效）。"
    ) % (os.path.basename(file_path), "\n".join("- " + t for t in tips))
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": msg,
        }
    }
    sys.stdout.write(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
