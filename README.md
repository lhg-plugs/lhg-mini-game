<!-- About 简介（推送后填写到仓库 About 栏）：
小白一句话→可玩的H5小游戏：玩法模板匹配、单文件Canvas代码生成、移动端触摸优化、分享裂变点设计，零构建。 ｜ 一键安装：/plugin marketplace add lhg-plugs/lhg-mini-game
-->
<!-- topics（推送后打）：claude-code, claude-plugin, agent-skills, mini-game, h5-game, html5, canvas, wechat-share -->

<p align="center">
  <img src="./assets/readme/hero.svg" width="100%" alt="lhg-mini-game — 小白一句话→可玩的H5小游戏">
</p>

> **一句话介绍**：小白一句话→可玩的H5小游戏：玩法模板匹配、单文件Canvas代码生成、移动端触摸优化、分享裂变点设计，零构建。

**一键安装**：在 Claude Code 里运行

```bash
/plugin marketplace add lhg-plugs/lhg-mini-game
/plugin install lhg-mini-game@lhg-plugs
```

## 它能帮你做出什么

- **冒烟全绿**：`python3 smoke_test.py` 49 项全部通过（JSON 合法、frontmatter 完整、命令/skill/agent 齐全）。

## 它是什么

`lhg-mini-game` 是一个 Claude Code 插件（plugin 为主、skill 为辅）：

- **4 个命令**（小白入口）：`mini-game` 一句话玩法描述 → H5小游戏、`mini-game-audit` 游戏审计、`mini-game-share` 裂变点设计、`mini-game-template` 玩法模板库查询
- **4 个平台中立 skill**（方法论，可移植到豆包/Workbuddy 等 agent 平台）：lhg-mg-dev, lhg-mg-plan, lhg-mg-publish, lhg-mg-viral
- **2 个专家 agent**：mg-auditor, mg-builder
- **2 个 hooks**（`hooks/`：post_write_warn.py, pre_commit_audit.py），关键操作前自动把关

## 为什么是它

不是一个 prompt，而是一套互相兜底的机制：

1. **硬门，不是提醒**：hooks 在关键操作前自动拦截或警告（见 `hooks/`），而不是只在文档里写一句"请注意"。
2. **方法论沉淀在 skill 里**：流程、检查清单、口径都写在 `skills/` 的方法论里，命令只是入口；换个 agent 平台也能复用同一套做法。
3. **可验，不是可信**：`fixtures/` 备有坏/好对照用例，`smoke_test.py` 一键验证，规则有没有生效、自己跑一遍就知道。

## 快速上手

```bash
# 1. 安装（Claude Code 里运行）
/plugin marketplace add lhg-plugs/lhg-mini-game
/plugin install lhg-mini-game@lhg-plugs

# 2. 一句话玩法描述 → H5小游戏：模板匹配、单文件Canvas代码生成、移动端优化
/lhg-mini-game:mini-game
```

| 命令 | 作用 | 示例 |
|---|---|---|
| `/lhg-mini-game:mini-game` | 一句话玩法描述 → H5小游戏：模板匹配、单文件Canvas代码生成、移动端优化、分享裂变点、审计发布，一条龙交付。 | `/lhg-mini-game:mini-game` |
| `/lhg-mini-game:mini-game-audit` | 游戏审计：对游戏文件跑17条确定性规则（玩法完整性/移动端/性能/裂变），输出修复清单。 | `/lhg-mini-game:mini-game-audit` |
| `/lhg-mini-game:mini-game-share` | 裂变点设计：为已有游戏设计分享传播点（战绩海报/排行榜/邀请奖励/挑战接龙），含文案与合规检查。 | `/lhg-mini-game:mini-game-share` |
| `/lhg-mini-game:mini-game-template` | 玩法模板库查询：输入一句话玩法，匹配合成/跳跃/答题/抽奖四类模板并输出参数化设计。 | `/lhg-mini-game:mini-game-template` |

## 什么时候用 / 什么时候不用（FAQ）

**什么时候用：**

- 你需要一句话玩法描述 → H5小游戏时 → 用 `/lhg-mini-game:mini-game`
- 你需要游戏审计时 → 用 `/lhg-mini-game:mini-game-audit`
- 你需要裂变点设计时 → 用 `/lhg-mini-game:mini-game-share`

**什么时候不用：**

- 你只需要其中一个零散能力时 → 本插件是成套流程，单点需求用更轻量的 skill 更合适
- 你希望 AI 完全自由发挥、不接受任何自查与硬门时 → 它的规则审计与 hooks 会介入（可关，但那就别装它）
- 你的场景不在上面命令表覆盖范围内时 → 先看命令表，没有对应命令就别硬套

## 目录结构

```
lhg-mini-game/
├── smoke_test.py          # 一键冒烟测试
├── ATTRIBUTION.md         # 灵感来源与许可声明
├── LICENSE                # MIT
├── README.md              # 本文件
├── .claude-plugin/
├── agents/
├── commands/
├── fixtures/
├── hooks/
├── scripts/
├── skills/
```

## 自检与反馈

本插件自带质检：每次使用后可跑 `python3 smoke_test.py` 一键验证（本次实测 49 项全部通过）。

发现 bug 或有改进建议，以 `[QC] <一句话问题>` 为标题提交到 https://github.com/lhg-plugs/lhg-mini-game/issues，正文写清"复现步骤 → 实际表现 → 期望表现"。

同门插件见 [lhg-plugs](https://github.com/lhg-plugs)，86 个插件的完整矩阵在 [marketplace](https://github.com/lhg-plugs/marketplace) 维护。

## 出品：刘洪光

本插件由真人出镜 IP「刘洪光」（安徽合肥）出品，归属 [lhg-skills](https://github.com/lhg-skills)。

- GitHub 主页：https://github.com/lhg-skills —— 全部 skill 开源在此，欢迎 star
- 抖音：搜「刘老师讲AI实战」
- 微信：lhgsmsw
