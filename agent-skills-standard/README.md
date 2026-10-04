# Agent Skills Package Standard (Recommended)

Portable **full package** standard for multi-agent skills (Claude, Cursor, Antigravity, and other Agent Skills–compatible clients).

| File | Purpose |
|------|---------|
| [SPEC.md](./SPEC.md) | Normative layout, frontmatter, references/, scripts/, install.sh, naming |
| [CHECKLIST.md](./CHECKLIST.md) | Human author checklist (Core / Recommended / Full) |
| [validate_skill.py](./validate_skill.py) | Automated structural validator |

## Quick start

```bash
# Recommended level (default)
python validate_skill.py /path/to/my-skill

# Core only
python validate_skill.py /path/to/my-skill --level core

# Distribution-ready
python validate_skill.py /path/to/my-skill --level full

# JSON output for CI
python validate_skill.py /path/to/my-skill --level full --json
```

## Compliance levels

1. **Core** — valid `SKILL.md` + `name` + `description`, folder matches `name`
2. **Recommended** — Core + thin body, negative triggers, progressive disclosure via `references/`
3. **Full package** — Recommended + `install.sh` (dry-run, multi-target) + verify entrypoint under `scripts/`

This is independent of any single scraper or repo. Drop `SPEC.md` into your org docs and run `validate_skill.py` in CI.
