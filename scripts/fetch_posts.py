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


def resolve_cookie_file(cookies_file: str = None) -> str:
    """
    Ensure the cookie file is in Netscape format for Instaloader and yt-dlp.
    Searches in priority order:
    1. IG_COOKIES_PATH environment variable
    2. ~/.config/ig-skill-extractor/cookies.txt (outside repo for safety)
    3. Provided cookies_file path (e.g. cookies/instagram_cookies.txt)
    Automatically converts JSON-format cookie exports if detected.
    """
    candidate_paths = []
    
    # 1. Environment variable
    env_path = os.environ.get("IG_COOKIES_PATH")
    if env_path:
        candidate_paths.append(Path(env_path))

    # 2. User home config folder
    home_config = Path.home() / ".config" / "ig-skill-extractor"
    candidate_paths.append(home_config / "instagram_cookies.txt")
    candidate_paths.append(home_config / "cookies.txt")

    # 3. Local candidate path
    if cookies_file:
        candidate_paths.append(Path(cookies_file))

    target_cookie_path = None
    for p in candidate_paths:
        if p and p.exists() and p.is_file():
            target_cookie_path = p
            break

    if not target_cookie_path:
        return None

    str_path = str(target_cookie_path)

    # Test if it already loads as Netscape
    try:
        jar = MozillaCookieJar(str_path)
        jar.load(ignore_discard=True, ignore_expires=True)
        return str_path
    except Exception:
        pass

    # Try parsing as JSON cookie export
    try:
        with open(str_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        cookies = data.get("cookies", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        if not cookies:
            return None

        netscape_path = target_cookie_path.parent / "instagram_cookies.netscape.txt"
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
        logger.warning(f"Could not parse cookie file {str_path}: {e}")
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


def fetch_posts_direct_api(
    handle: str,
    limit: int = 50,
    cookies_file: str = None,
    request_delay: int = 3,
    processed_ids: set = None
) -> list:
    """
    Fallback fetcher using direct authenticated Instagram endpoints:
    1. Resolve user ID via web search endpoint
    2. Paginate user feed via /api/v1/feed/user/{user_id}/
    """
    import requests
    import datetime

    if processed_ids is None:
        processed_ids = set()

    resolved_cookie_file = resolve_cookie_file(cookies_file)
    session = requests.Session()
    if resolved_cookie_file and os.path.exists(resolved_cookie_file):
        try:
            jar = MozillaCookieJar(resolved_cookie_file)
            jar.load(ignore_discard=True, ignore_expires=True)
            session.cookies = jar
        except Exception as e:
            logger.warning(f"Failed to load cookies for direct API: {e}")

    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "X-IG-App-ID": "936619743392459",
        "X-ASBD-ID": "129477",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "*/*",
    })

    # Step 1: Resolve user pk
    logger.info(f"Resolving user ID for @{handle} via Instagram search endpoint...")
    search_url = f"https://www.instagram.com/api/v1/web/search/topsearch/?context=blended&query={handle}"
    user_id = None
    try:
        r = session.get(search_url, timeout=15)
        if r.status_code == 200:
            users = r.json().get("users", [])
            for u in users:
                user_obj = u.get("user", {})
                if user_obj.get("username", "").lower() == handle.lower():
                    user_id = str(user_obj.get("pk"))
                    break
            if not user_id and users:
                user_id = str(users[0].get("user", {}).get("pk"))
    except Exception as e:
        logger.warning(f"Search endpoint error: {e}")

    if not user_id:
        logger.error(f"Could not resolve user ID for handle @{handle}")
        return []

    logger.info(f"Resolved @{handle} to user ID: {user_id}. Fetching feed posts...")

    # Step 2: Fetch feed items
    fetched_posts = []
    max_id = None
    has_more = True

    while has_more and len(fetched_posts) < limit:
        feed_url = f"https://www.instagram.com/api/v1/feed/user/{user_id}/"
        params = {}
        if max_id:
            params["max_id"] = str(max_id)

        try:
            resp = session.get(feed_url, params=params, timeout=20)
            if resp.status_code != 200:
                logger.warning(f"Feed request returned status {resp.status_code}")
                break

            data = resp.json()
            items = data.get("items", [])
            if not items:
                break

            for item in items:
                post_id = str(item.get("pk") or item.get("id"))
                shortcode = item.get("code")
                if not shortcode:
                    continue

                if post_id in processed_ids:
                    logger.debug(f"Skipping already processed post {post_id} ({shortcode})")
                    continue

                media_type = item.get("media_type", 1)  # 1 = image, 2 = video, 8 = carousel
                is_video = (media_type == 2)
                video_versions = item.get("video_versions") or []
                video_url = video_versions[0].get("url") if (is_video and video_versions) else None

                taken_at = item.get("taken_at")
                date_str = ""
                if taken_at:
                    try:
                        date_str = datetime.datetime.fromtimestamp(taken_at, datetime.timezone.utc).strftime("%Y-%m-%d")
                    except Exception:
                        date_str = ""

                caption_obj = item.get("caption") or {}
                caption = caption_obj.get("text", "") if isinstance(caption_obj, dict) else ""

                post_data = {
                    "post_id": post_id,
                    "shortcode": shortcode,
                    "url": f"https://www.instagram.com/p/{shortcode}/",
                    "date": date_str,
                    "caption": caption,
                    "is_video": is_video,
                    "video_url": video_url,
                    "like_count": item.get("like_count", 0)
                }

                fetched_posts.append(post_data)
                logger.info(f"Fetched post [{len(fetched_posts)}/{limit}]: {shortcode} ({'video' if is_video else 'image'})")

                if len(fetched_posts) >= limit:
                    break

            has_more = bool(data.get("more_available", False))
            max_id = data.get("next_max_id")

            if has_more and len(fetched_posts) < limit:
                time.sleep(request_delay)

        except Exception as e:
            logger.error(f"Error while fetching user feed: {e}")
            break

    return fetched_posts


def fetch_posts_instaloader(
    handle: str,
    limit: int = 50,
    cookies_file: str = None,
    request_delay: int = 3,
    processed_ids: set = None
) -> list:
    """
    Fallback metadata fetcher using instaloader.
    Never downloads or persists media files.
    """
    if processed_ids is None:
        processed_ids = set()

    loader = setup_instaloader(cookies_file)
    fetched_posts = []

    try:
        profile = instaloader.Profile.from_username(loader.context, handle)
        logger.info(f"Instaloader resolved profile: @{handle} ({profile.mediacount} total posts)")

        for post in profile.get_posts():
            if len(fetched_posts) >= limit:
                break

            post_id = str(post.mediaid)
            if post_id in processed_ids:
                logger.debug(f"Skipping already-processed post ID: {post_id}")
                continue

            caption = post.caption or ""
            date_str = post.date_utc.strftime("%Y-%m-%d") if post.date_utc else ""
            is_video = post.is_video
            video_url = post.video_url if is_video else None

            post_data = {
                "post_id": post_id,
                "shortcode": post.shortcode,
                "url": f"https://www.instagram.com/p/{post.shortcode}/",
                "date": date_str,
                "caption": caption,
                "is_video": is_video,
                "video_url": video_url,
                "like_count": post.likes
            }

            fetched_posts.append(post_data)
            logger.info(f"Fetched post via Instaloader [{len(fetched_posts)}/{limit}]: {post.shortcode} ({'video' if is_video else 'image'})")

            time.sleep(request_delay)

    except Exception as e:
        logger.error(f"Instaloader fetch failed: {e}")

    return fetched_posts


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
    output_dir = paths_cfg.get("output_dir", "output")
    raw_data_dir = paths_cfg.get("raw_data_dir", "data/raw")
    state_file = paths_cfg.get("state_file", "state/processed.json")

    processed_ids = load_processed_ids(state_file)
    logger.info(f"Loaded {len(processed_ids)} previously processed post IDs.")

    # Target directories
    handle_out_dir = Path(output_dir) / handle
    handle_out_dir.mkdir(parents=True, exist_ok=True)
    out_posts_file = handle_out_dir / "posts.json"

    raw_handle_dir = Path(raw_data_dir) / handle
    raw_handle_dir.mkdir(parents=True, exist_ok=True)
    raw_posts_file = raw_handle_dir / "posts.json"

    # Load existing posts from output/ or data/raw/
    existing_posts = []
    existing_post_ids = set()

    for pfile in [out_posts_file, raw_posts_file]:
        if pfile.exists():
            try:
                with open(pfile, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > len(existing_posts):
                        existing_posts = data
                        existing_post_ids = {str(p.get("post_id")) for p in existing_posts}
            except Exception as e:
                logger.warning(f"Error reading existing posts from {pfile}: {e}")

    logger.info(f"Querying profile and posts for @{handle}...")
    new_posts = []
    
    # Primary attempt: Direct authenticated API
    try:
        new_posts = fetch_posts_direct_api(
            handle=handle,
            limit=limit,
            cookies_file=cookies_file,
            request_delay=request_delay,
            processed_ids=processed_ids.union(existing_post_ids)
        )
    except Exception as e:
        logger.warning(f"Direct API fetch failed ({e}). Attempting Instaloader fallback...")

    # Fallback attempt: Instaloader if direct API yielded no new posts
    if not new_posts and len(existing_posts) == 0:
        logger.info("Direct API yielded 0 posts. Running Instaloader fallback...")
        new_posts = fetch_posts_instaloader(
            handle=handle,
            limit=limit,
            cookies_file=cookies_file,
            request_delay=request_delay,
            processed_ids=processed_ids.union(existing_post_ids)
        )

    all_posts = existing_posts + new_posts
    
    # Save to output/<handle>/posts.json and data/raw/<handle>/posts.json
    for pfile in [out_posts_file, raw_posts_file]:
        with open(pfile, "w", encoding="utf-8") as f:
            json.dump(all_posts, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(all_posts)} posts ({len(new_posts)} new) to {out_posts_file}")
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
