# Skill: Manim 视频复刻还原（逐帧逆向实战定稿版）

> 实战背书：仅凭一段 26.6s 的成片视频 + 用户口头记忆（"转场主要用 Transform"），
> 完整逆向出 Manim CE 0.21 源代码（约 700 行），经用户 3 轮调整后相似度 ≈100%。
> 本文档是那次复刻的全流程经验定稿，供任何 AI / 人类拿一段目标视频按图索骥。
> 配套代码：`nine_worlds.py`（《我曾九次认识世界》，星空深蓝 + 9 张动态数学卡）。
> 姊妹文档：《Manim 混剪 skill 特制版（参考九次认识世界）.md》——那份讲"怎么从零做"，
> 这份讲"怎么从成片倒推回代码"。

---

## 0. 一句话方法论

**抽帧取证 → 结构反推 → 架构映射 → 渲染对照闭环 → 视觉验收。**
核心认知：Manim 视频的每一帧都是确定性的，画面上的一切（布局、颜色、数值、
动画时长、转场形态）都携带源代码信息——复刻就是做"逆向编译"，证据永远在帧里，
不在猜测里。

---

## 1. 情报采集（第一步就定精度）

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate,duration -of default=noprint_wrappers=1 视频.mp4
ffmpeg -loglevel error -i 视频.mp4 -vf fps=8 frames/f_%04d.png     # 全片抽帧
```

- 抽帧密度经验：**8 帧/秒是复刻甜点**——能看清形变转场的中间态（0.125s 步长），
  又不会帧数爆炸。26.6s ≈ 213 帧完全可承受。
- 验收阶段用 fps=4 抽成片即可；单帧诊断时对指定秒段再 `fps=15` 细抽。
- 帧号↔时间换算记牢：`fps=8` 时 `f_0043 ≈ (43-1)/8 = 5.25s`。

---

## 2. 逐帧分析（把画面读成规格书）

### 2.1 先建时间轴分段
按帧把视频切成：开场 / 卡1 / 转场1 / 卡2 / … / 收尾。每段记下起止帧号。
Manim 混剪的典型结构：固定壁纸层 + 开场大标题 + N 张卡（每卡 2~3s）+ 0.4~0.5s 转场 + 收尾淡出。

### 2.2 布局：像素坐标 → Manim 坐标
若源片是 16:9 且大概率用了 `frame_width=16`（主流设置），换算是线性的：

```
x_manim = (x_px - 960) / 120      y_manim = (540 - y_px) / 120
```

120 px/单位 = 1920 / 16。用这个把标题、公式、图、计数器的中心点全部换算成
`move_to([x, y, 0])`，布局一步到位，不用猜。

### 2.3 配色：直接从帧取色
标题九卡各一色（例：金 #E8B84B、蓝紫 #A8B8F0、青 #4DD0E1、橙 #F0A860、绿 #7FC98A、
粉 #F08BB8、紫 #B8A0E8…），坐标轴灰蓝 #5B7BA8，面积填充 = 金色 opacity≈0.45。
写成常量区，别在代码里散落魔法色值。

### 2.4 ★数值反推法（复刻"神似"的胜负手）
画面上出现的每个数字都是数学约束，用它反推源码参数：
- 面积计数停在 **S = 2.00**，曲线是直线 y=x/2 → 反推 `∫_a^b x/2 dx = 2` → **a=1, b=3** ✓
- 三根柱子 **1.14 / 1.51 / 1.67**、极限 2 → 反推 f_k = 1−e^{−kx} 在 [0,2] 的积分，**k=1,2,3** ✓
- **li(100) = 29.1** → 不是普通 li（那是 30.13），是主值/Ei 约定 → `li(x)=Ei(ln x)`，
  自己写级数：`γ + ln|x| + Σ x^k/(k·k!)`（90 项），曲线与 π(x)=25 对齐 ✓
- 计数器中途值不必较真（滚动数字），但**终值直接抄原片**（如 sin x₀=−0.899 / P₉(x₀)=−0.891）。

### 2.5 动画拆解：每卡列出"拍"清单
逐帧看每张卡内部，写出 `拍1: Create 轴+曲线 (0.5s) / 拍2: 面积扫描+计数 1.2s / 拍3: 箭头…`。
判断动画类型的手感：**路径从无到有 = Create/Write；整体淡入 = FadeIn(lag_ratio)；
数字滚动 = ChangeDecimalToValue；图形随时间变形 = ValueTracker + always_redraw。**

---

## 3. ★转场判定图谱（复刻成败的分水岭）

在转场中间帧（转场起点后 0.1~0.3s）找以下特征，一判一个准：

| 帧上看到 | 判定 | 源码 |
|---|---|---|
| 公式字形碎裂、拉伸旋转、新旧两式共存叠影 | `TransformMatchingTex` + **mismatches** | `TransformMatchingTex(old, new, transform_mismatches=True)`（不加参数则是"旧式淡出新式写入"，观感差一档） |
| 旧坐标轴被拉成水平亮线再立成新轴、旧曲线碎成波浪、面积边缘波纹化、旧文字碎片飞行 | **函数图像也在整组 ReplacementTransform** | `ReplacementTransform(VGroup(*旧extras), VGroup(*新extras))` |
| 旧元素整体透明度衰减、无位移无碎片 | 只是 FadeOut | `FadeOut` |
| 中文标题字形整族拉伸（字数不同也能变） | ReplacementTransform | 标题逐字 `Text` 整族形变 |

**血泪教训**：第一轮复刻时只对公式做了 transform，图像用了 FadeOut——用户二轮反馈
"图像也有 Transform"。回头再抽原片转场帧，证据一直在那里（轴的锯齿中间态）。
**规矩：第一轮就必须把每个转场的全部中间帧看完，不能只看卡片完成态。**

三路同拍结构（标题 + 公式 + 图像在同一个 `play` 里，run_time≈0.42s）是节奏连拍的关键。

---

## 4. 架构映射模板（Scene 骨架直接抄）

```python
class Remake(Scene):
    def construct(self):
        self.make_background()          # 壁纸层：最先 add，全程静止，绝不参与形变
        self.intro()                    # 开场（Write 大标题 → 淡出）
        for n in range(1, 10):
            getattr(self, f"card{n}")() # morph 进场 + 卡内动画
        self.outro()

    def cardN(self):                    # 每卡入口 = 转场 + 卡内动画
        self.morph_to(*self.cardN_parts())
        self.cardN_anim()

    def cardN_parts(self):              # ★必须返回新卡"底图"（轴/圆/点阵/首曲线）
        ...                              #   否则 morph 没有图像可承接形变
        return title, formula, [底图...]

    def cardN_anim(self):
        ...                              # 底图之上的生长动画（卡内从 self.cur_extras 取底图）
```

**morph 核心**（三路同拍 + 图像整组形变）：

```python
def morph_to(self, new_title, new_formula, new_extras, run_time=0.42):
    anims = [ReplacementTransform(self.cur_title, new_title),
             TransformMatchingTex(self.cur_formula, new_formula,
                                  transform_mismatches=True)]
    if self.cur_extras and new_extras:
        src_g = VGroup(*self.cur_extras)
        self.remove(*self.cur_extras)          # ★包装组顶替进 scene（见 §5）
        self.add(src_g)
        anims.append(ReplacementTransform(src_g, VGroup(*new_extras)))
    ...
    self.play(*anims, run_time=run_time)
```

---

## 5. 场景管理铁律（本次最贵的坑）

1. **track_extra 模式**：卡内产生的每个顶层 mob 用 `self.track_extra(*mobs)` **逐个**登记。
   严禁 `cur_extras[-1].add(...)` 往"不在 scene 的幽灵组"里塞——FadeOut / ReplacementTransform
   结束只移除传入的顶层对象，塞进去的子 mob 会**永久残留**在后面所有画面里。
2. **updater 即用即清**：`always_redraw` / 计数器 updater 在 play 结束立刻 `clear_updaters()`，
   否则下一卡形变时它们会"复活"。
3. **别遍历 scene 找对象**：morph 之后 scene 的分组结构变了，要拿底图直接 `self.cur_extras[0]`。
4. 壁纸层单独持有引用（`self.bg`），outro 淡出时跳过它。
5. 每卡尾部留 `wait(0.5~0.6)` 稳定展示窗口——这是验收硬指标，元素"闪过"等于没做。

---

## 6. 渲染-对照迭代闭环

```bash
python3 -c "compile(open('xxx.py').read(),'xxx.py','exec')"   # 语法检查先行
~/venvs/manim/bin/manim xxx.py SceneName -ql                  # 试渲染（快）
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 输出.mp4
ffmpeg -i 输出.mp4 -vf fps=8 chk/t_%03d.png                    # 成片抽帧
# 与原片同秒帧并排对照：布局 → 配色 → 数值 → 转场中间态
~/venvs/manim/bin/manim xxx.py SceneName -qh                  # 定稿 1080p60
```

- **Manim 按内容哈希缓存 partial movie file**：改一拍只重渲一拍，迭代很快，别加
  `--disable_caching`。
- **帧率陷阱（重要）**：60fps 成片比 15fps 试渲染**短约 1.4~1.5s**（每个 play 的帧数
  取整差异累计）。所有"稳定窗口是否足够"的判断必须以**最终 60fps 成片**抽帧为准，
  15fps 版合格 ≠ 60fps 版合格（本次卡 6/卡 8 就这样漏过验收，二轮才抓到）。

---

## 7. 视觉验收（AI 复刻的必要工序）

- 成片 fps=4 抽帧 + 原片参考帧，交给独立评审 agent（judge）逐卡对照，输出
  `{"card":..., "verdict":"pass|fail", "issues":[...]}`。
- **采样帧陷阱**：评审引用的帧可能恰好落在动画中间态（形变碎裂 ≠ 缺陷）。
  收到 fail 先抽相邻帧确认"稳定态是否存在"，再决定是修 bug 还是修时序。
  本次 4 个 fail 中 3 个实为"稳定窗口过短"而非元素缺失。
- 修复优先级：残留异物 > 要素缺失 > 稳定窗口 > 字形微瑕。

---

## 8. Manim CE 0.21 坑位速查（全部实测踩过）

| 坑 | 正确姿势 |
|---|---|
| `interpolate_color("#A","#B",t)` 报 str 无 interpolate | 包一层 `ManimColor("#A")` |
| `Axes(width=, height=)` TypeError | 用 `x_length=, y_length=` |
| `Dot(..., opacity=0.9)` TypeError | 构造后 `.set_opacity(0.9)` |
| `np.math.factorial` 已移除 | `import math; math.factorial` |
| `TransformMatchingTex` + `\underbrace` | IndexError，公式卡禁用 |
| 文字里放 ∫ ∑ 等数学符号 | 截半，数学符号一律 MathTex；希腊字母 Δθπω 可留在 Text |
| `(?:.*?\n)*` 贪婪回溯吞掉整个函数 | 非贪婪 `(?:.|\n)*?(?=下一个def)` |
| `interpolate_color` 等在 0.21 的行为变化 | 先小脚本冒烟，别整片渲染后才发现 |

---

## 9. 与用户的协作节奏

- **改前先取证**：用户说"转场主要用 Transform"→ 抽帧证实；用户说"图像也有 Transform"
  → 再抽帧找到证据再动手。画面证据 > 记忆，但用户的记忆是最佳的搜索指引。
- **严格限定 diff**：用户说"其他地方千万不用动"，就只动指定模块（本次只改
  `morph_to` + 各卡 parts），布局/时长/文案一概不碰。
- **文件所有权**：用户指定"桌面那份 py 不要动 / 覆盖它"，逐字执行，别自作主张同步。
- 每轮改动后：渲染 → 抽帧自查 → 更新交付物 → 用一句话说清"动了什么、没动什么"。

---

## 10. 新视频复刻检查单（开干前过一遍）

- [ ] ffprobe 拿到时长/分辨率/帧率
- [ ] fps=8 全片抽帧，建时间轴分段表
- [ ] 每卡四件套定位（标题/公式/图/计数器），px→manim 换算
- [ ] 配色常量表 + 数值反推（画面数字→数学参数）
- [ ] 每个转场的中间帧已逐帧看完，判定三路形变结构
- [ ] 骨架：parts（含底图）/ anim / morph_to / track_extra
- [ ] 语法检查 → -ql → 对照 → 修 → -qh
- [ ] 60fps 成片抽帧 + judge 逐卡验收 + 相邻帧核实 fail 项
- [ ] 交付：成片 + 源码放用户指定位置
