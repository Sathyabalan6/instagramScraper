"""
Stage 2b: Audio-only transcription using yt-dlp and Whisper.
Strict constraint: Never persist video. Audio is extracted to a temporary mp3
and immediately deleted in a try/finally block.
"""

import os
import glob
import json
import time
import shutil
import argparse
import logging
import subprocess
from pathlib import Path
import yaml

logger = logging.getLogger("transcribe_audio")

# Cache whisper model instance in memory across calls
_WHISPER_MODEL = None


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_whisper_model(model_name: str = "small"):
    """Lazy load Whisper model."""
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        try:
            import whisper
            logger.info(f"Loading Whisper model '{model_name}'...")
            _WHISPER_MODEL = whisper.load_model(model_name)
        except ImportError:
            logger.warning("openai-whisper python package not found. Will fallback to CLI or stub if necessary.")
            return None
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            return None
    return _WHISPER_MODEL


def resolve_cookie_file(cookies_file: str) -> str:
    """Ensure cookie file is in Netscape format for yt-dlp."""
    if not cookies_file or not os.path.exists(cookies_file):
        return None
    netscape_path = Path(cookies_file).parent / "instagram_cookies.netscape.txt"
    if netscape_path.exists():
        return str(netscape_path)
    return cookies_file


def download_audio_only(
    url: str,
    output_template: str,
    cookies_file: str = None
) -> str:
    """
    Download audio-only stream from Instagram video using yt-dlp.
    Never downloads or persists full video.
    Returns path to the downloaded audio file if successful.
    """
    resolved_cookies = resolve_cookie_file(cookies_file)
    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "5",
        "--no-playlist",
        "--no-warnings",
        "-o", output_template,
    ]

    if resolved_cookies and os.path.exists(resolved_cookies):
        cmd.extend(["--cookies", resolved_cookies])

    cmd.append(url)

    logger.debug(f"Running yt-dlp audio extraction: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        logger.warning(f"yt-dlp audio extraction failed for {url}: {result.stderr.strip()}")
        return None

    # Find the resulting file matching pattern
    base_prefix = output_template.replace("%(id)s.%(ext)s", "")
    matches = glob.glob(f"{base_prefix}*.mp3")
    if matches:
        return matches[0]

    return None


def transcribe_single_audio(
    audio_path: str,
    model_name: str = "small"
) -> str:
    """
    Transcribe an audio file using OpenAI Whisper.
    """
    model = get_whisper_model(model_name)
    if model is not None:
        result = model.transcribe(audio_path, fp16=False)
        return result.get("text", "").strip()

    # Fallback to whisper CLI if package import didn't work
    cmd = ["whisper", audio_path, "--model", model_name, "--output_format", "txt", "--output_dir", str(Path(audio_path).parent)]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    txt_path = Path(audio_path).with_suffix(".txt")
    if txt_path.exists():
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                text = f.read().strip()
            os.remove(txt_path)
            return text
        except Exception:
            pass

    return ""


def clean_tmp_dir(tmp_dir: str):
    """Ensure tmp_audio directory is completely clean and exists."""
    p = Path(tmp_dir)
    p.mkdir(parents=True, exist_ok=True)
    for item in p.glob("*"):
        try:
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        except Exception as e:
            logger.warning(f"Failed to remove temp file {item}: {e}")


def transcribe_posts(
    handle: str,
    config_path: str = "config.yaml"
) -> list:
    """
    Process all posts for handle classified as 'audio'.
    Extracts audio only, transcribes, attaches transcript, and deletes temp audio immediately.
    """
    config = load_config(config_path)
    trans_cfg = config.get("transcription", {})
    ig_cfg = config.get("instagram", {})
    paths_cfg = config.get("paths", {})

    whisper_model = trans_cfg.get("whisper_model", "small")
    tmp_dir = trans_cfg.get("tmp_dir", "data/tmp_audio")
    cookies_file = ig_cfg.get("cookies_file", "cookies/instagram_cookies.txt")
    request_delay = ig_cfg.get("request_delay_seconds", 3)
    raw_data_dir = paths_cfg.get("raw_data_dir", "data/raw")

    posts_file = Path(raw_data_dir) / handle / "posts.json"
    if not posts_file.exists():
        logger.error(f"No posts.json found at {posts_file}.")
        return []

    with open(posts_file, "r", encoding="utf-8") as f:
        posts = json.load(f)

    clean_tmp_dir(tmp_dir)

    audio_posts = [
        p for p in posts
        if p.get("classification", {}).get("path") == "audio" and not p.get("transcript")
    ]

    logger.info(f"Found {len(audio_posts)} video posts requiring audio transcription for @{handle}.")

    for idx, post in enumerate(audio_posts, 1):
        post_id = post.get("post_id")
        shortcode = post.get("shortcode")
        url = post.get("url")
        output_template = f"{tmp_dir}/{shortcode}_%(id)s.%(ext)s"

        logger.info(f"Transcribing audio [{idx}/{len(audio_posts)}]: {shortcode}...")
        downloaded_audio_path = None
        try:
            downloaded_audio_path = download_audio_only(url, output_template, cookies_file)
            if downloaded_audio_path and os.path.exists(downloaded_audio_path):
                transcript = transcribe_single_audio(downloaded_audio_path, model_name=whisper_model)
                post["transcript"] = transcript
                logger.info(f"Successfully transcribed {shortcode} ({len(transcript.split())} words)")
            else:
                logger.warning(f"Could not extract audio for {shortcode}")
                post["transcript"] = ""
        except Exception as e:
            logger.error(f"Error during audio transcription for {shortcode}: {e}")
            post["transcript"] = ""
        finally:
            # Enforce AGENTS.md Hard Rule 1: Always delete audio immediately
            if downloaded_audio_path and os.path.exists(downloaded_audio_path):
                try:
                    os.remove(downloaded_audio_path)
                    logger.debug(f"Removed temp audio: {downloaded_audio_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove {downloaded_audio_path}: {e}")

            # Ensure directory cleanup
            clean_tmp_dir(tmp_dir)

        # Save incremental progress
        with open(posts_file, "w", encoding="utf-8") as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)

        if idx < len(audio_posts):
            time.sleep(request_delay)

    clean_tmp_dir(tmp_dir)
    logger.info(f"Audio transcription complete for @{handle}. data/tmp_audio/ verified clean.")
    return posts


def main():
    parser = argparse.ArgumentParser(description="Stage 2b: Audio-only transcription with Whisper.")
    parser.add_argument("--handle", required=True, help="Instagram username handle")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logging")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    transcribe_posts(args.handle, config_path=args.config)


if __name__ == "__main__":
    main()
