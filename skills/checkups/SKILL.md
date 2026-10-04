---
name: checkups
description: >-
  Enforces actionable UI/UX design heuristics distilled from leading creators.
  Triggers when refining screen layouts, interaction patterns, or design tokens.
  Do NOT trigger for backend‑only changes, infrastructure configuration, or non‑UI data‑model adjustments.
  Compatibility: Requires Node.js 20+, and optionally a lint rule runner (e.g., ESLint) for automated checks.
---

# Checkups UI/UX Heuristics Protocol

Execute in Plan‑Validate‑Patch sequence:

1. **Plan**: Map extracted principles to target component/screen.
   - Review the detailed principles in `references/` to understand the heuristics.
   - Identify which principles apply to the current task.

2. **Validate**: Run verification scripts (see `scripts/`).
   - Execute the validation script to check for violations of the principles.
   - The script will report any issues that need to be addressed.

3. **Patch**: Apply fixes per principle guidance.
   - For each violation, apply the recommended changes as outlined in the principles.
   - Re-run validation to ensure all issues are resolved.

See `references/` for detailed principles, patterns, and verification details.
