#!/usr/bin/env python3
"""Transcribe an audio file with a locally installed OpenAI Whisper package."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def srt_time(seconds: float) -> str:
    milliseconds = round(max(0, seconds) * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def ensure_model(whisper: object, name: str, model_dir: Path) -> None:
    urls = getattr(whisper, "_MODELS", {})
    if name not in urls:
        return
    url = urls[name]
    expected_hash = url.rstrip("/").split("/")[-2]
    target = model_dir / f"{name}.pt"
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == expected_hash:
        return
    model_dir.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".download")
    subprocess.run(["curl", "-L", "--retry", "2", "-sS", url, "-o", str(temporary)], check=True)
    actual_hash = hashlib.sha256(temporary.read_bytes()).hexdigest()
    if actual_hash != expected_hash:
        temporary.unlink(missing_ok=True)
        raise RuntimeError("Downloaded Whisper model failed checksum verification")
    temporary.replace(target)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audio", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model", default="base")
    parser.add_argument("--model-dir", type=Path, default=Path.home() / ".cache" / "whisper")
    parser.add_argument("--language", help="Language code such as zh or en; omit for detection")
    parser.add_argument("--prompt", help="Expected names or technical vocabulary")
    args = parser.parse_args()

    try:
        import whisper
    except ImportError as error:
        raise RuntimeError("OpenAI Whisper is not installed; run: python3 -m pip install openai-whisper") from error

    if not args.audio.is_file():
        raise ValueError(f"Audio file does not exist: {args.audio}")
    ensure_model(whisper, args.model, args.model_dir)
    model = whisper.load_model(args.model, device="cpu", download_root=str(args.model_dir))
    options = {"fp16": False}
    if args.language:
        options["language"] = args.language
    if args.prompt:
        options["initial_prompt"] = args.prompt
    result = model.transcribe(str(args.audio), **options)
    segments = [
        {"id": segment["id"], "start": segment["start"], "end": segment["end"], "text": segment["text"].strip()}
        for segment in result.get("segments", [])
    ]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    payload = {"language": result.get("language"), "text": result.get("text", "").strip(), "segments": segments}
    (args.output_dir / "transcript.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output_dir / "transcript.txt").write_text(payload["text"] + "\n", encoding="utf-8")
    srt = "\n\n".join(
        f"{index}\n{srt_time(segment['start'])} --> {srt_time(segment['end'])}\n{segment['text']}"
        for index, segment in enumerate(segments, start=1)
    )
    (args.output_dir / "transcript.srt").write_text(srt + "\n", encoding="utf-8")
    print(json.dumps({"language": payload["language"], "segments": len(segments), "output_dir": str(args.output_dir)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
