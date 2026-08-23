# IG Design-Skill Extractor — Project Spec

**Goal:** Given an Instagram handle, pull their recent posts (captions + audio-only for video posts), extract the design principles they teach, and continuously build/merge a Claude `SKILL.md` for UI/UX design — usable by Claude to both *create* and *critique* design work.

**Where this runs:** Locally, in Claude Code, on your machine. Uses your own Instagram session/cookies. Not something that can run inside a hosted chat (no IG network access, no persistent local state, no cookie storage there).

---

## 1. Project structure

```
ig-design-skill-extractor/
├── README.md
├── requirements.txt
├── config.yaml
├── .gitignore
├── cookies/
│   └── instagram_cookies.txt          # exported via browser extension, gitignored
├── state/
│   └── processed.json                 # tracks which post IDs are already processed
├── data/
│   ├── raw/
│   │   └── <handle>/
│   │       └── posts.json             # metadata dump from instaloader (captions, urls, dates)
│   └── tmp_audio/                     # scratch space, wiped after each transcription
├── skills/
│   └── design-ui-ux/
│       ├── SKILL.md                   # the actual deliverable — human/Claude-readable
│       └── principles.json            # structured backing store (source of truth)
├── scripts/
│   ├── fetch_posts.py                 # Stage 1
│   ├── classify_posts.py              # Stage 2 (caption vs audio branch)
│   ├── transcribe_audio.py            # Stage 2b
│   ├── extract_principles.py          # Stage 3
│   ├── merge_skill.py                 # Stage 4
│   └── run_pipeline.py                # orchestrator — runs 1→4 for one handle
└── logs/
    └── run_<timestamp>.log
```

---

## 2. Setup (what Claude Code should install/configure first)

**Python deps** (`requirements.txt`):
```
instaloader
yt-dlp
openai-whisper        # or faster-whisper for speed
pyyaml
rapidfuzz             # for dedup/similarity matching in merge stage
tqdm
```

**System deps:** `ffmpeg` (required by yt-dlp/whisper for audio handling — audio-only extraction, never full video).

**Cookies:** Export your logged-in Instagram cookies via a browser extension (e.g. "Get cookies.txt LOCALLY" for Chrome/Firefox) → save as `cookies/instagram_cookies.txt`. Add this file to `.gitignore` immediately — never commit it. Instaloader can use this via `--load-cookies` or by pointing at your browser's cookie jar directly (`instaloader --cookiefile=...`).

**Rate limiting matters here:** Instagram flags/blocks aggressive scraping even with valid cookies. Config should default to conservative pacing — a few seconds delay between requests, and a hard cap of ~50 posts per run. Don't loop over multiple handles back-to-back in one session.

---

## 3. Stage 1 — Fetch posts (`fetch_posts.py`)

- Input: `--handle <instagram_username>` `--limit 50`
- Uses `instaloader` in **metadata-only mode**: `--no-pictures --no-videos --no-video-thumbnails --no-compress-json`
- For each post, capture:
  ```json
  {
    "post_id": "...",
    "shortcode": "...",
    "url": "https://instagram.com/p/...",
    "date": "2026-08-01",
    "caption": "full caption text",
    "is_video": true,
    "video_url": "direct CDN url or null",
    "like_count": 0
  }
  ```
- Write to `data/raw/<handle>/posts.json`.
- Skip any post_id already present in `state/processed.json`.

---

## 4. Stage 2 — Classify & branch (`classify_posts.py`)

For each new post, decide the extraction path:

**Heuristic for "caption has substance":**
- Caption word count > ~40, AND
- Contains at least one design-signal keyword: `tip|rule|spacing|contrast|hierarchy|padding|grid|typography|font|color|palette|shadow|radius|alignment|whitespace|breakpoint|accessibility|a11y|UX|UI` (case-insensitive)

→ **If true:** mark `path = "caption"`, send text straight to Stage 3.
→ **If false and `is_video` is true:** mark `path = "audio"`, queue for Stage 2b.
→ **If false and not video (e.g. thin caption, static image with no real text):** mark `path = "skip"` — log and move on, don't waste a transcription call on a post with nothing to extract.

---

## 5. Stage 2b — Audio-only transcription (`transcribe_audio.py`)

**Critical constraint: never persist video.**

```
yt-dlp -x --audio-format mp3 --audio-quality 5 \
  -o "data/tmp_audio/%(id)s.%(ext)s" \
  --cookies cookies/instagram_cookies.txt \
  <post_url>
```
- `-x` extracts audio only; yt-dlp discards the video stream during extraction, so it's never fully downloaded to disk.
- Run Whisper on the resulting mp3 (`whisper data/tmp_audio/<id>.mp3 --model small --output_format txt`).
- **Immediately `os.remove()` the mp3** after the transcript is captured — wrap in try/finally so cleanup happens even on transcription failure.
- Store transcript text back onto the post record (not as a separate media file).

Model choice: `small` is a good default (speed vs. accuracy). Bump to `medium` if transcripts come out garbled — design-tip audio is usually clear, single-speaker, so `small` should be fine.

---

## 6. Stage 3 — Extract principles (`extract_principles.py`)

This is the step that should call **Claude** (via API, using your own key, or by having Claude Code itself do the extraction inline — simplest is to just let Claude Code read the text and extract directly, no separate API call needed).

For each post's text (caption or transcript), extract a structured record:

```json
{
  "principle": "8pt spacing grid",
  "category": "spacing",
  "rule": "Paraphrased, in Claude's own words — never a copied caption/transcript quote",
  "why": "Reasoning given by the creator, if any",
  "example": "Before/after or concrete instance mentioned, if any",
  "source_handle": "<handle>",
  "source_date": "2026-08-01",
  "source_url": "https://instagram.com/p/...",
  "confidence": "high|medium|low"
}
```

**Important:** paraphrase, don't quote captions/transcripts verbatim into the skill file — keeps it copyright-clean and makes the skill read as a coherent style guide rather than a scrape log.

If a post has *no* extractable design principle (personal post, ad, meme, etc.), extraction should return `null` and the post gets logged as `path: "no_content"` — not everything on an IG feed is a lesson.

---

## 7. Stage 4 — Merge into SKILL.md (`merge_skill.py`)

This is the step that makes it a *skill* and not a dump.

- Load existing `skills/design-ui-ux/principles.json` (the structured store).
- For each new extracted principle, check for near-duplicates against existing entries using fuzzy match (`rapidfuzz`) on the `principle` name + category.
  - **Duplicate found:** merge — add the new source as an additional citation, and if the new `why`/`example` adds something the old entry didn't have, enrich it rather than overwrite.
  - **New:** append as a new entry.
- Regenerate `skills/design-ui-ux/SKILL.md` from `principles.json`, grouped by category:

```markdown
# UI/UX Design Skill

Use this skill when creating or critiquing UI/UX design work — layouts, 
spacing, color, typography, hierarchy, accessibility, motion.

## Spacing
### 8pt Spacing Grid
Rule: ...
Why: ...
Example: ...
Sources: 3 posts, most recent 2026-08-01

## Color
...
## Typography
...
```

- SKILL.md should follow the standard Claude Skill format (frontmatter description for triggering + body content) so it activates automatically when you ask Claude to do design work.

---

## 8. Orchestration (`run_pipeline.py`)

```
python run_pipeline.py --handle <username> --limit 40
```
Runs stages 1→4 in sequence, updates `state/processed.json` at the end so a rerun (same or different handle) only processes new posts. Logs progress with `tqdm`, writes a run log to `logs/`.

---

## 9. Things to watch out for

- **IG will rate-limit or temporarily block** aggressive automated access even with valid cookies — keep delays between requests (2–5 sec), and don't run this against many handles in one sitting.
- **Cookie expiry** — session cookies go stale; expect to re-export periodically.
- **This is for personal/research use** — respect Instagram's Terms of Service; this pulls public post metadata/audio for personal learning, not for redistributing creators' content.
- **Whisper cost/time** — local Whisper is free but slow on CPU; if you have a lot of video posts, consider `faster-whisper` or a paid transcription API for speed.
- **Don't over-trust the keyword heuristic** in Stage 2 — periodically spot-check `path: "skip"` posts to make sure real content isn't being missed.

---

## 10. Suggested build order for Claude Code

1. Scaffold folder structure + `requirements.txt` + `.gitignore`.
2. Get `fetch_posts.py` working end-to-end against one test handle — confirm metadata-only, no media saved.
3. Add `classify_posts.py` heuristic, hand-check the caption/audio split on real data.
4. Add `transcribe_audio.py`, confirm mp3s are deleted after use (check `data/tmp_audio/` is empty after a run).
5. Add `extract_principles.py` — this is where Claude Code itself does the reading/extraction; validate output schema on a handful of posts by hand.
6. Add `merge_skill.py`, run it, open the generated `SKILL.md` and read it like a human would.
7. Wire up `run_pipeline.py`, test full run on one handle at limit=10 before scaling to 40-50.
