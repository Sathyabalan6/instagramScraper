"""
Stage 2: Classify posts and branch extraction path.
Determines whether to extract principles directly from caption, queue for audio transcription, or skip.
"""

import os
import re
import json
import argparse
import logging
from pathlib import Path
import yaml

logger = logging.getLogger("classify_posts")


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def classify_single_post(
    post: dict,
    min_words: int = 40,
    keywords: list = None
) -> dict:
    """
    Classify a post into 'caption', 'audio', or 'skip' path.
    """
    if keywords is None:
        keywords = [
            "tip", "rule", "spacing", "contrast", "hierarchy", "padding",
            "grid", "typography", "font", "color", "palette", "shadow",
            "radius", "alignment", "whitespace", "breakpoint", "accessibility",
            "a11y", "ux", "ui", "clutter", "balance", "cta", "button",
            "landing", "card", "nav", "navbar", "animation", "motion",
            "micro-interaction", "glassmorphism", "elevation", "wireframe",
            "mockup", "figma", "token", "system", "responsive", "darkmode", "lightmode"
        ]

    caption = post.get("caption") or ""
    # Split into words (ignoring extra whitespace and hashtags/symbols)
    words = re.findall(r"\b\w+\b", caption)
    word_count = len(words)

    # Check for keyword matches (word boundary matching, case-insensitive)
    matched_keywords = []
    caption_lower = caption.lower()
    for kw in keywords:
        pattern = rf"\b{re.escape(kw.lower())}\b"
        if re.search(pattern, caption_lower):
            matched_keywords.append(kw)

    has_substance = (word_count >= min_words) and (len(matched_keywords) > 0)

    if has_substance:
        path = "caption"
        reason = f"Detailed caption ({word_count} words) with design keywords: {', '.join(matched_keywords[:3])}"
    elif post.get("is_video", False):
        path = "audio"
        reason = "Video reel with brief caption; queued for audio transcription"
    else:
        path = "skip"
        reason = f"Static image without substantial design caption ({word_count} words, {len(matched_keywords)} keywords)"

    return {
        "path": path,
        "reason": reason,
        "word_count": word_count,
        "matched_keywords": matched_keywords
    }


def classify_posts(
    handle: str,
    config_path: str = "config.yaml"
) -> list:
    """
    Load raw posts for handle, run classification heuristic on each, and save results.
    """
    config = load_config(config_path)
    classify_cfg = config.get("classify", {})
    paths_cfg = config.get("paths", {})

    min_words = classify_cfg.get("min_caption_words", 40)
    keywords = classify_cfg.get("keywords", [])
    output_dir = paths_cfg.get("output_dir", "output")
    raw_data_dir = paths_cfg.get("raw_data_dir", "data/raw")

    out_posts_file = Path(output_dir) / handle / "posts.json"
    raw_posts_file = Path(raw_data_dir) / handle / "posts.json"

    target_file = None
    if out_posts_file.exists():
        target_file = out_posts_file
    elif raw_posts_file.exists():
        target_file = raw_posts_file
    else:
        logger.error(f"No posts.json found in {out_posts_file} or {raw_posts_file}. Run fetch_posts.py first.")
        return []

    with open(target_file, "r", encoding="utf-8") as f:
        posts = json.load(f)

    stats = {"caption": 0, "audio": 0, "skip": 0}

    for post in posts:
        classification = classify_single_post(post, min_words=min_words, keywords=keywords)
        post["classification"] = classification
        stats[classification["path"]] += 1
        logger.debug(
            f"Post {post.get('shortcode')}: path={classification['path']}, "
            f"words={classification['word_count']}, matched={classification['matched_keywords']}"
        )

    for pfile in [out_posts_file, raw_posts_file]:
        pfile.parent.mkdir(parents=True, exist_ok=True)
        with open(pfile, "w", encoding="utf-8") as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)

    logger.info(
        f"Classified {len(posts)} posts for @{handle} -> "
        f"caption: {stats['caption']}, audio: {stats['audio']}, skip: {stats['skip']}"
    )

    return posts


def main():
    parser = argparse.ArgumentParser(description="Stage 2: Classify posts into caption/audio/skip paths.")
    parser.add_argument("--handle", required=True, help="Instagram username handle")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logging")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    classify_posts(args.handle, config_path=args.config)


if __name__ == "__main__":
    main()
