---
name: extract-bilibili-video
description: Extract evidence from public Bilibili videos for accurate summaries, analysis, research, or downstream article planning. Use when a request includes a bilibili.com or b23.tv video URL, a BV identifier, or asks Codex to inspect what a Bilibili video actually says. Collect public metadata, tags, comments, available subtitles, low-resolution media, audio, and contact sheets; use local speech-to-text when subtitles are unavailable.
---

# Extract Bilibili Video

Build an evidence set before analyzing a video. Prefer subtitles, then local transcription, and verify important claims against frames and metadata.

## Quick Start

Set the skill directory and use a temporary output directory:

```bash
SKILL_DIR="${CODEX_HOME:-$HOME/.codex}/skills/extract-bilibili-video"
python3 "$SKILL_DIR/scripts/extract_bilibili.py" \
  'https://www.bilibili.com/video/BV1xxxxxxxxx' \
  --output-dir /tmp/bilibili-video
```

Inspect `evidence.json`, `comments.txt`, and any `subtitle-*.txt` files first. Download media only when subtitles are missing or visual verification is necessary:

```bash
python3 "$SKILL_DIR/scripts/extract_bilibili.py" \
  'BV1xxxxxxxxx' \
  --output-dir /tmp/bilibili-video \
  --media
```

The `--media` option requires `ffmpeg` and produces `video.mp4`, `audio.wav`, and `contact-sheet.jpg`.

## Workflow

1. Run `extract_bilibili.py` without `--media` to collect lightweight public evidence.
2. Read the title, description, duration, author, publication time, tags, pinned comments, and available subtitles.
3. Treat comments as audience reactions or source leads, not as facts about the video.
4. Rerun with `--media` when no public subtitle exists or when the request depends on diagrams, demonstrations, or on-screen text.
5. View `contact-sheet.jpg` to identify topic transitions and claims that need closer inspection.
6. Transcribe `audio.wav` when no subtitle exists. Prefer an already installed local speech-to-text tool.
7. Compare names, numbers, formulas, code, and technical terms in the transcript with the relevant frames. Correct obvious recognition errors without silently inventing missing content.
8. Separate three categories in the final analysis: what the video explicitly states, what the visuals show, and what Codex infers or critiques.

## Local Whisper Transcription

Check for OpenAI Whisper:

```bash
python3 -c 'import whisper; print(whisper.__version__)'
```

If it is unavailable, install it only when dependency installation is within scope:

```bash
python3 -m pip install openai-whisper
```

Then run:

```bash
python3 "$SKILL_DIR/scripts/transcribe_audio.py" \
  /tmp/bilibili-video/audio.wav \
  --output-dir /tmp/bilibili-video \
  --language zh \
  --model base
```

Use `--prompt` for expected proper nouns or technical vocabulary. Read `transcript.srt` for timestamped evidence and `transcript.txt` for continuous text.

## Output Contract

- `evidence.json`: curated metadata, statistics, tags, comments, subtitle status, and warnings.
- `comments.txt`: public comment messages with authors and like counts.
- `subtitle-<language>.json` and `.txt`: public subtitle data when available.
- `video.mp4`: public low-resolution analysis copy when `--media` is used.
- `audio.wav`: mono 16 kHz audio suitable for speech recognition.
- `contact-sheet.jpg`: up to 24 evenly spaced frames for visual verification.
- `transcript.json`, `.txt`, and `.srt`: local Whisper output.

## Evidence Rules

- Cite the Bilibili URL and include timestamps for material claims when a transcript is available.
- Identify translated, reposted, or AI-generated material when metadata or pinned comments disclose it.
- Do not infer the full content from the title, description, tags, or comments alone.
- Do not present automatic transcription as verbatim. Note material uncertainty and verify proper nouns and numbers visually.
- Do not bypass login, paywalls, regional restrictions, creator-only access, or other platform controls.
- Keep downloaded media in a temporary directory and do not redistribute it.
- Refresh extraction by rerunning the script when a signed media URL expires; do not reuse stored signed URLs.

## Failure Handling

- If a public API returns an error, retry once and then use browser-accessible evidence or report the limitation.
- If subtitle metadata says login is required, continue with public media and local transcription instead of attempting authentication.
- If media download fails, rerun extraction to request a fresh play URL.
- If local transcription is unavailable, analyze only the verified metadata and frames, and state that the spoken content was not fully recovered.

## Scripts

- `scripts/extract_bilibili.py`: collect public evidence and optionally extract media artifacts.
- `scripts/transcribe_audio.py`: transcribe extracted audio with a locally installed OpenAI Whisper package.
