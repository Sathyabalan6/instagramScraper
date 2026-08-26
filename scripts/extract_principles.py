"""
Stage 4: Extract design principles from captions and transcripts using real LLM analysis.
Strict constraints:
- Always paraphrase — never quote captions or transcripts verbatim (Rule 3).
- Real LLM analysis only — no synthetic template fallbacks (prevents fabrication).
- Outputs structured JSON adhering to the project schema.
"""

import os
import re
import sys
import json
import argparse
import logging
from pathlib import Path
import urllib.request
import yaml

# Try loading .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger("extract_principles")

EXTRACTION_SYSTEM_PROMPT = """
You are an expert UI/UX design synthesizer. Your job is to analyze real Instagram post captions and video transcripts, and extract actionable UI/UX design principles actually taught or demonstrated in them.

CATEGORIES ALLOWED:
- spacing
- color
- typography
- hierarchy
- motion
- accessibility
- layout

HARD QUALITY & COPYRIGHT CONSTRAINTS:
1. ALWAYS PARAPHRASE: Under no circumstances should you copy or quote text verbatim from the source. State the rule, why, and example clearly in your own concise, authoritative words.
2. STRICT ACTIONABILITY & SPECIFICITY TEST:
   - If the rule could apply to any UI decision without meaningfully constraining it (e.g. 'maintain visual balance', 'use consistent styling', 'structure elements cleanly', 'use systematic color rules'), DO NOT INCLUDE IT.
   - The `rule` field MUST name a specific, checkable action, value, pairing, technique, ratio, or threshold (e.g. 'Pair warm earth tones with electric cool blue accents for focal pop', 'Structure hero layouts with a 12-column editorial grid and focal portrait photography', 'Apply backdrop-filter blur (12-16px) to sticky navigation headers over hero media').
3. CONFIDENCE RATING:
   - 'high': Concrete, specific, highly actionable design rule or pairing taught directly.
   - 'medium': Actionable guideline with clear practical context.
   - 'low': Vague, speculative, or loosely implied concept (will be quarantined).
4. NO FABRICATION: If the post does not contain any concrete, actionable UI/UX design guideline (e.g. it is a personal vlog, general photo edit, lifestyle clip, sponsorship, meme, or vague promotional text), you MUST return an empty array `[]`.
5. EVIDENCE FIDELITY & NO INVENTED MEASUREMENTS:
   - Only include specific numerical values, percentages, opacities, or color hex codes (e.g. '16px', '10%', '#E2E8F0') if they are EXPLICITLY stated in the creator's transcript or caption text.
   - If the creator demonstrates a visual technique conceptually without citing exact numbers, describe the technique (e.g. 'subtle low opacity', 'soft backdrop blur', 'light neutral border') rather than fabricating specific measurements.

Return ONLY a JSON array matching this schema:
[
  {
    "principle": "<Concise, descriptive title, e.g. 'Warm Earth and Cool Accent Color Contrast'>",
    "category": "<one of: spacing|color|typography|hierarchy|motion|accessibility|layout>",
    "rule": "<Specific, imperative, checkable UI/UX rule>",
    "why": "<Cognitive, visual, or ergonomic rationale>",
    "example": "<Concrete UI implementation or component before/after>",
    "confidence": "<high|medium|low>"
  }
]
Only output valid JSON. No conversational filler or markdown fences outside the JSON.
"""


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def call_llm_for_extraction(text: str, categories: list = None) -> tuple:
    """
    Call an available LLM API (Anthropic, OpenAI, Gemini, Groq, or OpenAI-compatible endpoint).
    Returns (list_of_principles, provider_info_dict).
    Raises RuntimeError if no LLM API key/endpoint is configured.
    """
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    groq_key = os.environ.get("GROQ_API_KEY")
    openai_base = os.environ.get("OPENAI_BASE_URL")
    attempt_errors = []

    # 1. Anthropic Claude
    if anthropic_key:
        try:
            model = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
            req_data = {
                "model": model,
                "max_tokens": 1200,
                "system": EXTRACTION_SYSTEM_PROMPT,
                "messages": [
                    {"role": "user", "content": f"Extract design principles from this creator content:\n\n{text}"}
                ]
            }
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=json.dumps(req_data).encode("utf-8"),
                headers={
                    "x-api-key": anthropic_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply_text = data.get("content", [{}])[0].get("text", "")
                match = re.search(r"\[.*\]", reply_text, re.DOTALL)
                if match:
                    return json.loads(match.group(0)), {"provider": "anthropic", "model": model}
        except Exception as e:
            logger.warning(f"Anthropic provider failed ({e}). Falling back to next available provider...")
            attempt_errors.append(f"Anthropic: {e}")

    # 2. OpenAI / Compatible endpoint
    if openai_key or openai_base:
        try:
            model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
            base_url = openai_base.rstrip("/") if openai_base else "https://api.openai.com/v1"
            req_data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Extract design principles from this creator content:\n\n{text}"}
                ],
                "temperature": 0.1
            }
            headers = {"Content-Type": "application/json"}
            if openai_key:
                headers["Authorization"] = f"Bearer {openai_key}"

            req = urllib.request.Request(
                f"{base_url}/chat/completions",
                data=json.dumps(req_data).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply_text = data["choices"][0]["message"]["content"]
                match = re.search(r"\[.*\]", reply_text, re.DOTALL)
                if match:
                    return json.loads(match.group(0)), {"provider": "openai", "model": model}
        except Exception as e:
            logger.warning(f"OpenAI provider failed ({e}). Falling back to next available provider...")
            attempt_errors.append(f"OpenAI: {e}")

    # 3. Groq (Fast Cloud LLM)
    if groq_key:
        try:
            model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
            req_data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Extract design principles from this creator content:\n\n{text}"}
                ],
                "temperature": 0.1
            }
            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=json.dumps(req_data).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {groq_key}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply_text = data["choices"][0]["message"]["content"]
                match = re.search(r"\[.*\]", reply_text, re.DOTALL)
                if match:
                    return json.loads(match.group(0)), {"provider": "groq", "model": model}
        except Exception as e:
            logger.warning(f"Groq provider failed ({e}). Falling back to next available provider...")
            attempt_errors.append(f"Groq: {e}")

    # 4. Google Gemini
    if gemini_key:
        model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        req_data = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{EXTRACTION_SYSTEM_PROMPT}\n\nCreator Content to Analyze:\n{text}"}
                    ]
                }
            ],
            "generationConfig": {"temperature": 0.1}
        }

        # Retry up to 3 times on 429 / rate limits
        for attempt in range(4):
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(req_data).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "X-goog-api-key": gemini_key
                    },
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=45) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    reply_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    # Clean possible markdown fence ```json ... ```
                    clean_text = re.sub(r"^```(?:json)?\s*", "", reply_text.strip(), flags=re.MULTILINE)
                    clean_text = re.sub(r"\s*```$", "", clean_text.strip(), flags=re.MULTILINE)
                    match = re.search(r"\[.*\]", clean_text, re.DOTALL)
                    if match:
                        return json.loads(match.group(0)), {"provider": "gemini", "model": model}
                    elif clean_text.startswith("[") and clean_text.endswith("]"):
                        return json.loads(clean_text), {"provider": "gemini", "model": model}
                    return [], {"provider": "gemini", "model": model}
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < 3:
                    wait_time = (attempt + 1) * 5
                    logger.warning(f"Gemini API 429 rate limit hit. Backing off for {wait_time}s (attempt {attempt + 1}/3)...")
                    import time
                    time.sleep(wait_time)
                else:
                    logger.warning(f"Gemini API HTTP Error {e.code}: {e}")
                    attempt_errors.append(f"Gemini: HTTP {e.code} - {e}")
                    break
            except Exception as e:
                logger.warning(f"Gemini API extraction error: {e}")
                attempt_errors.append(f"Gemini: {e}")
                break

    # If providers were attempted but all failed
    if attempt_errors:
        raise RuntimeError(
            f"All configured LLM extraction providers failed:\n" + "\n".join(f"  - {err}" for err in attempt_errors)
        )

    # No LLM configured at all — FAIL LOUDLY
    raise RuntimeError(
        "NO LLM API KEY CONFIGURED! Real LLM extraction is strictly required to prevent fabricating design principles.\n"
        "Please configure one of the following environment variables or add them to your .env file:\n"
        "  - ANTHROPIC_API_KEY (e.g. Claude 3.5 Sonnet / Haiku)\n"
        "  - OPENAI_API_KEY    (e.g. GPT-4o / GPT-4o-mini)\n"
        "  - GEMINI_API_KEY    (e.g. Gemini 3.5 Flash Lite)\n"
        "  - GROQ_API_KEY      (e.g. Llama 3.3 70B on Groq)\n"
        "  - OPENAI_BASE_URL   (Local Ollama / LM Studio endpoint)"
    )


def extract_principles_from_text(
    text: str,
    handle: str,
    date: str,
    url: str,
    allowed_categories: list
) -> tuple:
    """
    Extract structured principles from text using genuine LLM analysis.
    Returns (principles_list, provider_info).
    """
    if not text or len(text.strip().split()) < 6:
        return [], {"provider": "skipped_too_short", "model": "none"}

    extracted, info = call_llm_for_extraction(text, categories=allowed_categories)

    # Attach provenance sources and validate schema
    valid_principles = []
    for item in extracted:
        if not isinstance(item, dict):
            continue
        cat = item.get("category", "layout").lower()
        if allowed_categories and cat not in allowed_categories:
            cat = "layout"

        p_name = (item.get("principle") or "Design Principle").strip()
        rule = (item.get("rule") or "").strip()
        why = (item.get("why") or "").strip()
        example = (item.get("example") or "None specified").strip()
        confidence = (item.get("confidence") or "medium").lower()

        if not p_name or not rule:
            continue

        valid_principles.append({
            "principle": p_name,
            "category": cat,
            "rule": rule,
            "why": why,
            "example": example,
            "confidence": confidence,
            "sources": [{
                "handle": handle,
                "date": date,
                "url": url
            }]
        })

    return valid_principles, info


def extract_principles(
    handle: str,
    config_path: str = "config.yaml"
) -> list:
    """
    Load classified & transcribed posts, extract principles via LLM analysis,
    and save creator-isolated output.
    """
    config = load_config(config_path)
    extract_cfg = config.get("extraction", {})
    paths_cfg = config.get("paths", {})

    allowed_cats = extract_cfg.get("categories", [
        "spacing", "color", "typography", "hierarchy", "motion", "accessibility", "layout"
    ])
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
        logger.error(f"No posts.json found for @{handle}.")
        return []

    with open(target_file, "r", encoding="utf-8") as f:
        posts = json.load(f)

    all_extracted = []
    extraction_stats = {"llm_calls": 0, "principles_found": 0, "posts_analyzed": 0}
    provider_used = "unknown"

    for idx, post in enumerate(posts, 1):
        classification = post.get("classification", {})
        path = classification.get("path")
        shortcode = post.get("shortcode")
        url = post.get("url")
        date = post.get("date")

        # Determine source text (caption or transcript)
        source_text = None
        if path == "caption":
            source_text = post.get("caption", "")
        elif path == "audio":
            source_text = post.get("transcript", "")
            if not source_text:
                source_text = post.get("caption", "")

        if not source_text or len(source_text.strip().split()) < 6:
            logger.debug(f"Post {shortcode}: No sufficient text for principle extraction.")
            post["principles"] = []
            continue

        extraction_stats["posts_analyzed"] += 1
        logger.info(f"Extracting principles via LLM [{extraction_stats['posts_analyzed']}]: Post {shortcode}...")

        try:
            principles, info = extract_principles_from_text(
                source_text,
                handle=handle,
                date=date,
                url=url,
                allowed_categories=allowed_cats
            )
            provider_used = f"{info.get('provider')}:{info.get('model')}"
            extraction_stats["llm_calls"] += 1
            extraction_stats["principles_found"] += len(principles)
            post["principles"] = principles
            post["extraction_metadata"] = {
                "method": "llm",
                "provider": info.get("provider"),
                "model": info.get("model"),
                "principles_count": len(principles)
            }
            all_extracted.extend(principles)
            logger.info(f"  -> Extracted {len(principles)} principle(s) from {shortcode} using {provider_used}")
            import time
            time.sleep(3)
        except RuntimeError as e:
            logger.error(str(e))
            raise
        except Exception as e:
            logger.error(f"Error extracting principles for {shortcode}: {e}")
            post["principles"] = []

    # Save updated posts.json with extraction data
    for pfile in [out_posts_file, raw_posts_file]:
        pfile.parent.mkdir(parents=True, exist_ok=True)
        with open(pfile, "w", encoding="utf-8") as f:
            json.dump(posts, f, indent=2)

    # Gather all principles across all posts for full source-of-truth integrity
    full_principles_list = []
    for post in posts:
        for p in (post.get("principles", []) or post.get("extracted_principles", [])):
            full_principles_list.append(p)

    # Save creator-specific principles.json
    out_principles_file = Path(output_dir) / handle / "principles.json"
    out_principles_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_principles_file, "w", encoding="utf-8") as f:
        json.dump(full_principles_list, f, indent=2)

    logger.info(
        f"Extraction complete for @{handle}: {len(all_extracted)} new principle(s) extracted "
        f"({len(full_principles_list)} total across {len(posts)} posts, Provider: {provider_used})."
    )
    return full_principles_list


def main():
    parser = argparse.ArgumentParser(description="Extract design principles via LLM analysis")
    parser.add_argument("--handle", required=True, help="Instagram handle (without @)")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    extract_principles(args.handle, config_path=args.config)


if __name__ == "__main__":
    main()
