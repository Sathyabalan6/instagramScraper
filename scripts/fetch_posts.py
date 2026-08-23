"""
Stage 1: Fetch Instagram post metadata without downloading images or video files.
Follows strict constraints: metadata only, rate limited, respects processed state.
"""

import os
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from http.cookiejar import MozillaCookieJar
import yaml
import instaloader

# Configure logger
logger = logging.getLogger("fetch_posts")


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_processed_ids(state_file: str) -> set:
    """Load already processed post IDs to ensure idempotency."""
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return set(str(item) for item in data)
                elif isinstance(data, dict):
                    return set(str(k) for k in data.keys())
        except Exception as e:
            logger.warning(f"Could not read state file {state_file}: {e}")
    return set()


def resolve_cookie_file(cookies_file: str) -> str:
    """
    Ensure the cookie file is in Netscape format for Instaloader and yt-dlp.
    Automatically converts JSON-format cookie exports if detected.
    """
    if not cookies_file or not os.path.exists(cookies_file):
        return None

    # Test if it already loads as Netscape
    try:
        jar = MozillaCookieJar(cookies_file)
        jar.load(ignore_discard=True, ignore_expires=True)
        return cookies_file
    except Exception:
        pass

    # Try parsing as JSON cookie export
    try:
        with open(cookies_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        cookies = data.get("cookies", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        if not cookies:
            return None

        netscape_path = Path(cookies_file).parent / "instagram_cookies.netscape.txt"
        lines = ["# Netscape HTTP Cookie File", "# Auto-converted from JSON format"]

        for c in cookies:
            domain = c.get("domain", ".instagram.com")
            flag = "TRUE" if domain.startswith(".") else "FALSE"
            path = c.get("path", "/")
            secure = "TRUE" if c.get("secure", False) else "FALSE"
            expiration = int(c.get("expirationDate", 0)) if c.get("expirationDate") else 2147483647
            name = c.get("name", "")
            value = c.get("value", "")
            if name:
                lines.append(f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}")

        with open(netscape_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        logger.info(f"Converted JSON cookies to Netscape format ({len(cookies)} cookies).")
        return str(netscape_path)
    except Exception as e:
        logger.warning(f"Could not parse cookie file {cookies_file}: {e}")
        return None


def setup_instaloader(cookies_file: str = None) -> instaloader.Instaloader:
    """
    Initialize Instaloader strictly in metadata-only mode.
    Disables downloading pictures, videos, thumbnails, and comments.
    """
    loader = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        quiet=True
    )

    resolved_cookie_file = resolve_cookie_file(cookies_file)
    if resolved_cookie_file and os.path.exists(resolved_cookie_file):
        try:
            cookie_jar = MozillaCookieJar(resolved_cookie_file)
            cookie_jar.load(ignore_discard=True, ignore_expires=True)
            loader.context._session.cookies = cookie_jar
            logger.info("Loaded Instagram session cookies successfully.")
        except Exception as e:
            logger.warning(f"Failed to load cookies from {resolved_cookie_file}: {e}")

    return loader


def fetch_posts(
    handle: str,
    limit: int = 50,
    config_path: str = "config.yaml"
) -> list:
    """
    Fetch up to `limit` new posts from `handle`, saving metadata to data/raw/<handle>/posts.json.
    Never downloads or persists image/video media files.
    """
    config = load_config(config_path)
    ig_cfg = config.get("instagram", {})
    paths_cfg = config.get("paths", {})

    request_delay = ig_cfg.get("request_delay_seconds", 3)
    cookies_file = ig_cfg.get("cookies_file", "cookies/instagram_cookies.txt")
    raw_data_dir = paths_cfg.get("raw_data_dir", "data/raw")
    state_file = paths_cfg.get("state_file", "state/processed.json")

    processed_ids = load_processed_ids(state_file)
    logger.info(f"Loaded {len(processed_ids)} previously processed post IDs.")

    handle_dir = Path(raw_data_dir) / handle
    handle_dir.mkdir(parents=True, exist_ok=True)
    posts_file = handle_dir / "posts.json"

    # Load existing posts for this handle if available
    existing_posts = []
    existing_post_ids = set()
    if posts_file.exists():
        try:
            with open(posts_file, "r", encoding="utf-8") as f:
                existing_posts = json.load(f)
                existing_post_ids = {str(p.get("post_id")) for p in existing_posts}
        except Exception as e:
            logger.warning(f"Error reading existing posts from {posts_file}: {e}")

    loader = setup_instaloader(cookies_file)

    logger.info(f"Querying profile for @{handle}...")
    try:
        profile = instaloader.Profile.from_username(loader.context, handle)
    except Exception as e:
        logger.error(f"Failed to fetch profile for @{handle}: {e}")
        return existing_posts

    new_posts = []
    fetched_count = 0

    logger.info(f"Iterating posts for @{handle} (limit: {limit})...")
    for post in profile.get_posts():
        post_id = str(post.mediaid)

        # Check if already processed or already fetched
        if post_id in processed_ids or post_id in existing_post_ids:
            logger.debug(f"Skipping already processed post {post_id} ({post.shortcode})")
            continue

        post_data = {
            "post_id": post_id,
            "shortcode": post.shortcode,
            "url": f"https://www.instagram.com/p/{post.shortcode}/",
            "date": post.date_utc.strftime("%Y-%m-%d"),
            "caption": post.caption or "",
            "is_video": bool(post.is_video),
            "video_url": post.video_url if post.is_video else None,
            "like_count": post.likes
        }

        new_posts.append(post_data)
        existing_post_ids.add(post_id)
        fetched_count += 1
        logger.info(f"Fetched post [{fetched_count}/{limit}]: {post.shortcode} ({'video' if post.is_video else 'image'})")

        if fetched_count >= limit:
            break

        time.sleep(request_delay)

    all_posts = existing_posts + new_posts
    with open(posts_file, "w", encoding="utf-8") as f:
        json.dump(all_posts, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(all_posts)} posts ({len(new_posts)} new) to {posts_file}")
    return all_posts


def main():
    parser = argparse.ArgumentParser(description="Stage 1: Fetch post metadata from Instagram.")
    parser.add_argument("--handle", required=True, help="Instagram username handle (without @)")
    parser.add_argument("--limit", type=int, default=50, help="Maximum number of new posts to fetch")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logging")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    fetch_posts(args.handle, limit=args.limit, config_path=args.config)


if __name__ == "__main__":
    main()
