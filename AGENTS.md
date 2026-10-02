# AGENTS.md

Instructions for any coding agent (Claude Code, Antigravity, Cursor, etc.) working in this repository.

## What this project does

Pulls recent posts from an Instagram handle, profile URL, or saved bookmark collection (captions + audio-only transcripts — **never full video**), extracts the UI/UX design principles taught in them via LLM synthesis, and compiles isolated, target-specific Claude Skill folders (`skills/<clean_name>/`) alongside raw scraping metadata (`output/<target>/`) that AI agents can load when creating or critiquing UI/UX design work. There is **no global skill directory**; every run creates a skill package dedicated to the specific collection or creator.

Full design specs: see `PROJECT_SPEC.md` and `ARCHITECTURE.md` in this repo. Read them before making structural changes — they define the pipeline stages, data schemas, and build contracts.

---

## Hard rules — do not violate these

1. **Never persist video files to disk.** Audio-only extraction via `yt-dlp -x` only.
   Any temp audio file written to `data/tmp_audio/` must be deleted (`os.remove`, in a
   `try/finally`) immediately after transcription completes or fails. If you write code
   that downloads a `.mp4`/full video, that's a blocking bug — stop and fix it.
2. **Never commit cookies.** `cookies/instagram_cookies.txt` must stay in `.gitignore`.
   Never print cookie contents to logs or stdout.
3. **Never quote captions/transcripts verbatim into SKILL.md.** Every `rule`/`why`/
   `example` field in `principles.json` must be a paraphrase in Claude's own words.
   This is a copyright requirement, not a style preference — treat it as a hard
   constraint on `extract_principles.py`, not a suggestion.
4. **Rate limit Instagram requests.** Minimum 2–5 second delay between requests to
   Instagram-owned endpoints (via direct API or instaloader). Do not parallelize requests
   to Instagram. Cap any single run at `limit` posts as configured (default 50).
5. **Idempotency.** Re-running the pipeline on a handle or collection already processed
   should only touch new posts. Always check `state/processed.json` (Schema v2.0) before
   re-fetching or re-transcribing a post_id.
6. **Don't skip the dedup step.** New principles must be fuzzy-matched against
   `principles.json` before being appended — see `merge_skill.py`. Duplicate entries in
   `SKILL.md` are a bug.
7. **Adhere to SKILL.md v2 Specification.** The generated deliverable must include the
   Pre-Flight UI/UX Audit Checklist, Parametric Design Tokens Table, structured `Do This`
   vs `Avoid` patterns, and clean consensus badges (zero emojis).
8. **Target-isolated skill folder convention (NO global skill).** Every extraction target
   (saved collection or creator handle) produces a dedicated folder in `skills/<clean_name>/`
   containing `SKILL.md`, `principles.json`, and `SUMMARY.md`. Saved collections strip
   `collection_` prefixes (e.g., `collection_checkups` -> `skills/checkups/`), while handles
   strip `@` (e.g., `@zanderwhitehurst` -> `skills/zanderwhitehurst/`). Never generate or
   resurrect a global aggregate skill directory (`skills/design-ui-ux/`).

---

## Repo layout

```
instagramScraper/
├── app.py                          # FastAPI backend & Web Studio API
├── templates/
│   └── index.html                  # Apple HIG-styled Web Studio frontend (Vue 3 + Tailwind)
├── output/                         # Target-isolated raw scrape data
│   └── <target>/                   # e.g., collection_checkups or zanderwhitehurst
│       ├── SKILL.md                # Target-specific Claude Skill deliverable (mirror)
│       ├── SUMMARY.md              # Visual markdown report with metrics & post index (mirror)
│       ├── principles.json         # Structured JSON schema source of truth (mirror)
│       └── posts.json              # Full metadata & Whisper audio transcripts
├── skills/
│   └── <clean_target_name>/        # Target-isolated Claude Skill (e.g. checkups, zanderwhitehurst)
│       ├── SKILL.md                # Production-ready Claude Skill deliverable (v2 spec)
│       ├── SUMMARY.md              # Visual markdown report with metrics & post index
│       └── principles.json         # Structured JSON schema backing store
├── scripts/
│   ├── fetch_posts.py              # Stage 1: Dual-engine metadata fetcher (Direct API + Instaloader)
│   ├── classify_posts.py           # Stage 2: Caption vs. Audio heuristic branching
│   ├── transcribe_audio.py         # Stage 3: Audio-only faster-whisper STT
│   ├── extract_principles.py       # Stage 4: Micro-batched LLM principle synthesis
│   ├── merge_skill.py              # Stage 5: Deduplication, consensus & target SKILL v2 compiler
│   ├── run_pipeline.py             # Pipeline orchestrator & CLI
│   └── clean_secrets.py            # Security & cookie management utility
├── tests/
│   └── test_pipeline.py            # Automated test suite (13 tests)
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions continuous integration workflow
├── cookies/                        # gitignored — exported IG session
├── state/
│   └── processed.json              # Stage-aware state ledger (Schema v2.0)
├── data/
│   ├── raw/<target>/posts.json     # metadata dump, no media
│   └── tmp_audio/                  # scratch, must be empty after every run
├── config.yaml
├── requirements.txt
├── ARCHITECTURE.md
├── PROJECT_SPEC.md
└── README.md
```

---

## Build & execution order

1. Scaffold structure + `requirements.txt` + `.gitignore` (complete).
2. `fetch_posts.py` — metadata harvesting. Supports `@handle`, profile URLs, and saved collection feeds with JA4 TLS impersonation. **Verify `data/raw/<target>/` contains only `posts.json`, no images/video**.
3. `classify_posts.py` — caption-vs-audio heuristic routing.
4. `transcribe_audio.py` — `faster-whisper` CTranslate2 int8 transcription with PyAV 14+ compatibility monkey-patch. **Confirm `data/tmp_audio/` is empty after every run**.
5. `extract_principles.py` — micro-batching (4 posts/prompt) with Gemini 3.5 Flash Lite default. Verify zero verbatim quoting.
6. `merge_skill.py` — fuzzy deduplication, confidence upgrades, and compilation of `skills/<clean_name>/SKILL.md` (v2 spec with pre-flight checklist and design tokens).
7. `run_pipeline.py` — orchestrate stages 1 $\rightarrow$ 5. Test with `--limit 10` before scaling up.

---

## Commands an agent will typically run

```bash
# Run test suite (All 13 tests must pass)
pytest tests/ -v

# Run extraction on a creator handle
python3 scripts/run_pipeline.py --target "@zanderwhitehurst" --limit 10

# Run extraction on a saved collection URL
python3 scripts/run_pipeline.py --target "https://www.instagram.com/<user>/saved/<name>/<id>/" --limit 20

# Run Web Studio dashboard
python3 app.py
```

---

## When something looks wrong

- **Video file appeared anywhere under `data/`**: Stop immediately. This is a Rule 1 violation; fix the extraction command before continuing.
- **SKILL.md has two entries that are clearly the same principle**: Dedup logic in `merge_skill.py` needs a lower similarity threshold (`threshold=80.0`). Do not hand-merge; fix the code.
- **Instagram returns errors/blocks mid-run**: Back off; do not retry aggressively in a loop. Respect the 2–5 second polite rate limit.
- **PyAV throws `TypeError: open() got an unexpected keyword argument 'metadata_errors'`**: PyAV 14+ removed this argument. Ensure the monkey-patch at the top of `scripts/transcribe_audio.py` is active.
- **LLM extraction is slow**: Verify micro-batching is enabled and no artificial `time.sleep` calls exist in `extract_principles.py`.
