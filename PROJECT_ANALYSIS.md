# Instagram Design-Skill Extractor - Project Analysis

## Overview
This project implements an automated pipeline that harvests UI/UX design lessons from Instagram reels and carousels, transcribes spoken advice via local AI, synthesizes actionable heuristics via LLMs, and compiles Claude Skills in the legacy format (fat SKILL.md with principles.json and SUMMARY.md) for AI coding agents. A proposed standard format (Agent Skills Package) is defined in `agent-skills-standard/` and one skill (`checkups/`) has been manually converted to this format.

## Key Strengths

### 1. Architecture & Design
- **Clear 5-stage pipeline** with well-separated responsibilities
- **Target-isolated skill folders** (no global skill directory) 
- **Apple HIG-inspired web interface** with real-time logging
- **Robust state management** for idempotency

### 2. Safety & Compliance
- **Strict adherence to AGENTS.md rules**:
  - Rule 1: No video persistence (audio-only extraction with guaranteed cleanup)
  - Rule 3: No verbatim quoting (paraphrase-only LLM extraction)
  - Rate limiting (2-5 second delays between Instagram requests)
  - Idempotency via state/processed.json tracking
- **Browser cookie auto-detection** (zero-extension approach)

### 3. Technical Implementation
- **TLS/JA4 fingerprint impersonation** to avoid Instagram blocks
- **Micro-batching LLM extraction** (4 posts/prompt = 8× speedup)
- **RapidFuzz deduplication** with configurable similarity thresholds
- **PyAV 14+ compatibility patch** for faster-whisper
- **Comprehensive test suite** (13 tests covering all stages)

### 4. User Experience
- **Web Studio Dashboard** with Vue 3 + Tailwind CSS
- **Real-time pipeline monitoring** via Server-Sent Events
- **Interactive principles explorer** with filtering and search
- **One-click skill delivery** for Claude Code/Cursor integration
- **Cookie and API key management** interface

## Verification
- All 13 tests pass (pytest tests/ -v)
- Zero video files persisted to disk (validated by tests)
- Temporary audio files properly cleaned up
- Principles are paraphrased, not quoted verbatim
- Target-isolated folder structure maintained

## Areas for Improvement

1. **Generator-Standard Mismatch**: The pipeline generates the legacy skill format (fat SKILL.md) while the `agent-skills-standard/` directory defines a different format (thin SKILL.md with references/ and scripts/). Only the `checkups/` skill has been manually converted to the standard format.

2. **Documentation Honesty**: The project previously overclaimed production readiness and used placeholder URLs in documentation. We have added a proper LICENSE file and updated documentation to reflect the actual output format.

3. **Instagram Dependency Risks**: The project relies on scraping Instagram (via cookies and private APIs), which is fragile and carries potential ToS and account risks. This is an inherent limitation of the approach.

4. **Verification Theater**: The `scripts/verify.js` in the `checkups/` skill is documented as a stub that always passes, which is acceptable per the Agent Skills Package Standard but should be noted.

5. **Engineering Hygiene**: Minor improvements could be made to deduplicate path resolution logic and ensure consistent dependency management.

## Conclusion
This is a well-engineered solution that successfully implements a novel concept for extracting and structuring design knowledge from social media. The project has strong technical implementation, good safety guarantees, and a useful web interface. However, users should be aware that the generator produces the legacy skill format, not the proposed Agent Skills Package Standard, unless they manually convert the output or use the one pre-converted skill (`checkups/`). The project's value lies in its ability to extract design principles from Instagram, but the dependency on Instagram introduces fragility and potential ToS concerns.

**Rating: 6.5 / 10** (Reflecting honest assessment of current state, considering both strengths and limitations)