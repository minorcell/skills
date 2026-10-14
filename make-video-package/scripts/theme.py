# -*- coding: utf-8 -*-
"""主题层：把「画面风格」从绘制代码里抽出来，做成可切换的主题。

两种风格：
  flat       米白纸底 + 圆角卡片 + 投影。信息密度高，适合讲原理、
             讲流程、命令演示多的教程。
  handdrawn  Anthropic 编辑部手绘风：暖色平涂底 + 象牙色承载形状 +
             近黑手绘线。留白大、比喻强，适合讲概念、讲心智模型。

切主题：
    from theme import get_theme
    T = get_theme("handdrawn")
    T.paper, T.ink, T.accent
    T.card(...), T.wobble_line(...), T.hand_rect(...)

手绘的关键不在「看起来乱」，而在三条硬规则：
  1. 线要粗、端点要圆、走向要轻微不匀 —— 几何完美的手绘是假的。
  2. 平涂，不用渐变、不用投影、不用高光。
  3. 一帧只讲一个比喻，形状要有意不对称。
"""
import math
import random
import functools

# ---------------------------------------------------------------- flat 主题
FLAT = dict(
    name="flat",
    paper      = (246, 242, 234),   # 页面底色
    paper_alt  = (240, 235, 226),
    ink        = (34, 32, 30),      # 主文字
    ink_soft   = (80, 75, 68),
    muted      = (128, 121, 111),
    card       = (255, 255, 255),   # 卡片底
    border     = (227, 219, 205),
    border_d   = (206, 196, 178),
    accent     = (240, 81, 51),     # 橙红
    accent_d   = (203, 58, 30),
    accent_l   = (253, 231, 224),
    green      = (40, 150, 86),
    green_l    = (224, 242, 230),
    blue       = (54, 106, 160),
    blue_l     = (225, 236, 248),
    purple     = (122, 92, 165),
    purple_l   = (235, 229, 245),
    amber      = (206, 143, 34),
    amber_l    = (251, 239, 217),
    red        = (200, 60, 55),
    red_l      = (250, 228, 226),
    term_bg    = (32, 29, 27),      # 终端窗口
    term_bg2   = (24, 22, 20),
    term_txt   = (232, 227, 218),
    term_dim   = (140, 133, 124),
    # 形状参数
    radius     = 22,                # 卡片圆角
    shadow     = True,              # 是否投影
    line_w     = 5,                 # 描边宽度
    wobble     = 0.0,               # 手绘抖动幅度（0 = 不用）
)

# ---------------------------------------------------------------- 手绘主题
# 取自 Anthropic 编辑插画的可观测规则：暖色平涂底、象牙承载形状、
# 近黑手绘线，全程平涂无渐变。暖灰一律带黄褐底调，不用冷蓝灰。
HANDDRAWN = dict(
    name="handdrawn",
    paper      = (217, 119, 87),    # clay 陶土：整幅满铺的强调底
    paper_alt  = (188, 209, 202),   # cactus 仙人掌绿（章节交替用）
    ink        = (20, 20, 19),      # 近黑手绘线
    ink_soft   = (61, 61, 58),
    muted      = (94, 93, 89),
    card       = (250, 249, 245),   # ivory 象牙承载形状
    border     = (232, 230, 220),
    border_d   = (209, 207, 197),
    accent     = (201, 100, 66),    # terracotta 品牌陶土
    accent_d   = (160, 72, 44),
    accent_l   = (227, 218, 204),   # oat 燕麦
    green      = (60, 110, 90),     # 收敛的绿，避免荧光感
    green_l    = (188, 209, 202),
    blue       = (106, 155, 204),   # sky
    blue_l    = (203, 202, 219),    # heather
    purple     = (196, 102, 134),   # fig
    purple_l   = (203, 202, 219),
    amber      = (227, 218, 204),
    amber_l    = (240, 238, 230),
    red        = (181, 51, 51),
    red_l      = (227, 210, 205),
    # 手绘风里终端仍要深色，否则代码对比度不够
    term_bg    = (24, 22, 20),
    term_bg2   = (18, 17, 15),
    term_txt   = (240, 238, 226),
    term_dim   = (140, 133, 124),
    # 形状参数
    radius     = 6,                 # 手绘形状接近方正，只用很小的圆角
    shadow     = False,             # 手绘风禁用投影
    line_w     = 7,                 # 更粗的墨线
    wobble     = 2.6,               # 手绘抖动幅度（像素）
)

THEMES = {"flat": FLAT, "handdrawn": HANDDRAWN, "hand": HANDDRAWN}


class Theme(dict):
    """带绘制方法的主题字典。属性直接取色，方法负责画形状。"""

    # ------------------------------------------------------------ 手绘基底
    @property
    def wobble_amp(self):
        return self["wobble"]

    def _rng(self, salt):
        """按 salt 取确定性随机数 —— 同一帧多次绘制必须完全一致，
        否则视频会闪烁。"""
        return random.Random(hash(str(salt)) & 0xFFFFFFFF)

    def hand_path(self, p0, p1, salt=0, segments=None):
        """返回一条从 p0 到 p1 的轻微抖动折线点列。

        抖动是「沿法线的低频扰动」，不是逐点噪声 —— 逐点噪声看起来
        像信号干扰，低频扰动才像手绘。
        """
        amp = self["wobble"]
        if amp <= 0:
            return [p0, p1]
        rng = self._rng(salt)
        segs = segments or max(6, int(math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / 42))
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        # 两三个低频扰动叠加，端点略微外延（起笔收笔的溢出感）
        f1, f2 = rng.uniform(0.5, 1.4), rng.uniform(1.8, 3.2)
        ph1, ph2 = rng.uniform(0, 6.28), rng.uniform(0, 6.28)
        ext = amp * 1.1
        pts = []
        for i in range(segs + 1):
            u = i / segs
            w = math.sin(u * math.pi * f1 + ph1) * 0.62 + \
                math.sin(u * math.pi * f2 + ph2) * 0.38
            e = 0.0
            if i == 0 or i == segs:          # 端点外延，像手写起止
                e = ext * rng.uniform(0.5, 1.0)
            o = w * amp + (e if i == 0 else -e)
            pts.append((p0[0] + dx * u + nx * o, p0[1] + dy * u + ny * o))
        return pts

    def hand_rect(self, d, box, seed=0, outline=None, fill=None, width=None,
                  radius=None):
        """手绘方框：四条略微外凸的抖动边，角上留空隙。

        用四条独立线条而不是闭合多边形，交角处自然留缝，
        这正是手绘框看起来「松」的原因。
        """
        x0, y0, x1, y1 = [int(v) for v in box]
        col = outline or self["ink"]
        w = width if width is not None else self["line_w"]
        if fill is not None:
            d.rounded_rectangle([x0, y0, x1, y1],
                                radius=radius if radius is not None else self["radius"],
                                fill=fill)
        if w <= 0:
            return
        rng = self._rng(f"rect{seed}")
        # 每个角往内缩一点，制造手绘的「不过角」
        g = 3
        edges = [
            ((x0 + g, y0), (x1 - g, y0)),
            ((x1, y0 + g), (x1, y1 - g)),
            ((x1 - g, y1), (x0 + g, y1)),
            ((x0, y1 - g), (x0, y0 + g)),
        ]
        for i, (a, b) in enumerate(edges):
            pts = self.hand_path(a, b, salt=f"r{seed}{i}")
            d.line(pts, fill=col, width=w, joint="curve")
            # 补一个圆头端点，避免线端发尖
            for p in (pts[0], pts[-1]):
                d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=col)

    def hand_round_rect(self, d, box, seed=0, outline=None, fill=None, width=None,
                        radius=14):
        """带圆角的手绘框（卡片用）。圆角用短圆弧，边仍抖动。"""
        import math as _m
        x0, y0, x1, y1 = box
        col = outline or self["ink"]
        w = width if width is not None else self["line_w"]
        if fill is not None:
            d.rounded_rectangle(box, radius=radius, fill=fill)
        if w <= 0:
            return
        r = radius
        arcs = [
            # (圆心, 起始角, 结束角)
            ((x0 + r, y0 + r), _m.pi, _m.pi * 1.5),
            ((x1 - r, y0 + r), _m.pi * 1.5, _m.pi * 2),
            ((x1 - r, y1 - r), 0, _m.pi * 0.5),
            ((x0 + r, y1 - r), _m.pi * 0.5, _m.pi),
        ]
        straight = [
            ((x0 + r, y0), (x1 - r, y0)),
            ((x1, y0 + r), (x1, y1 - r)),
            ((x1 - r, y1), (x0 + r, y1)),
            ((x0, y1 - r), (x0, y0 + r)),
        ]
        for i, (a, b) in enumerate(straight):
            pts = self.hand_path(a, b, salt=f"rr{seed}{i}")
            d.line(pts, fill=col, width=w, joint="curve")
            for p in (pts[0], pts[-1]):
                d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=col)
        for i, (c, a0, a1) in enumerate(arcs):
            rng = self._rng(f"arc{seed}{i}")
            jitter = rng.uniform(-1.2, 1.2)
            pts = []
            n = 6
            for k in range(n + 1):
                ang = a0 + (a1 - a0) * k / n
                rr = r + jitter * _m.sin(k / n * _m.pi)
                pts.append((c[0] + rr * _m.cos(ang), c[1] + rr * _m.sin(ang)))
            d.line(pts, fill=col, width=w, joint="curve")

    def hand_blob(self, d, cx, cy, rx, ry, seed=0, fill=None, outline=None,
                  width=None, points=14):
        """一个手绘感的不规则椭圆 —— 手绘风里代替正圆的形状。"""
        rng = self._rng(f"blob{seed}")
        pts = []
        for i in range(points):
            a = 2 * math.pi * i / points
            j = 1 + rng.uniform(-0.07, 0.07)
            pts.append((cx + rx * j * math.cos(a), cy + ry * j * math.sin(a)))
        if fill is not None:
            d.polygon(pts, fill=fill)
        if outline is not None and (width or self["line_w"]) > 0:
            d.line(pts + [pts[0]], fill=outline,
                   width=width if width is not None else self["line_w"], joint="curve")

    def hand_arrow(self, d, p0, p1, seed=0, color=None, w=None, head=None):
        """手绘箭头：抖动杆 + 两笔不等的箭头。"""
        col = color or self["ink"]
        w = w if w is not None else self["line_w"]
        head = head or (w * 4)
        pts = self.hand_path(p0, p1, salt=f"arr{seed}")
        d.line(pts, fill=col, width=w, joint="curve")
        end = pts[-1]
        prev = pts[max(0, len(pts) - 3)]
        ang = math.atan2(end[1] - prev[1], end[0] - prev[0])
        rng = self._rng(f"arrh{seed}")
        for s in (-1, 1):
            # 两笔长度略有差别，这是手绘的常态
            ln = head * rng.uniform(0.82, 1.05)
            a = ang + s * math.radians(rng.uniform(144, 158))
            d.line([end, (end[0] + ln * math.cos(a), end[1] + ln * math.sin(a))],
                   fill=col, width=w)

    def hand_underline(self, d, x0, x1, y, seed=0, color=None, w=None):
        """手绘下划线：粗、略斜、带两次提速。强调标题用。"""
        col = color or self["accent"]
        w = w if w is not None else self["line_w"]
        drop = max(1, int(w * 0.7))
        pts = self.hand_path((x0, y), (x1, y + drop), salt=f"ul{seed}")
        d.line(pts, fill=col, width=w, joint="curve")

    def scribble(self, d, box, color=None, seed=0, loops=7, w=None):
        """涂改线：用来划掉「论文最终版2」这类内容。"""
        x0, y0, x1, y1 = box
        col = color or self["red"]
        w = w if w is not None else self["line_w"]
        cy = (y0 + y1) / 2
        pts = []
        n = loops * 6
        for i in range(n + 1):
            u = i / n
            x = x0 + (x1 - x0) * u
            y = cy + math.sin(u * math.pi * loops) * (y1 - y0) * 0.22
            pts.append((x, y))
        d.line(pts, fill=col, width=w, joint="curve")

    # ------------------------------------------------------------ 通用形状
    def card(self, d, box, seed=0, fill=None, outline=None, width=None,
             radius=None, shadow=None):
        """主题感知的卡片：flat 画圆角+投影，handdrawn 画手绘框。"""
        fill = fill if fill is not None else self["card"]
        outline = outline if outline is not None else self["border_d"]
        radius = radius if radius is not None else self["radius"]
        width = width if width is not None else (2 if self["name"] == "flat"
                                                 else self["line_w"])
        use_shadow = self["shadow"] if shadow is None else shadow
        x0, y0, x1, y1 = box
        if use_shadow:
            for i in range(5, 0, -1):
                g = 10 * i / 5
                a = 0.13 * (1 - (i - 1) / 5) * 0.2
                c = tuple(int(self["paper"][k] + (0 - self["paper"][k]) * min(0.5, a))
                          for k in range(3))
                d.rounded_rectangle([x0 - g, y0 - g * 0.6 + 8, x1 + g, y1 + g * 1.15 + 8],
                                    radius=radius + g, fill=c)
        if self["name"] == "flat":
            d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
        else:
            self.hand_round_rect(d, box, seed=seed, fill=fill, outline=outline,
                                 width=width, radius=radius)


@functools.lru_cache(maxsize=8)
def get_theme(name="flat"):
    key = (name or "flat").lower()
    if key not in THEMES:
        raise KeyError(f"未知主题 {name!r}；可选：{sorted(THEMES)}")
    return Theme(THEMES[key])


def list_themes():
    return ["flat", "handdrawn"]


if __name__ == "__main__":
    for n in list_themes():
        t = get_theme(n)
        print(f"{n:10s} paper={t['paper']} ink={t['ink']} accent={t['accent']} "
              f"radius={t['radius']} wobble={t['wobble']} shadow={t['shadow']}")
