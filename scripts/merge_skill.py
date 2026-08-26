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


def generate_skill_markdown(
    principles: list,
    output_path: str,
    skill_name: str = "design-ui-ux",
    description: str = None
):
    """
    Generate clean, authoritative SKILL.md formatted for Claude skills.
    Includes confidence filtering, rich triggering frontmatter, and consensus weighting.
    """
    # Filter verified vs unverified
    verified_principles = [p for p in principles if p.get("confidence", "medium").lower() in ["high", "medium"]]
    unverified_principles = [p for p in principles if p.get("confidence", "medium").lower() == "low"]

    # Gather active categories and topics for dynamic frontmatter
    active_categories = sorted(list(set(p.get("category", "layout").lower() for p in verified_principles)))
    cat_str = ", ".join(c.title() for c in active_categories) if active_categories else "Color, Layout, Hierarchy"

    if description is None:
        description = (
            f"Actionable UI/UX design style guide covering {cat_str}. "
            "Use this skill whenever creating, reshaping, critiquing, or reviewing UI/UX interfaces — "
            "including landing pages, dashboards, hero layouts, typography hierarchy, dark/light color palettes, "
            "interactive cards, navigation headers, and modal states — even if the user does not explicitly request 'design principles.'"
        )

    grouped = {cat: [] for cat in CATEGORIES_ORDER}
    for p in verified_principles:
        cat = p.get("category", "layout").lower()
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(p)

    lines = [
        "---",
        f"name: {skill_name}",
        f'description: "{description}"',
        "---",
        "",
        "# UI/UX Design Skill",
        "",
        "This style guide provides actionable, production-ready UI/UX rules distilled from leading design creators.",
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
            confidence = item.get("confidence", "medium").upper()

            lines.append(f"### {title}")
            lines.append(f"- **Rule**: {rule}")
            if why:
                lines.append(f"- **Why**: {why}")
            if example and example != "None specified":
                lines.append(f"- **Example**: {example}")

            # Source Diversity & Consensus Weighting
            if sources:
                unique_handles = sorted(list(set(s.get("handle") for s in sources if s.get("handle"))))
                dates = [s.get("date") for s in sources if s.get("date")]
                most_recent = max(dates) if dates else "recent"

                if len(unique_handles) >= 2:
                    handles_str = ", ".join(f"@{h}" for h in unique_handles)
                    lines.append(f"- **Consensus**: ⭐ **Industry Standard** (Cross-validated across {len(unique_handles)} creators: {handles_str})")
                elif unique_handles:
                    lines.append(f"- **Consensus**: 🎯 **Creator Pattern** (Verified across {len(sources)} post(s) by @{unique_handles[0]})")

                source_links = [f"[@{s.get('handle', 'creator')}]({s.get('url')})" for s in sources if s.get("url")]
                citations = ", ".join(source_links) if source_links else f"{len(sources)} posts"
                lines.append(f"- **Sources**: {len(sources)} post(s) (latest: {most_recent}) — {citations}")

            lines.append("")

    # Quarantined / Unverified Low-Confidence Drafts (if any)
    if unverified_principles:
        lines.append("## Unverified / Draft Observations\n")
        lines.append("> _Note: The following observations were extracted with low confidence and require manual verification before production use._\n")
        for item in unverified_principles:
            lines.append(f"### [Draft] {item.get('principle', 'Observation')}")
            lines.append(f"- **Rule**: {item.get('rule', '')}")
            lines.append(f"- **Category**: {item.get('category', 'layout')}")
            lines.append("")

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).strip() + "\n")

    logger.info(f"Generated {output_path} with {total_principles} verified principles across {len(CATEGORIES_ORDER)} categories.")


def generate_creator_summary_markdown(
    handle: str,
    principles: list,
    posts: list,
    output_path: str
):
    """
    Generate a visual, comprehensive summary report for a specific creator.
    """
    total_posts = len(posts)
    transcribed_count = sum(1 for p in posts if p.get("transcript"))
    video_count = sum(1 for p in posts if p.get("is_video"))
    dates = [p.get("date") for p in posts if p.get("date")]
    date_range = f"{min(dates)} to {max(dates)}" if dates else "Recent"

    cat_counts = {cat: 0 for cat in CATEGORIES_ORDER}
    for p in principles:
        cat = p.get("category", "layout").lower()
        if cat in cat_counts:
            cat_counts[cat] += 1

    lines = [
        f"# Design Skill Extraction Report: @{handle}",
        "",
        f"> **Creator Profile:** [@{handle}](https://www.instagram.com/{handle}/)  ",
        f"> **Extracted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"> **Analyzed Post Range:** {date_range}",
        "",
        "---",
        "",
        "## Overview & Extraction Metrics",
        "",
        "| Metric | Count |",
        "|---|---|",
        f"| **Total Posts Analyzed** | `{total_posts}` |",
        f"| **Video Reels Transcribed** | `{transcribed_count}` / `{video_count}` |",
        f"| **Unique Design Principles** | `{len(principles)}` |",
        f"| **Active Categories** | `{sum(1 for c, n in cat_counts.items() if n > 0)}` / `{len(CATEGORIES_ORDER)}` |",
        "",
        "### Category Distribution",
        "",
        "| Category | Principles Extracted |",
        "|---|---|",
    ]

    for cat in CATEGORIES_ORDER:
        cnt = cat_counts.get(cat, 0)
        if cnt > 0:
            lines.append(f"| **{cat.title()}** | `{cnt}` principle(s) |")

    lines.extend([
        "",
        "---",
        "",
        "## Distilled Design Principles",
        ""
    ])

    grouped = {cat: [] for cat in CATEGORIES_ORDER}
    for p in principles:
        cat = p.get("category", "layout").lower()
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(p)

    for cat in CATEGORIES_ORDER:
        items = grouped.get(cat, [])
        if not items:
            continue

        lines.append(f"### {cat.title()}\n")
        for item in sorted(items, key=lambda x: x.get("principle", "")):
            title = item.get("principle", "Principle")
            rule = item.get("rule", "")
            why = item.get("why", "")
            example = item.get("example", "")
            sources = item.get("sources", [])

            lines.append(f"#### {title}")
            lines.append(f"- **Guideline**: {rule}")
            if why:
                lines.append(f"- **Rationale**: {why}")
            if example and example != "None specified":
                lines.append(f"- **Practical Application**: {example}")
            if sources:
                source_links = [f"[{s.get('date', 'Link')}]({s.get('url')})" for s in sources if s.get("url")]
                citations = ", ".join(source_links) if source_links else f"{len(sources)} posts"
                lines.append(f"- **Cited Sources ({len(sources)})**: {citations}")
            lines.append("")

    lines.extend([
        "---",
        "",
        "## Source Posts Index",
        "",
        "| Shortcode | Date | Type | Likes | Caption Summary | Reel Transcript Available | Link |",
        "|---|---|---|---|---|---|---|"
    ])

    for p in posts:
        code = p.get("shortcode", "")
        pdate = p.get("date", "")
        ptype = "Video/Reel" if p.get("is_video") else "Image/Carousel"
        likes = f"{p.get('like_count', 0):,}"
        cap = (p.get("caption") or "").replace("\n", " ").strip()
        cap_summary = (cap[:45] + "...") if len(cap) > 45 else cap
        has_trans = "Yes" if p.get("transcript") else "No"
        url = p.get("url", f"https://www.instagram.com/p/{code}/")
        lines.append(f"| `{code}` | {pdate} | {ptype} | {likes} | {cap_summary} | {has_trans} | [View Post]({url}) |")

    lines.append("")

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).strip() + "\n")

    logger.info(f"Generated creator summary at {output_path}")


def merge_skill(
    handle: str = None,
    config_path: str = "config.yaml",
    new_principles: list = None
) -> list:
    """
    Merge newly extracted principles into creator-specific files (output/<handle>/)
    and aggregate into the global principles store (skills/design-ui-ux/).
    """
    config = load_config(config_path)
    merge_cfg = config.get("merge", {})
    paths_cfg = config.get("paths", {})

    threshold = float(merge_cfg.get("dedup_similarity_threshold", 85))
    skill_output_path = merge_cfg.get("skill_output_path", "skills/design-ui-ux/SKILL.md")
    store_path = merge_cfg.get("principles_store_path", "skills/design-ui-ux/principles.json")
    output_dir = paths_cfg.get("output_dir", "output")
    raw_data_dir = paths_cfg.get("raw_data_dir", "data/raw")

    # --- Step 1: Process specific handle if provided ---
    if handle:
        handle_out_dir = Path(output_dir) / handle
        handle_out_dir.mkdir(parents=True, exist_ok=True)

        creator_principles_raw = []
        creator_posts = []

        # Load creator posts
        for pfile in [handle_out_dir / "posts.json", Path(raw_data_dir) / handle / "posts.json"]:
            if pfile.exists():
                try:
                    with open(pfile, "r", encoding="utf-8") as f:
                        creator_posts = json.load(f)
                        for post in creator_posts:
                            for p in post.get("extracted_principles", []):
                                creator_principles_raw.append(p)
                    break
                except Exception as e:
                    logger.warning(f"Error reading posts for creator merge: {e}")

        # If new_principles passed explicitly, add them
        if new_principles:
            creator_principles_raw.extend(new_principles)

        # Deduplicate creator's own principles
        creator_merged = merge_principles_list(creator_principles_raw, [], threshold=threshold)

        # Save creator-specific outputs
        creator_store_path = handle_out_dir / "principles.json"
        creator_skill_path = handle_out_dir / "SKILL.md"
        creator_summary_path = handle_out_dir / "SUMMARY.md"

        save_principles_store(creator_merged, str(creator_store_path))
        generate_skill_markdown(
            principles=creator_merged,
            output_path=str(creator_skill_path),
            skill_name=f"design-ui-ux-{handle}",
            description=f"UI/UX design principles distilled from @{handle} content."
        )
        generate_creator_summary_markdown(
            handle=handle,
            principles=creator_merged,
            posts=creator_posts,
            output_path=str(creator_summary_path)
        )

    # --- Step 2: Global multi-creator aggregation ---
    all_raw_principles = []
    
    # Gather principles from all handles under output/ and data/raw/
    searched_handles = set()
    for base_dir in [Path(output_dir), Path(raw_data_dir)]:
        if base_dir.exists():
            for h_dir in base_dir.iterdir():
                if h_dir.is_dir() and h_dir.name not in searched_handles:
                    searched_handles.add(h_dir.name)
                    pfile = h_dir / "posts.json"
                    if pfile.exists():
                        try:
                            with open(pfile, "r", encoding="utf-8") as f:
                                posts = json.load(f)
                                for post in posts:
                                    for p in post.get("extracted_principles", []):
                                        all_raw_principles.append(p)
                        except Exception as e:
                            logger.warning(f"Error reading {pfile}: {e}")

    existing_global = load_principles_store(store_path)
    global_merged = merge_principles_list(all_raw_principles, existing_global, threshold=threshold)
    save_principles_store(global_merged, store_path)
    generate_skill_markdown(global_merged, skill_output_path)

    return global_merged


def main():
    parser = argparse.ArgumentParser(description="Stage 4: Merge principles into SKILL.md with fuzzy deduplication.")
    parser.add_argument("--handle", default=None, help="Instagram username handle for creator-specific output")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--threshold", type=float, default=None, help="Override similarity threshold (0-100)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logging")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    merge_skill(handle=args.handle, config_path=args.config)


if __name__ == "__main__":
    main()
