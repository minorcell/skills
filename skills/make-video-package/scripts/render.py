# -*- coding: utf-8 -*-
"""逐帧渲染并直接管道给 ffmpeg，避免落盘大量 PNG。"""
import json
import os
import subprocess
import sys

from project import configure_source

configure_source()

import engine
from engine import W, H, FPS, LEAD, TAIL, header
import scenes
from content import SCENES
from timing import Warp

# 应用 content.py 里的主题。必须在任何绘制之前调用：
# 它会把 engine 与 scenes 里的颜色名重新绑定到新主题。
scenes.setup()

def render_scene(sc, dur, out_path, progress_base, progress_span):
    """把单场景渲染成无声的 mp4。dur 为该场配音时长。"""
    fn = scenes.RENDERERS[sc["render"]]
    chapter = sc["chapter"]

    warp = Warp(fn, sc["narration"], dur)
    # 终端脚本拉伸到本场最后一个名义节点
    engine.SCENE_NOMINAL_END = warp.last_nominal if warp.knots else None

    total = LEAD + dur + TAIL
    nframes = int(round(total * FPS))

    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0",
        "-an",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
        "-pix_fmt", "yuv420p", "-g", str(FPS * 2),
        out_path,
    ]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for i in range(nframes):
            t = i / FPS
            local_t = t - LEAD
            img, d = scenes.new_frame()
            if local_t < 0:
                engine.SCENE_REAL_T = None
                prog = progress_base
                header(img, d, chapter, prog)
            else:
                prog = progress_base + progress_span * (local_t / max(dur, 0.001))
                header(img, d, chapter, min(1.0, prog))
                engine.SCENE_REAL_T = local_t
                engine.SCENE_REAL_DUR = dur
                nom = warp(local_t)
                fn(img, d, nom, dur, local_t / max(dur, 0.001))
            p.stdin.write(img.tobytes())
    finally:
        p.stdin.close()
        p.wait()
    return total


def main():
    durs = json.load(open(sys.argv[1]))
    outdir = sys.argv[2]
    only = None
    if len(sys.argv) > 3 and sys.argv[3] != "all":
        only = set(sys.argv[3].split(","))
    os.makedirs(outdir, exist_ok=True)

    total_all = sum(durs[s["sid"]] for s in SCENES)
    acc = 0.0
    manifest = []
    for i, sc in enumerate(SCENES):
        dur = durs[sc["sid"]]
        pb = acc / total_all
        span = dur / total_all
        acc += dur
        if only and sc["sid"] not in only:
            continue
        outp = os.path.join(outdir, f"{i:02d}_{sc['sid']}.mp4")
        t = render_scene(sc, dur, outp, pb, span)
        manifest.append(dict(idx=i, sid=sc["sid"], file=outp, dur=dur, total=t))
        print(f"[{i+1}/{len(SCENES)}] {sc['sid']:16s} {dur:6.2f}s -> {outp}", flush=True)
    with open(os.path.join(outdir, f"manifest_{only and 'part' or 'all'}.json"), "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print("ALL DONE")


if __name__ == "__main__":
    main()
