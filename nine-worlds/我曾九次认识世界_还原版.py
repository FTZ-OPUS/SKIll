# -*- coding: utf-8 -*-
"""
《我曾九次认识世界》—— 九大数学名场面公式混剪（Manim 还原版）
结构：星空壁纸层(全程静止) + 开场大标题 + 9 张动态卡片 + 收尾淡出
转场灵魂：TransformMatchingTex(transform_mismatches=True) 三路同拍形变
"""
from manim import *
import numpy as np
import math

config.pixel_width  = 1920
config.pixel_height = 1080
config.frame_width  = 16.0
config.frame_height = 9.0

# ---------------- 调色板（逐帧比对取色） ----------------
GOLD   = "#E8B84B"   # 金
LILAC  = "#A8B8F0"   # 卡2 标题蓝紫
CYAN2  = "#4DD0E1"   # 卡3 青
BLUE2  = "#6FA8F0"   # 卡4 蓝
LAV    = "#B8A8E8"   # 卡5 淡紫
ORNG   = "#F0A860"   # 卡6 橙
MINT   = "#7FC98A"   # 卡7 绿
PINK2  = "#F08BB8"   # 卡8 粉
PURP2  = "#B8A0E8"   # 卡9 紫
ROSE   = "#E88BB0"   # sinθ 粉
VIOB   = "#8B9BE8"   # 事件B 蓝紫
GREE2  = "#6FCF8F"   # 事件A∩B 亮绿
AXCOL  = "#5B7BA8"   # 坐标轴
STEPY  = "#E8D48B"   # π(x) 阶梯黄
B1     = "#7C8CE8"   # 频谱柱1
B2     = "#A99BE8"   # 频谱柱2
B3     = "#E89BB8"   # 频谱柱3

TITLE_POS = UP * 3.55
FORM_POS  = UP * 2.15
KAI = "Kaiti SC"

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
          53, 59, 61, 67, 71, 73, 79, 83, 89, 97]


# ---------------- 数学工具 ----------------
def _Ei(x):
    """Ei(x) 级数（x 可为 ndarray），用于 li(x)=Ei(ln x)"""
    x = np.asarray(x, dtype=float)
    s = np.zeros_like(x)
    term = np.ones_like(x)
    for k in range(1, 90):
        term = term * x / k
        s += term / k
    return 0.5772156649015329 + np.log(np.abs(x)) + s


def li_fn(x):
    return _Ei(np.log(np.asarray(x, dtype=float)))


def taylor_sin(n, x):
    x = np.asarray(x, dtype=float)
    s = np.zeros_like(x)
    for k in range(n // 2 + 1):
        s = s + (-1) ** k * x ** (2 * k + 1) / float(math.factorial(2 * k + 1))
    return s


def counter(text_str, init, places=2, color=GOLD, tsize=30, nsize=34, font=KAI):
    """Text 前缀 + DecimalNumber 计数器组合"""
    num = DecimalNumber(init, num_decimal_places=places,
                        font_size=nsize, color=color)
    grp = VGroup(Text(text_str, font=font, font_size=tsize, color=WHITE), num)
    grp.arrange(RIGHT, buff=0.10)
    return grp, num


def mk_title(s, color, font_size=58):
    t = Text(s, font=KAI, weight="BOLD", font_size=font_size, color=color)
    t.set_stroke(color=WHITE, width=1.2, opacity=0.9)
    halo = (t.copy()
            .set_stroke(color=color, width=11, opacity=0.20)
            .set_fill(opacity=0))
    return VGroup(halo, t).move_to(TITLE_POS)


def star_cross(size=0.16, opacity=0.9):
    return VGroup(
        Line(UP, DOWN).set_length(2 * size),
        Line(LEFT, RIGHT).set_length(2 * size),
    ).set_stroke(WHITE, 1.2, opacity)


# ---------------- 场景 ----------------
class NineWorlds(Scene):
    def construct(self):
        self.make_background()
        self.intro()
        self.card1()
        self.card2()
        self.card3()
        self.card4()
        self.card5()
        self.card6()
        self.card7()
        self.card8()
        self.card9()
        self.outro()

    # ============ 壁纸层：星空 + 同心圆 + 轨道 + 幽灵符号 ============
    def make_background(self):
        rnd = np.random.default_rng(20260913)
        bg = VGroup()
        bg.add(Rectangle(width=16.6, height=9.6).set_stroke(width=0)
               .set_fill("#04070F", 1))
        for i in range(14):                      # 径向渐变（叠环近似）
            r = 0.55 + i * 0.60
            col = interpolate_color(ManimColor("#2A3F6E"), ManimColor("#04070F"), i / 13)
            bg.add(Circle(radius=r).set_stroke(width=0).set_fill(col, 0.155))
        for r in (0.85, 1.55, 2.35, 3.3, 4.4, 5.65):   # 同心圆细线
            bg.add(Circle(radius=r).set_stroke("#31456E", 1.1, 0.42)
                   .set_fill(opacity=0))
        bg.add(Dot(ORIGIN, radius=0.045, color=GOLD).set_opacity(0.9))
        bg.add(Circle(radius=0.10).set_stroke(GOLD, 1.0, 0.5)
               .set_fill(opacity=0).move_to(ORIGIN))
        # 两条椭圆轨道 + 行星点
        for (rx, ry, rot, op, pts) in ((7.6, 2.05, -0.055, 0.75, (0.20, 0.55, 0.86)),
                                       (8.7, 3.15, -0.035, 0.5, (0.08, 0.60, 0.97))):
            orb = (Circle(radius=1).stretch(rx, 0).stretch(ry, 1).rotate(rot)
                   .set_stroke("#5C4E2E", 1.4, op).set_fill(opacity=0))
            bg.add(orb)
            for t in pts:
                p = orb.point_from_proportion(t)
                bg.add(Dot(p, radius=0.05, color=GOLD).set_opacity(0.95))
                bg.add(Circle(radius=0.105).set_stroke(GOLD, 1, 0.45)
                       .set_fill(opacity=0).move_to(p))
        # 十字星（固定布局仿原片）+ 随机小星
        for (x, y, s) in ((-5.9, 3.35, 0.15), (-5.55, 0.9, 0.13), (-5.95, -2.6, 0.12),
                          (-6.45, -3.0, 0.14), (2.05, -3.6, 0.12), (2.3, -4.05, 0.11),
                          (6.6, -2.2, 0.13), (6.0, -3.4, 0.12), (4.25, -2.5, 0.10),
                          (-2.6, 4.1, 0.10), (7.4, 2.9, 0.11)):
            bg.add(star_cross(s).move_to([x, y, 0]),
                   Dot([x, y, 0], radius=0.022, color=WHITE).set_opacity(0.95))
        for _ in range(22):
            bg.add(Dot([rnd.uniform(-7.9, 7.9), rnd.uniform(-4.35, 4.35), 0],
                       radius=rnd.uniform(0.015, 0.032), color=WHITE
                       ).set_opacity(rnd.uniform(0.3, 0.8)))
        for _ in range(9):
            bg.add(Dot([rnd.uniform(-7.9, 7.9), rnd.uniform(-4.3, 4.3), 0],
                       radius=0.028, color=GOLD).set_opacity(0.8))
        # 幽灵数学符号
        ghosts = [
            (r"\partial", -5.75, 1.05, 1.0, 42), (r"\sigma", -1.6, 0.5, 0.85, 40),
            (r"\pi", 1.55, 0.62, 0.85, 44), (r"\theta", -1.25, -0.85, 0.9, 46),
            (r"\mu", -1.95, -1.75, 0.95, 54), (r"\hbar", -1.2, -2.7, 0.9, 46),
            (r"\alpha", -0.65, -3.35, 0.95, 42), (r"\pm", 0.55, -3.65, 0.95, 40),
            (r"\nabla", 2.25, -3.62, 0.95, 42), (r"\times", 4.6, -3.2, 0.85, 38),
            (r"\infty", 0.7, 2.95, 0.95, 46), (r"\lambda", -0.62, 3.1, 0.95, 46),
            (r"\Delta", -3.65, 2.6, 1.0, 56), (r"\Delta", -2.25, 2.78, 0.9, 48),
            (r"\Sigma", 1.95, 1.7, 1.55, 74), (r"\sigma", -5.4, -0.35, 0.75, 36),
        ]
        for tex, x, y, sc, fs in ghosts:
            m = MathTex(tex, font_size=fs).set_color("#7A90C0").set_opacity(0.13)
            m.scale(sc).rotate(rnd.uniform(-0.12, 0.12)).move_to([x, y, 0])
            bg.add(m)
        bg.add(MathTex("e", font_size=40, color=WHITE).set_opacity(0.55)
               .move_to([-5.02, 0.38, 0]))
        self.bg = bg
        self.add(bg)

    # ============ 转场工具 ============
    def set_cur(self, title, formula, extras):
        self.cur_title, self.cur_formula, self.cur_extras = title, formula, list(extras)

    def track_extra(self, *mobs):
        """把卡内产生的顶层 mob 登记进转场清理列表"""
        self.cur_extras.extend([m for m in mobs if m is not None])

    def morph_to(self, new_title, new_formula, new_extras, run_time=0.42):
        """三路同拍形变：标题整族 ReplacementTransform + 公式碎片形变
        + 函数图像整组 ReplacementTransform（旧图丝滑形变为新图，对齐原片）"""
        anims = [
            ReplacementTransform(self.cur_title, new_title),
            TransformMatchingTex(self.cur_formula, new_formula,
                                 transform_mismatches=True),
        ]
        if self.cur_extras and new_extras:
            src_g = VGroup(*self.cur_extras)
            self.remove(*self.cur_extras)   # 包装组顶替进 scene，保证替换干净
            self.add(src_g)
            anims.append(ReplacementTransform(src_g, VGroup(*new_extras)))
        elif self.cur_extras:
            src_g = VGroup(*self.cur_extras)
            self.remove(*self.cur_extras)
            self.add(src_g)
            anims.append(FadeOut(src_g))
        elif new_extras:
            anims.append(FadeIn(VGroup(*new_extras), lag_ratio=0.08))
        self.play(*anims, run_time=run_time)
        self.set_cur(new_title, new_formula,
                     list(new_extras) if new_extras else [VGroup()])

    def clear_extras(self):
        if self.cur_extras:
            self.play(*[FadeOut(e) for e in self.cur_extras], run_time=0.4)
            self.cur_extras = []

    # ============ 开场 ============
    def intro(self):
        t = Text("我曾九次认识世界", font=KAI, weight="BOLD", font_size=74,
                 color=GOLD).set_stroke(WHITE, 1.5, 0.9)
        halo = (t.copy().set_stroke(GOLD, 12, 0.18).set_fill(opacity=0))
        big = VGroup(halo, t).move_to(ORIGIN)
        self.play(Write(big), run_time=1.15)
        self.wait(0.3)
        self.play(FadeOut(big), run_time=0.25)
        self.cur_title = big          # 占位（card1 内会被替换）
        self.cur_formula = MathTex("x")              # 占位
        self.cur_extras = []
        self.remove(self.cur_title, self.cur_formula)

    # ============ 卡1 微积分基本定理 ============
    def card1(self):
        title = mk_title("微积分基本定理", GOLD)
        formula = MathTex(
            r"\int_a^b f'(x)\,dx \;=\; f(b) - f(a)", font_size=58,
            tex_to_color_map={r"f'(x)": GOLD, r"f(b)": GOLD, r"f(a)": GOLD},
        ).move_to(FORM_POS)
        axL = Axes(x_range=[0, 4.3, 1], y_range=[0, 2.6, 1], x_length=6.7, y_length=2.75,
                   axis_config={"stroke_color": AXCOL, "stroke_width": 2.5,
                                "include_ticks": True, "tick_size": 0.06,
                                "include_tip": False}
                   ).move_to([-4.15, -1.35, 0])
        axR = Axes(x_range=[0, 4.3, 1], y_range=[0, 2.6, 1], x_length=6.7, y_length=2.75,
                   axis_config={"stroke_color": AXCOL, "stroke_width": 2.5,
                                "include_ticks": True, "tick_size": 0.06,
                                "include_tip": False}
                   ).move_to([4.3, -1.35, 0])
        gL = axL.plot(lambda t: t / 2, x_range=[0.15, 3.85], color=GOLD, stroke_width=5)
        gR = axR.plot(lambda t: t * t / 4, x_range=[0.2, 3.85], color=GOLD, stroke_width=5)
        a, b = 1.0, 3.0
        dash = VGroup()
        for ax in (axL, axR):
            for x in (a, b):
                dash.add(DashedLine(ax.c2p(x, -0.02), ax.c2p(x, 2.42),
                                    dash_length=0.09, stroke_width=2.2,
                                    color="#9FB4D8"))
        lab1 = MathTex(r"f'(x)=\dfrac{x}{2}", font_size=42, color=GOLD).move_to([-5.45, -0.05, 0])
        lab2 = MathTex(r"f(x)=\dfrac{x^2}{4}", font_size=42, color=GOLD).move_to([2.6, -0.4, 0])

        grpS, numS = counter("面积 S =", 0.00, color=GOLD)
        grpD, numD = counter("净变化 Δf =", 0.00, color=GOLD)
        grpS.move_to([-4.35, -3.32, 0]); grpD.move_to([3.95, -3.32, 0])
        eeq = MathTex(r"\Longleftrightarrow", font_size=52).move_to([0, -1.35, 0])
        sumf = MathTex(r"\int_a^b f'\,dx \;=\; f(b)-f(a)", font_size=38,
                       tex_to_color_map={r"f(b)-f(a)": GOLD}).move_to([0.15, -3.32, 0])

        self.play(Write(title), Create(axL), Create(axR),
                  Create(gL), Create(gR), run_time=0.5)
        self.set_cur(title, formula, [VGroup(axL, axR, gL, gR, dash, lab1, lab2)])
        self.play(Write(formula), Create(dash), FadeIn(lab1), FadeIn(lab2),
                  run_time=0.42)

        tr = ValueTracker(a)
        area = always_redraw(lambda: axL.get_area(
            gL, x_range=[a, max(tr.get_value(), a + 1e-4)],
            color=GOLD, opacity=0.42))
        pL = always_redraw(lambda: Dot(axL.c2p(tr.get_value(), tr.get_value() / 2),
                                       radius=0.06, color=WHITE))
        pR = always_redraw(lambda: Dot(axR.c2p(tr.get_value(), tr.get_value() ** 2 / 4),
                                       radius=0.06, color=WHITE))
        self.add(area, pL, pR)
        self.play(FadeIn(grpS), FadeIn(grpD), run_time=0.2)
        self.play(tr.animate.set_value(b),
                  ChangeDecimalToValue(numS, 2.00),
                  ChangeDecimalToValue(numD, 2.00), run_time=1.1)
        for m in (area, pL, pR):
            m.clear_updaters()
        arrow = Arrow(axR.c2p(3.3, 1.05), axR.c2p(3.3, 2.45), buff=0,
                      color=GOLD, stroke_width=5)
        self.play(GrowArrow(arrow), run_time=0.25)
        self.play(FadeIn(eeq), FadeIn(sumf), run_time=0.25)
        self.track_extra(area, pL, pR, arrow, grpS, grpD, eeq, sumf)
        self.wait(0.45)



    def card2(self):
        self.morph_to(*self.card2_parts())
        self.card2_anim()

    def card3(self):
        self.morph_to(*self.card3_parts())
        self.card3_anim()

    def card4(self):
        self.morph_to(*self.card4_parts())
        self.card4_anim()

    def card5(self):
        self.morph_to(*self.card5_parts())
        self.card5_anim()

    def card6(self):
        self.morph_to(*self.card6_parts())
        self.card6_anim()

    def card7(self):
        self.morph_to(*self.card7_parts())
        self.card7_anim()

    def card8(self):
        self.morph_to(*self.card8_parts())
        self.card8_anim()

    def card9(self):
        self.morph_to(*self.card9_parts())
        self.card9_anim()

    def card2_parts(self):
        title = mk_title("泰勒展开", LILAC)
        formula = MathTex(
            r"f(x)=\sum_{n=0}^{\infty}\frac{f^{(n)}(a)}{n!}(x-a)^n",
            font_size=54, color=WHITE).move_to(FORM_POS)
        ax = Axes(x_range=[-4.3, 4.3, 1], y_range=[-1.6, 1.6, 1],
                  x_length=13.6, y_length=3.15,
                  axis_config={"stroke_color": AXCOL, "stroke_width": 2.2,
                               "include_ticks": True, "tick_size": 0.06,
                               "include_tip": False}).move_to([0, -1.55, 0])
        sinc = DashedVMobject(
            ax.plot(np.sin, x_range=[-4.25, 4.25], stroke_width=3), num_dashes=70
        ).set_stroke(WHITE, 3, opacity=0.9)
        return title, formula, [VGroup(ax, sinc)]

    def card2_anim(self):
        grp2 = self.cur_extras[0]
        ax = [s for s in grp2 if isinstance(s, Axes)][0]
        colp = "#93A8F0"
        polys = [
            r"P_1(x)=x",
            r"P_3(x)=x-\dfrac{x^3}{6}",
            r"P_5(x)=x-\dfrac{x^3}{6}+\dfrac{x^5}{120}",
            r"P_7(x)=x-\dfrac{x^3}{6}+\dfrac{x^5}{120}-\dfrac{x^7}{5040}",
            r"P_9(x)=x-\dfrac{x^3}{6}+\dfrac{x^5}{120}-\dfrac{x^7}{5040}+\dfrac{x^9}{362880}",
        ]
        ns = [1, 3, 5, 7, 9]
        curves = [ax.plot(lambda t, nn=n: taylor_sin(nn, np.array([t]))[0],
                          x_range=[-4.1, 4.1], color=colp, stroke_width=4.5)
                  for n in ns]
        poly_mobs = [MathTex(p, font_size=38, color=colp).move_to([-2.55, -3.32, 0])
                     for p in polys]
        nlab = [MathTex(rf"n = {n}", font_size=40, color=colp).move_to([-4.5, 0.78, 0])
                for n in ns]
        sinlab = MathTex(r"\sin x", font_size=42).move_to([5.65, 0.78, 0])

        self.play(FadeIn(curves[0]), Write(nlab[0]), Write(poly_mobs[0]),
                  FadeIn(sinlab), run_time=0.35)
        self.track_extra(curves[0], nlab[0], poly_mobs[0], sinlab)
        for i in range(1, 5):
            self.play(ReplacementTransform(curves[i - 1], curves[i]),
                      ReplacementTransform(nlab[i - 1], nlab[i]),
                      TransformMatchingTex(poly_mobs[i - 1], poly_mobs[i],
                                           transform_mismatches=True),
                      run_time=0.27)
        self.track_extra(curves[-1], nlab[-1], poly_mobs[-1])

        # x₀ 扫描对比
        grp1, num1 = counter(r"", 0.00, color=GOLD)
        s1 = MathTex(r"\sin x_0 =", font_size=36).move_to([1.7, -3.32, 0])
        num1.next_to(s1, RIGHT, buff=0.1)
        g1 = VGroup(s1, num1)
        s2 = MathTex(r"\;,\;\;\; P_9(x_0) =", font_size=36, color=colp).move_to([4.35, -3.32, 0])
        num2 = DecimalNumber(0.00, num_decimal_places=3, font_size=32, color=WHITE)
        num2.next_to(s2, RIGHT, buff=0.08)
        g2 = VGroup(s2, num2)
        x0line = DashedLine(ax.c2p(1.2, -1.5), ax.c2p(1.2, 1.5),
                            dash_length=0.09, stroke_width=2.4, color=GOLD)
        self.play(FadeIn(g1), FadeIn(g2), Create(x0line), run_time=0.3)
        self.play(x0line.animate.move_to(ax.c2p(4.26, 0)),
                  ChangeDecimalToValue(num1, -0.899),
                  ChangeDecimalToValue(num2, -0.891), run_time=0.5)
        self.track_extra(x0line, g1, g2)
        self.wait(0.5)

    # ============ 卡3 欧拉公式 ============
    def card3_parts(self):
        title = mk_title("欧拉公式", CYAN2)
        formula = MathTex(
            r"e^{i\theta} \;=\; \cos\theta + i\sin\theta", font_size=58,
            tex_to_color_map={r"\cos\theta": CYAN2, r"i\sin\theta": CYAN2},
        ).move_to(FORM_POS)
        circ = (Circle(radius=1.32, color="#8FA8C8", stroke_width=2.5)
                .move_to([-4.65, -1.35, 0]))
        ax = Axes(x_range=[0, 6.6, 1], y_range=[-1.1, 1.1, 1],
                  x_length=9.3, y_length=2.4,
                  axis_config={"stroke_color": AXCOL, "stroke_width": 2.2,
                               "include_ticks": True, "tick_size": 0.06,
                               "include_tip": False}).move_to([3.0, -1.35, 0])
        return title, formula, [VGroup(circ, ax)]

    def card3_anim(self):
        circ, ax = self.cur_extras[0]
        c0 = circ.get_center()
        th = ValueTracker(0.01)
        rad = always_redraw(lambda: Line(c0, c0 + 1.32 * np.array(
            [np.cos(th.get_value()), np.sin(th.get_value()), 0]),
            stroke_width=4.5, color=CYAN2))
        knob = always_redraw(lambda: Dot(c0 + 1.32 * np.array(
            [np.cos(th.get_value()), np.sin(th.get_value()), 0]),
            radius=0.09, color=CYAN2))
        arc = always_redraw(lambda: Arc(radius=0.45, start_angle=0,
                                        angle=max(th.get_value(), 0.01),
                                        color=GOLD, stroke_width=3
                                        ).set_stroke(opacity=float(
                                            0.9 - 0.65 * min(th.get_value() / TAU, 1)))
                                   .move_to(c0))
        cc = always_redraw(lambda: ParametricFunction(
            lambda t: ax.c2p(t, np.cos(t)), t_range=[0.01, max(th.get_value(), 0.02)],
            color=CYAN2, stroke_width=4))
        ss = always_redraw(lambda: ParametricFunction(
            lambda t: ax.c2p(t, np.sin(t)), t_range=[0.01, max(th.get_value(), 0.02)],
            color=ROSE, stroke_width=4))
        kth, numth = counter("θ =", 0.00, places=2, color=GOLD)
        kcs, numcs = counter("cosθ =", 1.00, places=2, color=CYAN2)
        ksn, numsin = counter("sinθ =", 0.00, places=2, color=ROSE)
        kc = VGroup(kth, kcs, ksn).arrange(RIGHT, buff=0.55).move_to([-3.4, -3.35, 0])
        labc = MathTex(r"\cos\theta", font_size=40, color=CYAN2).move_to([7.1, 0.35, 0])
        labs = MathTex(r"\sin\theta", font_size=40, color=ROSE).move_to([5.75, -2.35, 0])
        self.add(rad, knob, arc, cc, ss)
        self.play(FadeIn(kc), FadeIn(labc), FadeIn(labs), run_time=0.25)
        self.play(th.animate.set_value(2 * np.pi),
                  ChangeDecimalToValue(numth, 6.28),
                  ChangeDecimalToValue(numcs, 1.00),
                  ChangeDecimalToValue(numsin, 0.00), run_time=1.45)
        for m in (rad, knob, arc, cc, ss):
            m.clear_updaters()
        self.track_extra(rad, knob, arc, cc, ss, kc, labc, labs)
        self.wait(0.55)

    # ============ 卡4 傅里叶变换 ============
    def card4_parts(self):
        title = mk_title("傅里叶变换", BLUE2)
        formula = MathTex(
            r"F(\omega)=\int_{-\infty}^{+\infty} f(x)\,e^{-i\omega x}\,dx",
            font_size=54, color=WHITE).move_to(FORM_POS)

        def wave(fn, base, amp, color, sw=3.5):
            return ParametricFunction(
                lambda t: np.array([-5.05 + 1.0 * t, base + amp * fn(t), 0]),
                t_range=[-2.3, 2.3], color=color, stroke_width=sw)

        mix = wave(lambda t: 0.55 * np.sin(2 * t) + 0.30 * np.sin(4.3 * t + 1)
                   + 0.20 * np.sin(7.1 * t + 2), -1.45, 1.0, "#9FB0E8", 4)
        return title, formula, [mix]

    def card4_anim(self):
        def wave(fn, base, amp, color, sw=3.5):
            return ParametricFunction(
                lambda t: np.array([-5.05 + 1.0 * t, base + amp * fn(t), 0]),
                t_range=[-2.3, 2.3], color=color, stroke_width=sw)

        mix = self.cur_extras[0]
        w1 = wave(np.sin, -1.0, 0.5, "#8B9DE8")
        w2 = wave(lambda t: 0.72 * np.sin(4.3 * t), -1.95, 0.36, "#A88BE8")
        w3 = wave(lambda t: 0.5 * np.sin(7.1 * t), -2.8, 0.25, "#E88BB0")
        l1 = MathTex(r"\omega_1 = 2.0", font_size=34).move_to([-2.4, -1.0, 0])
        l2 = MathTex(r"\omega_2 = 4.3", font_size=34).move_to([-2.4, -1.95, 0])
        l3 = MathTex(r"\omega_3 = 7.1", font_size=34).move_to([-2.4, -2.8, 0])
        tdom = Text("时域", font=KAI, font_size=34, color=BLUE2).move_to([-4.55, 0.8, 0])
        flab = VGroup(MathTex(r"|F(\omega)|", font_size=36),
                      Text("(幅值)", font=KAI, font_size=26)).arrange(RIGHT, buff=0.12)
        flab.move_to([4.6, 0.25, 0])
        arr = Arrow([-0.8, -1.35, 0], [1.3, -1.35, 0], buff=0,
                    stroke_width=4).set_opacity(0.85)
        vax = Line([1.5, -1.05, 0], [1.5, -2.85, 0], color=AXCOL, stroke_width=2.2)
        hax = Line([1.4, -2.85, 0], [7.55, -2.85, 0], color=AXCOL, stroke_width=2.2)
        wl = Text("ω (频率)", font=KAI, font_size=28).move_to([5.7, -3.35, 0])
        bars, nums = VGroup(), VGroup()
        for (wx, v, c) in ((2.0, 0.62, B1), (4.3, 0.34, B2), (7.1, 0.17, B3)):
            x = 1.5 + wx * 0.75
            bar = (Rectangle(width=0.34, height=v * 2.0)
                   .set_stroke(c, 1.5, 0.9).set_fill(c, 0.85)
                   .move_to([x, -2.85 + v, 0]))
            bars.add(bar)
            nums.add(DecimalNumber(v, num_decimal_places=2, font_size=30,
                                   color=WHITE).move_to([x, -2.85 + v * 2.0 + 0.28, 0]))
        self.play(FadeOut(mix), FadeIn(w1), FadeIn(w2), FadeIn(w3),
                  FadeIn(l1), FadeIn(l2), FadeIn(l3), run_time=0.38)
        self.play(FadeIn(tdom), FadeIn(flab), FadeIn(arr),
                  FadeIn(vax), FadeIn(hax), FadeIn(wl), run_time=0.3)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars],
                              lag_ratio=0.2), run_time=0.55)
        self.play(FadeIn(nums, lag_ratio=0.15), run_time=0.3)
        self.track_extra(w1, w2, w3, l1, l2, l3, tdom, flab, arr,
                         vax, hax, wl, bars, nums)
        self.wait(0.6)

    # ============ 卡5 高斯散度定理 ============
    def card5_parts(self):
        title = mk_title("高斯散度定理", LAV)
        formula = MathTex(
            r"\oint_{\partial\Omega} \mathbf{F}\cdot d\mathbf{S} \;=\;"
            r" \iiint_{\Omega} \nabla\cdot\mathbf{F}\;dV", font_size=52,
            tex_to_color_map={r"\nabla\cdot\mathbf{F}\;dV": LAV},
        ).move_to(FORM_POS)
        circ = (Circle(radius=1.78, color=LAV, stroke_width=3.5)
                .move_to([-4.35, -1.4, 0]).set_fill(opacity=0))
        return title, formula, [circ]

    def card5_anim(self):
        circ = self.cur_extras[0]
        c0 = circ.get_center()
        R = 1.78
        angs = [i * 30 + 10 for i in range(12)]
        dirs = [np.array([np.cos(np.radians(a)), np.sin(np.radians(a)), 0]) for a in angs]
        ins = VGroup(*[Arrow(c0 + 0.32 * R * u, c0 + 0.72 * R * u, buff=0,
                             stroke_width=2.6, color=LAV,
                             max_tip_length_to_length_ratio=0.4) for u in dirs])
        outs = VGroup(*[Arrow(c0 + 1.03 * R * u, c0 + 1.52 * R * u, buff=0,
                              stroke_width=3, color=LAV,
                              max_tip_length_to_length_ratio=0.35) for u in dirs])
        r1 = VGroup(Text("取", font=KAI, font_size=30),
                    MathTex(r"\mathbf{F} = (x,\; y)", font_size=40)
                    ).arrange(RIGHT, buff=0.15)
        r2 = MathTex(r"\nabla\cdot\mathbf{F} \;=\; 2 \;>\; 0", font_size=42, color=LAV)
        r3 = MathTex(r"\oint \mathbf{F}\cdot d\mathbf{S} \;=\; 2\pi R^2 \;\approx\; 13.2",
                     font_size=40, color=GOLD)
        r4 = Text("边界通量处处等强流出", font=KAI, font_size=30)
        rhs = VGroup(r1, r2, r3, r4).arrange(DOWN, buff=0.42).move_to([4.5, -1.45, 0])
        self.play(LaggedStart(*[GrowArrow(ar) for ar in ins], lag_ratio=0.06),
                  run_time=0.42)
        self.play(LaggedStart(*[GrowArrow(ar) for ar in outs], lag_ratio=0.06),
                  run_time=0.5)
        self.play(FadeIn(rhs, lag_ratio=0.15), run_time=0.7)
        self.track_extra(circ, ins, outs, rhs)
        self.wait(0.5)

    # ============ 卡6 留数定理 ============
    def card6_parts(self):
        title = mk_title("留数定理", ORNG)
        formula = MathTex(
            r"\oint_{\gamma} f(z)\,dz \;=\; 2\pi i \sum_{k} \mathrm{Res}(f, z_k)",
            font_size=52,
            tex_to_color_map={r"\mathrm{Res}(f, z_k)": GOLD},
        ).move_to(FORM_POS)
        c0 = np.array([-4.6, -1.4, 0])
        circ = (Circle(radius=1.52, color=ORNG, stroke_width=4).move_to(c0)
                .set_fill(opacity=0))
        xx = VGroup(
            Line(ORIGIN + 0.16 * UL, ORIGIN + 0.16 * DR),
            Line(ORIGIN + 0.16 * DL, ORIGIN + 0.16 * UR),
        ).set_stroke(ROSE, 6).move_to(c0)
        z0 = MathTex(r"z = 0", font_size=34).move_to(c0 + [0, -0.72, 0])
        knob = Dot(circ.point_from_proportion(0.12), radius=0.09, color=GOLD)
        return title, formula, [circ, xx, z0, knob]

    def card6_anim(self):
        circ, xx, z0, knob = self.cur_extras[:4]
        c0 = circ.get_center()
        l1 = MathTex(r"f(z) = \dfrac{e^z}{z^2},\qquad |z| = 1", font_size=42)
        l2 = MathTex(r"\dfrac{e^z}{z^2} = \dfrac{1}{z^2} + \dfrac{1}{z}"
                     r" + \dfrac{1}{2} + \dfrac{z}{6} + \cdots", font_size=38)
        l3 = MathTex(r"\mathrm{Res}_{z=0} f = \Big[\dfrac{1}{z}\Big] = 1",
                     font_size=38, color=GOLD)
        l4 = MathTex(r"\oint_{|z|=1} f\,dz = 2\pi i \times 1 = 2\pi i",
                     font_size=38, color=GOLD)
        rhs = VGroup(l1, l2, l3, l4).arrange(DOWN, buff=0.32).move_to([3.5, -0.7, 0])
        bot = Text("洛朗展开中 1/z 项的系数即留数", font=KAI, font_size=30)
        bot.move_to([2.85, -3.18, 0])
        self.play(Rotate(knob, TAU, about_point=c0), run_time=0.6)
        self.play(FadeIn(rhs, lag_ratio=0.18), FadeIn(bot), run_time=0.85)
        self.track_extra(circ, xx, z0, knob, rhs, bot)
        self.wait(0.6)

    # ============ 卡7 贝叶斯公式 ============
    def card7_parts(self):
        title = mk_title("贝叶斯公式", MINT)
        formula = MathTex(
            r"P(A\mid B) \;=\; \frac{P(B\mid A)\,P(A)}{P(B)}", font_size=62,
            tex_to_color_map={r"P(B)": MINT, r"P(B\mid A)": MINT},
        ).move_to([0.1, 2.3, 0])
        rnd = np.random.default_rng(9)
        dots = VGroup()
        for r in range(5):
            for c in range(20):
                dots.add(Dot([-7.15 + c * 0.325, -1.05 - r * 0.44, 0],
                             radius=0.045, color="#5A6478").set_opacity(0.9))
        cap = Text("100 人总体（每个点 = 1 人）", font=KAI, font_size=30)
        cap.move_to([-4.5, -0.55, 0])
        return title, formula, [dots, cap]

    def card7_anim(self):
        rnd = np.random.default_rng(9)
        dots, cap = self.cur_extras[:2]
        param = MathTex(r"P(A)=0.10,\;\; P(B\mid A)=0.90,\;\; P(B)=0.45",
                        font_size=36).move_to([3.55, 0.9, 0])
        idx_blue = set(rnd.choice(100, 45, replace=False).tolist())
        idx_green = set(rnd.choice(sorted(idx_blue), 9, replace=False).tolist())
        dblue = [dots[i] for i in sorted(idx_blue)]
        dgreen = [dots[i] for i in sorted(idx_green)]
        self.play(LaggedStart(*[d.animate.set_color(VIOB) for d in dblue],
                              lag_ratio=0.015), run_time=0.55)
        self.play(LaggedStart(*[d.animate.set_color(GREE2).set_z_index(3) for d in dgreen],
                              lag_ratio=0.05), run_time=0.4)
        leg = VGroup(
            Text("蓝色 = 事件 B（45 人）", font=KAI, font_size=28, color=VIOB),
            Text("亮绿 = 其中事件 A（9 人）", font=KAI, font_size=28, color=GREE2),
        ).arrange(RIGHT, buff=0.5).move_to([-2.7, -3.5, 0])
        calc = MathTex(
            r"P(A\mid B)=\frac{P(B\mid A)P(A)}{P(B)}"
            r"=\frac{0.90\times 0.10}{0.45}=0.20", font_size=34,
            tex_to_color_map={r"0.20": MINT}).move_to([3.95, 0.05, 0])
        bar1 = (Rectangle(width=0.78, height=0.32).set_stroke(width=0)
                .set_fill("#8A94A8", 0.85).move_to([4.2, -0.95, 0]))
        n1 = Text("0.10", font=KAI, font_size=26).next_to(bar1, RIGHT, buff=0.18)
        bar2 = (Rectangle(width=1.72, height=0.32).set_stroke(width=0)
                .set_fill(MINT, 0.9).move_to([4.68, -1.68, 0]))
        n2 = Text("0.20", font=KAI, font_size=26).next_to(bar2, RIGHT, buff=0.18)
        self.play(FadeIn(leg), FadeIn(param), run_time=0.3)
        self.play(FadeIn(calc), run_time=0.3)
        self.play(GrowFromEdge(bar1, LEFT), FadeIn(n1), run_time=0.25)
        self.play(GrowFromEdge(bar2, LEFT), FadeIn(n2), run_time=0.3)
        self.track_extra(dots, cap, leg, param, calc, bar1, n1, bar2, n2)
        self.wait(0.5)

    # ============ 卡8 对数积分函数 ============
    def card8_parts(self):
        title = mk_title("对数积分函数", PINK2)
        formula = MathTex(
            r"\mathrm{li}(x) \;=\; \int_0^{x} \frac{dt}{\ln t}", font_size=54,
            tex_to_color_map={r"\int_0^{x}": PINK2, r"\frac{dt}{\ln t}": PINK2},
        ).move_to(FORM_POS)
        ax = Axes(x_range=[0, 100, 10], y_range=[0, 32, 8],
                  x_length=9.7, y_length=2.75,
                  axis_config={"stroke_color": AXCOL, "stroke_width": 2.2,
                               "include_ticks": True, "tick_size": 0.06,
                               "include_tip": False}).move_to([-0.05, -1.55, 0])
        return title, formula, [ax]

    def card8_anim(self):
        ax = self.cur_extras[0]
        xs = np.linspace(1.45, 100, 380)
        li_pts = [ax.c2p(x, li_fn(x)) for x in xs]
        lic = VMobject().set_points_as_corners(li_pts).set_stroke(PINK2, 4.5)
        lilab = MathTex(r"\mathrm{li}(x)", font_size=40, color=PINK2).move_to([2.3, -0.35, 0])
        pilab = MathTex(r"\pi(x)", font_size=36, color=STEPY).move_to([2.6, -1.35, 0])
        gpi, npi = counter("π(x) =", 0, places=0, color=GOLD, nsize=30)
        gli, nli = counter("li(x) =", 0.0, places=1, color=PINK2, nsize=30)
        gg = VGroup(gpi, gli).arrange(DOWN, buff=0.25).move_to([6.15, 0.55, 0])
        vline = DashedLine(ax.c2p(100, -0.02), ax.c2p(100, 31),
                           dash_length=0.09, stroke_width=2.2, color="#9FB4D8")
        bot = Text("素数定理：π(x) 与 li(x) 高度贴合", font=KAI, font_size=30)
        bot.move_to([0.05, -3.5, 0])
        pdots = VGroup(*[Dot(ax.c2p(p, 0), radius=0.04, color=GOLD).set_opacity(0.95)
                         for p in PRIMES])

        self.play(Create(lic), FadeIn(lilab), run_time=0.35)
        self.track_extra(ax, lic, lilab)
        scan = ValueTracker(0.0)

        def pi_count():
            return float(np.searchsorted(PRIMES, scan.get_value() + 1e-9))

        def step_upto():
            xv = max(scan.get_value(), 1.5)
            pts = [ax.c2p(0, 0)]
            done = True
            for i, p in enumerate(PRIMES):
                if p <= xv:
                    pts += [ax.c2p(p, i), ax.c2p(p, i + 1)]
                else:
                    pts += [ax.c2p(xv, i)]
                    done = False
                    break
            if done:
                pts.append(ax.c2p(xv, 25))
            m = VMobject().set_points_as_corners(pts).set_stroke(STEPY, 3.5)
            return m

        stepd = always_redraw(step_upto)
        lined = always_redraw(lambda: DashedLine(
            ax.c2p(max(scan.get_value(), 1.5), -0.02),
            ax.c2p(max(scan.get_value(), 1.5), 31),
            dash_length=0.09, stroke_width=2.2, color="#9FB4D8"))
        npi.add_updater(lambda m: (m.set_value(pi_count())))
        nli.add_updater(lambda m: (m.set_value(min(li_fn(max(scan.get_value(), 1.6)), 29.1))))
        self.add(stepd, lined)
        self.play(FadeIn(pdots, lag_ratio=0.03), FadeIn(gg), FadeIn(pilab),
                  run_time=0.35)
        self.play(scan.animate.set_value(100), run_time=0.9)
        for m in (stepd, lined):
            m.clear_updaters()
        npi.clear_updaters(); nli.clear_updaters()
        self.play(FadeIn(vline), FadeIn(bot), run_time=0.3)
        self.track_extra(stepd, lined, pdots, gg, pilab, vline, bot)
        self.wait(0.6)

    # ============ 卡9 勒贝格单调收敛定理 ============
    def card9_parts(self):
        title = mk_title("勒贝格单调收敛定理", PURP2)
        formula = MathTex(
            r"0\le f_1\le f_2\le\cdots\;\Rightarrow\;"
            r"\int \lim_{n\to\infty} f_n\,d\mu \;=\; \lim_{n\to\infty}\int f_n\,d\mu",
            font_size=44,
            tex_to_color_map={
                r"\int \lim_{n\to\infty} f_n\,d\mu": PURP2,
                r"\lim_{n\to\infty}\int f_n\,d\mu": PURP2,
            }).move_to(FORM_POS)
        formula.scale_to_fit_width(14.6)
        ax = Axes(x_range=[0, 2.05, 1], y_range=[0, 1.12, 1],
                  x_length=7.9, y_length=3.0,
                  axis_config={"stroke_color": AXCOL, "stroke_width": 2.2,
                               "include_ticks": True, "tick_size": 0.06,
                               "include_tip": False}).move_to([-4.25, -1.45, 0])
        fh = DashedLine(ax.c2p(0, 1), ax.c2p(2.02, 1), dash_length=0.09,
                        stroke_width=2.2, color=WHITE)
        fhlab = MathTex(r"f\equiv 1", font_size=36).next_to(fh, UP, buff=0.12)
        fhlab.move_to([ax.c2p(0.32, 1.12)[0], ax.c2p(0, 1.1)[1] + 0.12, 0])
        goldf = MathTex(r"\int \lim_{n\to\infty} f_n\,d\mu \;=\;"
                        r" \lim_{n\to\infty}\int f_n\,d\mu",
                        font_size=38, color=GOLD).move_to([4.35, -0.15, 0])
        return title, formula, [ax, fh, fhlab, goldf]

    def card9_anim(self):
        ax, fh, fhlab, goldf = self.cur_extras[:4]

        def fk(k):
            return ax.plot(lambda t: 1 - np.exp(-k * t), x_range=[0, 2],
                           color=PURP2, stroke_width=4.5)

        def ak(k):
            return ax.get_area(fk(k), x_range=[0, 2], color=PURP2, opacity=0.32)

        limrow = VGroup(Text("极限", font=KAI, font_size=30),
                        MathTex(r"\lim\int f_n = 2", font_size=38, color=GOLD)
                        ).arrange(RIGHT, buff=0.18).move_to([4.35, -1.05, 0])
        limline = Line([2.6, -1.5, 0], [6.1, -1.5, 0]).set_stroke(WHITE, 2)
        bars, flabs, nums = VGroup(), VGroup(), VGroup()
        vals = [1.135, 1.509, 1.667]
        for i, v in enumerate(vals):
            x = 3.0 + i * 1.3
            h = v * 0.9
            bars.add(Rectangle(width=0.7, height=h).set_stroke(LAV, 2.5)
                     .set_fill(LAV, 0.3).move_to([x, -3.05 + h / 2, 0]))
            flabs.add(MathTex(rf"\int f_{i+1}", font_size=33, color=PURP2)
                      .move_to([x, -3.28, 0]))
            nums.add(DecimalNumber(0.00, num_decimal_places=2, font_size=26)
                     .move_to([x, -3.85, 0]))
        f1lab = MathTex(r"f_1", font_size=34, color=PURP2).move_to(ax.c2p(1.12, 0.74))
        f3lab = MathTex(r"f_3", font_size=34, color=PURP2).move_to(ax.c2p(1.0, 1.06))

        self.track_extra(ax, fh, fhlab, goldf)
        c1, a1 = fk(1), ak(1)
        self.play(Create(c1), FadeIn(a1), FadeIn(f1lab),
                  FadeIn(limrow), Create(limline), run_time=0.4)
        self.play(LaggedStart(GrowFromEdge(bars[0], DOWN), FadeIn(nums[0]),
                              lag_ratio=0.3), run_time=0.32)
        self.play(ChangeDecimalToValue(nums[0], 1.14), run_time=0.2)
        c2, a2 = fk(2), ak(2)
        self.play(Create(c2), FadeIn(a2),
                  c1.animate.set_stroke(opacity=0.45), a1.animate.set_opacity(0.12),
                  LaggedStart(GrowFromEdge(bars[1], DOWN), FadeIn(nums[1]),
                              lag_ratio=0.3), run_time=0.38)
        self.play(ChangeDecimalToValue(nums[1], 1.51), run_time=0.2)
        c3, a3 = fk(3), ak(3)
        self.play(Create(c3), FadeIn(a3), FadeIn(f3lab),
                  c2.animate.set_stroke(opacity=0.45), a2.animate.set_opacity(0.12),
                  LaggedStart(GrowFromEdge(bars[2], DOWN), FadeIn(nums[2]),
                              lag_ratio=0.3), run_time=0.38)
        self.play(ChangeDecimalToValue(nums[2], 1.67), run_time=0.2)
        self.track_extra(c1, a1, c2, a2, c3, a3, f1lab, f3lab, limrow, limline,
                         bars, flabs, nums)
        self.wait(0.6)

    # ============ 收尾 ============
    def outro(self):
        mobs = [m for m in list(self.mobjects) if m is not self.bg]
        self.play(*[FadeOut(m) for m in mobs], run_time=0.45)
        self.wait(0.1)
