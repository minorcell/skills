# -*- coding: utf-8 -*-
"""每个分镜的具体画面绘制。所有 draw_* 接收 (img, t, dur, prog)。

颜色从 engine 导入。注意 `from engine import BG` 会在导入的瞬间把值绑死，
所以主题必须在**导入本模块之前**由管线调好（render.py / covers.py 会做）。
"""
import math
from PIL import Image, ImageDraw, ImageFont

import engine
from engine import (
    W, H, BG, BG_ALT, INK, INK_SOFT, MUTED, CARD, BORDER, BORDER_D,
    ORANGE, ORANGE_D, ORANGE_L, TEAL, TEAL_D, TEAL_L, GREEN, GREEN_L,
    BLUE, BLUE_L, PURPLE, PURPLE_L, AMBER, AMBER_L, RED, RED_L,
    TERMBG, TERMBG2, TERMTXT, TERMDIM,
    font, blend, clamp01, ease_out, ease_out_soft, ease_in_out, ease_back,
    reveal, lerp, measure, wrap, para, para_h, card, chip, arrow,
    arrow_curved, Terminal, header, title, subtitle_band,
    draw_terminal_text, text_w,
)

_COLOR_NAMES = ("BG", "BG_ALT", "INK", "INK_SOFT", "MUTED", "CARD", "BORDER",
                "BORDER_D", "ORANGE", "ORANGE_D", "ORANGE_L", "TEAL", "TEAL_D",
                "TEAL_L", "GREEN", "GREEN_L", "BLUE", "BLUE_L", "PURPLE",
                "PURPLE_L", "AMBER", "AMBER_L", "RED", "RED_L",
                "TERMBG", "TERMBG2", "TERMTXT", "TERMDIM")


def setup():
    """把 content.py 里的主题应用上，并重新绑定颜色常量。

    必须在导入本模块之后调用一次（管线脚本的 main 开头会调）。
    """
    from content import BRAND, THEME
    engine.use_theme(THEME)
    engine.BRAND = BRAND
    g = globals()
    for n in _COLOR_NAMES:
        g[n] = getattr(engine, n)


def new_frame():
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)


def caption(d, text, alpha=1.0):
    """底部解说字幕（非对白式，用于强调画面文字）。"""
    if alpha <= 0.01:
        return
    subtitle_band_alpha(d, text, alpha)


def subtitle_band_alpha(d, text, alpha):
    f = font(38)
    lines = wrap(d, text, f, 1360)
    lh = 54
    bh = len(lines) * lh + 30
    bx0, bx1 = W // 2 - 730, W // 2 + 730
    by0 = H - 34 - bh
    c = blend(BG, (30, 28, 26), alpha)
    d.rounded_rectangle([bx0, by0, bx1, by0 + bh], radius=16, fill=c)
    yy = by0 + 15
    txt = blend(BG, (248, 246, 242), alpha)
    for ln in lines:
        d.text((W // 2, yy + lh / 2 - 3), ln, font=f, fill=txt, anchor="mm")
        yy += lh


# ================================================================ 1 开场
def draw_hook(img, d, t, dur, prog):
    """文档被误删的焦虑场景 -> 引出问题。"""
    from random import Random
    rnd = Random(7)

    # 背景：一台笔记本电脑的抽象表现 —— 文档窗口
    wx0, wy0, wx1, wy1 = 390, 190, 1180, 880
    d.rounded_rectangle([wx0, wy0, wx1, wy1], radius=16, fill=(252, 251, 249),
                        outline=BORDER_D, width=3)
    d.rounded_rectangle([wx0, wy0, wx1, wy0 + 52], radius=16, fill=(238, 234, 226))
    d.rectangle([wx0, wy0 + 34, wx1, wy0 + 52], fill=(238, 234, 226))
    for i, col in enumerate([(224, 106, 96), (232, 186, 96), (128, 196, 140)]):
        d.ellipse([wx0 + 22 + i * 24 - 7, wy0 + 26 - 7, wx0 + 22 + i * 24 + 7, wy0 + 26 + 7], fill=col)
    d.text((wx0 + 130, wy0 + 26), "毕业论文 最终版（真的最终）.docx",
           font=font(22), fill=MUTED, anchor="lm")

    # 正文行
    lines = [0.86, 0.94, 0.72, 0.90, 0.55, 0.88, 0.93, 0.66, 0.83, 0.45, 0.79, 0.90, 0.60]
    line_y0 = wy0 + 92
    lh = 52
    # 第一阶段 0 -> 5.5s: 正常；5.5 -> 7.5: 选中一大段；7.5 -> 8.5 删除 -> 空洞
    del_start, del_done = 5.2, 6.6
    sel_a = clamp01((t - 4.0) / 1.0)
    gone = clamp01((t - del_start) / (del_done - del_start))
    # 选中的行范围 3..7
    sel_lo, sel_hi = 3, 7

    for i, fr in enumerate(lines):
        y = line_y0 + i * lh
        if y > wy1 - 60:
            break
        w = (wx1 - wx0 - 130) * fr
        selected = sel_lo <= i <= sel_hi
        if selected and sel_a > 0.05:
            selw = w if i != sel_hi else w * 0.6
            d.rectangle([wx0 + 62, y - 8, wx0 + 62 + selw, y + 30],
                        fill=blend((252, 251, 249), (168, 205, 240), sel_a * 0.85))
        if selected:
            if i == sel_hi:
                w = w * (1 - gone)
            elif i > sel_lo:
                w = w * (1 - clamp01((t - del_start - 0.18 * (i - sel_lo)) / 0.5))
            else:
                w = w * (1 - clamp01((t - del_start) / (del_done - del_start)) * 0.98)
        if w > 2:
            d.rounded_rectangle([wx0 + 62, y, wx0 + 62 + w, y + 22], radius=6,
                                fill=blend((252, 251, 249), (198, 191, 182), 0.9))

    # 保存 / 关闭按钮的示意
    bx, by = wx1 - 60, wy0 + 26
    if 2.4 < t < 9:
        pulse = 1 + 0.12 * math.sin((t - 2.4) * 6)
        d.ellipse([bx - 11 * pulse, by - 11 * pulse, bx + 11 * pulse, by + 11 * pulse],
                  fill=blend(BG, (226, 100, 90), min(1.0, (t - 2.4) / 0.4)))

    # 保存提示气泡
    if 2.6 < t < 11:
        a = reveal(t, 2.6, 0.4) * (1 - clamp01((t - 9.6) / 0.6))
        bx0, by0 = 96, wy0 + 250
        d.rounded_rectangle([bx0, by0, bx0 + 330, by0 + 96], radius=16,
                            fill=blend(BG, ORANGE_L, a), outline=blend(BG, ORANGE, a), width=3)
        d.text((bx0 + 165, by0 + 30), "Ctrl + S  保存", font=font(28, "b"),
               fill=blend(BG, ORANGE_D, a), anchor="mm")
        d.text((bx0 + 165, by0 + 66), "旧版本被覆盖了", font=font(21),
               fill=blend(BG, INK_SOFT, a), anchor="mm")
        # 指向窗口的箭头
        arrow(d, (bx0 + 340, by0 + 48), (wx0 + 240, by0 + 48),
              color=blend(BG, ORANGE, a), w=4, head=16)

    # 右侧：时间线示意 —— 版本被覆盖
    tx = 1460
    d.text((tx, 210), "你保存的", font=font(26, "b"), fill=MUTED, anchor="ma")
    d.text((tx, 248), "一直都是最新那一版", font=font(26, "b"), fill=MUTED, anchor="ma")
    for i in range(4):
        a = reveal(t, 0.6 + i * 0.28, 0.5)
        yy = 330 + i * 130
        # 被划掉的旧版本
        d.rounded_rectangle([tx - 200, yy, tx + 200, yy + 96], radius=14,
                            fill=blend(BG, CARD, a), outline=blend(BG, BORDER, a), width=2)
        d.text((tx, yy + 30), ["第一版", "第二版", "第三版", "第十版"][i],
               font=font(28, "b"), fill=blend(BG, INK if i == 3 else MUTED, a), anchor="mm")
        d.text((tx, yy + 68), ["已覆盖", "已覆盖", "已覆盖", "今天 · 还在"][i],
               font=font(20), fill=blend(BG, (MUTED if i < 3 else GREEN), a), anchor="mm")
        if i < 3 and a > 0.5:
            d.line([tx - 150, yy + 48, tx + 150, yy + 48],
                   fill=blend(BG, RED, a * 0.75), width=5)

    # 顶部大标题
    a = reveal(t, 0.0, 0.7)
    d.text((W // 2, 92), "你有没有丢过改好的文件？",
           font=font(56, "b"), fill=blend(BG, INK, a), anchor="ma")

    # 结尾引出
    if t > 12.5:
        a2 = reveal(t, 12.5, 0.8)
        d.rounded_rectangle([W // 2 - 480, 940, W // 2 + 480, 1032], radius=18,
                            fill=blend(BG, (28, 26, 24), a2))
        d.text((W // 2, 986), "问题出在：保存会覆盖旧版本", font=font(36, "b"),
               fill=blend(BG, (250, 248, 244), a2), anchor="mm")


# ================================================================ 2 存档比喻
def draw_savepoint(img, d, t, dur, prog):
    """游戏存档比喻。"""
    a = reveal(t, 0.2, 0.7)
    d.text((W // 2, 86), "版本控制 = 给文件装一个「存档」系统",
           font=font(56, "b"), fill=blend(BG, INK, a), anchor="ma")

    # 左：游戏进度条
    gx0, gy0, gx1, gy1 = 140, 250, 860, 830
    d.rounded_rectangle([gx0, gy0, gx1, gy1], radius=22, fill=CARD, outline=BORDER, width=3)
    d.text(((gx0 + gx1) / 2, gy0 + 44), "游戏：打 BOSS 之前先存档",
           font=font(26, "b"), fill=INK_SOFT, anchor="mm")

    stages = ["出生点", "第一关", "存档点", "BOSS 前"]
    for i, s in enumerate(stages):
        aa = reveal(t, 0.6 + i * 0.35, 0.5)
        x = gx0 + 90 + i * 190
        y = gy0 + 190
        col = (GREEN if i == 2 else (ORANGE if i == 3 else BLUE))
        is_save = (i == 2)
        r = 34 if is_save else 24
        # 连接线
        if i > 0:
            d.line([x - 190 + r, y, x - r, y], fill=blend(CARD, BORDER_D, aa), width=5)
        d.ellipse([x - r, y - r, x + r, y + r], fill=blend(CARD, col, aa),
                  outline=blend(CARD, blend(col, (0, 0, 0), 0.2), aa), width=4)
        if is_save:
            p = 1 + 0.1 * math.sin(t * 4)
            d.ellipse([x - r * 1.7 * p, y - r * 1.7 * p, x + r * 1.7 * p, y + r * 1.7 * p],
                      outline=blend(CARD, GREEN, aa * 0.5 * (1 - (p - 1) * 6)), width=4)
        d.text((x, y + 62), s, font=font(23, "b" if is_save else "r"),
               fill=blend(CARD, INK if is_save else MUTED, aa), anchor="mm")

    # 读档箭头
    if t > 2.4:
        ap = reveal(t, 2.4, 0.6)
        arrow_curved(d, (gx0 + 470, gy0 + 400), (gx0 + 90, gy0 + 400),
                     color=blend(CARD, RED, ap), w=5, bend=0.18)
        d.text((gx0 + 280, gy0 + 330), "打输了 → 读档重来", font=font(24, "b"),
               fill=blend(CARD, RED, ap), anchor="mm")

    d.text(((gx0 + gx1) / 2, gy1 - 76), "随时回到任何一个存档点",
           font=font(25), fill=MUTED, anchor="mm")

    # 右：Git 存档
    rx0, ry0, rx1, ry1 = 940, 250, 1780, 830
    d.rounded_rectangle([rx0, ry0, rx1, ry1], radius=22, fill=CARD, outline=BORDER, width=3)
    d.text(((rx0 + rx1) / 2, ry0 + 44), "Git：每完成一小段就提交一次",
           font=font(26, "b"), fill=INK_SOFT, anchor="mm")

    msgs = ["搭好项目结构", "写完登录页", "修好价格计算", "加上导出功能"]
    times = ["周一 10:20", "周二 15:40", "周三 09:05", "周四 21:30"]
    for i in range(4):
        aa = reveal(t, 1.1 + i * 0.4, 0.55)
        y = ry0 + 112 + i * 116
        d.rounded_rectangle([rx0 + 60, y, rx1 - 60, y + 96], radius=14,
                            fill=blend(CARD, BG_ALT, aa), outline=blend(CARD, BORDER, aa), width=2)
        cx, cy = rx0 + 112, y + 48
        d.ellipse([cx - 19, cy - 19, cx + 19, cy + 19], fill=blend(CARD, ORANGE, aa))
        d.text((cx, cy), str(i + 1), font=font(21, "b"), fill=blend(CARD, (255, 255, 255), aa), anchor="mm")
        if i < 3:
            d.line([cx, cy + 19, cx, cy + 97], fill=blend(CARD, BORDER_D, aa), width=3)
        d.text((rx0 + 152, y + 18), msgs[i], font=font(27, "b"),
               fill=blend(CARD, INK, aa), anchor="la")
        d.text((rx0 + 152, y + 58), times[i] + "  ·  记录谁改的、改了哪几个文件",
               font=font(19), fill=blend(CARD, MUTED, aa), anchor="la")

    # 底部结论
    if t > 4.6:
        aa = reveal(t, 4.6, 0.7)
        d.rounded_rectangle([W // 2 - 680, 906, W // 2 + 680, 1008], radius=18,
                            fill=blend(BG, TEAL_L, aa), outline=blend(BG, TEAL, aa * 0.7), width=3)
        d.text((W // 2, 957), "比游戏存档更强：每个存档都有说明、作者和时间",
               font=font(32, "b"), fill=blend(BG, TEAL_D, aa), anchor="mm")


# ================================================================ 3 手动管理的痛
def draw_manual_pain(img, d, t, dur, prog):
    a = reveal(t, 0.15, 0.6)
    d.text((W // 2, 84), "不用工具，自己手动管理行不行？",
           font=font(54, "b"), fill=blend(BG, INK, a), anchor="ma")

    # 一排"另存为"的文件，越堆越乱
    names = ["论文.docx", "论文最终版.docx", "论文最终版2.docx",
             "论文真正最终版.docx", "论文打死也不改.docx", "论文最终版(1).docx"]
    base_x, base_y = 150, 250
    for i, n in enumerate(names):
        aa = reveal(t, 0.5 + i * 0.32, 0.45)
        col = i % 3
        row = i // 3
        x = base_x + col * 415 + (row * 34)
        y = base_y + row * 165
        tilt = (i % 3 - 1) * 1.4
        cardw, cardh = 330, 118
        # 轻微旋转的错觉：用偏移量画
        d.rounded_rectangle([x, y, x + cardw, y + cardh], radius=12,
                            fill=blend(BG, CARD, aa), outline=blend(BG, BORDER_D, aa), width=2)
        d.rectangle([x + 22, y + 26, x + 58, y + 74], fill=blend(BG, BLUE_L, aa),
                    outline=blend(BG, BLUE, aa * 0.6), width=2)
        d.text((x + 76, y + 34), n, font=font(23, "b"), fill=blend(BG, INK_SOFT, aa), anchor="la")
        d.text((x + 76, y + 72), ["昨天", "前天", "上周", "上个月", "更早", "刚刚"][i],
               font=font(19), fill=blend(BG, MUTED, aa), anchor="la")

    if t > 1.5:
        aa = reveal(t, 1.5, 0.6)
        d.text((W // 2, 620), "？？？  哪个才是我要的那一版",
               font=font(40, "b"), fill=blend(BG, RED, aa), anchor="ma")

    # 三个硬伤
    problems = [
        ("看不出改了什么", "只能靠文件名猜", RED, RED_L),
        ("两个人改同一个文件", "只能互相传，最后手动合并", AMBER, AMBER_L),
        ("磁盘一坏全没", "所有版本一起消失", PURPLE, PURPLE_L),
    ]
    for i, (t1, t2, col, light) in enumerate(problems):
        aa = reveal(t, 3.0 + i * 0.7, 0.6)
        x = 130 + i * 580
        y = 720
        d.rounded_rectangle([x, y, x + 530, y + 216], radius=20,
                            fill=blend(BG, CARD, aa), outline=blend(BG, col, aa), width=3)
        d.ellipse([x + 34, y + 34, x + 78, y + 78], fill=blend(BG, col, aa))
        d.text((x + 56, y + 56), "!", font=font(30, "b"), fill=blend(BG, (255, 255, 255), aa), anchor="mm")
        d.text((x + 96, y + 40), t1, font=font(28, "b"), fill=blend(BG, INK, aa), anchor="la")
        d.text((x + 96, y + 84), t2, font=font(20), fill=blend(BG, MUTED, aa), anchor="la")

    if t > 5.6:
        aa = reveal(t, 5.6, 0.7)
        d.text((W // 2, 986), "版本控制系统，就是来替你干这三件事的",
               font=font(34, "b"), fill=blend(BG, TEAL_D, aa), anchor="mm")


# ================================================================ 4 Git 是什么
def draw_git_intro(img, d, t, dur, prog):
    a = reveal(t, 0.15, 0.6)
    d.text((W // 2, 78), "Git 是什么？", font=font(58, "b"),
           fill=blend(BG, INK, a), anchor="ma")

    # 中央 Git 标志
    cx, cy = W // 2, 250
    aa = reveal(t, 0.35, 0.7, ease_back)
    s = lerp(0.6, 1.0, clamp01(aa))
    # 用旋转的方块 + 分支线示意 Git 标志
    d.rounded_rectangle([cx - 62 * s, cy - 62 * s, cx + 62 * s, cy + 62 * s], radius=18,
                        fill=blend(BG, ORANGE, aa))
    pts = [(cx - 62, cy + 30), (cx, cy - 10), (cx + 62, cy + 26)]
    for p0, p1 in zip(pts, pts[1:]):
        d.line([(p0[0], p0[1]), (p1[0], p1[1])], fill=blend(BG, (255, 255, 255), aa), width=10)
    for px, py in [(cx - 62, cy + 30), (cx, cy - 10), (cx + 62, cy + 26)]:
        d.ellipse([px - 13, py - 13, px + 13, py + 13], fill=blend(BG, (255, 255, 255), aa))
    d.text((cx, cy + 96), "Git", font=font(48, "b", mono=True),
           fill=blend(BG, INK, aa), anchor="ma")

    # 2005 林纳斯
    if t > 1.6:
        aa = reveal(t, 1.6, 0.7)
        d.rounded_rectangle([300, 400, 1620, 512], radius=16, fill=blend(BG, BG_ALT, aa),
                            outline=blend(BG, BORDER, aa), width=2)
        d.text((340, 434), "2005 年，Linux 的作者林纳斯·托瓦兹亲手做出来",
               font=font(30, "b"), fill=blend(BG, INK_SOFT, aa), anchor="la")
        d.text((340, 476), "因为当时他管理的项目太大，已有的工具都不够快、不够可靠",
               font=font(22), fill=blend(BG, MUTED, aa), anchor="la")

    # 三个特点
    feats = [
        ("快", "几十万个文件，切换版本一瞬间", TEAL, TEAL_L),
        ("完整", "每次提交都完整记下，不怕折腾", GREEN, GREEN_L),
        ("分布式", "你电脑上就有一份完整历史", BLUE, BLUE_L),
    ]
    for i, (t1, t2, col, light) in enumerate(feats):
        aa = reveal(t, 2.9 + i * 0.6, 0.6)
        x = 190 + i * 525
        y = 600
        d.rounded_rectangle([x, y, x + 480, y + 230], radius=20,
                            fill=blend(BG, CARD, aa), outline=blend(BG, col, aa), width=3)
        d.rounded_rectangle([x + 34, y + 34, x + 34 + 96, y + 34 + 44], radius=10,
                            fill=blend(BG, col, aa))
        d.text((x + 82, y + 56), t1, font=font(26, "b"),
               fill=blend(BG, (255, 255, 255), aa), anchor="mm")
        d.text((x + 34, y + 112), t2, font=font(23), fill=blend(BG, INK_SOFT, aa), anchor="la")

    if t > 5.2:
        aa = reveal(t, 5.2, 0.7)
        d.text((W // 2, 930), "GitHub 这些代码托管网站，底层用的就是 Git",
               font=font(30, "b"), fill=blend(BG, ORANGE_D, aa), anchor="mm")


# ================================================================ 5 三个区域
def draw_three_areas(img, d, t, dur, prog):
    a = reveal(t, 0.15, 0.6)
    d.text((W // 2, 62), "最核心的一张图：Git 的三个区域",
           font=font(52, "b"), fill=blend(BG, INK, a), anchor="ma")

    areas = [
        dict(name="工作区", en="Working Directory", desc="你眼前能编辑的文件夹\n改文件就在这里",
             col=BLUE, light=BLUE_L, icon="edit"),
        dict(name="暂存区", en="Staging Area", desc="像超市购物车\n先挑好这一件",
             col=AMBER, light=AMBER_L, icon="cart"),
        dict(name="仓库", en="Repository", desc="真正存档的地方\n提交就存在这里",
             col=GREEN, light=GREEN_L, icon="box"),
    ]
    cw, ch = 445, 300
    x0 = 62
    y0 = 290
    gap = 230
    centers = []
    for i, ar in enumerate(areas):
        aa = reveal(t, 0.45 + i * 0.55, 0.65, ease_back)
        x = x0 + i * (cw + gap)
        yy = y0 + (1 - clamp01(aa)) * 28
        d.rounded_rectangle([x, yy, x + cw, yy + ch], radius=24,
                            fill=blend(BG, CARD, aa), outline=blend(BG, ar["col"], aa), width=4)
        # 顶部色条
        d.rounded_rectangle([x, yy, x + cw, yy + 12], radius=6, fill=blend(BG, ar["col"], aa))
        d.text((x + 36, yy + 50), ar["name"], font=font(40, "b"),
               fill=blend(BG, INK, aa), anchor="la")
        d.text((x + 36, yy + 108), ar["en"], font=font(21, mono=True),
               fill=blend(BG, MUTED, aa), anchor="la")
        yy2 = yy + 152
        d.rounded_rectangle([x + 36, yy2, x + cw - 36, yy2 + 118], radius=14,
                            fill=blend(BG, ar["light"], aa))
        for j, ln in enumerate(ar["desc"].split("\n")):
            d.text((x + cw / 2, yy2 + 34 + j * 42), ln, font=font(22),
                   fill=blend(BG, INK_SOFT, aa), anchor="mm")
        centers.append((x + cw / 2, yy + ch))
        # 编号
        d.ellipse([x + cw - 68, yy + 34, x + cw - 24, yy + 78], fill=blend(BG, ar["col"], aa))
        d.text((x + cw - 46, yy + 56), str(i + 1), font=font(26, "b"),
               fill=blend(BG, (255, 255, 255), aa), anchor="mm")

    # 箭头 + 动作标签（放在卡片上方的空隙里，避免压住卡片）
    for i, (label, sub) in enumerate([("git add", "放进购物车"), ("git commit", "结账存档")]):
        aa = reveal(t, 2.3 + i * 0.9, 0.6)
        cx = (centers[i][0] + centers[i + 1][0]) / 2
        cy = y0 + 150
        arrow(d, (cx - 52, cy), (cx + 52, cy), color=blend(BG, ORANGE, aa), w=6, head=20)
        d.rounded_rectangle([cx - 86, y0 + 192, cx + 86, y0 + 252], radius=12,
                            fill=blend(BG, ORANGE_L, aa), outline=blend(BG, ORANGE, aa), width=2)
        d.text((cx, y0 + 208), label, font=font(21, "b", mono=True),
               fill=blend(BG, ORANGE_D, aa), anchor="ma")
        d.text((cx, y0 + 236), sub, font=font(17), fill=blend(BG, INK_SOFT, aa), anchor="ma")

    # 底部：三步流程
    if t > 4.3:
        aa = reveal(t, 4.3, 0.7)
        yb = 620
        d.rounded_rectangle([62, yb, 1858, yb + 132], radius=20,
                            fill=blend(BG, BG_ALT, aa), outline=blend(BG, BORDER, aa), width=2)
        steps = [("1. 改文件", "在工作区改"), ("2. git add", "放进暂存区"),
                 ("3. git commit", "存进仓库")]
        for i, (s1, s2) in enumerate(steps):
            x = 62 + 110 + i * 595
            d.text((x, yb + 40), s1, font=font(30, "b"),
                   fill=blend(BG, INK, aa), anchor="la")
            d.text((x, yb + 84), s2, font=font(21),
                   fill=blend(BG, MUTED, aa), anchor="la")
            if i < 2:
                arrow(d, (x + 400, yb + 62), (x + 480, yb + 62),
                      color=blend(BG, BORDER_D, aa), w=4, head=14)

    # 为什么需要购物车
    if t > 5.8:
        aa = reveal(t, 5.8, 0.7)
        d.rounded_rectangle([62, 790, 1858, 1010], radius=22,
                            fill=blend(BG, CARD, aa), outline=blend(BG, TEAL, aa * 0.8), width=3)
        d.text((110, 826), "为什么要多一个购物车？",
               font=font(32, "b"), fill=blend(BG, TEAL_D, aa), anchor="la")
        d.text((110, 882), "因为一次提交应该只讲一件事。",
               font=font(27), fill=blend(BG, INK_SOFT, aa), anchor="la")
        d.text((110, 928), "改了五个文件，其中两个其实是另一件事 —— "
                           "购物车让你先结一件事，再结另一件，历史会清楚很多。",
               font=font(27), fill=blend(BG, INK_SOFT, aa), anchor="la")


# ================================================================ 6 安装配置
def draw_install(img, d, t, dur, prog):
    a = reveal(t, 0.15, 0.6)
    d.text((W // 2, 76), "动手之前：安装 + 自我介绍",
           font=font(54, "b"), fill=blend(BG, INK, a), anchor="ma")

    # 左：下载步骤
    d.rounded_rectangle([120, 190, 900, 470], radius=22, fill=CARD, outline=BORDER, width=3)
    d.text((160, 226), "第一步：装 Git", font=font(32, "b"), fill=INK, anchor="la")
    for i, s in enumerate(["浏览器搜索 Git，进官网 git-scm.com",
                           "下载对应系统的安装包",
                           "一路点「下一步」，装完即可"]):
        aa = reveal(t, 0.6 + i * 0.5, 0.5)
        y = 292 + i * 56
        d.ellipse([164, y + 8, 186, y + 30], fill=blend(CARD, ORANGE, aa))
        d.text((175, y + 19), str(i + 1), font=font(17, "b"),
               fill=blend(CARD, (255, 255, 255), aa), anchor="mm")
        d.text((206, y + 6), s, font=font(24), fill=blend(CARD, INK_SOFT, aa), anchor="la")

    # 终端在哪
    d.rounded_rectangle([120, 510, 900, 800], radius=22, fill=CARD, outline=BORDER, width=3)
    d.text((160, 546), "第二步：找到终端", font=font(32, "b"), fill=INK, anchor="la")
    items = [("Windows", "开始菜单搜「Git Bash」", TEAL),
             ("Mac", "打开「终端」应用", BLUE)]
    for i, (os_, txt, col) in enumerate(items):
        aa = reveal(t, 2.4 + i * 0.5, 0.5)
        y = 620 + i * 88
        d.rounded_rectangle([160, y, 400, y + 60], radius=12, fill=blend(CARD, col, aa))
        d.text((280, y + 30), os_, font=font(26, "b"),
               fill=blend(CARD, (255, 255, 255), aa), anchor="mm")
        d.text((424, y + 30), txt, font=font(24), fill=blend(CARD, INK_SOFT, aa), anchor="lm")

    # 右：终端
    term = Terminal([970, 190, 1810, 800], fsize=26, title="终端 / Git Bash")
    script = [
        ("dim", "# 一次性设置：告诉 Git 你是谁"),
        ("gap", 0.4),
        ("cmd", 'git config --global user.name "你的名字"', 15),
        ("cmd", 'git config --global user.email "you@example.com"', 15),
        ("gap", 0.6),
        ("dim", "# 检查一下是否设置成功"),
        ("cmd", "git config --global --list", 15),
        ("ok", "user.name=你的名字"),
        ("ok", "user.email=you@example.com"),
    ]
    term.draw(img, script, t, t0=1.2, speed=13)

    if t > 6.0:
        aa = reveal(t, 6.0, 0.7)
        d.rounded_rectangle([120, 840, 1810, 1000], radius=20,
                            fill=blend(BG, AMBER_L, aa), outline=blend(BG, AMBER, aa), width=3)
        d.text((170, 872), "为什么要设置名字和邮箱？", font=font(30, "b"),
               fill=blend(BG, (150, 100, 20), aa), anchor="la")
        d.text((170, 926), "因为每一次提交都会记下「是谁存的档」。"
                           "这两条命令每台电脑只要做一次，以后不用再管。",
               font=font(26), fill=blend(BG, INK_SOFT, aa), anchor="la")


# ================================================================ 7 git init + status
def draw_init(img, d, t, dur, prog):
    a = reveal(t, 0.15, 0.6)
    d.text((W // 2, 76), "创建你的第一个仓库：git init",
           font=font(54, "b"), fill=blend(BG, INK, a), anchor="ma")

    # 左侧：文件夹变化示意
    fx0, fy0, fx1, fy1 = 120, 190, 800, 620
    d.rounded_rectangle([fx0, fy0, fx1, fy1], radius=22, fill=CARD, outline=BORDER, width=3)
    d.text((fx0 + 40, fy0 + 34), "my-project 文件夹", font=font(28, "b"), fill=INK, anchor="la")
    files = ["index.html", "style.css", "readme.md"]
    for i, fn in enumerate(files):
        y = fy0 + 104 + i * 58
        d.rectangle([fx0 + 46, y + 8, fx0 + 74, y + 36], fill=BLUE_L, outline=BLUE, width=2)
        d.text((fx0 + 92, y + 22), fn, font=font(23), fill=INK_SOFT, anchor="lm")
    # init 后出现的 .git
    if t > 1.3:
        aa = reveal(t, 1.3, 0.6)
        y = fy0 + 104 + 3 * 58
        d.rectangle([fx0 + 46, y + 8, fx0 + 74, y + 36], fill=blend(CARD, ORANGE_L, aa),
                    outline=blend(CARD, ORANGE, aa), width=2)
        d.text((fx0 + 92, y + 22), ".git  （Git 的仓库就在这里面）",
               font=font(23, "b"), fill=blend(CARD, ORANGE_D, aa), anchor="lm")
    if t > 2.0:
        aa = reveal(t, 2.0, 0.6)
        d.text((fx0 + 40, fy1 - 66), "一个文件夹只需要 init 一次",
               font=font(22), fill=blend(CARD, MUTED, aa), anchor="la")

    # 右侧终端
    term = Terminal([860, 190, 1810, 800], fsize=26, title="终端")
    script = [
        ("dim", "# 先进到你想管理的文件夹"),
        ("cmd", "cd ~/Desktop/my-project", 14),
        ("gap", 0.4),
        ("dim", "# 初始化仓库，让 Git 开始看着这个文件夹"),
        ("cmd_wait", "git init", 12, 1.2),
        ("ok", "Initialized empty Git repository in .../my-project/.git/"),
        ("gap", 0.5),
        ("dim", "# 看看现在的状态"),
        ("cmd_wait", "git status", 12, 1.0),
        ("out", "On branch main"),
        ("out", ""),
        ("warn", "No commits yet"),
        ("out", ""),
        ("key", "Untracked files:"),
        ("out", "        index.html"),
        ("out", "        style.css"),
        ("out", ""),
        ("dim", 'nothing added to commit but untracked files present'),
    ]
    term.draw(img, script, t, t0=1.0, speed=13)

    # 底部解释
    if t > 8.2:
        aa = reveal(t, 8.2, 0.7)
        d.rounded_rectangle([120, 840, 1810, 1000], radius=20,
                            fill=blend(BG, TEAL_L, aa), outline=blend(BG, TEAL, aa), width=3)
        d.text((170, 870), "git status —— 你会用一辈子的命令",
               font=font(30, "b"), fill=blend(BG, TEAL_D, aa), anchor="la")
        d.text((170, 924), "它告诉你哪些文件是新出现的、哪些改了还没提交。"
                           "记不住别的命令没关系，敲一下它，它会告诉你下一步该干嘛。",
               font=font(25), fill=blend(BG, INK_SOFT, aa), anchor="la")


# ================================================================ 8 git add + commit
def draw_commit(img, d, t, dur, prog):
    a = reveal(t, 0.15, 0.6)
    d.text((W // 2, 76), "放进购物车，然后结账：add 与 commit",
           font=font(52, "b"), fill=blend(BG, INK, a), anchor="ma")

    # 左：购物车示意
    cx0, cy0, cx1, cy1 = 110, 180, 720, 620
    d.rounded_rectangle([cx0, cy0, cx1, cy1], radius=22, fill=CARD, outline=BORDER, width=3)
    d.text((cx0 + 36, cy0 + 32), "暂存区 = 购物车", font=font(28, "b"), fill=INK, anchor="la")
    items = ["index.html", "style.css"]
    for i, it in enumerate(items):
        aa = reveal(t, 1.0 + i * 0.55, 0.5, ease_back)
        y = cy0 + 120 + i * 76
        x = cx0 + 70 + (1 - clamp01(aa)) * -50
        d.rounded_rectangle([x, y, x + 440, y + 60], radius=12,
                            fill=blend(CARD, GREEN_L, aa), outline=blend(CARD, GREEN, aa), width=2)
        d.text((x + 22, y + 30), "✓", font=font(26, "b"), fill=blend(CARD, GREEN, aa), anchor="lm")
        d.text((x + 62, y + 30), it, font=font(24), fill=blend(CARD, INK, aa), anchor="lm")
        d.text((x + 410, y + 30), "已放入", font=font(19),
               fill=blend(CARD, GREEN, aa), anchor="rm")
    aa = reveal(t, 2.3, 0.6)
    d.text((cx0 + 36, cy1 - 70), "购物车里是「这次要一起存的东西」",
           font=font(21), fill=blend(CARD, MUTED, aa), anchor="la")

    # 右侧终端
    term = Terminal([780, 180, 1810, 800], fsize=25, title="终端")
    script = [
        ("dim", "# 把改动的文件放进暂存区（购物车）"),
        ("cmd_wait", "git add index.html", 13, 0.5),
        ("cmd_wait", "git add style.css", 13, 0.5),
        ("dim", "# 或者一次全放进去： git add ."),
        ("gap", 0.5),
        ("dim", "# 再确认一下状态"),
        ("cmd_wait", "git status", 13, 0.9),
        ("key", "Changes to be committed:"),
        ("out", "        new file:   index.html"),
        ("out", "        new file:   style.css"),
        ("gap", 0.6),
        ("dim", "# 结账：写一句说明，正式存档"),
        ("cmd_wait", 'git commit -m "完成首页布局"', 13, 1.2),
        ("ok", "[main (root-commit) 3f2a1b9] 完成首页布局"),
        ("ok", " 2 files changed, 42 insertions(+)"),
    ]
    term.draw(img, script, t, t0=0.9, speed=13)

    if t > 10.5:
        aa = reveal(t, 10.5, 0.7)
        d.rounded_rectangle([110, 840, 1810, 1000], radius=20,
                            fill=blend(BG, ORANGE_L, aa), outline=blend(BG, ORANGE, aa), width=3)
        d.text((160, 870), "那句说明（-m 后面的文字）是写给未来的自己看的",
               font=font(30, "b"), fill=blend(BG, ORANGE_D, aa), anchor="la")
        d.text((160, 924), "「完成首页布局」✓    「更新」✗    「改了一下」✗   —— "
                           "三个月后你绝对看不懂后者",
               font=font(25), fill=blend(BG, INK_SOFT, aa), anchor="la")


# ================================================================ 9 git log / diff
def draw_log(img, d, t, dur, prog):
    a = reveal(t, 0.15, 0.6)
    d.text((W // 2, 76), "查看历史：git log 与 git diff",
           font=font(54, "b"), fill=blend(BG, INK, a), anchor="ma")

    term = Terminal([110, 180, 1130, 800], fsize=24, title="终端")
    script = [
        ("cmd_wait", "git log", 12, 1.0),
        ("key", "commit 3f2a1b9c4d5e6f7089a0b1c2d3e4f5a6b7c8d9e0"),
        ("out", "Author: 你的名字 <you@example.com>"),
        ("out", "Date:   Mon Oct 13 10:24:31 2026 +0800"),
        ("out", ""),
        ("out", "    完成首页布局"),
        ("out", ""),
        ("key", "commit 8c1d4e7a2b3f5a6c8d9e0f1a2b3c4d5e6f708192"),
        ("out", "Author: 你的名字 <you@example.com>"),
        ("out", "Date:   Sun Oct 12 21:05:12 2026 +0800"),
        ("out", ""),
        ("out", "    搭好项目结构"),
        ("gap", 0.6),
        ("dim", "# 输出太啰嗦？每条只占一行"),
        ("cmd", "git log --oneline", 13),
        ("ok", "3f2a1b9 完成首页布局"),
        ("ok", "8c1d4e7 搭好项目结构"),
    ]
    term.draw(img, script, t, t0=0.9, speed=13)

    # 右侧：解释
    rx0, ry0 = 1190, 180
    aa = reveal(t, 1.6, 0.6)
    d.rounded_rectangle([rx0, ry0, 1810, 480], radius=20, fill=blend(BG, CARD, aa),
                        outline=blend(BG, ORANGE, aa), width=3)
    d.text((rx0 + 36, ry0 + 32), "那一长串字母数字是什么？", font=font(27, "b"),
           fill=blend(BG, INK, aa), anchor="la")
    d.text((rx0 + 36, ry0 + 86), "3f2a1b9c4d5e6f7...", font=font(24, mono=True),
           fill=blend(BG, ORANGE_D, aa), anchor="la")
    d.text((rx0 + 36, ry0 + 136), "这是这次提交的唯一编号，叫哈希值。",
           font=font(23), fill=blend(BG, INK_SOFT, aa), anchor="la")
    d.text((rx0 + 36, ry0 + 180), "你可以把它当成存档的编号 —— 太长记不住，",
           font=font(23), fill=blend(BG, INK_SOFT, aa), anchor="la")
    d.text((rx0 + 36, ry0 + 224), "一般写前六七位就够了。", font=font(23),
           fill=blend(BG, INK_SOFT, aa), anchor="la")

    aa = reveal(t, 3.0, 0.6)
    d.rounded_rectangle([rx0, 510, 1810, 800], radius=20, fill=blend(BG, CARD, aa),
                        outline=blend(BG, TEAL, aa), width=3)
    d.text((rx0 + 36, 542), "git diff —— 看具体改了哪几行", font=font(27, "b"),
           fill=blend(BG, TEAL_D, aa), anchor="la")
    diffs = [("+  <h1>我的主页</h1>", GREEN, GREEN_L),
             ("-  <h1>Hello</h1>", RED, RED_L),
             ("   <p>欢迎</p>", MUTED, BG_ALT)]
    for i, (txt, col, light) in enumerate(diffs):
        da = reveal(t, 3.5 + i * 0.4, 0.5)
        y = 606 + i * 56
        d.rounded_rectangle([rx0 + 36, y, rx0 + 580, y + 44], radius=8,
                            fill=blend(BG, light, da))
        d.text((rx0 + 52, y + 22), txt, font=font(21, mono=True),
               fill=blend(BG, col, da), anchor="lm")
    d.text((rx0 + 36, 764 - 0), "加号是新增的行，减号是删掉的行",
           font=font(19), fill=blend(BG, MUTED, reveal(t, 4.8, 0.5)), anchor="la")


# ================================================================ 10 回退
def draw_undo(img, d, t, dur, prog):
    a = reveal(t, 0.15, 0.6)
    d.text((W // 2, 76), "改错了怎么回去？先分清两种情况",
           font=font(54, "b"), fill=blend(BG, INK, a), anchor="ma")

    # 情况一
    aa = reveal(t, 0.5, 0.6)
    d.rounded_rectangle([110, 180, 940, 560], radius=22,
                        fill=blend(BG, CARD, aa), outline=blend(BG, BLUE, aa), width=3)
    d.rounded_rectangle([110, 180, 940, 246], radius=22, fill=blend(BG, BLUE, aa))
    d.rectangle([110, 228, 940, 246], fill=blend(BG, BLUE, aa))
    d.text((146, 213), "情况一：改了，但还没提交", font=font(28, "b"),
           fill=blend(BG, (255, 255, 255), aa), anchor="lm")
    aa2 = reveal(t, 1.1, 0.5)
    d.rounded_rectangle([146, 280, 904, 336], radius=10, fill=blend(BG, TERMBG, aa2))
    d.text((172, 308), "git restore index.html", font=font(24, mono=True),
           fill=blend(BG, (150, 235, 165), aa2), anchor="lm")
    d.text((146, 366), "把文件恢复到上一次提交时的样子。", font=font(24),
           fill=blend(BG, INK_SOFT, aa2), anchor="la")
    aa3 = reveal(t, 1.8, 0.5)
    d.rounded_rectangle([146, 424, 904, 520], radius=12,
                        fill=blend(BG, RED_L, aa3), outline=blend(BG, RED, aa3 * 0.7), width=2)
    d.text((172, 448), "⚠  不可撤销", font=font(24, "b"),
           fill=blend(BG, RED, aa3), anchor="la")
    d.text((172, 484), "刚才没提交的改动会真的消失", font=font(21),
           fill=blend(BG, INK_SOFT, aa3), anchor="la")

    # 情况二
    aa = reveal(t, 2.6, 0.6)
    d.rounded_rectangle([980, 180, 1810, 560], radius=22,
                        fill=blend(BG, CARD, aa), outline=blend(BG, GREEN, aa), width=3)
    d.rounded_rectangle([980, 180, 1810, 246], radius=22, fill=blend(BG, GREEN, aa))
    d.rectangle([980, 228, 1810, 246], fill=blend(BG, GREEN, aa))
    d.text((1016, 213), "情况二：提交了，但说明写错了", font=font(28, "b"),
           fill=blend(BG, (255, 255, 255), aa), anchor="lm")
    aa2 = reveal(t, 3.2, 0.5)
    d.rounded_rectangle([1016, 280, 1774, 336], radius=10, fill=blend(BG, TERMBG, aa2))
    d.text((1042, 308), "git commit --amend", font=font(24, mono=True),
           fill=blend(BG, (150, 235, 165), aa2), anchor="lm")
    d.text((1016, 366), "amend 是「修正」，把最后一次提交重做一遍。",
           font=font(24), fill=blend(BG, INK_SOFT, aa2), anchor="la")
    d.text((1016, 424), "漏放文件也可以补进去，或者改掉那句说明。",
           font=font(24), fill=blend(BG, INK_SOFT, reveal(t, 3.8, 0.5)), anchor="la")

    # 时间线示意
    if t > 4.6:
        aa = reveal(t, 4.6, 0.7)
        y = 700
        xs = [230, 470, 710, 950, 1190, 1430, 1670]
        d.line([xs[0], y, xs[-1], y], fill=blend(BG, BORDER_D, aa), width=5)
        for i, x in enumerate(xs):
            col = ORANGE if i <= 3 else BORDER_D
            r = 20 if i <= 3 else 15
            d.ellipse([x - r, y - r, x + r, y + r], fill=blend(BG, col, aa))
            d.text((x, y + 46), f"v{i+1}", font=font(21, mono=True),
                   fill=blend(BG, INK_SOFT if i <= 3 else MUTED, aa), anchor="mm")
        # restore 箭头
        d.text((230, y - 108), "restore 回到上一个提交", font=font(22, "b"),
               fill=blend(BG, BLUE, aa), anchor="la")
        arrow(d, (xs[3], y - 70), (xs[2], y - 70), color=blend(BG, BLUE, aa), w=4, head=14)
        d.text((230, y + 92), "reset 可以退回到更早的提交", font=font(22, "b"),
               fill=blend(BG, PURPLE, aa), anchor="la")
        arrow(d, (xs[3], y + 130), (xs[0] + 30, y + 130), color=blend(BG, PURPLE, aa), w=4, head=14)
        d.text((230, y + 166), "但别加 --hard，它会连文件改动一起删掉",
               font=font(21), fill=blend(BG, RED, aa), anchor="la")


# ================================================================ 11 分支概念
def draw_branch_concept(img, d, t, dur, prog):
    a = reveal(t, 0.15, 0.6)
    d.text((W // 2, 76), "Git 最强大的功能：分支",
           font=font(56, "b"), fill=blend(BG, INK, a), anchor="ma")

    # 主线
    y_main = 460
    xs = [250, 460, 670]
    aa = reveal(t, 0.5, 0.6)
    d.line([xs[0], y_main, 700, y_main], fill=blend(BG, INK, aa), width=7)
    for i, x in enumerate(xs):
        da = reveal(t, 0.6 + i * 0.3, 0.5, ease_back)
        d.ellipse([x - 26, y_main - 26, x + 26, y_main + 26], fill=blend(BG, INK, da))
    d.text((470, y_main + 70), "main 主线：稳定运行，不敢乱改",
           font=font(26, "b"), fill=blend(BG, INK_SOFT, aa), anchor="ma")

    # 新分支
    if t > 1.9:
        aa = reveal(t, 1.9, 0.9)
        bx = 670
        by = 300
        # 曲线
        pts = []
        for i in range(30):
            u = i / 29
            x = lerp(bx, 1600, u)
            y = lerp(y_main, by, clamp01((u) / 0.32)) if u < 0.32 else by
            pts.append((x, y))
        cut = int(len(pts) * clamp01(aa))
        if cut > 1:
            d.line(pts[:cut], fill=blend(BG, ORANGE, min(1, aa * 1.4)), width=7)
        for i in range(3):
            px = 950 + i * 230
            da = reveal(t, 2.6 + i * 0.35, 0.5, ease_back)
            if da > 0.02:
                d.ellipse([px - 24, by - 24, px + 24, by + 24], fill=blend(BG, ORANGE, da))
        d.text((1280, by - 78), "feature 分支：在这里随便折腾",
               font=font(26, "b"), fill=blend(BG, ORANGE_D, aa), anchor="ma")

    # 平行宇宙标签
    if t > 3.6:
        aa = reveal(t, 3.6, 0.6)
        d.rounded_rectangle([230, 200, 700, 262], radius=14,
                            fill=blend(BG, PURPLE_L, aa), outline=blend(BG, PURPLE, aa), width=2)
        d.text((465, 231), "像游戏里的「平行宇宙」", font=font(25, "b"),
               fill=blend(BG, PURPLE, aa), anchor="mm")

    # 合并 / 删除
    if t > 4.6:
        aa = reveal(t, 4.6, 0.9)
        # 合并曲线回到主线
        pts = []
        for i in range(30):
            u = i / 29
            x = lerp(1600, 900, u)
            y = lerp(by, y_main, clamp01((u - 0.68) / 0.32)) if u > 0.68 else by
            pts.append((x, y))
        cut = int(len(pts) * clamp01(aa))
        if cut > 1:
            d.line(pts[:cut], fill=blend(BG, GREEN, min(1, aa * 1.3)), width=7)
        if aa > 0.85:
            d.ellipse([900 - 26, y_main - 26, 900 + 26, y_main + 26], fill=GREEN)
        d.text((1180, y_main + 130), "做成了 → 合并回主线",
               font=font(25, "b"), fill=blend(BG, GREEN, aa), anchor="mm")

    if t > 5.8:
        aa = reveal(t, 5.8, 0.7)
        d.text((700, 830), "做失败了 → 直接删掉这条线，主线毫发无损",
               font=font(25, "b"), fill=blend(BG, MUTED, aa), anchor="mm")
        d.text((W // 2, 930), "默认的那条主线叫 main（老版本也叫 master）",
               font=font(31, "b"), fill=blend(BG, INK, aa), anchor="mm")


# ================================================================ 12 分支实操
def draw_branch_do(img, d, t, dur, prog):
    a = reveal(t, 0.15, 0.6)
    d.text((W // 2, 76), "分支怎么用：三条命令走完一圈",
           font=font(54, "b"), fill=blend(BG, INK, a), anchor="ma")

    term = Terminal([110, 175, 1230, 890], fsize=23, title="终端")
    script = [
        ("dim", "# 1. 创建一条新分支"),
        ("cmd_wait", "git branch feature", 13, 0.5),
        ("dim", "# 2. 切换过去"),
        ("cmd_wait", "git checkout feature", 13, 0.7),
        ("ok", "Switched to branch 'feature'"),
        ("gap", 0.4),
        ("dim", "# 在新分支上正常改文件、add、commit"),
        ("cmd_wait", 'git commit -m "加上导出功能"', 13, 0.9),
        ("ok", "[feature 7b1e4c2] 加上导出功能"),
        ("gap", 0.5),
        ("dim", "# 3. 切回主线，把成果合并进来"),
        ("cmd_wait", "git checkout main", 13, 0.6),
        ("ok", "Switched to branch 'main'"),
        ("cmd_wait", "git merge feature", 13, 1.0),
        ("ok", "Updating 3f2a1b9..7b1e4c2"),
        ("ok", "Fast-forward"),
        ("gap", 0.5),
        ("dim", "# 用完了就删掉这条分支"),
        ("cmd", "git branch -d feature", 13),
        ("ok", "Deleted branch feature (was 7b1e4c2)."),
    ]
    term.draw(img, script, t, t0=0.9, speed=13)

    # 右侧步骤卡
    rx = 1290
    steps = [
        ("git branch feature", "创建新分支", ORANGE),
        ("git checkout feature", "切换过去", ORANGE),
        ("改文件 → add → commit", "在新分支上正常干活", TEAL),
        ("git checkout main", "切回主线", GREEN),
        ("git merge feature", "把成果合并进来", GREEN),
        ("git branch -d feature", "删掉没用的分支", MUTED),
    ]
    for i, (cmd, desc, col) in enumerate(steps):
        aa = reveal(t, 2.0 + i * 1.5, 0.55)
        if aa <= 0.02:
            continue
        y = 205 + i * 108
        d.rounded_rectangle([rx, y, 1815, y + 90], radius=14,
                            fill=blend(BG, CARD, aa), outline=blend(BG, col, aa), width=3)
        d.text((rx + 26, y + 26), cmd, font=font(22, mono=True, weight="b"),
               fill=blend(BG, col, aa), anchor="la")
        d.text((rx + 26, y + 58), desc, font=font(20),
               fill=blend(BG, MUTED, aa), anchor="la")


# ================================================================ 13 远程仓库
def draw_remote(img, d, t, dur, prog):
    a = reveal(t, 0.15, 0.6)
    d.text((W // 2, 76), "远程仓库：给代码一个云端保险柜",
           font=font(54, "b"), fill=blend(BG, INK, a), anchor="ma")

    # 左：本地
    aa = reveal(t, 0.5, 0.6)
    d.rounded_rectangle([130, 250, 700, 620], radius=22, fill=blend(BG, CARD, aa),
                        outline=blend(BG, BLUE, aa), width=3)
    d.text((415, 296), "本地仓库", font=font(30, "b"), fill=blend(BG, BLUE, aa), anchor="mm")
    d.text((415, 340), "你的工作台", font=font(21), fill=blend(BG, MUTED, aa), anchor="mm")
    for i in range(3):
        da = reveal(t, 0.9 + i * 0.3, 0.5)
        y = 400 + i * 62
        d.rounded_rectangle([180, y, 650, y + 46], radius=10, fill=blend(BG, BLUE_L, da))
        d.text((210, y + 23), ["搭好项目结构", "写完登录页", "修好价格计算"][i],
               font=font(21), fill=blend(BG, INK_SOFT, da), anchor="lm")

    # 右：远程
    aa = reveal(t, 1.2, 0.6)
    d.rounded_rectangle([1220, 250, 1790, 620], radius=22, fill=blend(BG, CARD, aa),
                        outline=blend(BG, PURPLE, aa), width=3)
    d.text((1505, 296), "远程仓库", font=font(30, "b"), fill=blend(BG, PURPLE, aa), anchor="mm")
    d.text((1505, 340), "云端保险柜 + 共享文件夹", font=font(21),
           fill=blend(BG, MUTED, aa), anchor="mm")
    for i in range(3):
        da = reveal(t, 1.5 + i * 0.3, 0.5)
        y = 400 + i * 62
        d.rounded_rectangle([1270, y, 1740, y + 46], radius=10, fill=blend(BG, PURPLE_L, da))
        d.text((1300, y + 23), ["搭好项目结构", "写完登录页", "修好价格计算"][i],
               font=font(21), fill=blend(BG, INK_SOFT, da), anchor="lm")

    # 中间连线
    aa = reveal(t, 2.2, 0.7)
    arrow(d, (720, 420), (1200, 420), color=blend(BG, ORANGE, aa), w=6, head=22)
    arrow(d, (1200, 470), (720, 470), color=blend(BG, TEAL, aa), w=6, head=22)
    d.text((960, 388), "git push 推上去", font=font(24, "b"),
           fill=blend(BG, ORANGE_D, aa), anchor="mm")
    d.text((960, 502), "git pull 拉下来", font=font(24, "b"),
           fill=blend(BG, TEAL_D, aa), anchor="mm")

    # GitHub
    if t > 3.4:
        aa = reveal(t, 3.4, 0.6)
        d.rounded_rectangle([130, 680, 1790, 780], radius=18,
                            fill=blend(BG, BG_ALT, aa), outline=blend(BG, BORDER, aa), width=2)
        d.text((170, 730), "托管服务：GitHub（最常用）、Gitee 等。"
                           "建好仓库后你会得到一个网址，形如 github.com/你的用户名/仓库名",
               font=font(26), fill=blend(BG, INK_SOFT, aa), anchor="lm")

    # 两种接法
    if t > 4.6:
        aa = reveal(t, 4.6, 0.7)
        d.rounded_rectangle([130, 820, 940, 1000], radius=18, fill=blend(BG, CARD, aa),
                            outline=blend(BG, TEAL, aa), width=3)
        d.text((170, 848), "本地还没有这个项目", font=font(25, "b"),
               fill=blend(BG, TEAL_D, aa), anchor="la")
        d.rounded_rectangle([170, 896, 900, 944], radius=10, fill=blend(BG, TERMBG, aa))
        d.text((192, 920), "git clone <网址>", font=font(23, mono=True),
               fill=blend(BG, (150, 235, 165), aa), anchor="lm")
        d.text((170, 966), "连历史一起下载到电脑上", font=font(20),
               fill=blend(BG, MUTED, aa), anchor="la")

        d.rounded_rectangle([980, 820, 1790, 1000], radius=18, fill=blend(BG, CARD, aa),
                            outline=blend(BG, ORANGE, aa), width=3)
        d.text((1020, 848), "本地已经有仓库了", font=font(25, "b"),
               fill=blend(BG, ORANGE_D, aa), anchor="la")
        d.rounded_rectangle([1020, 896, 1750, 944], radius=10, fill=blend(BG, TERMBG, aa))
        d.text((1042, 920), "git remote add origin <网址>", font=font(23, mono=True),
               fill=blend(BG, (150, 235, 165), aa), anchor="lm")
        d.text((1020, 966), "origin 是大家习惯给远程仓库起的名字", font=font(20),
               fill=blend(BG, MUTED, aa), anchor="la")


# ================================================================ 14 push / pull
def draw_push_pull(img, d, t, dur, prog):
    a = reveal(t, 0.15, 0.6)
    d.text((W // 2, 76), "日常两个动作：push 与 pull",
           font=font(56, "b"), fill=blend(BG, INK, a), anchor="ma")

    # 两个大卡片
    cards = [
        ("git push", "推到云端", "同伴和云端都能看到你的成果", ORANGE, ORANGE_L, "↑"),
        ("git pull", "拉回本地", "同伴改了什么，一下就同步过来", TEAL, TEAL_L, "↓"),
    ]
    for i, (cmd, t1, t2, col, light, arw) in enumerate(cards):
        aa = reveal(t, 0.5 + i * 0.6, 0.65, ease_back)
        x = 180 + i * 810
        y = 230
        d.rounded_rectangle([x, y, x + 720, y + 380], radius=24,
                            fill=blend(BG, CARD, aa), outline=blend(BG, col, aa), width=4)
        d.rounded_rectangle([x + 40, y + 40, x + 40 + 110, y + 40 + 110], radius=20,
                            fill=blend(BG, light, aa))
        d.text((x + 95, y + 95), arw, font=font(52, "b"), fill=blend(BG, col, aa), anchor="mm")
        d.text((x + 180, y + 78), cmd, font=font(40, "b", mono=True),
               fill=blend(BG, col, aa), anchor="la")
        d.text((x + 180, y + 132), t1, font=font(24), fill=blend(BG, INK_SOFT, aa), anchor="la")
        d.text((x + 40, y + 220), t2, font=font(25), fill=blend(BG, INK_SOFT, aa), anchor="la")

    # 首次 push 提示
    if t > 2.6:
        aa = reveal(t, 2.6, 0.6)
        d.rounded_rectangle([180, 660, 1740, 748], radius=16, fill=blend(BG, AMBER_L, aa),
                            outline=blend(BG, AMBER, aa), width=3)
        d.text((220, 704), "第一次 push 会要求登录授权，跟着提示走就行；"
                           "也可以先用 git remote -v 检查远程地址是否配对",
               font=font(26), fill=blend(BG, INK_SOFT, aa), anchor="lm")

    # 节奏建议
    if t > 3.8:
        aa = reveal(t, 3.8, 0.7)
        d.rounded_rectangle([180, 790, 1740, 1010], radius=22, fill=blend(BG, CARD, aa),
                            outline=blend(BG, TEAL, aa), width=3)
        d.text((220, 822), "养成这个节奏", font=font(30, "b"),
               fill=blend(BG, TEAL_D, aa), anchor="la")
        tips = [("开始工作前", "先 pull 一下", TEAL),
                ("写完一小段", "就 commit 一次", GREEN),
                ("凑够一小段", "就 push 上去", ORANGE)]
        for i, (k, v, col) in enumerate(tips):
            da = reveal(t, 4.4 + i * 0.4, 0.5)
            x = 220 + i * 500
            d.rounded_rectangle([x, 886, x + 460, 986], radius=14, fill=blend(BG, BG_ALT, da))
            d.text((x + 24, 914), k, font=font(21), fill=blend(BG, MUTED, da), anchor="la")
            d.text((x + 24, 948), v, font=font(25, "b"), fill=blend(BG, col, da), anchor="la")
        aa2 = reveal(t, 5.8, 0.6)
        d.text((W // 2, 1032), "不要攒一个星期才推一次 —— 一旦出问题很难收拾，同伴也没法配合",
               font=font(24), fill=blend(BG, RED, aa2), anchor="mm")


# ================================================================ 15 冲突
def draw_conflict(img, d, t, dur, prog):
    a = reveal(t, 0.15, 0.6)
    d.text((W // 2, 76), "新手最怕的「冲突」，其实只是一个路口",
           font=font(52, "b"), fill=blend(BG, INK, a), anchor="ma")

    # 左：冲突文件
    f = font(20, mono=True)
    fx0, fy0, fx1, fy1 = 120, 175, 900, 700
    d.rounded_rectangle([fx0, fy0, fx1, fy1], radius=16, fill=(252, 251, 249),
                        outline=BORDER_D, width=3)
    d.rounded_rectangle([fx0, fy0, fx1, fy0 + 46], radius=16, fill=(238, 234, 226))
    d.rectangle([fx0, fy0 + 28, fx1, fy0 + 46], fill=(238, 234, 226))
    d.text((fx0 + 24, fy0 + 23), "index.html  ←  Git 停下来等你决定",
           font=font(21), fill=MUTED, anchor="lm")

    rows = [
        ("<p>欢迎来到我的网站</p>", "plain"),
        ("<<<<<<< HEAD", "mark"),
        ("<h1>我的主页</h1>", "mine"),
        ("=======", "mark"),
        ("<h1>Welcome</h1>", "theirs"),
        (">>>>>>> 7b1e4c2 同伴的提交", "mark"),
        ("<footer>2026</footer>", "plain"),
    ]
    for i, (txt, kind) in enumerate(rows):
        aa = reveal(t, 0.7 + i * 0.3, 0.5)
        y = fy0 + 76 + i * 66
        bgc = {"mark": (250, 240, 214), "mine": BLUE_L, "theirs": ORANGE_L, "plain": (252, 251, 249)}[kind]
        col = {"mark": (150, 110, 20), "mine": BLUE, "theirs": ORANGE_D, "plain": INK_SOFT}[kind]
        d.rounded_rectangle([fx0 + 22, y, fx1 - 22, y + 52], radius=8,
                            fill=blend((252, 251, 249), bgc, aa))
        d.text((fx0 + 40, y + 26), txt, font=f, fill=blend((252, 251, 249), col, aa), anchor="lm")

    # 图例
    if t > 2.6:
        aa = reveal(t, 2.6, 0.6)
        d.text((fx0 + 24, fy1 - 0), "", font=f, fill=BG)
        d.rounded_rectangle([fx0 + 22, fy1 + 20, fx1 - 22, fy1 + 96], radius=12,
                            fill=blend(BG, BLUE_L, aa))
        d.text((fx0 + 44, fy1 + 44), "HEAD 那一段 = 你的改动", font=font(22, "b"),
               fill=blend(BG, BLUE, aa), anchor="la")
        d.text((fx0 + 44, fy1 + 76), "编号那一段 = 同伴的改动", font=font(22, "b"),
               fill=blend(BG, ORANGE_D, aa), anchor="la")

    # 右侧：三步骤
    rx = 990
    steps = [
        ("1", "打开这个文件", "把不要的删掉，把要的留下", BLUE),
        ("2", "连记号一起删掉", "<<<<<<<、=======、>>>>>>> 都不要", AMBER),
        ("3", "git add + commit", "再 push 一次，冲突就解决了", GREEN),
    ]
    for i, (num, t1, t2, col) in enumerate(steps):
        aa = reveal(t, 1.4 + i * 0.7, 0.6)
        y = 195 + i * 168
        d.rounded_rectangle([rx, y, 1800, y + 140], radius=18, fill=blend(BG, CARD, aa),
                            outline=blend(BG, col, aa), width=3)
        d.ellipse([rx + 30, y + 34, rx + 86, y + 90], fill=blend(BG, col, aa))
        d.text((rx + 58, y + 62), num, font=font(28, "b"),
               fill=blend(BG, (255, 255, 255), aa), anchor="mm")
        d.text((rx + 112, y + 44), t1, font=font(28, "b"), fill=blend(BG, INK, aa), anchor="la")
        d.text((rx + 112, y + 92), t2, font=font(22), fill=blend(BG, MUTED, aa), anchor="la")

    if t > 4.4:
        aa = reveal(t, 4.4, 0.6)
        d.text((rx, 730), "别慌，这不是出错，只是 Git 让你做个选择",
               font=font(24, "b"), fill=blend(BG, TEAL_D, aa), anchor="la")

    if t > 5.2:
        aa = reveal(t, 5.2, 0.7)
        d.rounded_rectangle([120, 800, 1800, 1000], radius=20, fill=blend(BG, AMBER_L, aa),
                            outline=blend(BG, AMBER, aa), width=3)
        d.text((170, 830), "最省事的办法", font=font(28, "b"),
               fill=blend(BG, (150, 100, 20), aa), anchor="la")
        d.text((170, 886), "遇到冲突先别急着删别人的代码 —— "
                           "发消息问同伴一句「你这段是为什么改的」，往往比对着记号猜快得多。",
               font=font(26), fill=blend(BG, INK_SOFT, aa), anchor="la")
        d.text((170, 940), "团队里更常见的做法：按功能分工，尽量别两个人同时改同一个文件。",
               font=font(26), fill=blend(BG, INK_SOFT, aa), anchor="la")


# ================================================================ 16 结尾
def draw_outro(img, d, t, dur, prog):
    a = reveal(t, 0.15, 0.7)
    d.text((W // 2, 78), "快速回顾", font=font(54, "b"),
           fill=blend(BG, INK, a), anchor="ma")

    items = [
        ("核心模型", "工作区 → 暂存区 → 仓库", TEAL, "改文件 / add / commit"),
        ("日常三步", "改 → git add → git commit", ORANGE, "每次只讲一件事"),
        ("看历史", "git log  /  git log --oneline", BLUE, "diff 看具体改了哪几行"),
        ("要回退", "git restore  /  git commit --amend", PURPLE, "别急着用 reset --hard"),
        ("新尝试", "git branch + git checkout + git merge", GREEN, "失败了删掉即可"),
        ("跟人协作", "git pull  →  commit  →  git push", AMBER, "每天先 pull 再动手"),
    ]
    for i, (k, v, col, note) in enumerate(items):
        aa = reveal(t, 0.6 + i * 0.75, 0.55)
        row = i // 3
        col_i = i % 3
        x = 130 + col_i * 570
        y = 220 + row * 230
        d.rounded_rectangle([x, y, x + 530, y + 190], radius=20,
                            fill=blend(BG, CARD, aa), outline=blend(BG, col, aa), width=3)
        d.rounded_rectangle([x, y, x + 530, y + 10], radius=5, fill=blend(BG, col, aa))
        d.text((x + 32, y + 34), k, font=font(27, "b"), fill=blend(BG, INK, aa), anchor="la")
        d.text((x + 32, y + 82), v, font=font(22, mono=True),
               fill=blend(BG, col, aa), anchor="la")
        d.text((x + 32, y + 134), note, font=font(20),
               fill=blend(BG, MUTED, aa), anchor="la")

    if t > 6.0:
        aa = reveal(t, 6.0, 0.8)
        d.rounded_rectangle([W // 2 - 720, 800, W // 2 + 720, 950], radius=20,
                            fill=blend(BG, (28, 26, 24), aa))
        d.text((W // 2, 838), "不用背命令。卡住了就敲 git status，它会告诉你下一步。",
               font=font(28), fill=blend(BG, (250, 248, 244), aa), anchor="ma")
        d.text((W // 2, 892), "现在就找一个你最常用的文件夹，git init 一下吧。",
               font=font(28, "b"), fill=blend(BG, ORANGE, aa), anchor="ma")


RENDERERS = {
    "hook": draw_hook,
    "savepoint": draw_savepoint,
    "manual_pain": draw_manual_pain,
    "git_intro": draw_git_intro,
    "three_areas": draw_three_areas,
    "install": draw_install,
    "init": draw_init,
    "commit": draw_commit,
    "log": draw_log,
    "undo": draw_undo,
    "branch_concept": draw_branch_concept,
    "branch_do": draw_branch_do,
    "remote": draw_remote,
    "push_pull": draw_push_pull,
    "conflict": draw_conflict,
    "outro": draw_outro,
}
