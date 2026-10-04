#!/usr/bin/env python3
"""
Validate an Agent Skills package against the Recommended Full Package Standard (SPEC.md).

Usage:
  python validate_skill.py <skill_dir>
  python validate_skill.py <skill_dir> --level core|recommended|full
  python validate_skill.py <skill_dir> --json

Exit codes:
  0 = pass at requested level
  1 = fail
  2 = usage / path error
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VERIFY_NAMES = ("verify.js", "verify.py", "verify.sh", "verify.ts")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str] | tuple[None, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    block = m.group(1)
    body = text[m.end() :]
    data: dict[str, str] = {}
    current_key = None
    current_lines: list[str] = []

    def flush():
        nonlocal current_key, current_lines
        if current_key is not None:
            data[current_key] = "\n".join(current_lines).strip()
        current_key = None
        current_lines = []

    for line in block.splitlines():
        # continuation of folded/block scalar
        if current_key and (line.startswith("  ") or line.startswith("\t")):
            current_lines.append(line.strip())
            continue
        if ":" in line and not line.startswith(" "):
            flush()
            key, _, rest = line.partition(":")
            key = key.strip()
            rest = rest.strip()
            if rest in (">", ">-", "|", "|-"):
                current_key = key
                current_lines = []
            else:
                # strip optional quotes
                if (rest.startswith('"') and rest.endswith('"')) or (
                    rest.startswith("'") and rest.endswith("'")
                ):
                    rest = rest[1:-1]
                data[key] = rest
                current_key = None
                current_lines = []
        elif current_key:
            current_lines.append(line.strip())
    flush()
    return data, body


def check_core(skill_dir: Path, fm: dict[str, str] | None, body: str, skill_md: Path) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    folder_name = skill_dir.name

    if not skill_md.is_file():
        issues.append({"level": "core", "id": "skill_md_missing", "msg": "SKILL.md not found at package root"})
        return issues

    if fm is None:
        issues.append({"level": "core", "id": "frontmatter_missing", "msg": "SKILL.md must start with YAML frontmatter (--- ... ---)"})
        return issues

    name = (fm.get("name") or "").strip()
    desc = (fm.get("description") or "").strip()

    if not name:
        issues.append({"level": "core", "id": "name_missing", "msg": "Frontmatter field 'name' is required"})
    else:
        if not NAME_RE.match(name):
            issues.append(
                {
                    "level": "core",
                    "id": "name_invalid",
                    "msg": f"name '{name}' must be lowercase letters, numbers, hyphens only",
                }
            )
        if len(name) > 64:
            issues.append({"level": "core", "id": "name_too_long", "msg": f"name length {len(name)} > 64"})
        if name != folder_name:
            issues.append(
                {
                    "level": "core",
                    "id": "name_folder_mismatch",
                    "msg": f"frontmatter name '{name}' does not match folder name '{folder_name}'",
                }
            )
        for reserved in ("anthropic", "claude"):
            if name == reserved:
                issues.append({"level": "core", "id": "name_reserved", "msg": f"name '{name}' is reserved"})

    if not desc:
        issues.append({"level": "core", "id": "description_missing", "msg": "Frontmatter field 'description' is required"})
    else:
        if len(desc) > 1024:
            issues.append(
                {
                    "level": "core",
                    "id": "description_long",
                    "msg": f"description length {len(desc)} > 1024 (recommended max)",
                    "severity": True,
                }
            )
        # weak signal: should mention activation context
        lower = desc.lower()
        if "trigger" not in lower and "when" not in lower and "use" not in lower:
            issues.append(
                {
                    "level": "core",
                    "id": "description_weak_when",
                    "msg": "description should indicate when to use/activate the skill",
                    "severity": True,
                }
            )

    # secrets heuristic
    text_all = skill_md.read_text(encoding="utf-8", errors="replace")
    for pat, label in (
        (r"(?i)api[_-]?key\s*[:=]\s*['\"]?[a-zA-Z0-9_\-]{16,}", "possible API key"),
        (r"(?i)sessionid\s*[:=]", "possible session cookie"),
        (r"(?i)BEGIN (RSA |OPENSSH )?PRIVATE KEY", "private key material"),
    ):
        if re.search(pat, text_all):
            issues.append({"level": "core", "id": "secret_heuristic", "msg": f"Possible secret in SKILL.md ({label})"})

    return issues


def check_recommended(skill_dir: Path, fm: dict[str, str], body: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    desc = (fm.get("description") or "").strip().lower()

    neg_signals = ("do not trigger", "don't trigger", "do not use", "not for", "never use for")
    if not any(s in desc for s in neg_signals):
        issues.append(
            {
                "level": "recommended",
                "id": "missing_negative_trigger",
                "msg": "description should include a Do NOT trigger / negative scope clause",
            }
        )

    # Thin body heuristic: large skill bodies without references/ are discouraged
    refs = skill_dir / "references"
    body_len = len(body.strip())
    if body_len > 8000 and not refs.is_dir():
        issues.append(
            {
                "level": "recommended",
                "id": "fat_body_no_references",
                "msg": f"SKILL.md body is large ({body_len} chars) but references/ is missing — prefer progressive disclosure",
            }
        )

    if refs.is_dir():
        if "references/" not in body and "references`" not in body and "references" not in body.lower():
            issues.append(
                {
                    "level": "recommended",
                    "id": "body_missing_references_pointer",
                    "msg": "references/ exists but SKILL.md body does not point agents to it",
                }
            )
        pj = refs / "principles.json"
        if pj.is_file():
            try:
                data = json.loads(pj.read_text(encoding="utf-8"))
                if not isinstance(data, list):
                    issues.append(
                        {
                            "level": "recommended",
                            "id": "principles_not_list",
                            "msg": "references/principles.json should be a JSON array",
                        }
                    )
            except json.JSONDecodeError as e:
                issues.append(
                    {
                        "level": "recommended",
                        "id": "principles_invalid_json",
                        "msg": f"references/principles.json is invalid JSON: {e}",
                    }
                )
    else:
        # Not fatal for recommended if body is already thin and self-contained
        if body_len > 4000:
            issues.append(
                {
                    "level": "recommended",
                    "id": "no_references_dir",
                    "msg": "references/ recommended for heavy or structured content",
                    "severity": True,
                }
            )

    return issues


def check_full(skill_dir: Path, body: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []

    install = skill_dir / "install.sh"
    if not install.is_file():
        issues.append({"level": "full", "id": "install_missing", "msg": "install.sh is required for full package level"})
    else:
        text = install.read_text(encoding="utf-8", errors="replace")
        if "--dry-run" not in text and "dry-run" not in text:
            issues.append({"level": "full", "id": "install_no_dry_run", "msg": "install.sh should support --dry-run"})
        if "--help" not in text and "usage()" not in text.lower():
            issues.append({"level": "full", "id": "install_no_help", "msg": "install.sh should support --help or usage()"})
        if "--target" not in text and "-t" not in text:
            issues.append({"level": "full", "id": "install_no_target", "msg": "install.sh should support -t/--target for multi-agent install paths"})
        # executable bit (best-effort; may not work on all FS)
        try:
            if not (install.stat().st_mode & 0o111):
                issues.append(
                    {
                        "level": "full",
                        "id": "install_not_executable",
                        "msg": "install.sh is not marked executable (chmod +x)",
                        "severity": True,
                    }
                )
        except OSError:
            pass

    scripts = skill_dir / "scripts"
    verify_path = None
    if scripts.is_dir():
        for name in VERIFY_NAMES:
            candidate = scripts / name
            if candidate.is_file():
                verify_path = candidate
                break
    if verify_path is None:
        issues.append(
            {
                "level": "full",
                "id": "verify_missing",
                "msg": "scripts/verify.(js|py|sh|ts) recommended for full package when skill is verifiable",
            }
        )
    else:
        if "verify" not in body.lower() and "scripts/" not in body:
            issues.append(
                {
                    "level": "full",
                    "id": "body_missing_verify_pointer",
                    "msg": "verify script exists but SKILL.md body does not mention scripts/ or verification",
                }
            )

    return issues


def validate(skill_dir: Path, level: str) -> dict[str, Any]:
    skill_dir = skill_dir.resolve()
    skill_md = skill_dir / "SKILL.md"
    fm = None
    body = ""
    if skill_md.is_file():
        raw = skill_md.read_text(encoding="utf-8", errors="replace")
        fm, body = parse_frontmatter(raw)

    issues: list[dict[str, Any]] = []
    issues.extend(check_core(skill_dir, fm, body, skill_md))

    if level in ("recommended", "full") and fm is not None:
        issues.extend(check_recommended(skill_dir, fm, body))
    elif level in ("recommended", "full") and fm is None:
        pass  # core already failed

    if level == "full" and fm is not None:
        issues.extend(check_full(skill_dir, body))

    # Partition hard vs soft
    hard = [i for i in issues if not i.get("severity")]
    soft = [i for i in issues if i.get("severity")]

    passed = len(hard) == 0
    return {
        "skill_dir": str(skill_dir),
        "level": level,
        "passed": passed,
        "issues": issues,
        "hard_fail_count": len(hard),
        "advisory_count": len(soft),
        "frontmatter": fm,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Agent Skills package structure (SPEC.md)")
    parser.add_argument("skill_dir", type=Path, help="Path to skill folder containing SKILL.md")
    parser.add_argument(
        "--level",
        choices=("core", "recommended", "full"),
        default="recommended",
        help="Compliance level to enforce (default: recommended)",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    if not args.skill_dir.exists():
        print(f"Error: path does not exist: {args.skill_dir}", file=sys.stderr)
        return 2
    if not args.skill_dir.is_dir():
        print(f"Error: not a directory: {args.skill_dir}", file=sys.stderr)
        return 2

    result = validate(args.skill_dir, args.level)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"[{status}] {result['skill_dir']}  (level={result['level']})")
        if result["frontmatter"]:
            print(f"  name: {result['frontmatter'].get('name', '')}")
        for issue in result["issues"]:
            tag = "advisory" if issue.get("severity") else issue["level"]
            print(f"  - ({tag}) {issue['id']}: {issue['msg']}")
        if result["passed"] and not result["issues"]:
            print("  No issues found.")
        elif result["passed"] and result["advisory_count"]:
            print(f"  Passed with {result['advisory_count']} advisory item(s).")

    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
