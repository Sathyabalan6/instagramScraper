"""
Orchestrator: Runs stages 1 through 4 in sequence for a given Instagram handle.
Updates state/processed.json and writes run logs to logs/run_<timestamp>.log.
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Ensure project root and scripts directory are in sys.path
_CURRENT_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _CURRENT_DIR.parent
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))
if str(_CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(_CURRENT_DIR))

import yaml

try:
    from tqdm import tqdm
except ImportError:
    class tqdm:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def update(self, *args, **kwargs):
            pass
        def set_description(self, *args, **kwargs):
            pass

# Import pipeline stage modules
try:
    from scripts.fetch_posts import fetch_posts
    from scripts.classify_posts import classify_posts
    from scripts.transcribe_audio import transcribe_posts
    from scripts.extract_principles import extract_principles
    from scripts.merge_skill import merge_skill
except ImportError:
    from fetch_posts import fetch_posts
    from classify_posts import classify_posts
    from transcribe_audio import transcribe_posts
    from extract_principles import extract_principles
    from merge_skill import merge_skill


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def setup_pipeline_logging(logs_dir: str, verbose: bool = False) -> tuple:
    """Setup dual file and console logging."""
    p = Path(logs_dir)
    p.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = p / f"run_{timestamp}.log"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Clean existing handlers
    root_logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # File handler
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    root_logger.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG if verbose else logging.INFO)
    ch.setFormatter(formatter)
    root_logger.addHandler(ch)

    return root_logger, log_file


def resolve_target(
    target: str = None,
    handle: str = None,
    collection: str = None
) -> tuple:
    """
    Resolve target into (clean_handle, clean_collection).
    Auto-detects:
    - Collection URLs (e.g. https://www.instagram.com/<user>/saved/<name>/<id>/) -> collection
    - Profile URLs (e.g. https://www.instagram.com/<user>/) -> handle
    - Handles with or without @ (e.g. @zanderwhitehurst, zanderwhitehurst) -> handle
    """
    import re

    if handle:
        # Check if user passed a URL inside --handle
        if "http://" in handle or "https://" in handle or "/saved/" in handle:
            target = handle
            handle = None
        else:
            return handle.lstrip("@").strip(), None

    if collection:
        return None, collection.strip()

    if not target:
        raise ValueError("Either --target, --handle, or --collection must be specified.")

    target = target.strip()

    # Case 1: Saved collection URL or slug
    if "/saved/" in target or "/collection/" in target:
        return None, target

    # Case 2: Full Instagram profile URL
    if target.startswith("http://") or target.startswith("https://") or "instagram.com" in target:
        match = re.search(r"instagram\.com/([a-zA-Z0-9._]+)/?", target)
        if match:
            u = match.group(1)
            if u not in ["p", "reel", "stories", "explore", "direct"]:
                return u, None
        return None, target

    # Case 3: Standard creator handle
    return target.lstrip("@"), None


def update_processed_state(state_file: str, posts_or_ids: list):
    """
    Update state/processed.json with newly processed posts or IDs.
    Maintains a rich stage ledger while preserving full backward-compatibility with flat lists.
    """
    p = Path(state_file)
    p.parent.mkdir(parents=True, exist_ok=True)

    state_data = {"version": "2.0", "posts": {}}
    if p.exists():
        try:
            with open(p, "r", encoding="utf-8") as f:
                raw = json.load(f)
                if isinstance(raw, list):
                    for pid in raw:
                        state_data["posts"][str(pid)] = {
                            "stages": {"fetched": True, "completed": True},
                            "last_updated": datetime.now().isoformat()
                        }
                elif isinstance(raw, dict):
                    if "posts" in raw and isinstance(raw["posts"], dict):
                        state_data = raw
                    else:
                        for k, v in raw.items():
                            state_data["posts"][str(k)] = v if isinstance(v, dict) else {"stages": {"completed": True}}
        except Exception:
            pass

    for item in posts_or_ids:
        if isinstance(item, dict):
            pid = str(item.get("post_id") or "")
            if not pid:
                continue
            sc = item.get("shortcode", "")
            has_trans = bool(item.get("transcript"))
            has_prin = bool(item.get("principles"))
            state_data["posts"][pid] = {
                "shortcode": sc,
                "date": item.get("date", ""),
                "is_video": item.get("is_video", False),
                "stages": {
                    "fetched": True,
                    "transcribed": has_trans,
                    "extracted": has_prin,
                    "completed": True
                },
                "principles_count": len(item.get("principles", [])),
                "last_updated": datetime.now().isoformat()
            }
        else:
            pid = str(item)
            if pid and pid not in state_data["posts"]:
                state_data["posts"][pid] = {
                    "stages": {"fetched": True, "completed": True},
                    "last_updated": datetime.now().isoformat()
                }

    with open(p, "w", encoding="utf-8") as f:
        json.dump(state_data, f, indent=2)


def run_pipeline(
    target: str = None,
    handle: str = None,
    collection: str = None,
    limit: int = 50,
    config_path: str = "config.yaml",
    skip_transcribe: bool = False,
    verbose: bool = False,
    refresh: bool = False
):
    """
    Run full extraction pipeline:
    1. Resolve target (URL, @handle, or collection)
    2. Fetch posts metadata (from creator handle or saved collection)
    3. Classify posts (caption vs audio vs skip)
    4. Transcribe audio (audio-only, temporary mp3 cleaned up immediately)
    5. Extract structured principles via LLM analysis
    6. Merge into principles.json and update SKILL.md
    7. Record processed post IDs and stages in state/processed.json
    """
    handle, collection = resolve_target(target=target, handle=handle, collection=collection)

    config = load_config(config_path)
    paths_cfg = config.get("paths", {})
    logs_dir = paths_cfg.get("logs_dir", "logs")
    state_file = paths_cfg.get("state_file", "state/processed.json")
    raw_data_dir = paths_cfg.get("raw_data_dir", "data/raw")

    logger, log_file = setup_pipeline_logging(logs_dir, verbose)

    if collection:
        import re
        slug_match = re.search(r"/saved/([^/?#]+)", collection)
        col_slug = slug_match.group(1) if slug_match else collection.strip().rstrip("/").split("/")[-1]
        target_name = handle or f"collection_{col_slug.lower()}"
        display_name = f"Collection '{col_slug}'"
    else:
        target_name = handle
        display_name = f"@{handle}"

    logger.info(f"=== Starting IG Design-Skill Extractor for {display_name} ===")
    logger.info(f"Configuration: {config_path} | Post limit: {limit} | Log: {log_file}")

    total_stages = 4 if skip_transcribe else 5
    with tqdm(total=total_stages, desc=f"Pipeline {display_name}", unit="stage") as pbar:
        # Stage 1: Fetch
        pbar.set_description("Stage 1: Fetching post metadata")
        logger.info("--- Stage 1: Fetching post metadata ---")
        posts = fetch_posts(handle=handle, collection=collection, limit=limit, config_path=config_path)
        pbar.update(1)

        if not posts:
            logger.info("No posts to process.")
            return

        # Stage 2: Classify
        pbar.set_description("Stage 2: Classifying posts")
        logger.info("--- Stage 2: Classifying posts ---")
        classified_posts = classify_posts(target_name, config_path=config_path)
        pbar.update(1)

        # Stage 3: Transcribe (if not skipped)
        if not skip_transcribe:
            pbar.set_description("Stage 3: Transcribing audio")
            logger.info("--- Stage 3: Transcribing audio ---")
            transcribe_posts(target_name, config_path=config_path)
            pbar.update(1)

        # Stage Extract
        extract_stage = 3 if skip_transcribe else 4
        pbar.set_description(f"Stage {extract_stage}: Extracting principles")
        logger.info(f"--- Stage {extract_stage}: Extracting design principles ---")
        extracted = extract_principles(target_name, config_path=config_path, refresh=refresh)
        pbar.update(1)

        # Stage Merge
        merge_stage = 4 if skip_transcribe else 5
        pbar.set_description(f"Stage {merge_stage}: Merging skill")
        logger.info(f"--- Stage {merge_stage}: Merging into SKILL.md & creator output folder ---")
        merged = merge_skill(handle=target_name, config_path=config_path)
        pbar.update(1)

    # Update processed state with full stage ledger
    update_processed_state(state_file, posts)
    logger.info(f"Updated stage state ledger: {len(posts)} posts recorded in {state_file}")

    output_dir = paths_cfg.get("output_dir", "output")
    skills_dir = paths_cfg.get("skills_dir", "skills")
    creator_dir = Path(output_dir) / target_name

    from scripts.merge_skill import get_clean_skill_name
    clean_skill_name = get_clean_skill_name(target_name)
    skill_dir = Path(skills_dir) / clean_skill_name

    logger.info(f"=== Pipeline completed successfully for {display_name} ===")
    logger.info(f"Target Skill Directory: {skill_dir.resolve()}")
    logger.info(f"  |-- Skill Deliverable:  {skill_dir / 'SKILL.md'}")
    logger.info(f"  |-- Summary Report:     {skill_dir / 'SUMMARY.md'}")
    logger.info(f"  \\-- Principles JSON:    {skill_dir / 'principles.json'}")
    logger.info(f"Raw Posts & Media Data:   {creator_dir / 'posts.json'}")


def main():
    parser = argparse.ArgumentParser(description="IG Design-Skill Extractor Pipeline Orchestrator")
    parser.add_argument(
        "--target", "-t",
        help="Target Instagram handle, profile URL, or saved collection URL (smart auto-detection)"
    )
    parser.add_argument("--handle", help="Instagram handle (without @)")
    parser.add_argument(
        "--collection", "--collection-url",
        dest="collection",
        help="Instagram saved collection slug or URL"
    )
    parser.add_argument("--limit", type=int, default=50, help="Maximum number of new posts to process")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--skip-transcribe", action="store_true", help="Skip Whisper audio transcription")
    parser.add_argument("--refresh", action="store_true", help="Force re-extraction of design principles on all posts")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logs")

    args = parser.parse_args()

    if not args.target and not args.handle and not args.collection:
        parser.error("At least one target must be provided via --target, --handle, or --collection.")

    run_pipeline(
        target=args.target,
        handle=args.handle,
        collection=args.collection,
        limit=args.limit,
        config_path=args.config,
        skip_transcribe=args.skip_transcribe,
        verbose=args.verbose,
        refresh=args.refresh
    )


if __name__ == "__main__":
    main()

