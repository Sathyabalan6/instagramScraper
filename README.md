# IG Design-Skill Extractor

> Distills UI/UX design creator content into clean, actionable, production-ready **Claude Skills** (`SKILL.md`) using automated Instagram metadata harvesting, dual-engine scraping, audio-only Whisper transcription, and pure LLM distillation.

---

## Key Features

- **Audio-Only Extraction**: Zero video persisted to disk; audio streams are extracted via `yt-dlp`/`ffmpeg`, transcribed with OpenAI Whisper, and deleted immediately in `finally:` blocks.
- **Pure LLM Distillation**: Powered by Google Gemini 3.5 Flash Lite with automatic fallback to Claude / OpenAI / Groq, enforcing strict anti-fabrication and evidence-fidelity tests.
- **Dual-Engine Scraping**: Primary high-speed direct API harvesting with seamless automated fallback to `instaloader` in metadata-only mode.
- **Dedicated Creator Deliverables**: Every processed creator gets an isolated, self-contained output folder (`output/<handle>/`) with `SKILL.md`, visual `SUMMARY.md`, `principles.json`, and `posts.json`.
- **Cross-Category Semantic Deduplication**: Detects overlapping rules across categories using RapidFuzz C++ token set ratio, merging them and upgrading confidence scores (`high > medium > low`).
- **Cross-Creator Consensus**: Merges and deduplicates principles across handles into a global store (`skills/design-ui-ux/`), tagging guidelines as **⭐ Industry Standards** (multi-creator verified) vs. **🎯 Creator Patterns**.
- **Hardened Security**: Session cookies resolve from `~/.config/ig-skill-extractor/cookies.txt` or `IG_COOKIES_PATH`, with header-only API key authentication and an included `clean_secrets.py` audit tool.

---

## Repository Structure

```
ig-design-skill-extractor/
├── output/                         # Per-creator structured outputs
│   └── <username>/
│       ├── SKILL.md                # Creator-specific Claude Skill deliverable
│       ├── SUMMARY.md              # Visual markdown report with metrics & citations
│       ├── principles.json         # Structured JSON schema source of truth
│       └── posts.json              # Full metadata & Whisper audio transcripts
├── skills/
│   └── design-ui-ux/
│       ├── SKILL.md                # Global multi-creator aggregate Claude Skill
│       └── principles.json         # Global principles store
├── scripts/
│   ├── fetch_posts.py              # Stage 1: Dual-engine metadata scraper (Direct API + Instaloader)
│   ├── classify_posts.py           # Stage 2: Caption vs Audio branching heuristic
│   ├── transcribe_audio.py         # Stage 3: Audio-only Whisper transcription
│   ├── extract_principles.py       # Stage 4: Multi-provider LLM principle synthesis
│   ├── merge_skill.py              # Stage 5: Deduplication, confidence upgrade & SKILL generator
│   ├── run_pipeline.py             # Orchestrator CLI for full pipeline execution
│   └── clean_secrets.py            # Security & cookie management utility
├── state/
│   └── processed.json              # Processed post IDs tracking (idempotency)
├── config.yaml                     # Pipeline configuration (delays, categories, thresholds)
├── requirements.txt                # Python package dependencies
├── ARCHITECTURE.md                 # Complete technical system & flow documentation
├── PROJECT_SPEC.md                 # Full technical pipeline specification
├── AGENTS.md                       # Agent & pair-programming rules
└── README.md
```

---

## Quickstart

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/your-username/ig-design-skill-extractor.git
cd ig-design-skill-extractor

# Install dependencies
pip install -r requirements.txt
```
*Note: Requires `ffmpeg` installed on your system PATH for audio extraction.*

---

### 2. Configure API Keys (Multi-Provider Support)

Create a `.env` file in the project root:

```bash
# Google Gemini (Default & Recommended - Header-Only Auth)
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite

# Optional Fallback Providers (Automatically evaluated if primary fails)
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
```

---

### 3. Session Cookies Setup (Security Hardened)

Export your Instagram session cookies using a browser extension (e.g. *Get cookies.txt LOCALLY*). Save them safely to your user directory outside the repository:
or use the https://github.com/Sathyabalan6/session_export.git repo 
 1. go to the browser and enable the developer mode in extention
 2. unload this folder to the extention
 3. export the json file for the instagram. 
 4.for more details look into the https://github.com/Sathyabalan6/session_export.git readme file
```bash
# Place cookies in your user home config:
~/.config/ig-skill-extractor/cookies.txt
```

Alternatively, place them in `cookies/instagram_cookies.txt` (which is gitignored) and run:
```bash
python scripts/clean_secrets.py --clean
```

---

### 4. Running the Pipeline

To extract design principles from any UI/UX creator:

```bash
# Small test run (10 posts)
python scripts/run_pipeline.py --handle zanderwhitehurst --limit 10

# Full run (40-50 posts)
python scripts/run_pipeline.py --handle zanderwhitehurst --limit 50
```

---

## Deliverables Generated

After running for a handle (e.g., `@zanderwhitehurst`):

1. **[`output/<handle>/SKILL.md`](./output/)**: Production-ready, Claude-loadable UI/UX skill with dynamic frontmatter and checkable rules.
2. **[`output/<handle>/SUMMARY.md`](./output/)**: Detailed visual report with extraction stats, category breakdown, and source links.
3. **[`output/<handle>/principles.json`](./output/)**: Structured JSON source of truth.
4. **[`output/<handle>/posts.json`](./output/)**: Complete metadata and Whisper audio transcripts.
5. **[`skills/design-ui-ux/SKILL.md`](./skills/design-ui-ux/SKILL.md)**: Aggregated multi-creator skill synthesized with cross-creator consensus badges.

---

## Pipeline Stages

```
1. Fetch Metadata   ───▶ Direct API + Instaloader Fallback (Rate-limited, Netscape cookie auth)
2. Classify & Branch ───▶ Heuristic check: Substantive Caption vs. Video Reel
3. Transcribe Audio  ───▶ Audio-only stream extraction via ffmpeg/yt-dlp ──▶ Whisper STT
4. Extract Principles───▶ Multi-provider LLM chain with strict anti-fabrication & evidence fidelity
5. Merge & Dedupe   ───▶ Cross-category RapidFuzz matching ──▶ Confidence upgrade ──▶ SKILL.md
```
