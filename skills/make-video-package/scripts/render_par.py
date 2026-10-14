# -*- coding: utf-8 -*-
"""并行逐帧渲染：把每场分给一个独立进程，同时跑。

为什么需要它 —— render.py 是单线程的：
  Python + Pillow 逐帧绘制（纯 CPU，不走 GPU），画完 pipe 给本进程的 ffmpeg。
  一个渲染进程在 8 核机器上只吃约 1.4 个核（Python 主循环 ~95% + ffmpeg ~42%），
  其余核心全闲着。实测 load average 8.8 而实际占用 1.4 核。

场景之间完全独立（各自有配音时长、各自的 Warp、各自的输出文件），
所以天然可以并行 —— 每个 worker 处理一场，无共享状态。

用法：
    python3 render_par.py <durs.json> <输出目录> [场景过滤] [worker 数]

    场景过滤：all 或逗号分隔的 sid，例如 s06_crawl,s07_speed
    worker 数：默认 = min(场数, CPU 物理核数)

与 render.py 的兼容性：
  产出的文件名、manifest 格式完全一致，build_final.py / make_srt.py 不用改。
"""
import json
import multiprocessing as mp
import os
import sys
import time

# ---------------------------------------------------------------- worker
def render_one(args):
    """在独立进程里渲染一场。返回 (sid, 输出路径, 用时)。"""
    idx, sc, dur, outdir = args
    import time as _t
    t0 = _t.time()

    import engine
    import scenes
    from timing import Warp

    # 每个 worker 必须自己 setup：主题色在导入时绑定，
    # 子进程不会继承父进程的绑定结果（spawn 模式下也是重新导入）。
    scenes.setup()

    LEAD, TAIL = 0.30, 0.70
    fn = scenes.RENDERERS[sc["render"]]
    warp = Warp(fn, sc["narration"], dur)
    engine.SCENE_NOMINAL_END = warp.last_nominal if warp.knots else None

    total = LEAD + dur + TAIL
    nframes = int(round(total * engine.FPS))
    outp = os.path.join(outdir, f"{idx:02d}_{sc['sid']}.mp4")

    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{engine.W}x{engine.H}", "-r", str(engine.FPS), "-i", "pipe:0",
        "-an",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
        "-pix_fmt", "yuv420p", "-g", str(engine.FPS * 2),
        outp,
    ]
    import subprocess
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for i in range(nframes):
            t = i / engine.FPS
            local_t = t - LEAD
            img, d = scenes.new_frame()
            if local_t < 0:
                engine.SCENE_REAL_T = None
                engine.header(img, d, sc["chapter"], 0.0)
            else:
                engine.SCENE_REAL_T = local_t
                engine.SCENE_REAL_DUR = dur
                fn(img, d, warp(local_t), dur, local_t / max(dur, 0.001))
                engine.header(img, d, sc["chapter"],
                              min(1.0, local_t / max(dur, 0.001)))
            p.stdin.write(img.tobytes())
    finally:
        p.stdin.close()
        p.wait()

    return sc["sid"], outp, _t.time() - t0


def main():
    durs = json.load(open(sys.argv[1]))
    outdir = sys.argv[2]
    only = None
    if len(sys.argv) > 3 and sys.argv[3] != "all":
        only = set(sys.argv[3].split(","))
    workers = int(sys.argv[4]) if len(sys.argv) > 4 else None

    # 建目录等工作必须在 fork 之前做，避免子进程竞争
    os.makedirs(outdir, exist_ok=True)

    # 场景列表要在父进程读好（content.py 有主题配置，只读一次）
    from content import SCENES
    jobs = []
    for i, sc in enumerate(SCENES):
        if only and sc["sid"] not in only:
            continue
        jobs.append((i, sc, durs[sc["sid"]], outdir))

    if not jobs:
        print("没有匹配的场景")
        return

    nproc = mp.cpu_count()          # 含超线程/能效核
    try:
        phys = len(os.sched_getaffinity(0))       # Linux
    except AttributeError:
        phys = nproc                              # macOS 无此接口
    auto = max(1, min(len(jobs), phys))
    nw = workers or auto

    # 长场优先：先派出去，避免末尾剩一个长场把总时间拖长
    jobs.sort(key=lambda j: -j[2])
    # 排序后要复原输出文件名里的序号，所以按 idx 重排回稳定顺序处理结果
    t0 = time.time()
    print(f"并行渲染 {len(jobs)} 场，worker={nw}（可用核 {nproc}）", flush=True)

    results = []
    # 用 spawn 而非 fork：Pillow / fontTools 在 fork 后容易出状态问题，
    # 且 render_one 内部本来就会重新 import + setup，spawn 的开销可以接受。
    ctx = mp.get_context("spawn")
    with ctx.Pool(processes=nw) as pool:
        for sid, outp, el in pool.imap_unordered(render_one, jobs):
            results.append((sid, outp, el))
            print(f"  ✓ {sid:18s} {el:6.1f}s -> {os.path.basename(outp)}", flush=True)

    wall = time.time() - t0
    cpu_sum = sum(r[2] for r in results)
    print(f"\n完成 {len(results)} 场")
    print(f"  墙钟时间   {wall:7.1f}s = {wall/60:.2f} min")
    print(f"  单场耗时和 {cpu_sum:7.1f}s = {cpu_sum/60:.2f} min")
    print(f"  并行加速比 {cpu_sum/wall:5.2f}x")

    manifest = [dict(idx=i, sid=s, file=p, render_sec=e)
                for i, (s, p, e) in enumerate(sorted(
                    results, key=lambda r: r[1]))]
    tag = "part" if only else "all"
    with open(os.path.join(outdir, f"manifest_{tag}.json"), "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
