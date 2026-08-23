"""
Stage 4: Merge extracted principles into structured store (principles.json)
and regenerate the deliverable Claude Skill (SKILL.md).
Performs fuzzy deduplication using rapidfuzz.
"""

import os
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
import yaml

try:
    from rapidfuzz import fuzz

    def compute_similarity(s1: str, s2: str) -> float:
        return fuzz.token_sort_ratio(s1, s2)
except ImportError:
    from difflib import SequenceMatcher

    def compute_similarity(s1: str, s2: str) -> float:
        # Normalize and sort tokens for token-sort similarity
        tokens1 = " ".join(sorted(s1.lower().split()))
        tokens2 = " ".join(sorted(s2.lower().split()))
        return SequenceMatcher(None, tokens1, tokens2).ratio() * 100.0

logger = logging.getLogger("merge_skill")

CATEGORIES_ORDER = [
    "spacing",
    "color",
    "typography",
    "hierarchy",
    "motion",
    "accessibility",
    "layout"
]


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_principles_store(store_path: str) -> list:
    """Load existing principles store."""
    if os.path.exists(store_path):
        try:
            with open(store_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception as e:
            logger.warning(f"Failed to read principles store at {store_path}: {e}")
    return []


def save_principles_store(principles: list, store_path: str):
    """Save principles store to JSON file."""
    p = Path(store_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(principles, f, indent=2, ensure_ascii=False)


def find_matching_principle(new_p: dict, existing_list: list, threshold: float = 85.0) -> int:
    """
    Find index of matching principle in existing_list using rapidfuzz token_sort_ratio.
    Returns index if match score >= threshold, else -1.
    """
    new_name = new_p.get("principle", "").lower().strip()
    new_cat = new_p.get("category", "").lower().strip()

    best_idx = -1
    best_score = 0.0

    for idx, item in enumerate(existing_list):
        item_cat = item.get("category", "").lower().strip()
        if item_cat != new_cat:
            continue

        item_name = item.get("principle", "").lower().strip()
        score = compute_similarity(new_name, item_name)

        if score > best_score and score >= threshold:
            best_score = score
            best_idx = idx

    return best_idx


def merge_principles_list(
    new_principles: list,
    existing_principles: list,
    threshold: float = 85.0
) -> list:
    """
    Deduplicate and merge new principles into existing list.
    """
    merged = list(existing_principles)

    for new_p in new_principles:
        match_idx = find_matching_principle(new_p, merged, threshold=threshold)

        # Normalize sources format
        new_source = {
            "handle": new_p.get("source_handle", ""),
            "date": new_p.get("source_date", ""),
            "url": new_p.get("source_url", "")
        }

        if match_idx >= 0:
            target = merged[match_idx]
            logger.info(f"Duplicate found: '{new_p.get('principle')}' matches '{target.get('principle')}' -> Merging.")

            # Ensure target has sources list
            if "sources" not in target:
                target["sources"] = []
                if "source_url" in target:
                    target["sources"].append({
                        "handle": target.get("source_handle", ""),
                        "date": target.get("source_date", ""),
                        "url": target.get("source_url", "")
                    })

            # Check if new source is already cited
            existing_urls = {s.get("url") for s in target["sources"]}
            if new_source.get("url") and new_source["url"] not in existing_urls:
                target["sources"].append(new_source)

            # Enrich why/example if new one has more substance
            if len(new_p.get("why", "")) > len(target.get("why", "")):
                target["why"] = new_p["why"]
            if len(new_p.get("example", "")) > len(target.get("example", "")) and target.get("example") in ["None specified", ""]:
                target["example"] = new_p["example"]

        else:
            # Create new structured record
            record = {
                "principle": new_p.get("principle"),
                "category": new_p.get("category"),
                "rule": new_p.get("rule"),
                "why": new_p.get("why"),
                "example": new_p.get("example"),
                "confidence": new_p.get("confidence", "medium"),
                "sources": [new_source] if new_source.get("url") else []
            }
            merged.append(record)
            logger.info(f"Appended new principle: '{record['principle']}' [{record['category']}]")

    return merged


def generate_skill_markdown(principles: list, output_path: str):
    """
    Generate clean, authoritative SKILL.md formatted for Claude skills.
    """
    grouped = {cat: [] for cat in CATEGORIES_ORDER}
    for p in principles:
        cat = p.get("category", "layout").lower()
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(p)

    lines = [
        "---",
        "name: design-ui-ux",
        'description: UI/UX design principles compiled from design creator content (spacing, color, typography, hierarchy, motion, accessibility, layout). Use this skill whenever creating, reviewing, or critiquing UI/UX design work — web pages, app interfaces, dashboards, forms, or any visual layout — even if the user doesn\'t explicitly ask for "design principles."',
        "---",
        "",
        "# UI/UX Design Skill",
        "",
        "This style guide provides actionable, production-ready UI/UX rules distilled from leading design content.",
        "Use these principles to guide interface structure, component design, visual hierarchy, and accessibility audits.",
        ""
    ]

    total_principles = 0

    for cat in CATEGORIES_ORDER:
        cat_title = cat.title()
        lines.append(f"## {cat_title}\n")
        items = grouped.get(cat, [])
        if not items:
            lines.append("_(none yet)_\n")
            continue

        for item in sorted(items, key=lambda x: x.get("principle", "")):
            total_principles += 1
            title = item.get("principle", "Principle")
            rule = item.get("rule", "")
            why = item.get("why", "")
            example = item.get("example", "")
            sources = item.get("sources", [])

            lines.append(f"### {title}")
            lines.append(f"- **Rule**: {rule}")
            if why:
                lines.append(f"- **Why**: {why}")
            if example and example != "None specified":
                lines.append(f"- **Example**: {example}")

            if sources:
                dates = [s.get("date") for s in sources if s.get("date")]
                most_recent = max(dates) if dates else "recent"
                source_links = [f"[@{s.get('handle', 'creator')}]({s.get('url')})" for s in sources if s.get("url")]
                citations = ", ".join(source_links) if source_links else f"{len(sources)} posts"
                lines.append(f"- **Sources**: {len(sources)} post(s) (latest: {most_recent}) — {citations}")
            lines.append("")

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).strip() + "\n")

    logger.info(f"Generated {output_path} with {total_principles} principles across {len(CATEGORIES_ORDER)} categories.")


def merge_skill(config_path: str = "config.yaml", new_principles: list = None) -> list:
    """
    Merge newly extracted principles (or all from raw data) into principles.json and update SKILL.md.
    """
    config = load_config(config_path)
    merge_cfg = config.get("merge", {})
    paths_cfg = config.get("paths", {})

    threshold = float(merge_cfg.get("dedup_similarity_threshold", 85))
    skill_output_path = merge_cfg.get("skill_output_path", "skills/design-ui-ux/SKILL.md")
    store_path = merge_cfg.get("principles_store_path", "skills/design-ui-ux/principles.json")
    raw_data_dir = paths_cfg.get("raw_data_dir", "data/raw")

    existing_principles = load_principles_store(store_path)

    # If new_principles is not passed directly, gather from raw_data_dir
    if new_principles is None:
        new_principles = []
        raw_path = Path(raw_data_dir)
        if raw_path.exists():
            for handle_dir in raw_path.iterdir():
                if handle_dir.is_dir():
                    posts_file = handle_dir / "posts.json"
                    if posts_file.exists():
                        try:
                            with open(posts_file, "r", encoding="utf-8") as f:
                                posts = json.load(f)
                                for post in posts:
                                    for p in post.get("extracted_principles", []):
                                        new_principles.append(p)
                        except Exception as e:
                            logger.warning(f"Error reading {posts_file}: {e}")

    merged = merge_principles_list(new_principles, existing_principles, threshold=threshold)
    save_principles_store(merged, store_path)
    generate_skill_markdown(merged, skill_output_path)

    return merged


def main():
    parser = argparse.ArgumentParser(description="Stage 4: Merge principles into SKILL.md with fuzzy deduplication.")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--threshold", type=float, default=None, help="Override similarity threshold (0-100)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logging")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    merge_skill(config_path=args.config)


if __name__ == "__main__":
    main()
