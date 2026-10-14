"""渲染引擎：绘图原语。

字体与配色都不再写死在这里：
  * 字体走 fonts.py —— 自动探测各平台的中文字体，
    并提供中英混排的终端绘制（纯等宽字体缺中文字形会渲染成方块）。
  * 配色走 theme.py —— 切换 "flat" / "handdrawn" 主题即可换风格，
    场景代码不需要改动。

为了兼容既有场景代码，这里仍然导出 BG / INK / ORANGE 这类模块级颜色名，
但它们的值取自当前主题。切换主题请调用 use_theme()。
"""
import re
import math
import functools
from PIL import Image, ImageDraw, ImageFont

from fonts import F, draw_mono, mono_advance, has_cjk
from theme import get_theme

W, H = 1920, 1080
FPS = 30

# 每场开场前 / 结束后的留白（秒）。渲染、合成、字幕共用。
LEAD = 0.30
TAIL = 0.70

# 页眉左侧的品牌标记（ASCII，走等宽字体）。由 scenes.setup() 从
# content.py 的 BRAND 写入；空串表示不显示品牌，只画章节名。
BRAND = ""

# ---------------------------------------------------------------- 主题绑定
# 场景代码里的颜色名 -> 主题里的键。改主题后这些名字自动换值。
_COLOR_MAP = {
    "BG": "paper", "BG_ALT": "paper_alt",
    "INK": "ink", "INK_SOFT": "ink_soft", "MUTED": "muted",
    "CARD": "card", "BORDER": "border", "BORDER_D": "border_d",
    "ORANGE": "accent", "ORANGE_D": "accent_d", "ORANGE_L": "accent_l",
    # 主题里没有单独的 TEAL，用 green 族承载这一组强调色
    "TEAL": "green", "TEAL_D": "ink_soft", "TEAL_L": "green_l",
    "TERMBG": "term_bg", "TERMBG2": "term_bg2",
    "TERMTXT": "term_txt", "TERMDIM": "term_dim",
    "GREEN": "green", "GREEN_L": "green_l",
    "BLUE": "blue", "BLUE_L": "blue_l",
    "PURPLE": "purple", "PURPLE_L": "purple_l",
    "AMBER": "amber", "AMBER_L": "amber_l",
    "RED": "red", "RED_L": "red_l",
}

T = None          # 当前主题，由 use_theme() 设定


def use_theme(name="flat"):
    """切换主题。会就地更新模块里的颜色名，场景代码无需改动。"""
    global T
    T = get_theme(name)
    g = globals()
    for const_name, key in _COLOR_MAP.items():
        g[const_name] = T[key]
    return T


def _default_theme():
    """默认 flat，但如果场景文件自己调了 use_theme 也兼容。"""
    if T is None:
        use_theme("flat")


def blend(c1, c2, a):
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * a)) for i in range(3))


def rgba(c, a):
    return (c[0], c[1], c[2], int(a * 255))


# ---------------------------------------------------------------- 字体
def font(size, weight="r", mono=False):
    """取字体。mono=True 返回等宽字体——注意它通常不含中文字形。

    返回的字体对象带两个标记属性（Pillow 的字体对象允许附加属性）：
      .vsize 字号   .vmono 是否等宽
    这两个标记让 measure() 和 para() 能自动判断该走混排还是普通绘制。
    """
    f = F.mono(size) if mono else F.sans(size, bold=(weight == "b"))
    f.vsize = size
    f.vmono = bool(mono)
    f.vbold = (weight == "b")
    return f


def draw_terminal_text(d, xy, text, size, fill, cjk_fill=None):
    """终端文字入口：中英分段混排，汉字不会渲染成方块。"""
    return draw_mono(d, xy, text, size, fill, cjk_fill)


def text_w(d, text, size, mono=False, bold=False):
    """混排安全的测宽。"""
    if mono:
        return mono_advance(d, text, size)
    return d.textlength(text, font=F.sans(size, bold))


_default_theme()


# ---------------------------------------------------------------- 缓动
def clamp01(x):
    return 0.0 if x < 0 else (1.0 if x > 1 else x)


def ease_out(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_out_soft(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 2


def ease_in_out(x):
    x = clamp01(x)
    return 4 * x * x * x if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_back(x):
    x = clamp01(x)
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def reveal(t, start, dur=0.5, fn=ease_out):
    """在 [start, start+dur] 区间内返回 0→1 的进度。"""
    if dur <= 0:
        return 1.0 if t >= start else 0.0
    return fn((t - start) / dur)


def lerp(a, b, x):
    return a + (b - a) * x


# ---------------------------------------------------------------- 文本
_TOKEN_RE = re.compile(r"[A-Za-z0-9_\-./:+=~@#$%^&*()\[\]{}<>|\\'\"?,!;]+|\s+|.", re.S)


def _tokens(s):
    return [m.group(0) for m in _TOKEN_RE.finditer(s)]


def _is_mono(f):
    return getattr(f, "vmono", False)


def measure(d, s, f):
    """测宽。等宽字体走中英混排测量，否则汉字宽度会算错。"""
    if _is_mono(f):
        return mono_advance(d, s, getattr(f, "vsize", f.size))
    return d.textlength(s, font=f)


def wrap(d, s, f, maxw):
    """按宽度折行，保留西文单词完整。"""
    out = []
    for para in s.split("\n"):
        if not para:
            out.append("")
            continue
        line = ""
        for tok in _tokens(para):
            if tok == "\n":
                continue
            cand = line + tok
            if measure(d, cand, f) <= maxw or not line.strip():
                line = cand
            else:
                out.append(line.rstrip())
                line = tok if not tok.isspace() else ""
        out.append(line.rstrip())
    return out


def para(d, x, y, s, f, fill, maxw=900, lh=None, align="left", anchor_top=True):
    """绘制多行文本，返回结束的 y 坐标。

    等宽字体自动走中英混排绘制。注意混排绘制不支持 anchor，
    所以等宽分支只做左对齐。
    """
    lines = wrap(d, s, f, maxw)
    if lh is None:
        lh = int(f.size * 1.5)
    mono = _is_mono(f)
    yy = y
    for ln in lines:
        if ln:
            if mono:
                size = getattr(f, "vsize", f.size)
                xx = x
                if align == "center":
                    xx = x - mono_advance(d, ln, size) / 2
                draw_mono(d, (xx, yy), ln, size, fill)
            elif align == "center":
                d.text((x, yy), ln, font=f, fill=fill, anchor="ma" if anchor_top else "mm")
            else:
                d.text((x, yy), ln, font=f, fill=fill, anchor="la" if anchor_top else "lm")
        yy += lh
    return yy


def para_h(d, s, f, maxw, lh=None):
    lines = wrap(d, s, f, maxw)
    if lh is None:
        lh = int(f.size * 1.5)
    return len(lines) * lh


# ---------------------------------------------------------------- 形状
def soft_shadow(d, box, r=20, base=None, alpha=0.13, spread=10, steps=5, dx=0, dy=8):
    """在纯色背景上模拟柔和投影（多层递减的实心圆角矩形，比 RGBA 合成快得多）。"""
    base = BG if base is None else base
    x0, y0, x1, y1 = box
    for i in range(steps, 0, -1):
        g = spread * i / steps
        a = alpha * (1 - (i - 1) / steps) * (1.0 / steps) * 3.2
        c = blend(base, (0, 0, 0), min(0.5, a))
        d.rounded_rectangle(
            [x0 - g + dx, y0 - g * 0.6 + dy, x1 + g + dx, y1 + g * 1.15 + dy],
            radius=r + g, fill=c,
        )


def card(img, box, r=None, fill=None, border=None, bw=None, base=None, shadow=None,
         seed=0):
    """主题感知的卡片。手绘主题画抖动的墨线框，扁平主题画圆角+投影。"""
    fill = CARD if fill is None else fill
    border = BORDER if border is None else border
    base = BG if base is None else base
    radius = (T["radius"] if T else 22) if r is None else r
    if shadow is None:
        shadow = T["shadow"] if T else True
    if bw is None:
        bw = 2 if (T is None or T["name"] == "flat") else T["line_w"]
    d = ImageDraw.Draw(img)
    if T is not None and T["name"] == "handdrawn":
        T.card(d, box, seed=seed, fill=fill, outline=border, width=bw, radius=radius)
    else:
        if shadow:
            soft_shadow(d, box, r=radius, base=base)
        d.rounded_rectangle(box, radius=radius, fill=fill, outline=border, width=bw)
    return d


def chip(d, x, y, label, f, fill=None, bg=None, padx=18, pady=9, r=None, border=None):
    fill = INK if fill is None else fill
    bg = BG_ALT if bg is None else bg
    r = (T["radius"] if T else 12) if r is None else r
    w = measure(d, label, f)
    asc, desc = f.getmetrics()
    hgt = asc + desc
    box = [x, y, x + w + padx * 2, y + hgt + pady * 2]
    d.rounded_rectangle(box, radius=r, fill=bg, outline=border, width=2 if border else 0)
    d.text((x + padx, y + pady), label, font=f, fill=fill)
    return box[2] - box[0], box[3] - box[1]


def arrow(d, p0, p1, color=None, w=5, head=20):
    color = INK if color is None else color
    d.line([p0, p1], fill=color, width=w)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    for s in (-1, 1):
        a = ang + s * math.radians(150)
        d.line([p1, (p1[0] + head * math.cos(a), p1[1] + head * math.sin(a))],
               fill=color, width=w)


def arrow_curved(d, p0, p1, color=None, w=5, bend=0.3):
    """二次贝塞尔箭头。"""
    color = INK if color is None else color
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    nx, ny = -(p1[1] - p0[1]), (p1[0] - p0[0])
    L = math.hypot(nx, ny) or 1
    cx, cy = mx + nx / L * L * bend, my + ny / L * L * bend
    pts = []
    for i in range(25):
        u = i / 24
        x = (1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * cx + u ** 2 * p1[0]
        y = (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * cy + u ** 2 * p1[1]
        pts.append((x, y))
    d.line(pts, fill=color, width=w, joint="curve")
    p_end, p_prev = pts[-1], pts[-4]
    ang = math.atan2(p_end[1] - p_prev[1], p_end[0] - p_prev[0])
    for s in (-1, 1):
        a = ang + s * math.radians(152)
        d.line([p_end, (p_end[0] + 22 * math.cos(a), p_end[1] + 22 * math.sin(a))],
               fill=color, width=w)


# ---------------------------------------------------------------- 终端
# 每场渲染前由 render.py 设定这三个值。
# 终端用「真实秒数」而不是场景的名义时间：这样它能独立地把命令演示
# 拉伸到铺满整段讲话，而不是跟着画面的名义时间轴早早就打完。
SCENE_NOMINAL_END = None
SCENE_REAL_T = None
SCENE_REAL_DUR = None
TERMINAL_FILL = 0.90   # 终端打字占本场时长的比例


def _script_nominal_end(script, t0, default_speed):
    """算出脚本里最后一行出现/打完的名义时刻。"""
    cur = t0
    for item in script:
        kind = item[0]
        if kind in ("gap", "pause"):
            cur += item[1]
            continue
        text = item[1]
        if kind == "cmd":
            sp = item[2] if len(item) > 2 else default_speed
            cur += len(text) / sp + 0.36
        elif kind == "cmd_wait":
            sp = item[2] if len(item) > 2 else default_speed
            cur += len(text) / sp + (item[3] if len(item) > 3 else 1.1)
        else:
            cur += 0.10
    return cur


class Terminal:
    """带打字动画的终端窗口。"""

    def __init__(self, box, fsize=27, title="终端", base=None, prompt="~ $"):
        base = BG if base is None else base
        self.x0, self.y0, self.x1, self.y1 = box
        self.fsize = fsize
        self.f = font(fsize, mono=True)
        self.title = title
        self.base = base
        self.prompt = prompt
        self.bar = 46
        self.pad = 26

    @property
    def lines_per_screen(self):
        return int((self.y1 - self.y0 - self.bar - self.pad * 2) / (self.fsize * 1.55))

    def draw(self, img, script, t, t0=0.6, speed=16.0, max_lines=None, autoscroll=True):
        """script: [('cmd', 'git init'), ('out', '...'), ('gap', 0.4), ('dim','...')]

        t 是场景的名义时间。若 render.py 提供了真实时长，则改用真实时间轴，
        让本场终端铺满讲话时间。
        """
        if SCENE_REAL_T is not None and SCENE_REAL_DUR:
            t = SCENE_REAL_T * TERMINAL_FILL
        d = ImageDraw.Draw(img)
        x0, y0, x1, y1 = self.x0, self.y0, self.x1, self.y1
        soft_shadow(d, [x0, y0, x1, y1], r=18, base=self.base, alpha=0.30, spread=16, dy=12)
        d.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=TERMBG, outline=(52, 47, 43), width=2)
        d.rounded_rectangle([x0, y0, x1, y0 + self.bar], radius=18, fill=TERMBG2)
        d.rectangle([x0, y0 + self.bar - 18, x1, y0 + self.bar], fill=TERMBG2)
        for i, col in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
            cx = x0 + 30 + i * 26
            d.ellipse([cx - 9, y0 + self.bar / 2 - 9, cx + 9, y0 + self.bar / 2 + 9], fill=col)
        # 标题可能含中文（"终端"），必须走混排，不能直接 d.text()
        tw = mono_advance(d, self.title, 21)
        draw_mono(d, ((x0 + x1) / 2 - tw / 2, y0 + self.bar / 2 - 12),
                  self.title, 21, TERMDIM)

        # 把整段脚本按比例拉伸，铺满本场可用时间
        target = None
        if SCENE_REAL_DUR:
            target = SCENE_REAL_DUR * TERMINAL_FILL
        elif SCENE_NOMINAL_END:
            target = SCENE_NOMINAL_END - 0.4
        stretch = 1.0
        if target:
            natural = _script_nominal_end(script, t0, speed)
            if natural > 0.5:
                stretch = max(1.0, target / natural)
        speed = speed / stretch
        if stretch > 1.001:
            scaled = []
            for item in script:
                if item[0] in ("gap", "pause"):
                    scaled.append((item[0], item[1] * stretch))
                elif item[0] == "cmd":
                    sp = item[2] if len(item) > 2 else speed
                    scaled.append(("cmd", item[1], sp / stretch))
                elif item[0] == "cmd_wait":
                    sp = item[2] if len(item) > 2 else speed
                    extra = (item[3] if len(item) > 3 else 1.1) * stretch
                    scaled.append(("cmd_wait", item[1], sp / stretch, extra))
                else:
                    scaled.append(item)
            script = scaled

        # 展开 script 为带绝对时间的行
        lh = self.fsize * 1.55
        rows = []           # (kind, text, t_start, t_end)
        cur = t0
        for item in script:
            kind = item[0]
            if kind == "gap":
                cur += item[1]
                continue
            if kind == "pause":
                cur += item[1]
                continue
            text = item[1]
            if kind == "cmd":
                sp = item[2] if len(item) > 2 else speed
                dur = len(text) / sp
                rows.append(("cmd", text, cur, cur + dur))
                cur += dur + 0.36
            elif kind == "cmd_wait":
                sp = item[2] if len(item) > 2 else speed
                dur = len(text) / sp
                rows.append(("cmd", text, cur, cur + dur))
                cur += dur + (item[3] if len(item) > 3 else 1.1)
            else:
                rows.append((kind, text, cur, cur + 0.01))
                cur += 0.10

        if max_lines is None:
            max_lines = self.lines_per_screen
        # 只保留已经出现的行；必要时滚动
        started = [r for r in rows if r[2] <= t]
        offset = max(0, len(started) - max_lines) if autoscroll else 0
        shown = rows[offset:offset + max_lines]

        y = y0 + self.bar + self.pad
        for kind, text, ts, te in shown:
            if ts > t:
                break
            if kind == "cmd":
                prog = clamp01((t - ts) / max(1e-6, te - ts))
                n = int(round(prog * len(text)))
                shown_txt = text[:n]
                # 终端文字一律走混排绘制：纯等宽字体不含中文字形，
                # 直接 d.text() 会把汉字画成空方块。
                draw_mono(d, (x0 + self.pad, y), self.prompt, self.fsize, (120, 200, 140))
                px = x0 + self.pad + mono_advance(d, self.prompt, self.fsize) + 12
                draw_mono(d, (px, y), shown_txt, self.fsize, TERMTXT)
                if te <= t < te + 0.55:
                    cx = px + mono_advance(d, shown_txt, self.fsize) + 4
                    d.rectangle([cx, y + 3, cx + self.fsize * 0.55, y + self.fsize * 1.22], fill=(210, 205, 196))
            else:
                col = {"dim": TERMDIM, "ok": (120, 210, 145), "warn": (240, 180, 90),
                       "err": (250, 120, 110), "key": (170, 200, 250)}.get(kind, TERMTXT)
                draw_mono(d, (x0 + self.pad, y), text, self.fsize, col)
            y += lh


# ---------------------------------------------------------------- 通用页眉页脚
def header(img, d, chapter, progress):
    """顶部：细进度条 + 章节标签。"""
    d.rectangle([0, 0, W, 5], fill=blend(BG, INK, 0.08))
    d.rectangle([0, 0, int(W * progress), 5], fill=ORANGE)
    if chapter:
        f = font(21, "b")
        fw = font(21)
        x = 56
        if BRAND:
            brand_font = font(21, "b", mono=True)
            d.text((x, 40), BRAND, font=brand_font, fill=ORANGE)
            x += measure(d, BRAND, brand_font) + 16
            d.text((x, 40), "·", font=fw, fill=BORDER_D)
            x += 20
        d.text((x, 40), chapter, font=f, fill=MUTED)


def title(img, d, main, sub=None, y=104, maxw=1500, color=None, size=62, fsize=28):
    color = INK if color is None else color
    f = font(size, "b")
    d.text((W // 2, y), main, font=f, fill=color, anchor="ma")
    yy = y + int(size * 1.42)
    if sub:
        fs = font(fsize)
        for ln in wrap(d, sub, fs, maxw):
            d.text((W // 2, yy), ln, font=fs, fill=MUTED, anchor="ma")
            yy += int(fsize * 1.5)
    return yy


def subtitle_band(img, d, text):
    f = font(40)
    lines = wrap(d, text, f, 1400)
    lh = 56
    band_h = len(lines) * lh + 34
    bx0, bx1 = W // 2 - 760, W // 2 + 760
    by0 = H - 38 - band_h
    d.rounded_rectangle([bx0, by0, bx1, by0 + band_h], radius=18, fill=(28, 26, 24))
    yy = by0 + 17
    for ln in lines:
        d.text((W // 2, yy + lh / 2 - 3), ln, font=f, fill=(248, 246, 242), anchor="mm")
        yy += lh
