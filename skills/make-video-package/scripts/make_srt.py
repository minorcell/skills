# -*- coding: utf-8 -*-
"""生成 SRT 字幕。

优先使用 edge-tts 的 SentenceBoundary 时间戳（逐句精确）；
拿不到时间戳时（本地 TTS 兜底）才退回按字数比例估算。

字幕的全局时刻必须算上场景之间的留白：
    第 i 场开始 = 前面所有场的 (LEAD + 配音时长 + TAIL) 之和
留白值统一从 engine.py 读取。
"""
import json
import os
import subprocess
import sys

from project import configure_source

configure_source()

from content import SCENES  # noqa: E402
from engine import LEAD, TAIL  # noqa: E402


def dur(p):
    o = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", p], capture_output=True, text=True)
    try:
        return float(o.stdout.strip())
    except ValueError:
        return 0.0


def ts(sec):
    """SRT 时间戳：HH:MM:SS,mmm"""
    if sec < 0:
        sec = 0
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def split_sentences(text):
    out, buf = [], ""
    for ch in text:
        buf += ch
        if ch in "。！？":
            if buf.strip():
                out.append(buf.strip())
            buf = ""
    if buf.strip():
        out.append(buf.strip())
    return out


def load_marks(audio_dir, sid, narration, ad):
    """取该场逐句时间戳。优先读 tts.py 写出的 marks 文件。"""
    mp = os.path.join(audio_dir, sid + ".marks.json")
    if os.path.exists(mp):
        try:
            with open(mp, encoding="utf-8") as f:
                marks = json.load(f)
            if marks:
                return [(float(a), float(b), t) for a, b, t in marks]
        except (ValueError, TypeError):
            pass
    # 兜底：按字数比例估算
    sents = split_sentences(narration)
    lens = [max(1, len(s)) for s in sents]
    tot = sum(lens)
    out, t = [], 0.0
    for s, L in zip(sents, lens):
        d = ad * L / tot
        out.append((t, d, s))
        t += d
    return out


def main():
    audio_dir = sys.argv[1] if len(sys.argv) > 1 else "/tmp/audio"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "/tmp/sub.srt"

    entries = []
    clock = LEAD
    for i, sc in enumerate(SCENES):
        sid = sc["sid"]
        if i > 0:
            clock += TAIL + LEAD          # 上一场的留白 + 本场的开场留白
        ad = dur(os.path.join(audio_dir, sid + ".mp3"))
        for start, span, text in load_marks(audio_dir, sid, sc["narration"], ad):
            a = clock + start + 0.05
            b = clock + start + span - 0.05
            if b <= a:
                b = a + 0.4
            entries.append((a, b, text))
        clock += ad

    with open(out_path, "w", encoding="utf-8") as f:
        for n, (a, b, txt) in enumerate(entries, 1):
            f.write(f"{n}\n{ts(a)} --> {ts(b)}\n{txt}\n\n")
    print(f"wrote {out_path}  {len(entries)} entries  "
          f"总时长 {clock:.1f}s = {clock / 60:.2f} min")


if __name__ == "__main__":
    main()
