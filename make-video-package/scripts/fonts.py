# -*- coding: utf-8 -*-
"""跨平台中文字体解析。

两个必须解决的坑：
  1. Linux 与 macOS 的字体路径完全不同，不能写死。
  2. 纯等宽字体（Menlo / SF Mono / Monaco / DejaVu Sans Mono）几乎都没有
     中文字形。终端演示里一旦出现汉字就会渲染成空方块。
     所以终端文字走「中英分段混排」：ASCII 用等宽字体，汉字用中文字体。

用法：
    from fonts import F, mono_runs, has_cjk
    f = F.sans(40, bold=True)
"""
import functools
import glob
import os

from PIL import ImageFont

# ---------------------------------------------------------------- 候选表
# (路径, ttc 内索引)。按优先级排列，第一个能渲染汉字的胜出。
SANS_CANDIDATES = [
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 2),   # Linux
    ("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 2),
    ("/System/Library/Fonts/Hiragino Sans GB.ttc", 0),               # macOS
    ("/System/Library/Fonts/STHeiti Light.ttc", 0),
    ("/System/Library/Fonts/Supplemental/Songti.ttc", 0),
    ("/Library/Fonts/Arial Unicode.ttf", 0),
    ("C:/Windows/Fonts/msyh.ttc", 0),                                # Windows
    ("C:/Windows/Fonts/simhei.ttf", 0),
]

SANS_BOLD_CANDIDATES = [
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 2),
    ("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc", 2),
    ("/System/Library/Fonts/Hiragino Sans GB.ttc", 1),               # W6 作粗体
    ("/System/Library/Fonts/STHeiti Medium.ttc", 0),
    ("/System/Library/Fonts/Supplemental/Songti.ttc", 1),
    ("/Library/Fonts/Arial Unicode.ttf", 0),
    ("C:/Windows/Fonts/msyhbd.ttc", 0),
]

# 等宽：只要 ASCII 等宽即可，汉字会由 SANS 兜底。
MONO_CANDIDATES = [
    ("/usr/share/fonts/opentype/noto/NotoSansMonoCJK-Regular.ttc", 2),
    ("/System/Library/Fonts/Menlo.ttc", 0),
    ("/System/Library/Fonts/SFNSMono.ttf", 0),
    ("/System/Library/Fonts/Monaco.ttf", 0),
    ("/Library/Fonts/Andale Mono.ttf", 0),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 0),
    ("C:/Windows/Fonts/consola.ttf", 0),
]

_PROBE = "中文字形测试"
# 可能带中文字形的等宽字体藏在系统资源里，扫一遍当兜底（macOS AssetsV2）。
_MONO_CJK_GLOBS = [
    "/System/Library/AssetsV2/**/BIZ_UDGothic.ttc",
    "/System/Library/AssetsV2/**/OsakaMono.ttf",
]


def _usable(path, index, size=32, probe=_PROBE):
    """能打开、且汉字宽度合理（不是 0、不是豆腐块）才算可用。"""
    try:
        f = ImageFont.truetype(path, size, index=index)
    except Exception:
        return None
    try:
        w = f.getlength(probe)
    except Exception:
        return None
    # 汉字宽度应在 0.7em~1.4em 之间；过小说明回退成了别的字体
    per = w / len(probe)
    if size * 0.7 <= per <= size * 1.4:
        return f
    return None


def _usable_mono(path, index, size=32):
    """等宽字体只要 ASCII 等宽且能打开即可，不要求含汉字（汉字由 SANS 兜底）。"""
    try:
        f = ImageFont.truetype(path, size, index=index)
    except Exception:
        return False
    try:
        ws = [f.getlength(c) for c in "iWm."]
    except Exception:
        return False
    return ws[0] > 0 and (max(ws) - min(ws)) < 0.6


def _first_usable(cands, size=32, kind="sans"):
    for path, index in cands:
        if not os.path.exists(path):
            continue
        ok = (_usable_mono(path, index, size) if kind == "mono"
              else _usable(path, index, size) is not None)
        if ok:
            return path, index
    if kind == "mono":
        raise RuntimeError("找不到等宽字体，请安装 Menlo / DejaVu Sans Mono 之一。")
    raise RuntimeError(
        "找不到可用的中文字体。请安装 Noto Sans CJK（Linux："
        "apt install fonts-noto-cjk）后重试。")


@functools.lru_cache(maxsize=1)
def resolved():
    """返回 (sans_path, sans_idx, bold_path, bold_idx, mono_path, mono_idx)。"""
    s = _first_usable(SANS_CANDIDATES)
    try:
        b = _first_usable(SANS_BOLD_CANDIDATES)
    except RuntimeError:
        b = s                       # 没有粗体就退回常规体
    m = _first_usable(MONO_CANDIDATES, kind="mono")
    # 若等宽字体本身含中文（Linux 的 Noto Sans Mono CJK），那是最优解
    m = _upgrade_mono(m)
    return (*s, *b, *m)


def _upgrade_mono(mono):
    """等宽字体若自带中文就用它，否则保持 ASCII 等宽 + 中文兜底。"""
    if _usable(mono[0], mono[1]) and has_cjk(mono[0], mono[1]):
        return mono
    for pat in _MONO_CJK_GLOBS:
        for p in glob.glob(pat, recursive=True):
            if has_cjk(p, 0):
                return (p, 0)
    return mono


def has_cjk(path, index=0, size=32):
    """判断字体文件是否真的覆盖汉字（比较汉字与私用区码位的渲染宽度）。"""
    try:
        f = ImageFont.truetype(path, size, index=index)
    except Exception:
        return False
    try:
        # 私用区码位 PUA 在缺字形时通常返回与本字体一致的『回退宽度』，
        # 而真含汉字时两者宽度会有差别。
        han = f.getlength("汉")
        uni = f.getlength("\ue000")
        if abs(han - uni) > 0.6:
            return True
    except Exception:
        pass
    # 退一步：渲染出来看像素是否与「豆腐块」不同——比较两个不同汉字的字形
    try:
        a = f.getlength("汉")
        b = f.getlength("字")
        if a > 0 and b > 0 and abs(a - b) < 0.01:
            # 宽度相同不足以证明，改用 mask 比较
            from PIL import Image, ImageDraw
            def mask(ch):
                im = Image.new("L", (size * 2, size * 2), 0)
                ImageDraw.Draw(im).text((2, 2), ch, font=f, fill=255)
                return im.tobytes()
            return mask("汉") != mask("\ue000") and mask("汉") != mask("字")
    except Exception:
        pass
    return False


# ---------------------------------------------------------------- 字体工厂
class _Fonts:
    def __init__(self):
        sp, si, bp, bi, mp, mi = resolved()
        self.sans_path, self.sans_idx = sp, si
        self.bold_path, self.bold_idx = bp, bi
        self.mono_path, self.mono_idx = mp, mi

    def sans(self, size, bold=False):
        @functools.lru_cache(maxsize=512)
        def _f(sz, b):
            p, i = (self.bold_path, self.bold_idx) if b else (self.sans_path, self.sans_idx)
            return ImageFont.truetype(p, sz, index=i)
        return _f(size, bold)

    def mono(self, size):
        @functools.lru_cache(maxsize=512)
        def _f(sz):
            return ImageFont.truetype(self.mono_path, sz, index=self.mono_idx)
        return _f(size)


F = _Fonts()


# ---------------------------------------------------------------- 中英混排
def _is_cjk(ch):
    o = ord(ch)
    return (0x2E80 <= o <= 0x9FFF) or (0xF900 <= o <= 0xFAFF) or \
           (0xFF00 <= o <= 0xFFEF) or (0x3000 <= o <= 0x303F)


def mono_runs(text):
    """把字符串切成 [(kind, segment)]，kind 为 'lat' 或 'cjk'。

    终端文字用等宽字体排 ASCII，用中文等宽/常规字体排汉字，
    两者宽度都按 1:2 的网格对齐，视觉上仍然是等宽终端。
    """
    runs = []
    cur, kind = "", None
    for ch in text:
        k = "cjk" if _is_cjk(ch) else "lat"
        if kind is None or k == kind:
            cur += ch
            kind = k
        else:
            runs.append((kind, cur))
            cur, kind = ch, k
    if cur:
        runs.append((kind, cur))
    return runs


def text_width(draw, text, size, mono=False, bold=False):
    """混排宽度：ASCII 用等宽字体量，汉字用中文字体量。"""
    if not mono:
        return draw.textlength(text, font=F.sans(size, bold))
    fm, fc = F.mono(size), F.sans(size)
    total = 0.0
    for kind, seg in mono_runs(text):
        total += draw.textlength(seg, font=(fc if kind == "cjk" else fm))
    return total


def draw_mono(draw, xy, text, size, fill, cjk_fill=None):
    """在 xy 处混排绘制终端文字，返回结束 x 坐标。

    汉字宽度按两个 ASCII 格对齐（等宽终端里中文占两格），
    这样列对齐不会被汉字打乱。
    """
    fm, fc = F.mono(size), F.sans(size)
    x, y = xy
    cell = draw.textlength("M", font=fm)
    for kind, seg in mono_runs(text):
        if kind == "cjk":
            # 逐字推进，保证每个汉字正好占两格
            for ch in seg:
                draw.text((x, y), ch, font=fc, fill=cjk_fill or fill)
                x += cell * 2
        else:
            draw.text((x, y), seg, font=fm, fill=fill)
            x += draw.textlength(seg, font=fm)
    return x


def mono_advance(draw, text, size):
    """单行混排文字的前进宽度（用于换行/截断计算）。"""
    fm, fc = F.mono(size), F.sans(size)
    cell = draw.textlength("M", font=fm)
    total = 0.0
    for kind, seg in mono_runs(text):
        total += cell * 2 * len(seg) if kind == "cjk" else draw.textlength(seg, font=fm)
    return total


if __name__ == "__main__":
    sp, si, bp, bi, mp, mi = resolved()
    print("sans :", sp, si)
    print("bold :", bp, bi)
    print("mono :", mp, mi)
    print("mono 自带中文:", has_cjk(mp, mi))
