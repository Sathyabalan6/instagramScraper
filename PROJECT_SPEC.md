# Instagram Design-Skill Extractor — Engineering Specification

**Goal:** Given an Instagram handle, profile URL, or saved bookmark collection, harvest recent posts (captions + audio-only transcripts for video reels), extract the design principles taught via live LLM synthesis, and compile isolated, target-specific Claude Skill packages (`skills/<clean_name>/`) containing `SKILL.md` (v2 specification), `principles.json`, and `SUMMARY.md`, alongside raw scraping metadata in `output/<target>/posts.json`. There is **no global skill directory**; each collection or creator has its own dedicated skill folder named directly after the target.

**Environment:** Runs locally. Uses active browser session cookies or exported Netscape tokens and direct LLM API keys (Google Gemini, Anthropic Claude, OpenAI, or Groq).

---

## 1. Project Directory Layout

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
│   └── <clean_target_name>/        # Target-isolated Claude Skill folder (e.g. checkups, zanderwhitehurst)
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
│   └── test_pipeline.py            # Automated unit & integration test suite (13 tests)
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions continuous integration workflow
├── cookies/
│   └── instagram_cookies.txt       # Exported session cookies (Gitignored)
├── state/
│   └── processed.json              # Stage-aware state ledger (Schema v2.0)
├── config.yaml                     # Pipeline parameters & category lists
├── requirements.txt                # Python package dependencies
├── ARCHITECTURE.md                 # Deep technical architecture documentation
├── PROJECT_SPEC.md                 # Engineering specification (this file)
├── AGENTS.md                       # Operational rules for coding agents
└── README.md                       # Quickstart & user documentation
```

---

## 2. Dependencies & System Requirements

### Python Dependencies (`requirements.txt`)
- `fastapi>=0.110.0`: High-performance asynchronous API backend.
- `uvicorn>=0.28.0`: ASGI web server for Web Studio.
- `faster-whisper>=1.0.0`: CTranslate2-accelerated Whisper speech recognition (int8 quantization).
- `yt-dlp>=2024.1.0`: Audio stream demuxing CLI wrapper.
- `instaloader>=4.11`: Fallback Instagram scraping framework.
- `curl_cffi>=0.7.0`: Chrome 124 TLS/JA4 fingerprint impersonation client.
- `rapidfuzz>=3.6.0`: C++ Levenshtein and token-sort fuzzy matching algorithms.
- `pyyaml>=6.0`: YAML configuration parser.
- `python-dotenv>=1.0.0`: Environment variable isolation.
- `tqdm>=4.66.0`: Terminal progress bar.
- `requests>=2.31.0`: HTTP client.
- `pytest>=8.0.0` & `pytest-asyncio`: Automated test framework.

### System Prerequisites
- **`ffmpeg`**: Required for media stream demuxing directly to MP3.

---

## 3. Pipeline Stages & Execution Contracts

### Stage 1: Metadata Harvesting (`scripts/fetch_posts.py`)
- **Inputs**:
  - Target: Handle, profile URL, or saved collection URL.
  - Limit: Maximum posts to fetch (default: 50).
- **Execution**:
  1. Auto-detects session cookies from local browser profiles (Chrome, Firefox, Brave, Chromium) or loads Netscape cookie file.
  2. For collections: Paginates `/api/v1/feed/collection/{collection_id}/posts/` using Chrome 124 JA4 TLS impersonation.
  3. For creators: Queries direct REST endpoint `/api/v1/feed/user/{user_id}/` with automatic fallback to `instaloader`.
  4. Applies anti-automation pacing (2.5–4.5 second polite sleep between pagination cursors).
- **Output**: Writes metadata to `data/raw/<target>/posts.json` and mirrors to `output/<target>/posts.json`. **Never downloads images or videos**.

---

### Stage 2: Post Classification (`scripts/classify_posts.py`)
- **Heuristic Routing**:
  - `caption`: Caption word count $\ge 40$ AND contains UI/UX design keywords (`padding`, `typography`, `hierarchy`, `contrast`, `auto-layout`, `wcag`, etc.). Dispatched directly to Stage 4.
  - `audio`: Video reel (`is_video == True`) with short caption ($< 40$ words). Dispatched to Stage 3 for audio transcription.
  - `skip`: Promotional ads, sponsored posts (`#ad`), lifestyle clips, or image carousels with insufficient text.
- **Output**: Updates each post object in `posts.json` with a `classification` block.

---

### Stage 3: Audio Demuxing & Transcription (`scripts/transcribe_audio.py`)
- **Execution**:
  1. Filters posts where `classification.path == 'audio'` and `transcript` is missing.
  2. Demuxes audio stream with `yt-dlp -x --audio-format mp3` into `data/tmp_audio/<shortcode>_<id>.mp3`.
  3. Transcribes speech using `faster-whisper` (`compute_type="int8"` on CPU, PyAV 14+ compatibility patch applied).
  4. Guarantees immediate deletion of scratch `.mp3` files in a `finally:` block.
- **Hard Rule**: No full `.mp4` video files are ever downloaded or persisted.
- **Output**: Populates `post["transcript"]` in `posts.json`. Confirms `data/tmp_audio/` is empty upon exit.

---

### Stage 4: Micro-Batched Principle Synthesis (`scripts/extract_principles.py`)
- **Micro-Batching**: Posts needing extraction are grouped into batches of 4, cutting LLM latency by 8×.
- **Provider Chain**: Evaluates Gemini 3.5 Flash Lite $\rightarrow$ Claude 3.5 Sonnet $\rightarrow$ GPT-4o-mini $\rightarrow$ Groq Llama 3.3.
- **Prompt Constraints**:
  1. *Copyright Paraphrasing*: Zero verbatim copying permitted; rules must be synthesized into original guidelines.
  2. *Actionability*: Rejects generic platitudes; requires checkable constraints, ratios, pairings, or methods.
  3. *Evidence Fidelity*: Forbids inventing measurements, opacities, or color codes not in the creator's text.
  4. *No Fabrication*: Returns empty array `[]` if post teaches no concrete design heuristic.
- **Output**: Populates `post["principles"]` and saves `output/<target>/principles.json`.

---

### Stage 5: Deduplication, Consensus & Merge (`scripts/merge_skill.py`)
- **Deduplication Engine**:
  - RapidFuzz token sort ratio comparison:
    - Same-Category: $\ge 85\%$ threshold on Title or Rule.
    - Cross-Category: $\ge 80\%$ threshold to eliminate conceptual overlaps.
  - Upgrades confidence scores (`high > medium > low`) on reaffirmed guidelines.
  - Combines citations and updates latest date in `sources[]`.
- **Consensus Tagging**:
  - `Multi-Source Consensus`: Verified across $\ge 2$ unique creators.
  - `Creator Guideline`: Verified across 1 creator.
- **SKILL.md v2 Specification Generation**:
  - YAML frontmatter with Claude trigger criteria.
  - Pre-Flight UI/UX Audit Checklist (7 checks).
  - Parametric Design Tokens Table (Base grid, padding, touch targets, radius, hairline borders, typography scale).
  - Structured implementation patterns with explicit `Avoid` and `Do This` sub-bullets.
  - Zero informal emoji badges.
- **Output**: Writes target deliverables into `skills/<clean_name>/` (`SKILL.md`, `SUMMARY.md`, `principles.json`) and mirrors them into `output/<target>/`. No global skill directory is created.

---

## 4. State Ledger Specification (`state/processed.json`)

Tracks per-post lifecycle stages to provide true idempotency (Schema Version 2.0):
```json
{
  "version": "2.0",
  "posts": {
    "3997592712018040775": {
      "shortcode": "Dd6TWQ0hpfH",
      "date": "2026-09-30",
      "is_video": true,
      "stages": {
        "fetched": true,
        "transcribed": true,
        "extracted": true,
        "completed": true
      },
      "principles_count": 2,
      "last_updated": "2026-10-02T03:25:00.123456"
    }
  }
}
```

---

## 5. Verification & Testing

Every stage is audited against continuous integration tests (`pytest tests/ -v`):
1. `test_config_structure`: Config schema and category validity.
2. `test_classify_heuristic`: Caption vs audio routing accuracy.
3. `test_deduplication_same_category`: RapidFuzz matching threshold.
4. `test_merge_skill_confidence_upgrade`: Confidence upgrades and source combining.
5. `test_web_studio_dashboard_route`: Apple HIG Web Studio frontend rendering.
6. `test_web_studio_api_status`: Health and session diagnostics.
7. `test_web_studio_api_principles`: Principle query filtering.
8. `test_safety_constraints`: Zero video files, scratch audio cleanup.
9. `test_resolve_target`: URL, handle, and collection auto-detection.
10. `test_stage_ledger`: State ledger migration and stage tracking.
11. `test_skill_markdown_v2`: Pre-flight checklist, design tokens, and zero emojis.
12. `test_clean_skill_name`: Target name normalization and prefix cleaning.
13. `test_target_skill_folder_creation`: Verification of target-isolated `skills/<clean_name>/` structure without global skill.

