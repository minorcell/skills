# -*- coding: utf-8 -*-
"""把场景的「名义时间轴」对齐到配音的「句子节拍」。

思路：
  * 场景代码里写的都是名义时间（比如 t > 5.8 出现某个元素）。
  * 配音是逐句朗读的，每句的开始时刻可以按字数比例算出来。
  * 把场景里第 j 个动画节点，挪到第 j 句开始的那一刻；
    同一段内部动画按自然速度（>=1x）播放，播完就保持，
    直到下一句开始再触发下一个节点。
这样每个视觉元素都恰好在该句念到的时候出现，既不会卡住，也不会被截断。
"""
import inspect
import re
import functools

# 从场景函数源码里抠出所有"名义时间节点"
PATTERNS = [
    re.compile(r"reveal\(\s*t\s*,\s*([0-9]+(?:\.[0-9]+)?)"),
    re.compile(r"clamp01\(\s*\(\s*t\s*-\s*([0-9]+(?:\.[0-9]+)?)\s*\)"),
    re.compile(r"\bt\s*>\s*([0-9]+(?:\.[0-9]+)?)"),
    re.compile(r"if\s+([0-9]+(?:\.[0-9]+)?)\s*<\s*t\s*<"),
]
TAIL_PAT = re.compile(r"min\(1\.0,\s*\(\s*t\s*-\s*([0-9]+(?:\.[0-9]+)?)\s*\)")

# 画面在前百分之多少的时长里搭完，之后保持完整画面陪讲。
# 太小 → 元素挤在一起；太大 → 前半段稀稀拉拉、大片空白。
#
# 固定比例在长场景上会出问题：一段 40 秒的戏，62% 之后有 15 秒画面完全不动，
# 观众会以为视频卡了。所以构建窗口按时长自适应 —— 场景越长，搭得越久，
# 但至少给结尾留 BUILD_TAIL_MIN 秒的余量。
BUILD_FRACTION = 0.62
BUILD_FRACTION_MAX = 0.88      # 上限，避免把元素拖到最后
BUILD_TAIL_MIN = 5.0           # 结尾至少保留这么多秒的推进余量
MAX_GAP = 4.5                  # 锚点之间允许的最大静止间隔（秒）


def build_fraction(dur):
    """按场景时长算构建窗口比例。"""
    if dur <= 0:
        return BUILD_FRACTION
    # 每多 1 秒，窗口往后延一点点：够长就不靠固定比例
    f = BUILD_FRACTION + max(0.0, dur - 16.0) * 0.012
    # 保证末尾还有推进余量
    f = min(f, 1.0 - BUILD_TAIL_MIN / dur)
    return max(BUILD_FRACTION, min(BUILD_FRACTION_MAX, f))


def knots_of(fn):
    """返回场景里所有动画节点的名义时刻（去重升序）。

    先用源码解析兜底，再在 t=无穷大 处干跑一次场景，把 reveal() 实际收到的
    起始时刻全部录下来 —— 这样循环里生成的节点（比如 6 张卡片依次出现）
    也能被正确捕获，而源码解析只能看到字面量。
    """
    times = set()
    try:
        src = inspect.getsource(fn)
        for pat in PATTERNS + [TAIL_PAT]:
            for m in pat.finditer(src):
                times.add(round(float(m.group(1)), 3))
    except (OSError, TypeError):
        pass

    try:
        from PIL import Image
        import scenes as _scenes
        rec = []
        orig = _scenes.reveal

        def spy(t, start, dur=0.5, f=None):
            rec.append(round(float(start), 3))
            return orig(t, start, dur, f) if f is not None else orig(t, start, dur)

        _scenes.reveal = spy
        try:
            tiny = Image.new("RGB", (64, 64))
            from PIL import ImageDraw
            fn(tiny, ImageDraw.Draw(tiny), 1e6, 60.0, 1.0)
        finally:
            _scenes.reveal = orig
        times.update(rec)
    except Exception:
        pass

    return sorted(t for t in times if 0.05 < t < 900)


def sentence_spans(narration):
    """按句号/问号/叹号切句，返回 [(起始比例, 长度比例)]。"""
    parts, buf = [], ""
    for ch in narration:
        buf += ch
        if ch in "。！？":
            parts.append(buf.strip())
            buf = ""
    if buf.strip():
        parts.append(buf.strip())
    lens = [max(1, len(p)) for p in parts]
    tot = sum(lens)
    spans, acc = [], 0
    for L in lens:
        spans.append((acc / tot, L / tot))
        acc += L
    return spans, len(parts)


class Warp:
    """名义时间 -> 实际播放时间 的映射器。

    目标：每个视觉节点都在合适的时候出现，且整段讲话期间画面持续推进，
    不出现长时间静止。做法是把名义节点锚到「句子节拍」上；
    当日志节点太少、跟不上句子数量时，改为在整段时长上均匀铺开。
    """

    def __init__(self, fn, narration, real_dur):
        self.dur = max(real_dur, 0.2)
        self.knots = knots_of(fn)
        spans, nsent = sentence_spans(narration)
        self.nsent = nsent
        n = len(self.knots)
        self.anchors = []
        if n == 0:
            return

        sent_anchor = [s * self.dur for s, _ in spans]

        # 节点按名义时刻的先后顺序映射到句子节拍上。
        # 关键：同一段名义区间内的多个节点要均匀落在对应句子里，
        # 而不是挤在同一个锚点上。
        if n >= max(2, nsent * 0.6):
            A = [sent_anchor[min(int(round(i * (nsent - 1) / max(1, n - 1))), nsent - 1)]
                 for i in range(n)]
        else:
            # 节点比句子少 → 均匀铺满整段，避免长时间静止
            lo, hi = self.dur * 0.03, self.dur * 0.92
            A = [lo + (hi - lo) * i / max(1, n - 1) for i in range(n)]

        # 关键：把整组锚点压进 [0.03, build_fraction] 这段窗口。
        # 画面要在讲述过程中逐步搭好，最后用完整的图陪着讲完 —— 但不能搭得
        # 太早，否则长场景的尾部会长达十几秒毫无变化，看起来像卡住了。
        # 窗口比例随时长自适应（见 build_fraction）。
        lo, hi = self.dur * 0.03, self.dur * build_fraction(self.dur)
        if len(A) == 1:
            A = [lo]
        else:
            a0, a1 = A[0], A[-1]
            span = a1 - a0
            if span <= 0.01:
                A = [lo + (hi - lo) * i / (len(A) - 1) for i in range(len(A))]
            else:
                A = [lo + (hi - lo) * (a - a0) / span for a in A]

        # 保证严格递增
        for i in range(1, len(A)):
            if A[i] <= A[i - 1] + 0.12:
                A[i] = A[i - 1] + 0.12
        # 修正若把末尾推过头，就整体压回来
        if A and A[-1] > self.dur * 0.80:
            over = A[-1] - self.dur * 0.80
            A = [max(0.0, a - over) for a in A]

        # 节点在句子上会成簇（同一句里生成的好几个节点锚到同一时刻），
        # 结果是间隔极不均匀 —— 有的 0.1 秒，有的一下十几秒。
        # 超过 MAX_GAP 的间隔就是观众眼里的「卡住了」，所以一旦出现就
        # 放弃句子对齐，把整组锚点在窗口内均匀铺开。
        if len(A) >= 2:
            max_gap = max(A[i + 1] - A[i] for i in range(len(A) - 1))
            if max_gap > MAX_GAP:
                a, b = A[0], A[-1]
                A = [a + (b - a) * i / (len(A) - 1) for i in range(len(A))]
                # 均分后若仍超上限，就把窗口拉长到刚好够用
                if len(A) >= 2:
                    mg = max(A[i + 1] - A[i] for i in range(len(A) - 1))
                    if mg > MAX_GAP:
                        span_needed = MAX_GAP * (len(A) - 1)
                        end = min(self.dur * 0.95, A[0] + span_needed)
                        if end > A[0]:
                            A = [A[0] + (end - A[0]) * i / (len(A) - 1)
                                 for i in range(len(A))]
        self.anchors = A

    @property
    def last_nominal(self):
        return self.knots[-1] if self.knots else 0.0

    def __call__(self, t):
        """实际时间 t -> 名义时间。"""
        if not self.knots:
            return t
        k, A = self.knots, self.anchors
        if t < A[0]:
            # 开场：让第一个节点在其锚点时刻前刚好播完
            lead = min(A[0], 0.6)
            return max(0.0, k[0] - (A[0] - t) * (k[0] / max(lead, 0.01)))
        for i in range(len(k)):
            seg_start = A[i]
            seg_end_nom = k[i + 1] if i + 1 < len(k) else k[i] + 0.6
            seg_end_real = A[i + 1] if i + 1 < len(A) else self.dur
            if t < seg_end_real or i == len(k) - 1:
                span_nom = max(0.15, seg_end_nom - k[i])
                span_real = max(0.15, seg_end_real - seg_start)
                rate = max(1.0, span_nom / span_real)
                nom = k[i] + (t - seg_start) * rate
                return min(nom, seg_end_nom) if i + 1 < len(k) else nom
        return self.last_nominal
