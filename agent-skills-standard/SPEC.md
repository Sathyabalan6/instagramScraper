# Agent Skills Package Standard (Recommended)

**Version:** 1.0.0  
**Status:** Recommended (not minimal, not strict-enforced)  
**Compatibility target:** Claude Code, Cursor, Google Antigravity, and other Agent Skills–compatible clients  
**Based on:** [Agent Skills open format](https://agentskills.io) (name + description discovery, progressive disclosure)

This document defines a **full package standard**: folder layout, `SKILL.md` rules, recommended `references/` and `scripts/`, installer conventions, and naming rules. Use it when packaging domain knowledge (e.g. design heuristics, review protocols, runbooks) as portable skills.

---

## 1. Goals

1. **Portable** — Same skill folder works across multiple agent products.
2. **Progressive disclosure** — Agents load only `name` + `description` until the skill is activated; heavy content stays in `references/`.
3. **Actionable** — Skills describe *when* to run, *what* to do, and optionally *how to verify*.
4. **Installable** — Optional but recommended installer for common agent skill directories.
5. **Checkable** — Compliance can be validated with the companion checklist and `validate_skill.py`.

---

## 2. Package layout

### 2.1 Required

```
<skill-name>/
└── SKILL.md          # Required: YAML frontmatter + instructions
```

### 2.2 Recommended (full package)

```
<skill-name>/
├── SKILL.md              # Thin protocol + frontmatter (required)
├── install.sh            # Multi-agent installer (recommended)
├── references/           # On-demand documentation (recommended)
│   ├── principles.json   # Structured data (if applicable)
│   ├── SUMMARY.md        # Human-readable overview / metrics
│   └── …                 # Additional reference docs as needed
├── scripts/              # Executable helpers (recommended when verifiable)
│   └── verify.js         # or verify.py, verify.sh — entrypoint for validation
└── assets/               # Optional templates, images, fixtures
```

### 2.3 Rules

| Path | Required? | Rules |
|------|-----------|--------|
| `SKILL.md` | **Yes** | Must exist at package root. See §3. |
| `references/` | Recommended | Load only when instructions say so. Do not dump full catalogs into `SKILL.md`. |
| `scripts/` | Recommended if skill claims verification | Prefer one obvious entrypoint (`verify.js` / `verify.py` / `verify.sh`). |
| `install.sh` | Recommended for distribution | Idempotent; support at least `--dry-run` and a target env flag. |
| `assets/` | Optional | Static resources referenced by instructions. |

**Do not** put secrets, API keys, or session cookies inside a skill package.

---

## 3. SKILL.md specification

### 3.1 Frontmatter (required)

`SKILL.md` **must** start with YAML frontmatter:

```markdown
---
name: my-skill-name
description: >-
  One or more sentences: what the skill does AND when to use it.
  Prefer explicit negative triggers (Do NOT trigger for …).
---
```

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | **Yes** | Lowercase letters, numbers, hyphens only. Max 64 characters. Must match the folder name. No spaces, no `anthropic` / `claude` reserved words as the name. |
| `description` | **Yes** | Non-empty. Max 1024 characters recommended. Must state **what** it does and **when** to activate. Prefer a **Do NOT trigger** clause for non-goals. |

**Description quality (recommended):**

- Positive triggers: tasks, file types, UI areas, review stages.
- Negative triggers: backend-only, infra, unrelated domains.
- Optional: compatibility notes (e.g. Node 20+, Python 3.10+).

**Good example:**

```yaml
name: checkups
description: >-
  Enforces actionable UI/UX design heuristics distilled from leading creators.
  Triggers when refining screen layouts, interaction patterns, or design tokens.
  Do NOT trigger for backend-only changes, infrastructure configuration, or non-UI
  data-model adjustments.
```

**Weak example (avoid):**

```yaml
name: checkups
description: "UI/UX tips from Instagram."
```

### 3.2 Body (instructions)

After frontmatter, Markdown instructions for the agent.

**Recommended body style (thin protocol):**

1. Short title and purpose (1–3 sentences).
2. Ordered workflow (e.g. Plan → Validate → Patch).
3. Explicit pointers to `references/` for heavy content.
4. Explicit pointers to `scripts/` when verification exists.
5. Keep the body small enough that loading it does not replace the need for progressive disclosure.

**Avoid in root `SKILL.md`:**

- Full principle catalogs (dozens of rules with citations).
- Large tables that belong in `references/`.
- Duplicate copies of `principles.json` content.

**Allowed in root `SKILL.md`:**

- Short checklists (e.g. ≤ 7 high-priority items).
- Minimal token tables if they are core to every activation.
- Clear “see `references/…`” links.

### 3.3 Progressive disclosure contract

| Stage | What the agent should see |
|-------|---------------------------|
| Discovery | Only `name` + `description` from frontmatter |
| Activation | Full `SKILL.md` body |
| Execution | `references/*` and `scripts/*` only as instructed |

Skill authors **must** write the body so that detailed material is requested from `references/` rather than inlined by default.

---

## 4. `references/` conventions

| File | Recommended when | Purpose |
|------|------------------|---------|
| `principles.json` | Structured heuristics / rules | Machine-readable source of truth |
| `SUMMARY.md` | Extraction or multi-source skills | Metrics, post index, human overview |
| `PRINCIPLES.md` or domain docs | Long prose catalogs | Agent-readable detail on demand |

**`principles.json` (recommended schema when applicable):**

```json
[
  {
    "principle": "Short title",
    "category": "layout",
    "rule": "Actionable rule text",
    "why": "Rationale",
    "example": "Concrete example or Before/After",
    "confidence": "high",
    "sources": [
      {
        "handle": "creator-or-system",
        "date": "YYYY-MM-DD",
        "url": "https://..."
      }
    ]
  }
]
```

Fields may be extended; keep `principle` / `rule` / `category` stable for tooling.

---

## 5. `scripts/` conventions

- Prefer a single verification entrypoint: `scripts/verify.js`, `scripts/verify.py`, or `scripts/verify.sh`.
- Script should exit `0` on success, non-zero on failure.
- Placeholder verifiers are allowed but **must** document that they are stubs.
- `SKILL.md` should tell the agent how to run the script (e.g. `node scripts/verify.js`).

**Minimal acceptable stub (JS):**

```js
#!/usr/bin/env node
console.log("Running skill verification (stub)...");
process.exit(0);
```

---

## 6. `install.sh` conventions (recommended)

Support installing the skill directory into common locations:

| Target key | Default directory |
|------------|-------------------|
| `antigravity` | `~/.gemini/config/skills/` |
| `claude` | `~/.claude/skills/` |
| `cursor` | `~/.cursor/skills/` |
| `local` | `../.agents/skills/` (relative to skill parent) or project-local skills path |

**Required behaviors:**

- `--help`
- `--dry-run` (no filesystem writes)
- `-t` / `--target <env>`
- Refuse to install into a path inside the source skill directory (avoid self-copy loops)
- Copy the **entire** skill folder (preserve `references/`, `scripts/`, etc.)
- Executable bit: `chmod +x install.sh`

---

## 7. Naming conventions

| Entity | Rule |
|--------|------|
| Folder name | Same as frontmatter `name` |
| `name` field | `[a-z0-9]+(-[a-z0-9]+)*`, max 64 chars |
| Scripts | `verify` + conventional extension |
| References | Lowercase, descriptive; prefer stable names (`principles.json`, `SUMMARY.md`) |

---

## 8. Content quality bar (recommended)

Skills that encode design or process rules should:

1. Prefer **actionable** rules over slogans (“use 8px grid” vs “keep it clean”).
2. Prefer **paraphrase** over long verbatim third-party copyrighted text.
3. Cite sources in `references/` when content is derived from external creators.
4. Separate **high/medium** confidence guidance from **low** confidence drafts when both exist.
5. Include negative triggers in `description` so agents do not over-activate.

---

## 9. Non-goals

This standard does **not** require:

- A specific LLM provider
- Network access at skill runtime
- A particular programming language for scripts
- Publishing to a registry

This standard does **not** replace product-specific docs (Claude Code skill paths, Cursor config, etc.); it defines a **portable package shape** those products can consume.

---

## 10. Compliance levels

| Level | Meaning |
|-------|---------|
| **Core** | Valid `SKILL.md` with `name` + `description`; folder name matches `name` |
| **Recommended** | Core + thin body + `references/` for heavy content + clear progressive-disclosure pointers |
| **Full package** | Recommended + `scripts/` entrypoint (if verifiable) + `install.sh` with dry-run and multi-target support |

Use **Recommended** as the default bar for new skills. Aim for **Full package** when distributing installable skills across agents.

---

## 11. Companion artifacts

| File | Purpose |
|------|---------|
| `CHECKLIST.md` | Human review checklist for authors |
| `validate_skill.py` | Automated structural validation (Core / Recommended / Full) |

Run validation:

```bash
python validate_skill.py path/to/my-skill
python validate_skill.py path/to/my-skill --level full
```

---

## 12. Changelog

| Version | Date | Notes |
|---------|------|--------|
| 1.0.0 | 2026-10-04 | Initial recommended full-package standard for multi-agent portability |
