#!/usr/bin/env python3
"""Extract public evidence and optional media from a YouTube video."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse


YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtube-nocookie.com",
    "www.youtube-nocookie.com",
    "youtu.be",
}


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
        raise RuntimeError(detail)
    return result


def yt_dlp_command() -> list[str]:
    executable = shutil.which("yt-dlp")
    if executable:
        return [executable]
    if importlib.util.find_spec("yt_dlp"):
        return [sys.executable, "-m", "yt_dlp"]
    raise RuntimeError("yt-dlp is required; install or update it with: python -m pip install -U yt-dlp")


def js_runtime_args() -> list[str]:
    if shutil.which("deno"):
        return []
    for runtime, command in (("node", "node"), ("bun", "bun"), ("quickjs", "qjs")):
        executable = shutil.which(command)
        if executable:
            return ["--js-runtimes", f"{runtime}:{executable}"]
    return []


def validate_url(value: str) -> str:
    if not value.startswith(("http://", "https://")):
        raise ValueError("Expected a public YouTube video URL")
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    if host not in YOUTUBE_HOSTS:
        raise ValueError("Expected a youtube.com or youtu.be video URL")
    is_short_url = host == "youtu.be" and bool(parsed.path.strip("/"))
    is_watch_url = parsed.path == "/watch" and bool(parse_qs(parsed.query).get("v"))
    is_video_path = parsed.path.startswith(("/shorts/", "/live/", "/embed/", "/clip/"))
    if not (is_short_url or is_watch_url or is_video_path):
        raise ValueError("Expected a single YouTube video URL, not a channel or playlist URL")
    return value


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def timestamp(seconds: float) -> str:
    total = max(0, int(seconds))
    return f"{total // 3600:02d}:{total % 3600 // 60:02d}:{total % 60:02d}"


def published_at(info: dict) -> str | None:
    value = info.get("timestamp") or info.get("release_timestamp")
    if value is not None:
        return datetime.fromtimestamp(value, timezone.utc).isoformat()
    upload_date = info.get("upload_date")
    if upload_date and re.fullmatch(r"\d{8}", upload_date):
        return datetime.strptime(upload_date, "%Y%m%d").replace(tzinfo=timezone.utc).isoformat()
    return None


def warning_lines(stderr: str) -> list[str]:
    warnings: list[str] = []
    for line in stderr.splitlines():
        line = line.strip()
        if "WARNING:" in line:
            message = line.split("WARNING:", 1)[1].strip()
            if message.lower().startswith("ffmpeg not found."):
                continue
            if message not in warnings:
                warnings.append(message)
    return warnings


def safe_label(value: str, fallback: str) -> str:
    return re.sub(r"[^0-9A-Za-z_-]+", "-", value).strip("-") or fallback


def convert_subtitles(raw_dir: Path, output_dir: Path, info: dict) -> tuple[list[str], list[dict]]:
    files: list[str] = []
    tracks: list[dict] = []
    used_labels: set[str] = set()
    manual_languages = set((info.get("subtitles") or {}).keys())
    automatic_languages = set((info.get("automatic_captions") or {}).keys())

    for index, path in enumerate(sorted(raw_dir.glob("source.*.json3")), start=1):
        language = path.name.removeprefix("source.").removesuffix(".json3")
        label = safe_label(language, str(index))
        if label in used_labels:
            label = f"{label}-{index}"
        used_labels.add(label)
        kind = "manual" if language in manual_languages else "automatic"
        payload = json.loads(path.read_text(encoding="utf-8"))
        cues: list[dict] = []
        for event in payload.get("events", []):
            text = "".join(segment.get("utf8", "") for segment in event.get("segs", []))
            text = re.sub(r"\s+", " ", text).strip()
            if not text:
                continue
            start = event.get("tStartMs", 0) / 1000
            duration = event.get("dDurationMs", 0) / 1000
            cues.append({"start": start, "duration": duration, "text": text})

        json_name = f"subtitle-{label}.json"
        text_name = f"subtitle-{label}.txt"
        write_json(
            output_dir / json_name,
            {"language": language, "kind": kind, "cues": cues},
        )
        lines = [f"[{timestamp(cue['start'])}] {cue['text']}" for cue in cues]
        (output_dir / text_name).write_text("\n".join(lines) + "\n", encoding="utf-8")
        files.extend([json_name, text_name])
        tracks.append({"language": language, "kind": kind, "files": [json_name, text_name]})

    unavailable = sorted((manual_languages | automatic_languages) - {track["language"] for track in tracks})
    for language in unavailable:
        tracks.append({"language": language, "kind": "manual" if language in manual_languages else "automatic", "files": []})
    return files, tracks


def curate_comments(info: dict, limit: int) -> list[dict]:
    comments: list[dict] = []
    for item in (info.get("comments") or [])[:limit]:
        comments.append(
            {
                "author": item.get("author", ""),
                "author_id": item.get("author_id"),
                "message": item.get("text", ""),
                "likes": item.get("like_count", 0),
                "published_at": item.get("timestamp"),
                "pinned": bool(item.get("is_pinned") or item.get("is_pinned_comment")),
            }
        )
    return comments


def collect_evidence(url: str, output_dir: Path, comment_limit: int) -> tuple[dict, list[str], list[str]]:
    extractor_args = (
        "youtube:skip=translated_subs;comment_sort=top;"
        f"max_comments={comment_limit},{comment_limit},0,0,1"
    )
    with tempfile.TemporaryDirectory(prefix="youtube-evidence-") as temporary:
        raw_dir = Path(temporary)
        result = run(
            [
                *yt_dlp_command(),
                "--ignore-config",
                *js_runtime_args(),
                "--no-playlist",
                "--skip-download",
                "--write-info-json",
                "--write-comments",
                "--write-subs",
                "--write-auto-subs",
                "--sub-langs",
                "all,-live_chat",
                "--sub-format",
                "json3",
                "--extractor-args",
                extractor_args,
                "--paths",
                str(raw_dir),
                "--output",
                "source.%(ext)s",
                url,
            ]
        )
        info_path = raw_dir / "source.info.json"
        if not info_path.is_file():
            raise RuntimeError("yt-dlp did not produce video metadata")
        info = json.loads(info_path.read_text(encoding="utf-8"))
        subtitle_files, subtitle_tracks = convert_subtitles(raw_dir, output_dir, info)

    comments = curate_comments(info, comment_limit)
    warnings = warning_lines(result.stderr)
    if not subtitle_files:
        warnings.append("No public subtitle was downloaded; extract media and use local transcription.")

    video_id = info.get("id")
    source_url = info.get("webpage_url") or (f"https://www.youtube.com/watch?v={video_id}" if video_id else url)
    evidence = {
        "platform": "youtube",
        "source_url": source_url,
        "video_id": video_id,
        "title": info.get("title", ""),
        "description": info.get("description", ""),
        "duration_seconds": info.get("duration", 0),
        "published_at": published_at(info),
        "owner": {
            "name": info.get("channel") or info.get("uploader", ""),
            "channel_id": info.get("channel_id") or info.get("uploader_id"),
            "channel_url": info.get("channel_url") or info.get("uploader_url"),
        },
        "stats": {
            "views": info.get("view_count"),
            "likes": info.get("like_count"),
            "comments": info.get("comment_count"),
        },
        "availability": info.get("availability"),
        "live_status": info.get("live_status"),
        "age_limit": info.get("age_limit"),
        "categories": info.get("categories") or [],
        "tags": info.get("tags") or [],
        "chapters": info.get("chapters") or [],
        "comments": comments,
        "subtitle_files": subtitle_files,
        "subtitle_tracks": subtitle_tracks,
        "warnings": warnings,
    }
    return evidence, subtitle_files, warnings


def extract_media(url: str, duration: float, output_dir: Path) -> list[str]:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is required for --media")

    with tempfile.TemporaryDirectory(prefix="youtube-media-") as temporary:
        raw_dir = Path(temporary)
        run(
            [
                *yt_dlp_command(),
                "--ignore-config",
                *js_runtime_args(),
                "--no-playlist",
                "--format",
                "b[height<=360]/worst",
                "--paths",
                str(raw_dir),
                "--output",
                "source.%(ext)s",
                url,
            ]
        )
        candidates = [path for path in raw_dir.glob("source.*") if path.is_file() and path.suffix not in {".part", ".ytdl"}]
        if not candidates:
            raise RuntimeError("yt-dlp did not produce a media file")
        source = max(candidates, key=lambda path: path.stat().st_size)
        video = output_dir / "video.mp4"
        if source.suffix.lower() == ".mp4":
            shutil.copyfile(source, video)
        else:
            try:
                run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source), "-c", "copy", str(video)])
            except RuntimeError:
                run(
                    [
                        "ffmpeg",
                        "-hide_banner",
                        "-loglevel",
                        "error",
                        "-y",
                        "-i",
                        str(source),
                        "-c:v",
                        "libx264",
                        "-c:a",
                        "aac",
                        str(video),
                    ]
                )

    audio = output_dir / "audio.wav"
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(video),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(audio),
        ]
    )

    frame_count = min(24, max(1, math.ceil(duration / 20)))
    interval = max(1, duration / frame_count)
    columns = min(4, frame_count)
    rows = math.ceil(frame_count / columns)
    sheet = output_dir / "contact-sheet.jpg"
    filter_graph = f"fps=1/{interval:.3f},scale=480:-1,tile={columns}x{rows}"
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(video),
            "-vf",
            filter_graph,
            "-frames:v",
            "1",
            str(sheet),
        ]
    )
    return [video.name, audio.name, sheet.name]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", help="Public youtube.com or youtu.be video URL")
    parser.add_argument("--output-dir", type=Path, help="Output directory; defaults to /tmp/youtube-<video-id>")
    parser.add_argument("--comment-limit", type=int, default=20)
    parser.add_argument("--media", action="store_true", help="Download low-resolution media and extract audio/contact sheet")
    args = parser.parse_args()

    if not 1 <= args.comment_limit <= 100:
        raise ValueError("--comment-limit must be between 1 and 100")
    url = validate_url(args.video)
    temporary_output = args.output_dir is None
    output_dir = args.output_dir or Path(tempfile.mkdtemp(prefix="youtube-video-"))
    output_dir.mkdir(parents=True, exist_ok=True)

    evidence, subtitle_files, warnings = collect_evidence(url, output_dir, args.comment_limit)
    if temporary_output and evidence.get("video_id"):
        final_dir = Path(tempfile.gettempdir()) / f"youtube-{evidence['video_id']}"
        if not final_dir.exists():
            output_dir.rename(final_dir)
            output_dir = final_dir

    write_json(output_dir / "evidence.json", evidence)
    comments = evidence["comments"]
    comment_lines = [
        f"{'[pinned] ' if item['pinned'] else ''}{item['author']} ({item['likes']} likes): {item['message']}"
        for item in comments
    ]
    (output_dir / "comments.txt").write_text("\n\n".join(comment_lines) + "\n", encoding="utf-8")

    files = ["evidence.json", "comments.txt", *subtitle_files]
    if args.media:
        files.extend(extract_media(evidence["source_url"], evidence.get("duration_seconds") or 0, output_dir))
    print(json.dumps({"output_dir": str(output_dir), "files": files, "warnings": warnings}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (json.JSONDecodeError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
