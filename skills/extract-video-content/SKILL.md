---
name: extract-video-content
description: Extract evidence from public Bilibili and YouTube videos for accurate summaries, analysis, research, or downstream article planning. Use when a request includes a bilibili.com, b23.tv, youtube.com, or youtu.be video URL, a Bilibili BV identifier, or asks Codex to inspect what a Bilibili or YouTube video actually says. Collect public metadata, tags, comments, available subtitles, low-resolution media, audio, and contact sheets; use local speech-to-text when subtitles are unavailable.
---

# Extract Video Content

Build an evidence set before analyzing a video. Prefer creator-provided subtitles, then automatic captions or local transcription, and verify important claims against frames and metadata.

## Quick Start

Set the skill directory and use a temporary output directory. Select the extractor from the URL platform:

```bash
SKILL_DIR="${CODEX_HOME:-$HOME/.codex}/skills/extract-video-content"

python3 "$SKILL_DIR/scripts/extract_bilibili.py" \
  'https://www.bilibili.com/video/BV1xxxxxxxxx' \
  --output-dir /tmp/bilibili-video

python3 "$SKILL_DIR/scripts/extract_youtube.py" \
  'https://www.youtube.com/watch?v=xxxxxxxxxxx' \
  --output-dir /tmp/youtube-video
```

Inspect `evidence.json`, `comments.txt`, and any `subtitle-*.txt` files first. Download media only when subtitles are missing or visual verification is necessary:

```bash
python3 "$SKILL_DIR/scripts/extract_youtube.py" \
  'https://youtu.be/xxxxxxxxxxx' \
  --output-dir /tmp/youtube-video \
  --media
```

The YouTube extractor requires a current `yt-dlp`. The `--media` option on either platform also requires `ffmpeg` and produces `video.mp4`, `audio.wav`, and `contact-sheet.jpg`.

## Dependencies

Check for `yt-dlp` before extracting YouTube:

```bash
python3 -m yt_dlp --version
```

Install or update it only when dependency installation is within scope:

```bash
python3 -m pip install -U yt-dlp
```

Keep `yt-dlp` current because YouTube extraction changes frequently. A supported JavaScript runtime may also be needed; the extractor uses Deno by default or Node, Bun, or QuickJS when found on `PATH`. Follow `yt-dlp` warnings when a runtime or impersonation support is required. Do not pass browser cookies or other authentication unless the user explicitly authorizes access to their own session and the requested content.

## Workflow

1. Identify the platform from the URL. Run `extract_bilibili.py` for Bilibili/BV inputs or `extract_youtube.py` for YouTube URLs without `--media`.
2. Read the title, description, duration, author or channel, publication time, tags, chapters, pinned comments, and available subtitles.
3. Prefer manual subtitles over automatic captions. Treat automatic captions as fallible transcription.
4. Treat comments as audience reactions or source leads, not as facts about the video.
5. Rerun with `--media` when no public subtitle exists or when the request depends on diagrams, demonstrations, or on-screen text.
6. View `contact-sheet.jpg` to identify topic transitions and claims that need closer inspection.
7. Transcribe `audio.wav` when no usable subtitle exists. Prefer an already installed local speech-to-text tool.
8. Compare names, numbers, formulas, code, and technical terms in the transcript with the relevant frames. Correct obvious recognition errors without silently inventing missing content.
9. Separate three categories in the final analysis: what the video explicitly states, what the visuals show, and what Codex infers or critiques.

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
  /tmp/youtube-video/audio.wav \
  --output-dir /tmp/youtube-video \
  --model base
```

Use `--language zh` or `--language en` only when the language is known. Use `--prompt` for expected proper nouns or technical vocabulary. Read `transcript.srt` for timestamped evidence and `transcript.txt` for continuous text.

## Output Contract

- `evidence.json`: curated platform metadata, statistics, tags or categories, comments, subtitle status, and warnings.
- `comments.txt`: public comment messages with authors and like counts.
- `subtitle-<language>.json` and `.txt`: public subtitle or caption data when available; YouTube entries identify manual versus automatic tracks.
- `video.mp4`: public low-resolution analysis copy when `--media` is used.
- `audio.wav`: mono 16 kHz audio suitable for speech recognition.
- `contact-sheet.jpg`: up to 24 evenly spaced frames for visual verification.
- `transcript.json`, `.txt`, and `.srt`: local Whisper output.

## Evidence Rules

- Cite the original Bilibili or YouTube URL and include timestamps for material claims when a subtitle or transcript is available.
- Identify translated, reposted, dubbed, sponsored, or AI-generated material when the video or metadata discloses it.
- Do not infer the full content from the title, description, tags, thumbnail, or comments alone.
- Do not present automatic captions or local transcription as verbatim. Note material uncertainty and verify proper nouns and numbers visually.
- Distinguish manual YouTube subtitles from automatic captions using `subtitle_tracks` in `evidence.json`.
- Do not bypass login, paywalls, age or regional restrictions, members-only access, creator-only access, or other platform controls.
- Keep downloaded media in a temporary directory and do not redistribute it.
- Refresh extraction by rerunning the relevant script when a signed media or subtitle URL expires; do not reuse stored signed URLs.

## Failure Handling

- If a public endpoint or extractor returns an error, retry once and then use browser-accessible evidence or report the limitation.
- For YouTube failures, update `yt-dlp` before assuming the video is unavailable. Do not work around access controls.
- If subtitle access is unavailable, continue with public media and local transcription when permitted.
- If media download fails, rerun extraction to request fresh media URLs.
- If comments are disabled or unavailable, continue without them and retain the warning in `evidence.json`.
- If local transcription is unavailable, analyze only the verified metadata and frames, and state that the spoken content was not fully recovered.

## Scripts

- `scripts/extract_bilibili.py`: collect Bilibili public evidence and optionally extract media artifacts.
- `scripts/extract_youtube.py`: collect YouTube public evidence with `yt-dlp` and optionally extract media artifacts.
- `scripts/transcribe_audio.py`: transcribe extracted audio with a locally installed OpenAI Whisper package.
