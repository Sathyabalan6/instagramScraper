"""
Utility: Clean or audit secrets and cookies before sharing or archiving the repository.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

_ROOT_DIR = Path(__file__).resolve().parent.parent


def check_secrets():
    """Check for any local sensitive files in the repository."""
    found_secrets = []
    
    cookies_dir = _ROOT_DIR / "cookies"
    if cookies_dir.exists():
        for f in cookies_dir.glob("*.txt*"):
            if f.name != ".gitkeep" and f.name != "README.md":
                found_secrets.append(f)

    print("=== Secrets & Credentials Audit ===")
    if found_secrets:
        print(f"[WARNING] Found {len(found_secrets)} cookie/credential file(s) inside repo:")
        for s in found_secrets:
            print(f"  - {s.relative_to(_ROOT_DIR)}")
        print("\nRecommendation: Move these files to ~/.config/ig-skill-extractor/cookies.txt or run:")
        print("  python scripts/clean_secrets.py --clean")
        return False
    else:
        print("[OK] No local cookie files detected inside repository.")
        return True


def clean_secrets(backup_to_home: bool = True):
    """Clean local cookies and temp directories, optionally backing them up to ~/.config/."""
    home_dir = Path.home() / ".config" / "ig-skill-extractor"
    if backup_to_home:
        home_dir.mkdir(parents=True, exist_ok=True)

    cookies_dir = _ROOT_DIR / "cookies"
    cleaned = 0

    if cookies_dir.exists():
        for f in cookies_dir.glob("*.txt*"):
            if f.name in [".gitkeep", "README.md"]:
                continue
            if backup_to_home:
                dest = home_dir / f.name
                shutil.copy2(f, dest)
                print(f"Backed up {f.name} -> {dest}")
            os.remove(f)
            print(f"Removed local secret file: {f.relative_to(_ROOT_DIR)}")
            cleaned += 1

    tmp_audio = _ROOT_DIR / "data" / "tmp_audio"
    if tmp_audio.exists():
        for item in tmp_audio.glob("*"):
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        print("Cleaned data/tmp_audio/ directory.")

    print(f"\n[SUCCESS] Scrubbed {cleaned} secret file(s) from repo.")
    if backup_to_home:
        print(f"Your session cookies are safely preserved in: {home_dir}")
        print("The pipeline will automatically read them from there.")


def main():
    parser = argparse.ArgumentParser(description="Scrub or audit sensitive cookies before sharing repo.")
    parser.add_argument("--check", action="store_true", help="Audit repository for local cookies")
    parser.add_argument("--clean", action="store_true", help="Scrub local cookies (backs up to ~/.config/)")
    parser.add_argument("--no-backup", action="store_true", help="Do not backup to ~/.config/ when cleaning")

    args = parser.parse_args()

    if args.clean:
        clean_secrets(backup_to_home=not args.no_backup)
    else:
        check_secrets()


if __name__ == "__main__":
    main()
