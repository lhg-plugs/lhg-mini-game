---
name: lhg-mg-dev
description: H5小游戏代码规范：单文件HTML+Canvas、零构建、移动端触摸优先、rAF游戏循环、60fps性能基线、WebAudio合成音效。写游戏代码前加载。
license: MIT
compatibility: 适用于任何支持 Markdown 指令的 AI 编程助手（Claude Code、豆包、Workbuddy 等）
metadata:
  version: 1.0.0
  author: 刘洪光
---

# lhg-mg-dev：H5 小游戏代码规范

> 目标：生成的游戏"一次写对"——单文件、手机上顺滑 60fps、触摸无延迟、
> 断网也能玩。规范要点基于公开 Web 标准知识总结，实现细节为原创。
> 本 skill 的方法论为原创（单文件工程纪律与 60fps 基线清单均为本插件原创）。

## 1. 何时使用

- 生成/修改 H5 小游戏代码时 → 加载本 skill
- 审计报 MG-STRUCT/MG-MOBILE/MG-PERF 类问题时 → 按对应章节修复
- 用户问"游戏在手机上卡/点按延迟/画面糊"时 → 按第 5/6 节排查

## 2. 输入与输出

- **输入**：lhg-mg-plan 输出的一页纸 GDD（玩法、计分、结束条件已定）
- **输出**：单个 `.html` 文件（HTML+CSS+JS 全内联），双击/扫码即玩
- **硬约束**：零构建、零外部 js/css 文件引用（MG-STRUCT-001 是 blocker）

## 3. 单文件工程结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <!-- MG-MOBILE-001：缺了这行，手机上必错乱 -->
  <meta name="viewport" content="width=device-width, initial-scale=1,
        maximum-scale=1, user-scalable=no, viewport-fit=cover">
  <title>游戏名</title>
  <style>/* 全部样式内联；游戏画布 touch-action: none */</style>
</head>
<body>
  <canvas id="game"></canvas>
  <!-- UI 覆盖层：分数/计时/开始结束面板，用 DOM 做（比 Canvas 文字好维护） -->
  <div id="ui">...</div>
  <script>
  (function () {
    'use strict';
    // 1. 分辨率适配  2. 资源预加载  3. 状态机  4. 输入  5. 主循环  6. 裂变
  })();
  </script>
</body>
</html>
```

纪律：
1. **IIFE 包裹 + 'use strict'**：不污染全局，微信内置浏览器多游戏同页不冲突。
2. **CSS 全内联**：不许 `<link>` 引外部 css。
3. **JS 全内联**：不许 `<script src>` 引外部 js（CDN 也不建议：断网即挂，MG-STRUCT-002 会警告）。
4. **图片能画就别引**：简单图形用 Canvas 矢量绘制；必须用图时转 base64 内联（单文件 < 300KB，MG-HYG-001）。

## 4. 游戏循环（rAF + dt，唯一正确写法）

```js
var last = 0;
function loop(ts) {
  if (state !== 'playing') return;      // 状态机门控：暂停/结束即停
  var dt = Math.min((ts - last) / 16.7, 3); // dt 归一化：掉帧时逻辑不穿墙
  last = ts;
  update(dt);   // 逻辑：移动/碰撞/计分
  render();     // 绘制：只画，不算
  requestAnimationFrame(loop);
}
// 启动：requestAnimationFrame(loop)
```

铁律：
- **不许用 setInterval 做主循环**（MG-PERF-001）：后台切走仍在跑，费电且帧率不稳。
- **update 与 render 分离**：逻辑里不许直接调绘图，方便以后加"暂停"与"回放"。
- **dt 上限钳制**：`Math.min(..., 3)` 防止切后台回来时物体瞬移穿墙。

## 5. 移动端触摸优先

```js
// 触摸：必须 preventDefault，否则页面跟随滚动（MG-MOBILE-003）
canvas.addEventListener('touchstart', onTouch, { passive: false });
canvas.addEventListener('touchmove', onTouch, { passive: false });
canvas.addEventListener('touchend', onEnd, { passive: false });
function onTouch(e) {
  e.preventDefault();
  var t = e.touches[0];
  // 用 t.clientX/clientY，乘以 dpr 换算到 Canvas 坐标
}
// 桌面兜底：pointerdown（只做补充，不做主力）
canvas.addEventListener('pointerdown', onPointer);
```

铁律：
- **触摸是主力，click 只是兜底**：纯 click 在移动端有可感知的点按延迟（MG-MOBILE-002 是 blocker）。
- **CSS 配 `touch-action: none`**：双保险防缩放/滚动。
- **目标 ≥44px**：按钮/可点区域不小于 44×44 CSS 像素，手指点得中。
- **横竖屏**：玩法固定方向的，加 `orientationchange` 提示"建议竖屏"（MG-MOBILE-004）。

## 6. 60fps 性能基线

| 检查项 | 做法 | 审计规则 |
|---|---|---|
| 分辨率适配 | `devicePixelRatio` 上限取 2，Canvas 宽高 = CSS 尺寸 × dpr | MG-PERF-003 |
| 对象池 | 粒子/子弹/水果定长数组复用，不许每帧 new | MG-PERF-002 |
| 预加载 | 图片/音频在开始屏前加载完，循环内不许 `new Image/Audio` | MG-PERF-002 |
| 绘制节制 | 同屏绘制元素 < 200 个；粒子总数设上限 | — |
| 脏检查 | 分数/时间等 DOM 更新只在变化时写，避免每帧操作 DOM | — |
| 音效合成 | WebAudio 现场合成（beep/噪声），零外部音频文件 | — |

性能自测口径：低端安卓机（4 年前千元机）连续玩 3 分钟不掉帧感、无发烫；
做不到就砍粒子、砍阴影、砍分辨率——先保流畅再保好看。

## 7. 状态机（idle → playing → over，缺一不可）

```js
var state = 'idle'; // idle: 开始屏 | playing: 游戏中 | over: 结束屏
// 开始按钮：idle → playing（重置分数/计时/对象池）
// 结束条件触发：playing → over（显示分数+最高分+"再来一局"+分享按钮）
// 再来一局：over → playing（必须能一键重开，MG-DESIGN-003）
```

localStorage 存最高分（try/catch 包裹，微信隐身模式会抛异常）。

## 8. 音效规范

- WebAudio 合成：接到/失败/结束各一个短音（正弦波 0.15 秒足够）。
- **必须有静音开关**（MG-A11Y-001 是 nit，但用户体验是 blocker 级的）。
- 首次交互后初始化 AudioContext（浏览器自动播放策略：无用户手势不许发声）。

## 9. 反模式

- ❌ 多文件工程：webpack/vite 一套构建 → 小白部署时 100% 卡住
- ❌ setInterval 主循环 → 切后台继续跑，回来穿墙
- ❌ 循环内 new 对象 → 低端机 10 秒即卡
- ❌ 只用 click → 移动端点按延迟，玩家觉得"不跟手"
- ❌ 固定 750px 写死 → 大屏手机上下留白、小屏溢出
- ❌ console.log 上线 → MG-HYG-002，且可能泄露调试信息
- ❌ eval 解析配置 → MG-SEC-001，用 JSON.parse

## 10. 自检与反馈

**质检门**（代码交付前）：
- [ ] 单文件：无外部 js/css 引用
- [ ] viewport meta 已写
- [ ] 触摸事件为主力输入，含 preventDefault
- [ ] 主循环为 requestAnimationFrame + dt 钳制
- [ ] 结束条件与计分规则与 GDD 一致
- [ ] 跑 `python3 scripts/audit/gameplay_audit.py --target <文件>` 零 blocker

**标准冒烟用例**：用 fixtures/mg-good/game.html 跑审计 → 应零 blocker 零 warning。

**一键反馈**：规范覆盖不了的机型坑（如某机型 Canvas 黑屏），以 `[QC] <机型+现象>`
为标题提交到 https://github.com/lhg-plugs/lhg-mini-game/issues，正文写清"复现步骤 →
实际表现 → 期望表现"。

## 11. 出品：刘洪光

本 skill 由真人出镜 IP「刘洪光」（安徽合肥）出品，归属 [lhg-skills](https://github.com/lhg-skills)。

- GitHub 主页：https://github.com/lhg-skills —— 全部 skill 开源在此，欢迎 star
- 视频号：搜「刘洪光实名上网」
- 微信：lhgsmsw
