# Instagram Design-Skill Extractor - Project Analysis

## Overview
This project implements an automated pipeline that harvests UI/UX design lessons from Instagram reels and carousels, transcribes spoken advice via local AI, synthesizes actionable heuristics via LLMs, and compiles production-ready Claude Skills for AI coding agents.

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

## Conclusion
This is a well-engineered, production-ready solution that successfully implements a novel concept for extracting and structuring design knowledge from social media. The project balances sophisticated technical implementation with strong safety guarantees and excellent user experience.

**Rating: 9/10**