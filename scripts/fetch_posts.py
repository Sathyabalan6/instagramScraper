"""
Stage 1: Fetch Instagram post metadata without downloading images or video files.
Follows strict constraints: metadata only, rate limited, respects processed state.
"""

import os
import sys
import re
import json
import time
import random
import argparse
import logging
import sqlite3
import shutil
import glob
from pathlib import Path
from http.cookiejar import MozillaCookieJar
from typing import Dict, List, Optional, Tuple
import yaml

try:
    import instaloader
except ImportError:
    instaloader = None

try:
    from curl_cffi import requests as cffi_requests
    HAVE_CURL_CFFI = True
except ImportError:
    cffi_requests = None
    HAVE_CURL_CFFI = False

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


def save_cookies_as_netscape(cookies_dict: Dict[str, str], filepath: str = "cookies/instagram_cookies.txt") -> str:
    """Save dictionary of cookies to Netscape format file."""
    p = Path(filepath)
    p.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Netscape HTTP Cookie File", "# Auto-extracted directly from local browser profile"]
    now = int(time.time()) + 86400 * 30
    for name, value in cookies_dict.items():
        if name and value:
            lines.append(f".instagram.com\tTRUE\t/\tTRUE\t{now}\t{name}\t{value}")
    with open(p, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return str(p)


def extract_browser_cookies() -> Tuple[Dict[str, str], Optional[str]]:
    """
    Dynamically auto-detects and extracts active Instagram cookies directly from
    installed browsers (Firefox, Brave, Google Chrome, Chromium).
    Supports Native, Snap, and Flatpak installations on Linux.
    Returns (cookies_dict, source_description).
    """
    import sqlite3
    import shutil
    import glob

    home = Path.home()

    # 1. Firefox Profiles (Plaintext SQLite, highest fidelity on Linux)
    firefox_patterns = [
        home / "snap/firefox/common/.mozilla/firefox/*/cookies.sqlite",
        home / ".mozilla/firefox/*/cookies.sqlite",
        home / ".var/app/org.mozilla.firefox/.mozilla/firefox/*/cookies.sqlite"
    ]
    for pattern in firefox_patterns:
        for db_path in glob.glob(str(pattern)):
            temp_db = f"/tmp/ig_ff_cookies_{os.getpid()}_{random.randint(100, 999)}.sqlite"
            try:
                shutil.copy2(db_path, temp_db)
                conn = sqlite3.connect(temp_db)
                cur = conn.cursor()
                cur.execute(
                    "SELECT name, value FROM moz_cookies WHERE host LIKE '%instagram%'"
                )
                rows = cur.fetchall()
                conn.close()
                cookies = {r[0]: r[1] for r in rows if r[0] and r[1]}
                if "sessionid" in cookies and "ds_user_id" in cookies:
                    return cookies, f"Firefox Profile ({Path(db_path).parent.name})"
            except Exception:
                pass
            finally:
                if os.path.exists(temp_db):
                    try:
                        os.remove(temp_db)
                    except Exception:
                        pass

    # 2. Chromium-based browsers (Brave, Chrome, Chromium)
    chromium_patterns = [
        (home / ".config/BraveSoftware/Brave-Browser/*/Cookies", "Brave"),
        (home / ".config/google-chrome/*/Cookies", "Chrome"),
        (home / ".config/chromium/*/Cookies", "Chromium"),
        (home / "snap/brave/current/.config/BraveSoftware/Brave-Browser/*/Cookies", "Brave (Snap)"),
        (home / "snap/chromium/current/.config/chromium/*/Cookies", "Chromium (Snap)"),
    ]
    for pattern, browser_name in chromium_patterns:
        for db_path in glob.glob(str(pattern)):
            temp_db = f"/tmp/ig_chrom_cookies_{os.getpid()}_{random.randint(100, 999)}.sqlite"
            try:
                shutil.copy2(db_path, temp_db)
                conn = sqlite3.connect(temp_db)
                cur = conn.cursor()
                cur.execute(
                    "SELECT name, value FROM cookies WHERE host_key LIKE '%instagram%'"
                )
                rows = cur.fetchall()
                conn.close()
                cookies = {r[0]: r[1] for r in rows if r[0] and r[1]}
                if "sessionid" in cookies and "ds_user_id" in cookies:
                    return cookies, f"{browser_name} ({Path(db_path).parent.name})"
            except Exception:
                pass
            finally:
                if os.path.exists(temp_db):
                    try:
                        os.remove(temp_db)
                    except Exception:
                        pass

    return {}, None


def resolve_cookie_file(cookies_file: str = None) -> str:
    """
    Ensure the cookie file is in Netscape format for Instaloader and yt-dlp.
    Searches in priority order:
    1. IG_COOKIES_PATH environment variable
    2. ~/.config/ig-skill-extractor/cookies.txt (outside repo for safety)
    3. Provided cookies_file path (e.g. cookies/instagram_cookies.txt)
    4. Dynamically auto-extracts from local browser profiles (Firefox, Brave, Chrome).
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
        # Dynamically auto-extract from browser!
        browser_cookies, source = extract_browser_cookies()
        if browser_cookies and "sessionid" in browser_cookies:
            logger.info(f"Dynamically extracted active Instagram session directly from {source}!")
            netscape_file = save_cookies_as_netscape(browser_cookies, "cookies/instagram_cookies.txt")
            return netscape_file
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


def load_cookies_as_dict(cookies_file: str = None) -> Dict[str, str]:
    """
    Load cookies as a dictionary {name: value} from Netscape or JSON files.
    Searches:
    1. IG_COOKIES_PATH environment variable
    2. ~/.config/ig-skill-extractor/instagram_cookies.txt or cookies.txt
    3. Provided cookies_file path (e.g. cookies/instagram_cookies.txt)
    """
    candidate_paths = []
    env_path = os.environ.get("IG_COOKIES_PATH")
    if env_path:
        candidate_paths.append(Path(env_path))

    home_config = Path.home() / ".config" / "ig-skill-extractor"
    candidate_paths.append(home_config / "instagram_cookies.txt")
    candidate_paths.append(home_config / "cookies.txt")

    if cookies_file:
        candidate_paths.append(Path(cookies_file))
    candidate_paths.append(Path("cookies/instagram_cookies.txt"))
    candidate_paths.append(Path("cookies/cookies.txt"))

    target_path = None
    for p in candidate_paths:
        if p and p.exists() and p.is_file():
            target_path = p
            break

    if not target_path:
        browser_cookies, source = extract_browser_cookies()
        if browser_cookies and "sessionid" in browser_cookies:
            logger.info(f"Dynamically extracted active Instagram session directly from {source}!")
            try:
                save_cookies_as_netscape(browser_cookies, "cookies/instagram_cookies.txt")
            except Exception:
                pass
            return browser_cookies
        return {}

    cookies_dict = {}
    str_path = str(target_path)

    # Attempt 1: Parse as JSON cookie export
    try:
        with open(str_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("cookies", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        for item in items:
            name = item.get("name")
            val = item.get("value")
            if name and val is not None:
                cookies_dict[str(name)] = str(val)
        if cookies_dict:
            return cookies_dict
    except Exception:
        pass

    # Attempt 2: Parse as Netscape format via MozillaCookieJar
    try:
        jar = MozillaCookieJar(str_path)
        jar.load(ignore_discard=True, ignore_expires=True)
        for c in jar:
            cookies_dict[c.name] = c.value
        if cookies_dict:
            return cookies_dict
    except Exception:
        pass

    # Attempt 3: Line-by-line fallback for Netscape file
    try:
        with open(str_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) >= 7:
                    cookies_dict[parts[5]] = parts[6]
    except Exception as e:
        logger.warning(f"Failed parsing cookies from {str_path}: {e}")

    # If no file cookies or missing sessionid, auto-extract dynamically from local browser!
    if not cookies_dict or "sessionid" not in cookies_dict:
        browser_cookies, source = extract_browser_cookies()
        if browser_cookies and "sessionid" in browser_cookies:
            logger.info(f"Dynamically extracted active Instagram session directly from {source}!")
            try:
                save_cookies_as_netscape(browser_cookies, "cookies/instagram_cookies.txt")
            except Exception:
                pass
            return browser_cookies

    return cookies_dict


class InstagramCollectionPipeline:
    """
    Direct authenticated client for Instagram Web Saved Collections.
    Uses curl_cffi with Chrome TLS/JA4 fingerprint impersonation to bypass OpenSSL detection.
    """
    def __init__(self, cookies: Dict[str, str], user_agent: Optional[str] = None):
        self.user_agent = user_agent or (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        if HAVE_CURL_CFFI and cffi_requests is not None:
            self.session = cffi_requests.Session(impersonate="chrome124")
            logger.info("Initialized curl_cffi session with Chrome 124 TLS/JA4 fingerprint impersonation.")
        else:
            raise RuntimeError(
                "curl_cffi is required for collection ingestion to bypass Instagram's JA4 TLS fingerprint blocks. "
                "Please run: pip install curl_cffi"
            )

        required_keys = {"sessionid", "ds_user_id"}
        if not required_keys.issubset(cookies.keys()):
            missing = required_keys - set(cookies.keys())
            logger.warning(f"Cookies may be missing recommended keys: {missing}. If requests fail, re-export fresh session cookies.")

        self.cookies = cookies
        self.session.cookies.update(cookies)

        csrf_token = cookies.get("csrftoken", "")
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.instagram.com",
            "Referer": "https://www.instagram.com/",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Linux"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": self.user_agent,
            "X-ASBD-ID": "198387",
            "X-CSRFToken": csrf_token,
            "X-IG-App-ID": "936619743392459",
            "X-IG-WWW-Claim": "0",
            "X-Requested-With": "XMLHttpRequest",
        }
        self.session.headers.update(self.headers)

    @staticmethod
    def _slugify(text: str) -> str:
        """Converts collection names to URL slugs matching Instagram web routing."""
        text = text.lower().strip()
        text = re.sub(r"[^\w\s-]", "", text)
        return re.sub(r"[\s_-]+", "-", text)

    @staticmethod
    def extract_slug(input_str: str) -> str:
        """Extract slug from a URL or raw slug string."""
        input_str = input_str.strip().rstrip("/")
        # Matches https://www.instagram.com/<user>/saved/<slug>/
        match = re.search(r"/saved/([^/?#]+)", input_str)
        if match:
            return match.group(1).strip()
        # If user passed path or slug
        return input_str.split("/")[-1].strip()

    @staticmethod
    def list_local_saved_collections() -> List[Dict[str, str]]:
        """
        Discovers all saved collections previously visited by the user by inspecting
        local browser history profiles (Firefox Snap, Native, Flatpak, Chromium).
        Returns a list of dicts with keys: 'id', 'slug', 'name', 'url'.
        """
        import glob
        history_paths = []
        for p in [
            os.path.expanduser("~/snap/firefox/common/.mozilla/firefox/*/places.sqlite"),
            os.path.expanduser("~/.mozilla/firefox/*/places.sqlite"),
            os.path.expanduser("~/.var/app/org.mozilla.firefox/.mozilla/firefox/*/places.sqlite"),
            os.path.expanduser("~/.config/google-chrome/*/History"),
            os.path.expanduser("~/.config/BraveSoftware/Brave-Browser/*/History"),
            os.path.expanduser("~/.config/chromium/*/History"),
        ]:
            history_paths.extend(glob.glob(p))

        collections = {}
        for db_path in history_paths:
            if not os.path.exists(db_path):
                continue
            temp_db = f"/tmp/places_list_{os.getpid()}_{hash(db_path) % 10000}.sqlite"
            try:
                shutil.copy2(db_path, temp_db)
                conn = sqlite3.connect(temp_db)
                cur = conn.cursor()
                # Check for Firefox places or Chromium urls
                try:
                    cur.execute(
                        "SELECT url, title FROM moz_places WHERE url LIKE '%instagram.com%saved%' ORDER BY last_visit_date DESC LIMIT 300"
                    )
                except sqlite3.OperationalError:
                    cur.execute(
                        "SELECT url, title FROM urls WHERE url LIKE '%instagram.com%saved%' ORDER BY last_visit_time DESC LIMIT 300"
                    )
                rows = cur.fetchall()
                conn.close()
                for url, title in rows:
                    m = re.search(r"/saved/([^/?#]+)/(\d+)", url)
                    if m:
                        slug, cid = m.group(1).lower(), m.group(2)
                        clean_title = (title or "").split("•")[0].strip() or slug
                        if cid not in collections:
                            collections[cid] = {"id": cid, "slug": slug, "name": clean_title, "url": url}
            except Exception:
                pass
            finally:
                if os.path.exists(temp_db):
                    try:
                        os.remove(temp_db)
                    except Exception:
                        pass
        return list(collections.values())

    def get_collections_manifest(self) -> List[Dict]:
        """
        Fetches all custom and default saved collections for the user.
        Combines local browser history discovery with Instagram API.
        """
        # 1. First probe local browser history for known collections
        local_cols = self.list_local_saved_collections()
        manifest = []
        for c in local_cols:
            manifest.append({
                "collection_id": c["id"],
                "collection_name": c["name"],
                "slug": c["slug"],
                "source": "browser_history"
            })

        # 2. Attempt remote API collection manifest
        try:
            url = "https://www.instagram.com/api/v1/collections/list/"
            params = {
                "collection_types": json.dumps(["ALL_MEDIA_AUTO_COLLECTION", "MEDIA", "AUDIO_AUTO_COLLECTION"]),
                "get_cover_media_lists": "true",
                "include_public_only": "0",
                "max_id": "",
            }
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for item in data.get("items", []):
                    cid = str(item.get("collection_id"))
                    if not any(m["collection_id"] == cid for m in manifest):
                        manifest.append(item)
        except Exception as e:
            logger.debug(f"Direct collections/list endpoint query bypassed: {e}")

        # 3. If manifest is still empty, scan recent saved posts feed for saved_collection_ids
        if not manifest:
            try:
                logger.info("Scanning saved posts feed for active collection IDs...")
                resp = self.session.get("https://www.instagram.com/api/v1/feed/saved/posts/", timeout=15)
                if resp.status_code == 200:
                    feed_data = resp.json()
                    discovered_cids = set()
                    for it in feed_data.get("items", []):
                        m = it.get("media", it)
                        for cid in m.get("saved_collection_ids", []):
                            discovered_cids.add(str(cid))
                    for cid in discovered_cids:
                        manifest.append({
                            "collection_id": cid,
                            "collection_name": f"Collection {cid}",
                            "slug": cid,
                            "source": "saved_feed"
                        })
            except Exception as e:
                logger.debug(f"Feed scan fallback failed: {e}")

        return manifest

    def resolve_collection_id(self, target_slug_or_url: str) -> Tuple[str, str]:
        """
        Resolves a collection URL slug into (collection_id, collection_name).
        Supports:
        - Full collection URLs with numeric ID: https://www.instagram.com/<user>/saved/<slug>/<id>/
        - Named collection URLs: https://www.instagram.com/<user>/saved/<slug>/
        - Raw slugs: 'social-media-post-improvement'
        - Direct numeric collection IDs: '1387794532887117'
        - Root feeds: 'all-posts', 'saved' -> ALL_MEDIA_AUTO_COLLECTION
        """
        input_clean = target_slug_or_url.strip()

        # 1. If explicit numeric collection ID in URL or input
        m_id = re.search(r"/saved/[^/?#]+/(\d+)", input_clean)
        if m_id:
            cid = m_id.group(1)
            slug = self.extract_slug(input_clean)
            logger.info(f"Resolved from URL: collection_id={cid}, slug='{slug}'")
            return cid, slug.replace("-", " ").title()

        if input_clean.isdigit():
            logger.info(f"Direct collection ID provided: {input_clean}")
            return input_clean, f"Collection {input_clean}"

        target_slug = self.extract_slug(input_clean).lower()
        if target_slug in ("all-posts", "all_media_auto_collection", "saved", "all"):
            return "ALL_MEDIA_AUTO_COLLECTION", "All Saved Posts"

        # 2. Check local browser history first (instant, 100% accurate mapping)
        local_cols = self.list_local_saved_collections()
        for col in local_cols:
            col_slug = col["slug"].lower()
            col_id = str(col["id"])
            col_name = col["name"].lower()
            if (
                col_slug == target_slug
                or col_id == target_slug
                or col_name == target_slug.replace("-", " ")
                or target_slug in col_slug
            ):
                logger.info(f"Resolved '{target_slug}' via browser profile history -> Collection ID: {col_id} ('{col['name']}')")
                return col_id, col["name"]

        # 3. Check combined collections manifest
        collections = self.get_collections_manifest()
        for col in collections:
            col_name = col.get("collection_name", "")
            col_id = str(col.get("collection_id"))
            slugified = self._slugify(col_name)

            if slugified == target_slug or col_id == target_slug or col_name.lower() == target_slug.replace("-", " "):
                logger.info(f"Resolved slug '{target_slug}' -> Collection ID: {col_id} ('{col_name}')")
                return col_id, col_name

        available = [
            f"'{c.get('collection_name')}' (slug: {c.get('slug') or self._slugify(c.get('collection_name', ''))}, id: {c.get('collection_id')})"
            for c in collections
        ]
        raise ValueError(
            f"Collection slug '{target_slug}' could not be matched. Discovered collections for your account:\n  - " +
            ("\n  - ".join(available) if available else "None found. Try passing the full URL including collection ID: https://www.instagram.com/<user>/saved/<slug>/<id>/")
        )

    def fetch_collection_posts(
        self,
        collection_id: str,
        limit: int = 50,
        request_delay: float = 3.0,
        processed_ids: set = None
    ) -> List[Dict]:
        """
        Paginates through posts within a collection.
        Extracts pre-signed unauthenticated Meta CDN video URLs for safe audio extraction.
        """
        import datetime

        if processed_ids is None:
            processed_ids = set()

        if collection_id == "ALL_MEDIA_AUTO_COLLECTION":
            base_url = "https://www.instagram.com/api/v1/feed/saved/posts/"
        else:
            base_url = f"https://www.instagram.com/api/v1/feed/collection/{collection_id}/posts/"

        max_id: Optional[str] = None
        fetched_posts = []

        while len(fetched_posts) < limit:
            params = {"count": "48"}
            if max_id:
                params["max_id"] = str(max_id)

            logger.info(f"Querying collection feed: {base_url} (Cursor: {max_id or 'start'})")
            resp = self.session.get(base_url, params=params, timeout=20)

            if resp.status_code == 429:
                logger.warning("Encountered 429 Rate Limit. Pausing with extended backoff...")
                time.sleep(60.0 + random.uniform(5.0, 15.0))
                continue

            if resp.status_code == 401 or "login_required" in resp.text:
                raise PermissionError("Instagram session cookies expired or invalid.")

            if resp.status_code != 200:
                logger.error(f"Failed fetching collection page: {resp.status_code} - {resp.text[:200]}")
                break

            payload = resp.json()
            raw_items = payload.get("items", [])
            if not raw_items:
                logger.info("No more items returned in collection.")
                break

            for raw in raw_items:
                # Payload structures alternate between media container or direct dictionary
                media = raw.get("media", raw)
                post_id = str(media.get("pk") or media.get("id"))
                shortcode = media.get("code")
                if not shortcode:
                    continue

                if post_id in processed_ids:
                    logger.debug(f"Skipping already processed post {post_id} ({shortcode})")
                    continue

                media_type = media.get("media_type", 1)  # 1 = image, 2 = video, 8 = carousel
                video_versions = media.get("video_versions", [])
                is_video = (media_type == 2) or bool(video_versions)

                video_url = None
                if video_versions:
                    # Select highest resolution video stream
                    sorted_streams = sorted(video_versions, key=lambda x: x.get("width", 0), reverse=True)
                    video_url = sorted_streams[0].get("url")

                taken_at = media.get("taken_at")
                date_str = ""
                if taken_at:
                    try:
                        date_str = datetime.datetime.fromtimestamp(taken_at, datetime.timezone.utc).strftime("%Y-%m-%d")
                    except Exception:
                        date_str = ""

                caption_obj = media.get("caption") or {}
                caption = caption_obj.get("text", "") if isinstance(caption_obj, dict) else str(caption_obj)

                owner_obj = media.get("user") or {}
                owner_username = owner_obj.get("username", "") if isinstance(owner_obj, dict) else ""

                post_data = {
                    "post_id": post_id,
                    "shortcode": shortcode,
                    "url": f"https://www.instagram.com/p/{shortcode}/",
                    "date": date_str,
                    "caption": caption,
                    "is_video": is_video,
                    "video_url": video_url,  # Direct pre-signed unauthenticated Meta CDN URL
                    "video_duration": media.get("video_duration"),
                    "like_count": media.get("like_count", 0),
                    "owner_username": owner_username,
                }

                fetched_posts.append(post_data)
                logger.info(
                    f"Fetched collection post [{len(fetched_posts)}/{limit}]: {shortcode} "
                    f"(@{owner_username or 'unknown'}) - {'video' if is_video else 'image'}"
                )

                if len(fetched_posts) >= limit:
                    break

            more_available = bool(payload.get("more_available", False))
            next_max_id = payload.get("next_max_id")

            if not more_available or not next_max_id:
                logger.info(f"End of collection reached. Collected {len(fetched_posts)} items.")
                break

            max_id = next_max_id
            # Anti-automation pacing: Sleep 2.5 to 4.5 seconds between pages
            jitter_sleep = request_delay + random.uniform(-0.5, 1.5)
            time.sleep(max(2.0, jitter_sleep))

        return fetched_posts


def setup_instaloader(cookies_file: str = None):
    """
    Initialize Instaloader strictly in metadata-only mode.
    Disables downloading pictures, videos, thumbnails, and comments.
    """
    if instaloader is None:
        logger.debug("instaloader package is not installed; skipping instaloader initialization.")
        return None

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
    import datetime

    if processed_ids is None:
        processed_ids = set()

    cookies_dict = load_cookies_as_dict(cookies_file)

    if HAVE_CURL_CFFI and cffi_requests is not None:
        session = cffi_requests.Session(impersonate="chrome124")
        logger.info("Initialized curl_cffi session for direct API with Chrome 124 TLS/JA4 impersonation.")
    else:
        import requests
        session = requests.Session()
        logger.warning("curl_cffi not available; using standard requests session for direct API.")

    if cookies_dict:
        session.cookies.update(cookies_dict)

    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
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
    if loader is None:
        logger.warning("Instaloader is not available in environment; skipping Instaloader fallback.")
        return []

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
    handle: str = None,
    collection: str = None,
    limit: int = 50,
    config_path: str = "config.yaml"
) -> list:
    """
    Fetch up to `limit` new posts from `handle` or a saved `collection`,
    saving metadata to data/raw/<target>/posts.json and output/<target>/posts.json.
    Never downloads or persists image/video media files.
    """
    if not handle and not collection:
        raise ValueError("Either handle or collection must be specified.")

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

    # Collection ingestion path
    if collection:
        cookies_dict = load_cookies_as_dict(cookies_file)
        if not cookies_dict:
            raise PermissionError(
                f"No Instagram cookies found for private saved collection. "
                f"Please place your session cookies in {cookies_file} or set IG_COOKIES_PATH."
            )

        pipeline = InstagramCollectionPipeline(cookies=cookies_dict)
        collection_id, collection_name = pipeline.resolve_collection_id(collection)
        target_name = handle or f"collection_{pipeline._slugify(collection_name)}"

        handle_out_dir = Path(output_dir) / target_name
        handle_out_dir.mkdir(parents=True, exist_ok=True)
        out_posts_file = handle_out_dir / "posts.json"

        raw_handle_dir = Path(raw_data_dir) / target_name
        raw_handle_dir.mkdir(parents=True, exist_ok=True)
        raw_posts_file = raw_handle_dir / "posts.json"

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

        logger.info(f"Ingesting collection '{collection_name}' (ID: {collection_id}) -> target '{target_name}'...")
        new_posts = pipeline.fetch_collection_posts(
            collection_id=collection_id,
            limit=limit,
            request_delay=request_delay,
            processed_ids=processed_ids.union(existing_post_ids)
        )

        all_posts = existing_posts + new_posts
        for pfile in [out_posts_file, raw_posts_file]:
            with open(pfile, "w", encoding="utf-8") as f:
                json.dump(all_posts, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(all_posts)} posts ({len(new_posts)} new) from collection '{collection_name}' to {out_posts_file}")
        return all_posts

    # Standard public creator handle path
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
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--handle", help="Instagram username handle (without @)")
    group.add_argument(
        "--collection", "--collection-url",
        dest="collection",
        help="Instagram saved collection slug or URL (e.g. social-media-post-improvement)"
    )
    parser.add_argument("--limit", type=int, default=50, help="Maximum number of new posts to fetch")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logging")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    fetch_posts(handle=args.handle, collection=args.collection, limit=args.limit, config_path=args.config)


if __name__ == "__main__":
    main()

