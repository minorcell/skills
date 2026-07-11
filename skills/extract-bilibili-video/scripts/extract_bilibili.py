#!/usr/bin/env python3
"""Extract public evidence and optional media from a Bilibili video."""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode


API = "https://api.bilibili.com"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


def run(command: list[str], *, capture: bool = False) -> str:
    result = subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
    )
    return result.stdout if capture else ""


def curl_args(url: str, referer: str | None = None) -> list[str]:
    args = ["curl", "-L", "--retry", "2", "--connect-timeout", "20", "--max-time", "120", "-sS", "-A", USER_AGENT]
    if referer:
        args.extend(["-e", referer])
    args.append(url)
    return args


def fetch_json(path_or_url: str, params: dict[str, object] | None = None, referer: str | None = None) -> dict:
    url = path_or_url if path_or_url.startswith("http") else f"{API}{path_or_url}"
    if params:
        url = f"{url}?{urlencode(params)}"
    payload = json.loads(run(curl_args(url, referer), capture=True))
    if "code" in payload and payload["code"] != 0:
        raise RuntimeError(f"Bilibili API error {payload['code']}: {payload.get('message', '')}")
    return payload


def resolve_bvid(value: str) -> str:
    match = re.search(r"BV[0-9A-Za-z]{10}", value, re.IGNORECASE)
    if match:
        return "BV" + match.group(0)[2:]
    if value.startswith(("http://", "https://")):
        resolved = run([*curl_args(value), "-o", "/dev/null", "-w", "%{url_effective}"], capture=True)
        match = re.search(r"BV[0-9A-Za-z]{10}", resolved, re.IGNORECASE)
        if match:
            return "BV" + match.group(0)[2:]
    raise ValueError("Expected a Bilibili URL or BV identifier")


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def timestamp(seconds: float) -> str:
    total = max(0, int(seconds))
    return f"{total // 3600:02d}:{total % 3600 // 60:02d}:{total % 60:02d}"


def collect_replies(items: list[dict] | None, pinned: bool = False) -> list[dict]:
    output: list[dict] = []
    for item in items or []:
        output.append(
            {
                "author": item.get("member", {}).get("uname", ""),
                "message": item.get("content", {}).get("message", ""),
                "likes": item.get("like", 0),
                "pinned": pinned,
            }
        )
        output.extend(collect_replies(item.get("replies"), pinned=False))
    return output


def extract_subtitles(player: dict, output_dir: Path, referer: str) -> list[str]:
    files: list[str] = []
    subtitles = player.get("data", {}).get("subtitle", {}).get("subtitles", [])
    for index, subtitle in enumerate(subtitles, start=1):
        language = subtitle.get("lan") or subtitle.get("lan_doc") or str(index)
        safe_language = re.sub(r"[^0-9A-Za-z_-]+", "-", language).strip("-") or str(index)
        url = subtitle.get("subtitle_url", "")
        if url.startswith("//"):
            url = "https:" + url
        if not url:
            continue
        payload = fetch_json(url, referer=referer)
        json_name = f"subtitle-{safe_language}.json"
        text_name = f"subtitle-{safe_language}.txt"
        write_json(output_dir / json_name, payload)
        lines = [f"[{timestamp(row.get('from', 0))}] {row.get('content', '')}" for row in payload.get("body", [])]
        (output_dir / text_name).write_text("\n".join(lines) + "\n", encoding="utf-8")
        files.extend([json_name, text_name])
    return files


def extract_media(bvid: str, cid: int, duration: int, output_dir: Path, referer: str) -> list[str]:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is required for --media")
    play = fetch_json(
        "/x/player/playurl",
        {"bvid": bvid, "cid": cid, "qn": 16, "fnval": 0, "fourk": 0},
        referer,
    )
    urls = play.get("data", {}).get("durl", [])
    if not urls:
        raise RuntimeError("No public media URL was returned")
    video = output_dir / "video.mp4"
    run([*curl_args(urls[0]["url"], referer), "-o", str(video)])

    audio = output_dir / "audio.wav"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(audio)])

    frame_count = min(24, max(1, math.ceil(duration / 20)))
    interval = max(1, duration / frame_count)
    columns = min(4, frame_count)
    rows = math.ceil(frame_count / columns)
    sheet = output_dir / "contact-sheet.jpg"
    filter_graph = f"fps=1/{interval:.3f},scale=480:-1,tile={columns}x{rows}"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video), "-vf", filter_graph, "-frames:v", "1", str(sheet)])
    return [video.name, audio.name, sheet.name]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", help="Bilibili video URL, b23.tv URL, or BV identifier")
    parser.add_argument("--output-dir", type=Path, help="Output directory; defaults to /tmp/bilibili-<BV>")
    parser.add_argument("--comment-limit", type=int, default=20, choices=range(1, 50))
    parser.add_argument("--media", action="store_true", help="Download low-resolution media and extract audio/contact sheet")
    args = parser.parse_args()

    if not shutil.which("curl"):
        raise RuntimeError("curl is required")
    bvid = resolve_bvid(args.video)
    output_dir = args.output_dir or Path(f"/tmp/bilibili-{bvid}")
    output_dir.mkdir(parents=True, exist_ok=True)
    source_url = f"https://www.bilibili.com/video/{bvid}"

    view = fetch_json("/x/web-interface/view", {"bvid": bvid}, source_url)["data"]
    page = view.get("pages", [{}])[0]
    cid = page.get("cid") or view.get("cid")
    if not cid:
        raise RuntimeError("The video has no public content ID")

    tags_payload = fetch_json("/x/tag/archive/tags", {"bvid": bvid}, source_url)
    tags = [item.get("tag_name", "") for item in tags_payload.get("data", [])]
    player = fetch_json("/x/player/v2", {"bvid": bvid, "cid": cid}, source_url)
    replies_payload = fetch_json(
        "/x/v2/reply",
        {"type": 1, "oid": view["aid"], "sort": 2, "pn": 1, "ps": args.comment_limit},
        source_url,
    )
    reply_data = replies_payload.get("data") or {}
    comments = collect_replies(reply_data.get("top_replies"), pinned=True)
    comments.extend(collect_replies(reply_data.get("replies")))
    subtitle_files = extract_subtitles(player, output_dir, source_url)

    warnings: list[str] = []
    if not subtitle_files:
        warnings.append("No public subtitle was returned; extract media and use local transcription.")
    if player.get("data", {}).get("need_login_subtitle"):
        warnings.append("Bilibili reports that subtitle access may require login; authentication was not attempted.")

    evidence = {
        "source_url": source_url,
        "bvid": bvid,
        "aid": view.get("aid"),
        "cid": cid,
        "title": view.get("title", ""),
        "description": view.get("desc", ""),
        "part": page.get("part", ""),
        "duration_seconds": view.get("duration", 0),
        "published_at": datetime.fromtimestamp(view.get("pubdate", 0), timezone.utc).isoformat(),
        "owner": {"name": view.get("owner", {}).get("name", ""), "mid": view.get("owner", {}).get("mid")},
        "stats": view.get("stat", {}),
        "rights": view.get("rights", {}),
        "argument": view.get("argue_info", {}),
        "tags": tags,
        "comments": comments,
        "subtitle_files": subtitle_files,
        "warnings": warnings,
    }
    write_json(output_dir / "evidence.json", evidence)
    comment_lines = [f"{'[置顶] ' if item['pinned'] else ''}{item['author']} ({item['likes']} 赞): {item['message']}" for item in comments]
    (output_dir / "comments.txt").write_text("\n\n".join(comment_lines) + "\n", encoding="utf-8")

    files = ["evidence.json", "comments.txt", *subtitle_files]
    if args.media:
        files.extend(extract_media(bvid, cid, view.get("duration", 0), output_dir, source_url))
    print(json.dumps({"output_dir": str(output_dir), "files": files, "warnings": warnings}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (subprocess.CalledProcessError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
