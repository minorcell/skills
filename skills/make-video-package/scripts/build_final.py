# -*- coding: utf-8 -*-
"""把各场景片段与配音合成为成片。

用法：
    python3 build_final.py <输出.mp4> [视频片段目录] [配音目录]
默认视频片段目录 /tmp/vid，配音目录 /tmp/audio。
"""
import glob
import os
import subprocess
import sys

from project import configure_source

configure_source()

from content import SCENES  # noqa: E402
from engine import LEAD  # noqa: E402


def dur(p):
    o = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", p], capture_output=True, text=True)
    try:
        return float(o.stdout.strip())
    except ValueError:
        raise SystemExit(f"读不到时长，文件缺失或损坏：{p}")


def main():
    out_final = sys.argv[1] if len(sys.argv) > 1 else "/tmp/final.mp4"
    vid_dir = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("VID_DIR", "/tmp/vid")
    aud_dir = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("AUD_DIR", "/tmp/audio")
    work = os.path.dirname(os.path.abspath(out_final))

    segs = []
    for i, sc in enumerate(SCENES):
        sid = sc["sid"]
        vids = glob.glob(f"{vid_dir}/{i:02d}_{sid}.mp4")
        if not vids:
            raise SystemExit(f"找不到片段 {vid_dir}/{i:02d}_{sid}.mp4；"
                             f"先跑 render.py")
        vp = vids[0]
        ap = f"{aud_dir}/{sid}.mp3"
        if not os.path.exists(ap):
            raise SystemExit(f"找不到配音 {ap}；先跑 tts.generate()")
        ad = dur(ap)
        total = dur(vp)
        out = f"{work}/seg_{i:02d}.mp4"
        fade_st = max(0.1, total - 0.45)
        vf = (f"[0:v]fade=t=in:st=0:d=0.35,"
              f"fade=t=out:st={fade_st:.3f}:d=0.45,format=yuv420p[v]")
        af = (f"[1:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)},"
              f"apad,atrim=0:{total:.3f},"
              f"afade=t=out:st={fade_st:.3f}:d=0.45,"
              f"aformat=channel_layouts=stereo[a]")
        cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
               "-i", vp, "-i", ap,
               "-filter_complex", vf + ";" + af,
               "-map", "[v]", "-map", "[a]",
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
               "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
               "-t", f"{total:.3f}", out]
        subprocess.run(cmd, check=True)
        segs.append(out)
        print(f"{sid:16s} v={total:6.2f} a={ad:5.2f} -> {out}", flush=True)

    lst = f"{work}/seglist.txt"
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{s}'\n")

    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", out_final], check=True)
    print("FINAL:", out_final, f"{dur(out_final):.2f}s = {dur(out_final)/60:.2f} min")


if __name__ == "__main__":
    main()
