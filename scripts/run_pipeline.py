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
from tqdm import tqdm

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


def update_processed_state(state_file: str, new_post_ids: list):
    """Update state/processed.json with newly processed post IDs."""
    p = Path(state_file)
    p.parent.mkdir(parents=True, exist_ok=True)

    existing = []
    if p.exists():
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    existing = data
        except Exception:
            existing = []

    existing_set = set(str(x) for x in existing)
    for pid in new_post_ids:
        existing_set.add(str(pid))

    with open(p, "w", encoding="utf-8") as f:
        json.dump(sorted(list(existing_set)), f, indent=2)


def run_pipeline(
    handle: str,
    limit: int = 50,
    config_path: str = "config.yaml",
    skip_transcribe: bool = False,
    verbose: bool = False
):
    """
    Run full extraction pipeline:
    1. Fetch posts metadata
    2. Classify posts (caption vs audio vs skip)
    3. Transcribe audio (audio-only, temporary mp3 cleaned up immediately)
    4. Extract structured principles (paraphrased)
    5. Merge into principles.json and update SKILL.md
    6. Record processed post IDs in state/processed.json
    """
    config = load_config(config_path)
    paths_cfg = config.get("paths", {})
    logs_dir = paths_cfg.get("logs_dir", "logs")
    state_file = paths_cfg.get("state_file", "state/processed.json")
    raw_data_dir = paths_cfg.get("raw_data_dir", "data/raw")

    logger, log_file = setup_pipeline_logging(logs_dir, verbose)

    logger.info(f"=== Starting IG Design-Skill Extractor for @{handle} ===")
    logger.info(f"Configuration: {config_path} | Post limit: {limit} | Log: {log_file}")

    stages = [
        "1. Fetch Metadata",
        "2. Classify & Branch",
        "3. Transcribe Audio",
        "4. Extract Principles",
        "5. Merge & Generate Skill"
    ]

    with tqdm(total=5, desc=f"Pipeline @{handle}", unit="stage") as pbar:
        # Stage 1: Fetch
        pbar.set_description("Stage 1: Fetching post metadata")
        logger.info("--- Stage 1: Fetching post metadata ---")
        posts = fetch_posts(handle, limit=limit, config_path=config_path)
        pbar.update(1)

        if not posts:
            logger.info("No posts to process.")
            return

        # Stage 2: Classify
        pbar.set_description("Stage 2: Classifying posts")
        logger.info("--- Stage 2: Classifying posts ---")
        classified_posts = classify_posts(handle, config_path=config_path)
        pbar.update(1)

        # Stage 3: Transcribe
        pbar.set_description("Stage 3: Transcribing audio")
        logger.info("--- Stage 3: Transcribing audio ---")
        if not skip_transcribe:
            transcribe_posts(handle, config_path=config_path)
        else:
            logger.info("Skipping audio transcription (--skip-transcribe specified).")
        pbar.update(1)

        # Stage 4: Extract
        pbar.set_description("Stage 4: Extracting principles")
        logger.info("--- Stage 4: Extracting design principles ---")
        extracted = extract_principles(handle, config_path=config_path)
        pbar.update(1)

        # Stage 5: Merge
        pbar.set_description("Stage 5: Merging skill")
        logger.info("--- Stage 5: Merging into SKILL.md ---")
        merged = merge_skill(config_path=config_path)
        pbar.update(1)

    # Update processed state
    post_ids = [p.get("post_id") for p in posts if p.get("post_id")]
    update_processed_state(state_file, post_ids)
    logger.info(f"Updated state: {len(post_ids)} post IDs recorded in {state_file}")

    logger.info(f"=== Pipeline completed successfully for @{handle} ===")
    logger.info(f"Total structured principles: {len(merged)}")
    logger.info("Deliverable updated: skills/design-ui-ux/SKILL.md")


def main():
    parser = argparse.ArgumentParser(description="IG Design-Skill Extractor Pipeline Orchestrator")
    parser.add_argument("--handle", required=True, help="Instagram handle (without @)")
    parser.add_argument("--limit", type=int, default=50, help="Maximum number of new posts to process")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--skip-transcribe", action="store_true", help="Skip Whisper audio transcription")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logs")

    args = parser.parse_args()

    run_pipeline(
        handle=args.handle,
        limit=args.limit,
        config_path=args.config,
        skip_transcribe=args.skip_transcribe,
        verbose=args.verbose
    )


if __name__ == "__main__":
    main()
