# Skill: Manim 混剪·特制版（参考《我曾九次认识世界》）

以 26.6s 原片《我曾九次认识世界》（星空深蓝 + 九大数学名场面）逐帧逆向定稿。
在 `formula-mixcut-animation` 基础上的**三次实战升级**：
① 星空壁纸层系统化；② **函数图像整组 ReplacementTransform 转场**（原片灵魂，本次补齐）；
③ 动态计数器卡片（每卡 = 标题 + 公式 + 动态图 + 计数器 四件套）。
参照项目：`nine_worlds/nine_worlds.py`（约 700 行，28s 成片，9 卡全动态，judge 验收通过）。

---

## 1. 全局配置

```python
from manim import *
import numpy as np
import math

config.pixel_width  = 1920
config.pixel_height = 1080
config.frame_width  = 16.0      # 1920px / 120 = 16 manim 单位，帧像素↔坐标换算: x_px→(x-960)/120
config.frame_height = 9.0       # y_px→(540-y)/120
```

调色板先从原片抽帧取色写成常量（GOLD #E8B84B、LILAC #A8B8F0、CYAN2 #4DD0E1、
LAV #B8A8E8、ORNG #F0A860、MINT #7FC98A、PINK2 #F08BB8、PURP2 #B8A0E8、AXCOL #5B7BA8…），
九卡标题各占一色，公式分色用 `tex_to_color_map`（注意匹配子串别把等号卷进去）。

中文字体 `Text(font="Kaiti SC")`（macOS）；`weight="BOLD"`；Text 里**禁用 ∫ ∑ 等数学符号**
（会截半），希腊字母 Δ θ π ω 可以直出。

---

## 2. 三层画面结构 + 星空壁纸层

每卡四件套，**同屏只有一张卡**：

| 层 | 位置 | 规格 |
|----|------|------|
| 标题 | `UP*3.55`，楷体加粗 font_size 58 | 主色填充 + 白描边 1.2 + **halo 光晕层**（copy 放大 stroke 11、opacity 0.20 垫底） |
| 主公式 | `UP*2.15`，font_size 44~64 | `tex_to_color_map` 分色；超宽（勒贝格式）`scale_to_fit_width(14.6)` |
| 动态图 | 下半屏 | Axes/圆/点阵，轴色 AXCOL，含刻度无数字 |
| 计数器/标注 | `y≈-3.3` 一排 | Text 前缀 + DecimalNumber，数字金/主色 |

### 壁纸层（最先 add，全程静止，绝不参与任何形变）

```python
# ① 径向渐变：中心亮蓝→边缘近黑，用 14 层叠加圆环近似（原片同款观感）
for i in range(14):
    r = 0.55 + i*0.60
    col = interpolate_color(ManimColor("#2A3F6E"), ManimColor("#04070F"), i/13)
    bg.add(Circle(radius=r).set_stroke(width=0).set_fill(col, 0.155))
# ② 同心圆细线 6 圈 + 中心金点带细环
# ③ 两条暗金椭圆轨道（Circle().stretch(rx,0).stretch(ry,1).rotate(θ)）+ 轨道行星金点（点+外环）
# ④ 十字星（两条正交 Line）固定布局仿原片 + 随机小白点/金点（固定 seed）
# ⑤ 幽灵数学符号：MathTex ∂ σ π θ μ ℏ α ± ∇ × ∞ λ ∆ Σ，色 #7A90C0，opacity 0.13，
#    随机 scale/rotate，固定坐标布局（仿原片 ∂左中 Σ右上大 ∆左上 ×2 …）
```

固定随机种子 `np.random.default_rng(20260913)` 保证可复现。

---

## 3. 转场（灵魂中的灵魂，三路同拍形变）

```python
def morph_to(self, new_title, new_formula, new_extras, run_time=0.42):
    anims = [
        ReplacementTransform(self.cur_title, new_title),               # ① 中文标题整族字形拉伸
        TransformMatchingTex(self.cur_formula, new_formula,
                             transform_mismatches=True),               # ② 公式碎片互变（灵魂参数）
    ]
    if self.cur_extras and new_extras:
        src_g = VGroup(*self.cur_extras)
        self.remove(*self.cur_extras)     # ★包装组顶替进 scene（见 §5 铁律）
        self.add(src_g)
        anims.append(ReplacementTransform(src_g, VGroup(*new_extras)))  # ③ 图像整组形变
    elif self.cur_extras:
        ...  # FadeOut 保底
    elif new_extras:
        anims.append(FadeIn(VGroup(*new_extras), lag_ratio=0.08))
    self.play(*anims, run_time=run_time)
    self.set_cur(new_title, new_formula, list(new_extras) or [VGroup()])
```

- **★③ 是本次定稿升级**：函数图像不做 FadeOut+FadeIn，而是**旧图全家桶整组形变为新卡底图**。
  原片抽帧证据：旧坐标轴被拉成水平亮线再立成新轴、旧曲线碎成波浪飞散、旧面积边缘波纹化、
  计数器文字碎片化飞行——正是整组 `ReplacementTransform` 的中间态。公式管"字变"，图像管"形变"，
  三路同拍 0.42s，转场才有原片那种"整个画面都活着"的丝滑感。
- **底图前置模式**：`cardN_parts()` 必须返回新卡的"底图"（轴/圆/点阵/首条曲线），
  卡内动画只负责底图之上的生长。morph 才有东西可变。卡内原第一拍的 FadeIn/Create 直接删掉。
- `transform_mismatches=True` 必须加（公式碎片互变）；禁用 `\underbrace`（会 IndexError）。
- 中文标题用 `ReplacementTransform` 整族形变（字符数不同自动复制拉伸出拉丝感）。
- 开场第一卡不走 morph（大标题 Write 进场 + 各元素 Create 同拍）；末卡整体 FadeOut 收黑。

---

## 4. 动态计数器卡片（每卡的"活"全在这）

**计数器**：`Text 前缀 + DecimalNumber(num_decimal_places=…)` 组合，数字滚动用
`ChangeDecimalToValue(num, 终值)` 与 tracker 动画**同一个 play** 同拍滚动。
位数不变的滚动最稳；固定终值直接写原片数值（如 sin x₀=-0.899）忠实还原。

**动态图形**：`ValueTracker + always_redraw` 驱动，play(tracker.animate.set_value(终值), ChangeDecimalToValue(...), run_time=…)
一拍联动"图形生长 + 数字滚动"。**play 结束立即 `clear_updaters()` 冻结**，再 track_extra 登记。
- 面积扫描：`ax.get_area(g, x_range=[a, max(tr.get_value(), a+1e-4)])`（max 防区间反转）
- 曲线描画：`ParametricFunction(..., t_range=[0.01, max(th, 0.02)])`
- 旋转弧渐隐：`Arc(...).set_stroke(opacity=0.9-0.65*min(th/TAU,1))`（防整圈弧抢戏）

**卡内节奏模板**（每卡 2.2~2.9s）：底图已由 morph 送入 → 2~4 拍生长动画（每拍 0.3~0.85s，
LaggedStart(lag_ratio=0.06~0.2) 出系列元素）→ 尾部 `self.wait(0.5~0.6)` **稳定展示窗口**
→ morph。稳定窗口是验收硬指标，宁可总时长略超也不可"元素闪过"。

**九卡动态库**（按需取用）：
面积扫描计数（微积分基本定理）、泰勒逐阶 ReplacementTransform+公式逐项
TransformMatchingTex、单位圆旋转+双曲线描画、混合波分解+频谱柱 GrowFromEdge(DOWN)、
向量场内外双层箭头、围道动点 Rotate(TAU)+推导逐行 FadeIn(lag_ratio)、
100 人点阵随机变蓝变绿（random.default_rng 固定种子）+比例横条、
π(x) 阶梯 always_redraw 截断+PV 积分曲线、曲线族保留渐暗+三柱趋近极限。
柱高数值要对得上数学：f_k=1-e^{-kx} 在 [0,2] 积分，k=1,2,3 → 1.14/1.51/1.67（原片数值）。

---

## 5. 场景管理铁律（本次踩坑最贵的一条）

- `track_extra(*mobs)`：卡内产生的每个顶层 mob **逐个**登记进 `self.cur_extras` 列表。
  **严禁** `self.cur_extras[-1].add(...)` 往"不在 scene 的幽灵组"里塞——FadeOut/ReplacementTransform
  结束只移除传入的顶层对象，塞进去的子 mob 会**永远残留在后续画面**。
- morph 里整组 transform 前，必须 `self.remove(*cur_extras)` + `self.add(VGroup(*cur_extras))`
  让包装组顶替进 scene，ReplacementTransform 结束才能把旧图干净移除。
- 计数器/曲线的 updater 在 play 后立刻 clear；不再需要的引导帧 mob 及时移除。
- 找 morph 送入的底图：直接 `self.cur_extras[0]` 取，**不要遍历 self.mobjects 按 isinstance 搜**
  （morph 后 scene 分组结构变了，会搜不到或搜到背景）。

---

## 6. 还原流水线（逆向已有视频）

1. `ffprobe` 拿时长/分辨率/帧率；`ffmpeg -i 原片 -vf fps=8 frames/f_%04d.png` 全片抽帧。
2. **逐卡读帧**：布局按 px→manim 换算 ((x-960)/120, (540-y)/120)，标题/公式/图/计数器四件套定位；
   **数值反推**是点睛之笔：S=2.00 → ∫₁³ x/2 dx=2 → a=1,b=3；柱值 1.14/1.51/1.67 → f_k=1-e^{-kx},k=1,2,3；
   li(100)=29.1 → 用 Ei(ln x) 级数实现（γ+ln|x|+Σ x^k/(k·k!)，90 项足够）。
3. 转场段重点抽帧（fps=8 已够看中间态），确认旧图元素是形变还是淡出——**决定 morph 架构**。
4. 写码 → `compile()` 语法检查 → `-ql` 试渲染 → ffprobe 核时长 → 抽帧对比 → 修 → `-qh` 1080p60。
5. **judge 视觉验收**：成片按 fps=4 抽帧，连同原片参考帧一起交给评审 agent 逐卡对照，
   fail 项定位到帧修复后复核。注意采样帧可能恰好落在动画中间态——先看相邻帧再定性。
6. 成片 `cp media/videos/<scene>/1080p60/xxx.mp4 ~/Desktop/中文名.mp4`。

### 已验证的 Manim CE 0.21 坑位

| 坑 | 正确姿势 |
|----|---------|
| `interpolate_color("#A","#B",t)` 报 str | 包 `ManimColor("#A")` |
| `Axes(width=, height=)` 报错 | 用 `x_length=, y_length=` |
| `Dot(..., opacity=0.9)` 报错 | 构造后 `.set_opacity(0.9)` |
| `np.math.factorial` 已移除 | `import math; math.factorial` |
| 贪婪正则吞函数（`(?:.*?\n)*`） | 用非贪婪 `(?:.|\n)*?(?=下一个def)` |
| `always_redraw` 的 mob | play 后必须 `clear_updaters()` 冻结 |
| TransformMatchingTex | 禁 `\underbrace`；长公式跨卡形变 OK |

### 渲染注意

- **60fps 成片比 15fps 试渲染短约 1.4~1.5s**（每个 play 的帧数取整差异）：时序验收
  一律以最终 60fps 成片抽帧为准，稳定窗口在 15fps 版够≠60fps 版够。
- 帧像素↔manim：120px/单位（frame_width=16 时）。
- 中间产物 `media/` 缓存保留，改片增量渲染只重渲变化的 play。
