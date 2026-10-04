# Agent Skills Package Checklist

Use this before publishing or committing a skill. Map results to compliance levels in `SPEC.md` §10.

**Skill path:** `____________________________`  
**Reviewer:** `____________________________`  
**Date:** `____________________________`

---

## A. Core (must pass)

- [ ] Folder name is lowercase, hyphenated, matches frontmatter `name`
- [ ] `SKILL.md` exists at package root
- [ ] `SKILL.md` starts with YAML frontmatter (`---` … `---`)
- [ ] Frontmatter includes `name`
- [ ] Frontmatter includes `description`
- [ ] `name` uses only `[a-z0-9-]` and is ≤ 64 characters
- [ ] `description` states **what** the skill does
- [ ] `description` states **when** to activate
- [ ] `description` is not empty and is reasonably short (≤ 1024 chars recommended)
- [ ] No secrets, cookies, or API keys in the package

**Core result:** ☐ Pass  ☐ Fail

---

## B. Recommended (default bar)

- [ ] `description` includes a **Do NOT trigger** (or equivalent negative) clause
- [ ] Body is a **thin protocol** (workflow + pointers), not a full catalog dump
- [ ] Heavy content lives under `references/` when present
- [ ] Body explicitly points agents to `references/` for detail
- [ ] If structured rules exist, `references/principles.json` (or equivalent) is present and valid JSON
- [ ] Progressive disclosure: activating the skill does not require loading megabytes of inline principles in `SKILL.md`
- [ ] Language in body is actionable (rules/checks), not only slogans

**Recommended result:** ☐ Pass  ☐ Fail  ☐ N/A (Core only)

---

## C. Full package (distribution-ready)

- [ ] `install.sh` exists and is executable in spirit (`chmod +x`)
- [ ] `install.sh` supports `--help`
- [ ] `install.sh` supports `--dry-run`
- [ ] `install.sh` supports `-t` / `--target` for multiple agents (e.g. claude, cursor, antigravity, local)
- [ ] Installer refuses unsafe self-copy into source tree
- [ ] `scripts/` contains a clear verify entrypoint (`verify.js` / `verify.py` / `verify.sh`)
- [ ] `SKILL.md` tells the agent how to run the verify script
- [ ] Verify script exits 0 on success; non-zero on failure (stubs must be labeled as stubs)

**Full package result:** ☐ Pass  ☐ Fail  ☐ N/A

---

## D. Content quality (recommended, manual)

- [ ] Rules are specific enough to implement or check
- [ ] External/third-party material is paraphrased; sources cited in `references/` when derived
- [ ] Low-confidence items are separated or labeled if mixed with production guidance
- [ ] Naming is consistent across folder, `name`, and installer messages

**Content result:** ☐ Pass  ☐ Fail  ☐ Skipped

---

## E. Automated validation

```bash
python validate_skill.py /path/to/skill --level core
python validate_skill.py /path/to/skill --level recommended
python validate_skill.py /path/to/skill --level full
```

- [ ] `validate_skill.py` passes at the intended level

**Automated result:** ☐ Pass  ☐ Fail

---

## Sign-off

| Level claimed | Core | Recommended | Full |
|---------------|------|-------------|------|
| Intended      | ☐    | ☐           | ☐    |
| Achieved      | ☐    | ☐           | ☐    |

Notes:

```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```
