# IG Design-Skill Extractor — Project Spec

**Goal:** Given an Instagram handle, pull their recent posts (captions + audio-only for video posts), extract the design principles they teach via live LLM synthesis, and continuously build/merge isolated creator deliverables (`output/<handle>/`) alongside an aggregated Claude `SKILL.md` for UI/UX design — usable by Claude to both *create* and *critique* design work.

**Where this runs:** Locally on your machine. Uses your own Instagram session/cookies and direct LLM API keys (Google Gemini, Anthropic Claude, OpenAI, or Groq).

---

## 1. Project Structure

```
ig-design-skill-extractor/
├── README.md                          # Human-facing quickstart & documentation
├── ARCHITECTURE.md                    # In-depth technical architecture & flow guide
├── PROJECT_SPEC.md                    # Full pipeline specification (this file)
├── AGENTS.md                          # Hard rules for AI coding agents
├── requirements.txt                   # Python package dependencies
├── config.yaml                        # Configuration for delays, paths & categories
├── .gitignore
├── cookies/
│   └── instagram_cookies.txt          # Exported session cookies (Gitignored)
├── state/
│   └── processed.json                 # Tracks processed post IDs (idempotency)
├── data/
│   ├── raw/<handle>/posts.json        # Raw metadata cache
│   └── tmp_audio/                     # Scratch audio folder (wiped after every transcription)
├── output/                            # Dedicated creator deliverables
│   └── <handle>/
│       ├── SKILL.md                   # Standalone creator Claude Skill
│       ├── SUMMARY.md                 # Visual report with metrics & source index
│       ├── principles.json            # Structured JSON source of truth
│       └── posts.json                 # Complete post metadata & audio transcripts
├── skills/
│   └── design-ui-ux/
│       ├── SKILL.md                   # Global multi-creator aggregate Claude Skill
│       └── principles.json            # Global structured principles backing store
├── scripts/
│   ├── fetch_posts.py                 # Stage 1: Dual-engine metadata fetcher (Direct API + Instaloader)
│   ├── classify_posts.py              # Stage 2: Caption vs. Audio heuristic branching
│   ├── transcribe_audio.py            # Stage 3: Audio-only Whisper STT
│   ├── extract_principles.py          # Stage 4: Multi-provider LLM principle synthesis
│   ├── merge_skill.py                 # Stage 5: Deduplication, confidence upgrade & SKILL compiler
│   ├── run_pipeline.py                # Pipeline orchestrator
│   └── clean_secrets.py               # Security & cookie management utility
└── logs/
```

---

## 2. Dependencies & Security Setup

**Python Dependencies (`requirements.txt`):**
```
instaloader>=4.11
yt-dlp>=2024.1
openai-whisper>=20231117
pyyaml>=6.0
rapidfuzz>=3.6
tqdm>=4.66
python-dotenv>=1.0.0
requests>=2.31.0
```

**System Dependencies:** `ffmpeg` (required for audio stream demuxing — never full video).

**Security Architecture:**
- Cookies can be stored outside the repo at `~/.config/ig-skill-extractor/cookies.txt` or via `IG_COOKIES_PATH`.
- API keys are passed strictly via HTTP headers (`X-goog-api-key`, `Authorization`) without URL query parameters.
- `clean_secrets.py` audits and scrubs local cookies prior to committing or sharing code.

---

## 3. Pipeline Stages

### Stage 1 — Dual-Engine Metadata Harvesting (`scripts/fetch_posts.py`)
- Input: `--handle <username>` `--limit <int>`
- Direct API endpoint (`/api/v1/feed/user/{id}/`) queries post metadata at high speed.
- Seamless fallback to `instaloader` in metadata-only mode if Instagram changes private endpoints.
- Rate limiting: Configurable 2–5 second polite sleep between requests.

### Stage 2 — Classify & Branch (`scripts/classify_posts.py`)
- **`caption`**: Word count $\ge 40$ and contains UI/UX design keywords (`padding`, `typography`, `hierarchy`, `contrast`, `auto-layout`, etc.). Sent directly to LLM extraction.
- **`audio`**: Video reels with short captions. Queued for Whisper audio-only transcription.
- **`skip`**: Promotional spam, lifestyle clips, memes, or ad sponsorships.

### Stage 3 — Audio-Only Transcription (`scripts/transcribe_audio.py`)
- `yt-dlp -x --audio-format mp3` extracts audio stream directly.
- **Hard Rule**: No full `.mp4` video files are ever saved to disk.
- OpenAI Whisper (`small` model) transcribes audio locally.
- Temporary `.mp3` files in `data/tmp_audio/` are deleted immediately in `finally:` blocks.

### Stage 4 — Multi-Provider LLM Synthesis (`scripts/extract_principles.py`)
- Evaluates: **Anthropic Claude** $\rightarrow$ **OpenAI GPT-4o** $\rightarrow$ **Groq Llama 3.3** $\rightarrow$ **Google Gemini 3.5 Flash Lite**.
- Gracefully falls through the provider chain on 429 rate limits or errors.
- **Prompt Constraints**:
  - Pure paraphrasing (zero verbatim quoting for copyright safety).
  - Strict actionability test (no generic platitudes).
  - Evidence fidelity (no invented pixel values, opacities, or color codes).
  - Zero fabrication (returns `[]` if no concrete design principle is taught).

### Stage 5 — Deduplication, Consensus & Merge (`scripts/merge_skill.py`)
- RapidFuzz C++ similarity matching:
  - Same-category matching ($\ge 85\%$ threshold).
  - Cross-category semantic matching ($\ge 80\%$ threshold).
- Upgrades confidence ratings (`high > medium > low`) on reaffirmed guidelines.
- Compiles standalone creator outputs (`output/<handle>/`) and aggregates into global store ([`skills/design-ui-ux/SKILL.md`](./skills/design-ui-ux/SKILL.md)).
- Tags consensus: **⭐ Industry Standard** (cross-creator verified) vs. **🎯 Creator Pattern**.
