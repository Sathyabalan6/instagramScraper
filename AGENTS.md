# AGENTS.md

Instructions for any coding agent (Claude Code, Codex, etc.) working in this repository.

## What this project does

Pulls recent posts from a given Instagram handle (captions + audio-only transcripts —
**never full video**), extracts the design principles taught in them, and merges them
into a single, deduplicated `skills/design-ui-ux/SKILL.md` that Claude can load when
creating or critiquing UI/UX design work.

Full design spec: see `PROJECT_SPEC.md` in this repo. Read it before making structural
changes — it defines the pipeline stages, data schemas, and build order.

## Hard rules — do not violate these

1. **Never persist video files to disk.** Audio-only extraction via `yt-dlp -x` only.
   Any temp audio file written to `data/tmp_audio/` must be deleted (`os.remove`, in a
   `try/finally`) immediately after transcription completes or fails. If you write code
   that downloads a `.mp4`/full video, that's a bug — stop and fix it.
2. **Never commit cookies.** `cookies/instagram_cookies.txt` must stay in `.gitignore`.
   Never print cookie contents to logs or stdout.
3. **Never quote captions/transcripts verbatim into SKILL.md.** Every `rule`/`why`/
   `example` field in `principles.json` must be a paraphrase in Claude's own words.
   This is a copyright requirement, not a style preference — treat it as a hard
   constraint on `extract_principles.py`, not a suggestion.
4. **Rate limit Instagram requests.** Minimum 2–5 second delay between requests to
   Instagram-owned endpoints (via instaloader or yt-dlp). Do not parallelize requests
   to Instagram. Cap any single run at `limit` posts as configured (default 50).
5. **Idempotency.** Re-running the pipeline on a handle already processed should only
   touch new posts. Always check `state/processed.json` before re-fetching or
   re-transcribing a post_id.
6. **Don't skip the dedup step.** New principles must be fuzzy-matched against
   `principles.json` before being appended — see `merge_skill.py` spec in
   `PROJECT_SPEC.md` §7. Duplicate entries in SKILL.md are a bug.

## Repo layout

```
ig-design-skill-extractor/
├── AGENTS.md              # this file
├── PROJECT_SPEC.md         # full pipeline spec — read first
├── README.md               # human-facing quickstart
├── requirements.txt
├── config.yaml
├── .gitignore
├── cookies/                # gitignored — your exported IG session
├── state/processed.json    # which post_ids are already handled
├── data/
│   ├── raw/<handle>/posts.json     # metadata dump, no media
│   └── tmp_audio/                  # scratch, must be empty after every run
├── skills/design-ui-ux/
│   ├── SKILL.md             # generated deliverable
│   └── principles.json      # structured source of truth for SKILL.md
├── scripts/
│   ├── fetch_posts.py
│   ├── classify_posts.py
│   ├── transcribe_audio.py
│   ├── extract_principles.py
│   ├── merge_skill.py
│   └── run_pipeline.py
└── logs/
```

## Build order (do not reorder)

1. Scaffold structure + `requirements.txt` + `.gitignore` (done — see repo as-is).
2. `fetch_posts.py` — get this fully working against one test handle first.
   **Verify `data/raw/<handle>/` contains only `posts.json`, no images/video** before
   moving on.
3. `classify_posts.py` — implement the caption-vs-audio heuristic from
   `PROJECT_SPEC.md` §4. Spot-check its output against real posts by hand.
4. `transcribe_audio.py` — after running against a few video posts, confirm
   `data/tmp_audio/` is empty. If it isn't, that's a blocking bug, fix before continuing.
5. `extract_principles.py` — validate the JSON schema output on ~5 posts manually
   before running at scale. Confirm no verbatim caption/transcript text leaks into the
   `rule`/`why`/`example` fields.
6. `merge_skill.py` — run it, then actually open and read the generated `SKILL.md`.
   It should read like a coherent style guide, not a log dump.
7. `run_pipeline.py` — orchestrate 1→4 (in the numbered-stage sense from the spec).
   Test at `--limit 10` before scaling to 40–50.

## Commands an agent will typically run

```bash
pip install -r requirements.txt --break-system-packages   # if system python
python scripts/run_pipeline.py --handle <username> --limit 10   # small test run first
python scripts/run_pipeline.py --handle <username> --limit 40   # full run
```

## When something looks wrong

- Video file appeared anywhere under `data/`: stop, this is a rule-1 violation, fix
  the extraction command before continuing.
- SKILL.md has two entries that are clearly the same principle: dedup logic in
  `merge_skill.py` needs a lower similarity threshold — don't just hand-merge and
  move on, fix the code.
- Instagram starts returning errors/blocks mid-run: back off, don't retry
  aggressively in a loop — this usually means rate limiting kicked in.
