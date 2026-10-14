# -*- coding: utf-8 -*-
"""生成视频封面。按平台选尺寸，配色跟随 content.py 里的主题。

封面在手机信息流里很小，唯一原则是：大字 + 高对比。
主文案每行不超过 6 字，最多 3 行；不要放整屏代码截图。
出完必须做缩略图测试——缩到 300px 宽主标题还认得出来才算过。
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFilter

from project import configure_source

configure_source()

import engine  # noqa: E402
from engine import font, measure, wrap, blend  # noqa: E402

try:
    import scenes  # noqa: E402
except ImportError:            # 没带项目文件时仍可用主题默认值出图
    scenes = None

# 各平台封面尺寸：B 站 16:10，YouTube/generic 16:9，抖音竖屏 9:16。
PLATFORM_SIZE = {
    "bilibili": (1146, 717),
    "youtube": (1280, 720),
    "douyin": (1080, 1920),
    "generic": (1280, 720),
}

CW, CH = PLATFORM_SIZE["bilibili"]

BG      = (246, 242, 234)
CARD    = (255, 255, 255)
INK     = (28, 26, 24)
INK2    = (74, 68, 62)
MUTED   = (140, 132, 121)
ORANGE  = (240, 81, 51)
ORANGE_D= (196, 54, 26)
TEAL    = (14, 110, 107)
GREEN   = (40, 150, 86)
BLUE    = (54, 106, 160)
PAPER   = (252, 251, 249)
TERMBG  = (32, 29, 27)


def use_platform(platform="bilibili", theme=None):
    """切换封面尺寸，并把颜色绑到当前主题（默认读 content.py 的 THEME）。"""
    global CW, CH, BG, CARD, INK, INK2, MUTED, ORANGE, ORANGE_D, TEAL, GREEN, BLUE, TERMBG
    CW, CH = PLATFORM_SIZE.get(platform, PLATFORM_SIZE["bilibili"])
    if theme is not None:
        engine.use_theme(theme)
    elif scenes is not None:
        scenes.setup()                  # 应用 content.py 的 THEME
    T = engine.T
    g = globals()
    BG = T["paper"]; CARD = T["card"]; INK = T["ink"]
    INK2 = T["ink_soft"]; MUTED = T["muted"]
    ORANGE = T["accent"]; ORANGE_D = T["accent_d"]
    TEAL = T["green"]; GREEN = T["green"]; BLUE = T["blue"]
    TERMBG = T["term_bg"]
    return CW, CH


def _hand():
    """当前是不是手绘主题。"""
    return engine.T is not None and engine.T["name"] == "handdrawn"


def _box(d, box, seed=0, fill=None, outline=None, width=3, radius=12):
    """主题感知的方框。手绘主题画墨线框，扁平主题画圆角矩形。"""
    if _hand():
        engine.T.hand_round_rect(d, box, seed=seed, fill=fill, outline=outline,
                                 width=width, radius=min(radius, 8))
    else:
        d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline,
                            width=width)


def _solid(d, box, fill, seed=0, radius=14):
    """实心色块。手绘主题下边线也跟着抖，避免出现完美的几何块。"""
    if _hand():
        engine.T.hand_round_rect(d, box, seed=seed, fill=fill, outline=None,
                                 width=0, radius=min(radius, 8))
    else:
        d.rounded_rectangle(box, radius=radius, fill=fill)


def canvas(bg=None):
    img = Image.new("RGB", (CW, CH), bg or BG)
    return img, ImageDraw.Draw(img)


def grid(d, step=34, col=(232, 226, 214), w=CW, h=CH):
    for x in range(0, w, step):
        for y in range(0, h, step):
            d.point((x, y), fill=col)


def soft_shadow(d, box, r=18, spread=14, alpha=0.20, steps=6, dy=10, base=None):
    base = BG if base is None else base
    x0, y0, x1, y1 = box
    for i in range(steps, 0, -1):
        g = spread * i / steps
        a = alpha * (1 - (i - 1) / steps) * 0.55
        d.rounded_rectangle([x0 - g, y0 - g * 0.5 + dy, x1 + g, y1 + g + dy],
                            radius=r + g, fill=blend(base, (0, 0, 0), min(0.35, a)))


# ============================================================ 方案 A：大字型
def cover_a(sub="零基础 · 从安装到提交 · 全程真机演示", accent=ORANGE, fname="cover_a.png"):
    img, d = canvas()
    grid(d)

    # 左侧主标题块
    x = 78
    # 小标签
    d.rounded_rectangle([x, 92, x + 236, 152], radius=14, fill=accent)
    d.text((x + 118, 122), "零基础入门", font=font(34, "b"),
           fill=(255, 255, 255), anchor="mm")

    # 超大 Git
    d.text((x - 6, 168), "Git", font=font(210, "b", mono=True), fill=INK)
    # 下划线强调
    d.rounded_rectangle([x + 4, 396, x + 430, 414], radius=9, fill=accent)

    d.text((x + 2, 436), "版本控制", font=font(96, "b"), fill=INK)
    # 手绘主题的底就是暖橙，accent 字会糊在背景里 —— 改用深墨
    d.text((x + 2, 552), "一次讲透", font=font(72, "b"),
           fill=(INK if _hand() else accent))

    d.text((x + 4, 654), sub, font=font(30), fill=(INK2 if _hand() else MUTED))

    # 右侧：终端小窗 + 分支图
    tx0, ty0, tx1, ty1 = 636, 132, 1074, 452
    if not _hand():
        soft_shadow(d, [tx0, ty0, tx1, ty1], r=18, base=BG)
    _solid(d, [tx0, ty0, tx1, ty1], TERMBG, seed=70, radius=18)
    d.rectangle([tx0, ty0 + 20, tx1, ty0 + 42], fill=(24, 22, 20))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        cx = tx0 + 26 + i * 23
        d.ellipse([cx - 7, ty0 + 21 - 7, cx + 7, ty0 + 21 + 7], fill=c)
    lines = [("~ $ git init", (150, 235, 165)),
             ("~ $ git add .", (232, 227, 218)),
             ("~ $ git commit -m", (232, 227, 218)),
             ('    "完成首页布局"', (240, 190, 110)),
             ("[main 3f2a1b9] 完成首页布局", (150, 235, 165))]
    yy = ty0 + 64
    for t, c in lines:
        # 混排绘制：等宽字体不含中文字形，直接 d.text() 会画成方块
        engine.draw_terminal_text(d, (tx0 + 26, yy), t, 23, c)
        yy += 48

    # 右下：三段流程小图
    # 按钮宽度按最长标签 "git commit" 定，否则文字会溢出框外。
    # 三格总宽（含箭头间隙）必须落在终端窗口 636..1074 之内。
    px, py = 636, 486
    steps = [("改文件", BLUE), ("git add", accent), ("git commit", GREEN)]
    # 布局：3 个按钮平分终端窗口宽度，只留出箭头间隙。
    # 宽度公式必须减掉按钮总宽，否则 3 个按钮会互相重叠。
    n_btn = len(steps)
    arrow_gap = 46                       # 每个箭头的横向空间
    span = 1074 - px
    bw = int((span - arrow_gap * (n_btn - 1)) / n_btn)
    cell_w = bw + arrow_gap
    for i, (s, c) in enumerate(steps):
        bx = px + i * cell_w
        _box(d, [bx, py, bx + bw, py + 92], seed=80 + i, fill=CARD,
             outline=c, width=4, radius=14)
        fbtn = font(22, "b", mono=True)
        # 标签太长就缩字号，避免文字溢出框
        while measure(d, s, fbtn) > bw - 18 and fbtn.size > 14:
            fbtn = font(fbtn.size - 1, "b", mono=True)
        tw = measure(d, s, fbtn)
        engine.draw_terminal_text(d, (bx + (bw - tw) / 2, py + 33), s, fbtn.size, c)
        if i < 2:
            ax, ax2 = bx + bw, bx + cell_w
            mid = (ax + ax2) / 2
            if _hand():
                engine.T.hand_arrow(d, (ax + 6, py + 46), (ax2 - 6, py + 46),
                                    seed=90 + i, color=MUTED, w=4, head=13)
            else:
                d.line([ax + 6, py + 46, ax2 - 10, py + 46], fill=MUTED, width=4)
                d.polygon([(ax2 - 6, py + 46), (ax2 - 16, py + 40), (ax2 - 16, py + 52)],
                          fill=MUTED)

    # 底部色带
    band = INK if _hand() else accent
    _solid(d, [636, 602, 1074, 668], band, seed=95, radius=14)
    d.text((855, 635), "12 分钟 · 小白也能听懂", font=font(30, "b"),
           fill=(250, 248, 244), anchor="mm")

    img.save(fname)
    return fname


# ============================================================ 方案 B：痛点型
def cover_b(accent=ORANGE, fname="cover_b.png"):
    img, d = canvas()
    grid(d)

    d.text((64, 74), "你还在建这种文件名吗？", font=font(58, "b"), fill=INK,
           anchor="la")

    # 一堆乱糟糟的文件名
    names = ["论文.docx", "论文最终版.docx", "论文最终版2.docx",
             "论文真正最终版.docx", "论文打死也不改.docx", "论文最终版(1).docx"]
    for i, n in enumerate(names):
        col, row = i % 3, i // 3
        x = 74 + col * 348 + (row * 18)
        y = 168 + row * 106
        crossed = i < len(names) - 1
        _box(d, [x, y, x + 322, y + 84], seed=100 + i, fill=CARD,
             outline=(INK if _hand() else (214, 205, 190)), width=3, radius=12)
        d.rectangle([x + 18, y + 22, x + 44, y + 62], fill=(224, 236, 248),
                    outline=BLUE, width=2)
        d.text((x + 60, y + 42), n, font=font(24, "b"), fill=INK2, anchor="lm")
        if crossed:
            if _hand():
                # 手绘风用涂改线，而不是一条笔直的删除线
                engine.T.scribble(d, (x + 58, y + 28, x + 292, y + 58),
                                  color=(226, 110, 100), seed=110 + i, w=5)
            else:
                d.line([x + 58, y + 44, x + 292, y + 44], fill=(226, 110, 100), width=5)

    # 大字口号
    if _hand():
        _solid(d, [74, 406, 1072, 552], INK, seed=120, radius=10)
    else:
        d.rounded_rectangle([74, 406, 1072, 552], radius=22, fill=INK)
    d.text((96, 436), "学会 Git，", font=font(64, "b"), fill=(250, 248, 244))
    d.text((96, 508), "再也不怕把文件改坏", font=font(58, "b"),
           fill=(accent if not _hand() else (240, 160, 120)))

    d.text((76, 592), "零基础入门 · 从安装到提交 · 全程真机演示",
           font=font(30), fill=(INK2 if _hand() else MUTED))
    _solid(d, [76, 640, 396, 700], (INK if _hand() else accent), seed=130, radius=14)
    d.text((236, 670), "12 分钟讲完", font=font(30, "b"),
           fill=(255, 255, 255), anchor="mm")

    img.save(fname)
    return fname


# ============================================================ 方案 C：三区模型
def cover_c(accent=ORANGE, fname="cover_c.png", show_notes=True):
    img, d = canvas()
    grid(d)

    # ---- 标题区
    d.text((CW // 2, 48), "Git 到底在干什么？", font=font(64, "b"),
           fill=INK, anchor="ma")
    d.text((CW // 2, 136), "一张图讲清最核心的三个区域", font=font(32),
           fill=MUTED, anchor="ma")

    # ---- 三张卡片
    areas = [("工作区", "改文件", BLUE),
             ("暂存区", "购物车", accent),
             ("仓库", "存档", GREEN)]
    cw, ch = 290, 212
    gap = 78
    x0, y = 60, 286
    centers = []
    for i, (name, sub, c) in enumerate(areas):
        x = x0 + i * (cw + gap)
        if not _hand():
            soft_shadow(d, [x, y, x + cw, y + ch], r=20, base=BG)
            _box(d, [x, y, x + cw, y + ch], seed=10 + i, fill=CARD,
                 outline=c, width=5, radius=20)
            _solid(d, [x, y, x + cw, y + 14], c, seed=20 + i, radius=7)
        else:
            _box(d, [x, y, x + cw, y + ch], seed=10 + i, fill=CARD,
                 outline=INK, width=6, radius=8)
            # 手绘风不用色条，改在卡片内侧画一道强调线（必须在框内，
            # 画在框上会在边界外露出彩色毛边）
            engine.T.hand_underline(d, x + 30, x + cw - 30, y + 26,
                                    seed=20 + i, color=c, w=6)
        d.text((x + cw / 2, y + 92), name, font=font(50, "b"), fill=INK, anchor="mm")
        d.text((x + cw / 2, y + 158), sub, font=font(29), fill=MUTED, anchor="mm")
        centers.append(x + cw)
        # 箭头
        if i < 2:
            ymid = y + ch / 2
            ax = x + cw + 10
            if _hand():
                engine.T.hand_arrow(d, (ax, ymid), (ax + 52, ymid),
                                    seed=30 + i, color=accent, w=6)
            else:
                d.line([ax, ymid, ax + 40, ymid], fill=accent, width=6)
                d.polygon([(ax + 58, ymid), (ax + 38, ymid - 13), (ax + 38, ymid + 13)],
                          fill=accent)

    # ---- 命令标签（放在卡片上方的空隙里，不压卡片也不压副标题）
    if show_notes:
        for i, lab in enumerate(["git add", "git commit"]):
            cx = centers[i] + gap / 2
            fm = font(25, "b", mono=True)
            w = measure(d, lab, fm) + 44
            _box(d, [cx - w / 2, 210, cx + w / 2, 262], seed=40 + i,
                 fill=CARD, outline=accent, width=3, radius=12)
            tw = measure(d, lab, fm)
            # 混排绘制：等宽字体不含中文字形
            engine.draw_terminal_text(d, (cx - tw / 2, 224), lab, 25, accent)

    # ---- 底部结论横幅
    if _hand():
        _box(d, [60, 528, 1086, 632], seed=50, fill=INK, outline=INK, width=0, radius=8)
    else:
        _solid(d, [60, 528, 1086, 632], INK, seed=50, radius=20)
    d.text((CW // 2, 580), "零基础也能听懂的 Git 入门课", font=font(44, "b"),
           fill=(250, 248, 244), anchor="mm")

    # ---- 页脚
    # 手绘主题的底是陶土色，灰字对比度不够，改用深墨色
    foot_col = INK if _hand() else MUTED
    d.text((62, 660), "12:45 · 全程真机演示 · 命令逐字敲给你看",
           font=font(29), fill=foot_col)
    # 手绘主题下 accent 底与背景同为暖橙，会糊在一起 —— 用深墨底
    badge_fill = INK if _hand() else accent
    _solid(d, [842, 646, 1086, 710], badge_fill, seed=60, radius=14)
    d.text((964, 678), "零基础", font=font(31, "b"), fill=(255, 255, 255), anchor="mm")

    img.save(fname)
    return fname


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/covers"
    os.makedirs(out, exist_ok=True)
    made = []
    made.append(cover_c(accent=ORANGE, fname=f"{out}/cover_c.png"))
    made.append(cover_c(accent=TEAL, fname=f"{out}/cover_c_teal.png"))
    for m in made:
        print("wrote", m)
