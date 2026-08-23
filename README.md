# IG Design-Skill Extractor

Turns an Instagram design creator's posts into a reusable Claude Skill
(`skills/design-ui-ux/SKILL.md`) — no video ever saved to disk, audio deleted
right after transcription, captions/transcripts paraphrased not quoted.

Full pipeline design: see [`PROJECT_SPEC.md`](./PROJECT_SPEC.md).
Rules for any agent (Claude Code, etc.) working in this repo: see [`AGENTS.md`](./AGENTS.md).

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt --break-system-packages
   ```
   Also requires `ffmpeg` on your system (used for audio-only extraction).

2. **Export your Instagram cookies**
   Use a browser extension like "Get cookies.txt LOCALLY" while logged into
   Instagram in your browser. Save the export as:
   ```
   cookies/instagram_cookies.txt
   ```
   This file is gitignored — never commit it, never share it.

3. **Check `config.yaml`** — defaults are conservative (3s delay between
   Instagram requests, 50 post cap per run). Don't lower the delay; Instagram
   blocks aggressive automated access even with valid cookies.

## Usage

Test run first, small limit:
```bash
python scripts/run_pipeline.py --handle <username> --limit 10
```

Once verified, scale up:
```bash
python scripts/run_pipeline.py --handle <username> --limit 40
```

Check `skills/design-ui-ux/SKILL.md` afterward — it should read like a style
guide, organized by category (spacing, color, typography, hierarchy, motion,
accessibility, layout), not a raw dump of posts.

Re-running on the same handle only processes posts not already in
`state/processed.json`. Running against a new handle adds to the same
`SKILL.md`, merging/deduping against existing principles.

## Notes

- This pulls public post **metadata and audio-only transcripts** for personal
  learning/reference — it doesn't redistribute anyone's content. Respect
  Instagram's Terms of Service and don't run this aggressively across many
  accounts in one sitting.
- Whisper on CPU is slow. If you're processing a lot of video-only posts,
  consider `faster-whisper` or a paid transcription API.
- Session cookies expire — if fetches start failing, re-export them.
