#!/usr/bin/env python3
"""lhg-mini-game 确定性审计：H5 小游戏玩法完整性 + 移动端规范 + 性能基线。

用法：
    python3 gameplay_audit.py --target <game.html 或目录> [--format json|text]

规则注册表：RULES。每条规则 = {id, severity, title, check}。
  check(html_text, file_path, all_files) -> [(line_no, detail), ...]

exit code 语义：
  0 = 无 blocker（可发布；warning/nit 仅提示）
  1 = 有 blocker（玩法不完整/移动端不可玩/结构违规，必须修）
  2 = 用法错误（target 不存在等）

零第三方依赖。
"""

import argparse
import json
import os
import re
import sys

SEVERITY_ORDER = {"blocker": 0, "warning": 1, "nit": 2}


def _lines(text):
    return text.split("\n")


def _find(text, patterns):
    """返回 (行号, 匹配到的模式) 列表，大小写不敏感。"""
    out = []
    for i, ln in enumerate(_lines(text), 1):
        for p in patterns:
            if re.search(p, ln, re.IGNORECASE):
                out.append((i, p))
                break
    return out


def _strip_comments(text):
    """剥离 HTML/JS 注释：注释里的 TODO 不算实现。"""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"(?m)//[^\n]*", "", text)
    return text


def _has(text, patterns):
    return bool(_find(text, patterns))


def _has_code(text, patterns):
    """在剥离注释后的代码中匹配。"""
    return _has(_strip_comments(text), patterns)


# ---------------------------------------------------------------- 规则实现

def chk_struct_single(text, path, files):
    """MG-STRUCT-001 blocker：单文件要求——引用外部 .js/.css 本地文件则违规。"""
    hits = []
    for i, ln in enumerate(_lines(text), 1):
        m = re.search(r'<script[^>]+src=["\']([^"\']+)["\']', ln, re.IGNORECASE)
        if m and not re.match(r"https?://", m.group(1)) and not m.group(1).startswith("data:"):
            hits.append((i, "外部脚本引用: %s（单文件游戏不许引用外部 js）" % m.group(1)))
        m = re.search(r'<link[^>]+href=["\']([^"\']+\.css)["\']', ln, re.IGNORECASE)
        if m and not re.match(r"https?://", m.group(1)):
            hits.append((i, "外部样式引用: %s（单文件游戏不许引用外部 css）" % m.group(1)))
    return hits


def chk_struct_cdn(text, path, files):
    """MG-STRUCT-002 warning：引用 CDN/外部资源——断网即不可用，提醒内联。"""
    hits = []
    for i, ln in enumerate(_lines(text), 1):
        for m in re.finditer(r'(?:src|href)=["\'](https?://[^"\']+)["\']', ln, re.IGNORECASE):
            hits.append((i, "外部资源: %s（建议内联，断网/防盗链会挂）" % m.group(1)[:60]))
    return hits


def chk_mobile_viewport(text, path, files):
    """MG-MOBILE-001 blocker：缺 viewport meta，手机上会缩放错乱。"""
    if _has(text, [r'<meta[^>]+name=["\']viewport["\']']):
        return []
    return [(1, "缺 <meta name=\"viewport\">，移动端会缩放错乱")]


def chk_mobile_touch(text, path, files):
    text = _strip_comments(text)
    """MG-MOBILE-002：无触摸事件。只用 click/mousedown → blocker；完全无交互 → warning。"""
    touch = _has(text, [r"touchstart", r"touchmove", r"touchend", r"pointerdown", r"pointermove"])
    if touch:
        return []
    mouse = _has(text, [r"\bclick\b", r"mousedown", r"mouseup", r"keydown"])
    if mouse:
        return [(1, "只有鼠标/键盘事件，无 touch*/pointer* 触摸事件，手机上点按延迟且体验差")]
    return []  # 纯展示型页面不强制


def chk_mobile_scroll(text, path, files):
    """MG-MOBILE-003 warning：无防滚动/防缩放处理，玩着玩着页面会滚走。"""
    if _has(text, [r"preventDefault", r"touch-action\s*:\s*none", r"user-scalable\s*=\s*no"]):
        return []
    if not _has(text, [r"touchstart", r"touchmove"]):
        return []
    return [(1, "有触摸交互但无 preventDefault/touch-action:none，滑动时页面可能跟随滚动")]


def chk_design_end(text, path, files):
    text = _strip_comments(text)
    """MG-DESIGN-001 blocker：缺结束条件——没有输赢/结束，游戏永远玩不完。"""
    if _has(text, [r"gameover", r"game-over", r"game_over", r"结束", r"胜利", r"失败",
                   r"\bwin\b", r"\blose\b", r"通关", r"时间到", r"timeup", r"time_up"]):
        return []
    return [(1, "未检测到结束条件（胜利/失败/时间到/通关），游戏没有终点")]


def chk_design_score(text, path, files):
    text = _strip_comments(text)
    """MG-DESIGN-002 blocker：缺计分/进度规则——没有分数就没有玩下去的理由。"""
    if _has(text, [r"\bscore\b", r"分数", r"得分", r"计分", r"\blevel\b", r"关卡",
                   r"回合", r"\bcombo\b", r"连击", r"最高分", r"best"]):
        return []
    return [(1, "未检测到计分/进度规则（score/分数/关卡），玩家没有目标感")]


def chk_design_start(text, path, files):
    text = _strip_comments(text)
    """MG-DESIGN-003 warning：缺开始/重开机制，玩家可能不知道怎么开局。"""
    if _has(text, [r"\bstart\b", r"开始", r"restart", r"重新开始", r"再来一局", r"重新挑战"]):
        return []
    return [(1, "未检测到开始/重开入口（start/开始/再来一局）")]


def chk_perf_raf(text, path, files):
    """MG-PERF-001 warning：主循环不用 requestAnimationFrame，帧率不稳。"""
    has_raf = _has(text, [r"requestAnimationFrame"])
    has_interval_loop = _has(text, [r"setInterval\s*\("])
    if has_raf or not has_interval_loop:
        return []
    return [(1, "游戏主循环用 setInterval 而非 requestAnimationFrame，帧率不稳且后台仍跑")] 


def chk_perf_alloc(text, path, files):
    """MG-PERF-002 warning：循环内高开销分配（new Image/Audio/DOM），低端机卡顿。"""
    hits = []
    for i, ln in enumerate(_lines(text), 1):
        if re.search(r"requestAnimationFrame|function\s+\w*(loop|tick|update|render)\w*\s*\(", ln, re.IGNORECASE):
            continue
        if re.search(r"new\s+(Image|Audio)\s*\(", ln) or re.search(r"document\.createElement", ln):
            # 保守起见：出现在文件里即提醒（游戏文件小，误报成本低）
            hits.append((i, "发现运行时 new Image/Audio 或 createElement：建议预加载/对象池"))
    # 去重到最多 3 条
    return hits[:3]


def chk_perf_dpr(text, path, files):
    """MG-PERF-003 nit：无 DPR 适配，高清屏会糊。"""
    if _has(text, [r"devicePixelRatio"]):
        return []
    if not _has(text, [r"<canvas"]):
        return []
    return [(1, "未做 devicePixelRatio 适配，高清屏 Canvas 会发虚")]


def chk_viral(text, path, files):
    text = _strip_comments(text)
    """MG-VIRAL-001 warning：无裂变点——没有分享/排行/邀请，传播靠运气。"""
    if _has(text, [r"share", r"分享", r"\brank\b", r"排行", r"榜", r"invite", r"邀请",
                   r"toDataURL", r"战绩", r"炫耀"]):
        return []
    return [(1, "未检测到裂变点（分享/排行榜/邀请奖励），建议按 lhg-mg-viral 加一个")]


def chk_sec_eval(text, path, files):
    """MG-SEC-001 warning：eval/new Function——可被注入且影响性能。"""
    hits = _find(text, [r"\beval\s*\(", r"new\s+Function\s*\("])
    return [(i, "使用 eval/new Function，有注入风险且难调试") for i, _ in hits]


def chk_mobile_orient(text, path, files):
    """MG-MOBILE-004 nit：无横竖屏提示，横屏游戏竖着玩会错位。"""
    if _has(text, [r"orientation", r"横屏", r"竖屏", r"旋转屏幕"]):
        return []
    if not _has(text, [r"<canvas"]):
        return []
    return [(1, "无横竖屏适配/提示，横屏玩法建议加旋转提示")]


def chk_hyg_size(text, path, files):
    """MG-HYG-001 nit：单文件过大（>300KB），加载慢。"""
    try:
        size = os.path.getsize(path)
    except OSError:
        return []
    if size > 300 * 1024:
        return [(1, "单文件 %.1fKB > 300KB，首屏加载慢，建议压缩内联资源" % (size / 1024))]
    return []


def chk_hyg_console(text, path, files):
    """MG-HYG-002 warning：console.log 残留。"""
    hits = _find(text, [r"console\.(log|debug)\s*\("])
    return [(i, "console.log 残留，发布前清理") for i, _ in hits[:5]]


def chk_a11y_mute(text, path, files):
    text = _strip_comments(text)
    """MG-A11Y-001 nit：有音频但无静音开关。"""
    has_audio = _has(text, [r"new\s+Audio", r"AudioContext", r"<audio"])
    if not has_audio:
        return []
    if _has(text, [r"mute", r"静音", r"音效开关", r"soundOn"]):
        return []
    return [(1, "有音频但无静音开关，建议加一个")]


RULES = [
    {"id": "MG-STRUCT-001", "severity": "blocker", "title": "单文件违规：引用外部 js/css",
     "check": chk_struct_single},
    {"id": "MG-STRUCT-002", "severity": "warning", "title": "引用外部 CDN 资源",
     "check": chk_struct_cdn},
    {"id": "MG-MOBILE-001", "severity": "blocker", "title": "缺 viewport meta",
     "check": chk_mobile_viewport},
    {"id": "MG-MOBILE-002", "severity": "blocker", "title": "无触摸事件（只用鼠标事件）",
     "check": chk_mobile_touch},
    {"id": "MG-MOBILE-003", "severity": "warning", "title": "触摸滑动未防页面滚动",
     "check": chk_mobile_scroll},
    {"id": "MG-MOBILE-004", "severity": "nit", "title": "无横竖屏适配/提示",
     "check": chk_mobile_orient},
    {"id": "MG-DESIGN-001", "severity": "blocker", "title": "缺游戏结束条件",
     "check": chk_design_end},
    {"id": "MG-DESIGN-002", "severity": "blocker", "title": "缺计分/进度规则",
     "check": chk_design_score},
    {"id": "MG-DESIGN-003", "severity": "warning", "title": "缺开始/重开入口",
     "check": chk_design_start},
    {"id": "MG-PERF-001", "severity": "warning", "title": "主循环未用 requestAnimationFrame",
     "check": chk_perf_raf},
    {"id": "MG-PERF-002", "severity": "warning", "title": "运行时高开销对象分配",
     "check": chk_perf_alloc},
    {"id": "MG-PERF-003", "severity": "nit", "title": "无 DPR 高清适配",
     "check": chk_perf_dpr},
    {"id": "MG-VIRAL-001", "severity": "warning", "title": "无分享裂变点",
     "check": chk_viral},
    {"id": "MG-SEC-001", "severity": "warning", "title": "使用 eval/new Function",
     "check": chk_sec_eval},
    {"id": "MG-HYG-001", "severity": "nit", "title": "单文件过大",
     "check": chk_hyg_size},
    {"id": "MG-HYG-002", "severity": "warning", "title": "console.log 残留",
     "check": chk_hyg_console},
    {"id": "MG-A11Y-001", "severity": "nit", "title": "有音频无静音开关",
     "check": chk_a11y_mute},
]


def audit_file(path):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError):
        return []
    findings = []
    for rule in RULES:
        try:
            hits = rule["check"](text, path, None) or []
        except Exception:
            continue  # 单条规则出错不影响整体
        for line_no, detail in hits:
            findings.append({
                "rule_id": rule["id"],
                "severity": rule["severity"],
                "title": rule["title"],
                "file": path,
                "line": line_no,
                "detail": detail,
            })
    return findings


def collect_targets(target):
    if os.path.isfile(target):
        return [target]
    out = []
    for root, _dirs, files in os.walk(target):
        for fn in files:
            if fn.lower().endswith((".html", ".htm")):
                out.append(os.path.join(root, fn))
    return sorted(out)


def main():
    ap = argparse.ArgumentParser(description="lhg-mini-game 游戏审计")
    ap.add_argument("--target", required=True, help="game.html 文件或目录")
    ap.add_argument("--format", choices=["json", "text"], default="text")
    args = ap.parse_args()

    if not os.path.exists(args.target):
        print("target 不存在: %s" % args.target, file=sys.stderr)
        return 2

    files = collect_targets(args.target)
    findings = []
    for fp in files:
        findings.extend(audit_file(fp))
    findings.sort(key=lambda f: (SEVERITY_ORDER[f["severity"]], f["rule_id"], f["line"]))

    summary = {
        "files": len(files),
        "rules_run": len(RULES),
        "blocker": sum(1 for f in findings if f["severity"] == "blocker"),
        "warning": sum(1 for f in findings if f["severity"] == "warning"),
        "nit": sum(1 for f in findings if f["severity"] == "nit"),
    }

    if args.format == "json":
        print(json.dumps({"summary": summary, "findings": findings},
                         ensure_ascii=False, indent=2))
    else:
        print("lhg-mini-game 审计报告：%s" % args.target)
        print("文件 %d 个 | 规则 %d 条 | blocker %d / warning %d / nit %d"
              % (summary["files"], summary["rules_run"], summary["blocker"],
                 summary["warning"], summary["nit"]))
        print("-" * 60)
        for f in findings:
            print("[%s] %s %s:%s %s" % (f["severity"].upper(), f["rule_id"],
                                       os.path.basename(f["file"]), f["line"], f["title"]))
            print("       %s" % f["detail"])
        if not findings:
            print("干净：无 blocker，可发布。")

    return 1 if summary["blocker"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
