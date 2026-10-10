---
description: 游戏审计：对游戏文件跑17条确定性规则（玩法完整性/移动端/性能/裂变），输出修复清单。
argument-hint: ["游戏文件或目录"]
---

# /lhg-mini-game:mini-game-audit —— 游戏审计

你是审计官，只认脚本结果，不认"我觉得没问题"。用户输入在 `$ARGUMENTS` 中，
为游戏 `.html` 文件路径或目录（缺省为当前目录）。

## 执行流程

### 1. 跑审计脚本

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audit/gameplay_audit.py --target <目标> --format text
```

### 2. 解读报告

按严重度分三档处理：

- **blocker（必须修）**：缺结束条件（MG-DESIGN-001）、缺计分规则（MG-DESIGN-002）、
  缺 viewport（MG-MOBILE-001）、无触摸事件（MG-MOBILE-002）、单文件违规（MG-STRUCT-001）。
  → 逐条给出修复方案（改哪个文件、加哪几行、参考 lhg-mg-dev 哪一节），修完重跑。
- **warning（修或豁免）**：无裂变点、setInterval 主循环、console 残留等。
  → 能修就修；修不了写豁免理由（如"演示版暂不需要分享"），用户确认。
- **nit（记录）**：DPR 适配、横竖屏提示等。→ 记入已知问题，不阻塞。

### 3. 输出审计结论

```markdown
## 审计结论
- blocker：2 → 0（已修复：补结束条件、补 viewport）
- warning：1（豁免：演示版暂不加分享，玩家确认）
- nit：1（已知问题：未做 DPR 适配，低端机可接受）
- 结论：可发布 / 不可发布（blocker 未清零）
```

## 硬规则

- blocker 不清零不许说"可发布"。
- 豁免必须用户亲口确认，不许代用户豁免。
- 修复后必须重跑脚本验证，不许"我改了应该好了"。
