# -*- coding: utf-8 -*-
"""配音合成：edge-tts 神经语音 + 逐句时间戳。

为什么用 edge-tts 而不是系统 TTS：
  edge-tts 的中文神经语音（晓晓 / 云希 等）是接近人声的成片音色，
  系统自带的 `say` / espeak 音色机械，不能用于正式发布。

关键能力：stream() 会返回 SentenceBoundary 事件，带精确的
offset/duration。字幕与画面节拍由它驱动，不再靠字数比例猜。

若 edge-tts 因微软端点调整而报 403，先 `pip install -U edge-tts`
（2026-10 那次端点迁移就是靠升级到 7.3.1 修好的）；仍不行则回落到
本地引擎——音色差，仅供预览，不要发布。
"""
import asyncio
import json
import os
import shutil
import subprocess

DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"   # 晓晓：女声，讲解向
DEFAULT_RATE = "+8%"                      # 讲解视频略快于默认语速
VOICES = {
    "female": "zh-CN-XiaoxiaoNeural",
    "male": "zh-CN-YunxiNeural",
    "female_news": "zh-CN-XiaoyiNeural",
    "male_calm": "zh-CN-YunjianNeural",
}


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path],
        capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 0.0


def split_sentences(text):
    """按中文句末标点切句，与 edge-tts 的 SentenceBoundary 粒度对齐。"""
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


# ---------------------------------------------------------------- edge-tts
async def _synth_one(text, path, voice, rate):
    """合成单段，返回 [(start_sec, dur_sec, sentence)]，并写出 mp3。"""
    import edge_tts

    c = edge_tts.Communicate(text, voice, rate=rate)
    marks, audio = [], bytearray()
    async for ev in c.stream():
        t = ev["type"]
        if t == "audio":
            audio += ev["data"]
        elif t == "SentenceBoundary":
            marks.append((ev["offset"] / 1e7, ev["duration"] / 1e7, ev["text"]))
    if len(audio) < 800:
        raise RuntimeError("合成结果过小，可能被服务端拒绝")
    with open(path, "wb") as f:
        f.write(audio)
    return marks


async def _synth_retry(text, path, voice, rate, attempts=4):
    last = None
    for i in range(attempts):
        try:
            return await _synth_one(text, path, voice, rate)
        except Exception as e:                       # 网络抖动 / 限流
            last = e
            print(f"    重试 {i + 1}/{attempts}: {type(e).__name__} {str(e)[:80]}")
            await asyncio.sleep(1.5 + i * 1.5)
    raise RuntimeError(f"配音合成失败：{last}")


# ---------------------------------------------------------------- 本地兜底
def _local_tts(text, path):
    """macOS `say` 兜底，音色仅够预览，不要用于发布。"""
    if not shutil.which("say"):
        raise RuntimeError("本地无可用 TTS；请先 pip install -U edge-tts")
    aiff = path + ".aiff"
    subprocess.run(["say", "-v", "Tingting", "-o", aiff, text], check=True)
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-i", aiff, "-c:a", "libmp3lame", "-b:a", "160k", path],
                   check=True)
    os.remove(aiff)
    # 本地引擎没有时间戳，返回空，由字幕模块按字数比例兜底
    return []


# ---------------------------------------------------------------- 对外接口
def determine_marks(narration, dur, marks):
    """确保每个场景都有可用的逐句时间。缺失时按字数比例估算。"""
    if marks:
        return marks
    sents = split_sentences(narration)
    lens = [max(1, len(s)) for s in sents]
    tot = sum(lens)
    out, t = [], 0.0
    for s, L in zip(sents, lens):
        d = dur * L / tot
        out.append((t, d, s))
        t += d
    return out


def generate(scenes, audio_dir, voice=DEFAULT_VOICE, rate=DEFAULT_RATE,
             allow_local_fallback=True):
    """为每个场景生成配音。

    scenes: [dict(sid=..., narration=...), ...]
    返回 {sid: {"dur": float, "marks": [(start, dur, text), ...]}}
    """
    os.makedirs(audio_dir, exist_ok=True)
    result = {}

    def _load(path, marks_path, narration):
        with open(marks_path, encoding="utf-8") as f:
            marks = [tuple(m) for m in json.load(f)]
        d = probe_duration(path)
        return {"dur": d, "marks": determine_marks(narration, d, marks)}

    async def run():
        for sc in scenes:
            sid = sc["sid"]
            path = os.path.join(audio_dir, sid + ".mp3")
            marks_path = os.path.join(audio_dir, sid + ".marks.json")

            # 断点续跑：已生成且标记齐备就跳过
            if os.path.exists(path) and os.path.exists(marks_path) and \
                    probe_duration(path) > 0.4:
                result[sid] = _load(path, marks_path, sc["narration"])
                print(f"  {sid:20s} 复用  {result[sid]['dur']:6.2f}s")
                continue

            try:
                marks = await _synth_retry(sc["narration"], path, voice, rate)
            except Exception as e:
                if not allow_local_fallback:
                    raise
                print(f"  {sid} edge-tts 失败，回落本地引擎：{str(e)[:60]}")
                marks = _local_tts(sc["narration"], path)

            with open(marks_path, "w", encoding="utf-8") as f:
                json.dump(marks, f, ensure_ascii=False)
            result[sid] = _load(path, marks_path, sc["narration"])
            print(f"  {sid:20s} {result[sid]['dur']:6.2f}s  "
                  f"句={len(result[sid]['marks']):2d}  "
                  f"字/秒={len(sc['narration']) / max(result[sid]['dur'], .01):4.1f}")

    asyncio.run(run())
    total = sum(v["dur"] for v in result.values())
    print(f"\n配音合计 {total:.1f}s = {total / 60:.2f} 分钟")
    return result


def check_engine():
    """环境自检：确认能真正出声，而不只是能 import。"""
    import tempfile
    tmpdir = tempfile.mkdtemp()
    tmp = os.path.join(tmpdir, "probe.mp3")
    try:
        marks = asyncio.run(_synth_one("环境自检。", tmp, DEFAULT_VOICE, DEFAULT_RATE))
        d = probe_duration(tmp)
        if d <= 0:
            raise RuntimeError("生成了空音频")
        return True, f"edge-tts 可用（{DEFAULT_VOICE}，试听 {d:.2f}s，标记 {len(marks)} 条）"
    except Exception as e:
        return False, f"edge-tts 不可用：{type(e).__name__} {str(e)[:120]}"
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    ok, msg = check_engine()
    print(("OK   " if ok else "FAIL ") + msg)
