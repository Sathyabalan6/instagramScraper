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
import hashlib
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
You are an expert design-systems engineer and senior UI/UX reviewer synthesizing creator content into an instructive, actionable Claude Skill.

CATEGORIES ALLOWED:
- spacing
- color
- typography
- hierarchy
- motion
- accessibility
- layout

HARD QUALITY & ACTIONABILITY CONSTRAINTS:
1. ALWAYS PARAPHRASE: Under no circumstances copy or quote text verbatim from the source. State the guidance clearly in your own authoritative, production-grade technical vocabulary.
2. INSTRUCTIVE DIRECTIVE FORMAT:
   - "trigger_context": Describe the exact UI scenario or component where this applies (e.g., 'any primary action button that fires a network request', 'sticky navigation header over hero media', 'multi-step form checkout flows').
   - "do_this": Specific, imperative, checkable engineering action the agent must execute.
   - "dont_do_this": Specific anti-pattern or mistake that this principle prevents.
   - "rule": Concise imperative synthesis of the action.
3. SPECIFICITY TEST: If a rule could apply to any UI decision without constraining it (e.g. 'maintain balance', 'clean layout'), DO NOT INCLUDE IT. Must specify concrete techniques, values, or thresholds.
4. CONFIDENCE RATING:
   - 'high': Concrete, specific, highly actionable design rule or pairing taught directly.
   - 'medium': Actionable guideline with clear practical context.
   - 'low': Vague, speculative, or loosely implied concept.
5. NO FABRICATION: If the post does not contain any concrete UI/UX guideline, return an empty array `[]`.

Return ONLY a JSON array matching this schema:
[
  {
    "principle": "<Concise, descriptive title, e.g. 'Interactive Tap Debouncing'>",
    "category": "<one of: spacing|color|typography|hierarchy|motion|accessibility|layout>",
    "trigger_context": "<Specific UI scenario or component when this principle applies>",
    "do_this": "<Exact imperative action to execute>",
    "dont_do_this": "<Specific anti-pattern or mistake to avoid>",
    "rule": "<Specific, imperative, checkable UI/UX rule>",
    "why": "<Cognitive, visual, or ergonomic rationale and failure mode>",
    "example": "<Concrete UI implementation or component before/after>",
    "confidence": "<high|medium|low>"
  }
]
Only output valid JSON. No conversational filler or markdown fences outside the JSON.
"""

EXTRACTION_BATCH_SYSTEM_PROMPT = """You are an expert design-systems engineer and senior UI/UX reviewer synthesizing creator content into an instructive, actionable Claude Skill.
Your job is to analyze creator posts (captions or spoken video transcripts) and extract production-ready, actionable UI/UX and interface design principles.

Analyze each provided post independently. A post may contain zero, one, or multiple design principles.

Allowed categories:
- spacing
- color
- typography
- hierarchy
- motion
- accessibility
- layout

HARD QUALITY & COPYRIGHT CONSTRAINTS:
1. ALWAYS PARAPHRASE: Under no circumstances copy or quote text verbatim from the source. State the guidance clearly in your own authoritative, production-grade technical vocabulary.
2. INSTRUCTIVE DIRECTIVE FORMAT:
   - "trigger_context": Describe the exact UI scenario or component where this applies (e.g., 'any primary action button that fires a network request', 'sticky navigation header over hero media', 'multi-step form checkout flows').
   - "do_this": Specific, imperative, checkable engineering action the agent must execute.
   - "dont_do_this": Specific anti-pattern or mistake that this principle prevents.
   - "rule": Concise imperative synthesis of the action.
3. SPECIFICITY TEST: If a rule could apply to any UI decision without constraining it (e.g. 'maintain balance', 'clean layout'), DO NOT INCLUDE IT. Must specify concrete techniques, values, or thresholds.
4. CONFIDENCE RATING:
   - 'high': Concrete, specific, highly actionable design rule or pairing taught directly.
   - 'medium': Actionable guideline with clear practical context.
   - 'low': Vague, speculative, or loosely implied concept.
5. NO FABRICATION: If a post does not contain any concrete UI/UX guideline, return an empty array `[]`.
6. SHORTCODE MATCHING: You MUST include the "shortcode" field matching the corresponding post's shortcode.
7. FUSION DEDUPLICATION: If a post provides both a video transcript and a caption describing the same underlying design rule, synthesize them into a SINGLE comprehensive principle citing both aspects. Never output duplicate or overlapping principles for the same post.

Return ONLY a JSON array matching this schema:
[
  {
    "shortcode": "<post shortcode matching the input post, e.g. 'Dd6TWQ0hpfH'>",
    "principle": "<Concise, descriptive title, e.g. 'Interactive Tap Debouncing'>",
    "category": "<one of: spacing|color|typography|hierarchy|motion|accessibility|layout>",
    "trigger_context": "<Specific UI scenario or component when this principle applies>",
    "do_this": "<Exact imperative action to execute>",
    "dont_do_this": "<Specific anti-pattern or mistake to avoid>",
    "rule": "<Specific, imperative, checkable UI/UX rule>",
    "why": "<Cognitive, visual, or ergonomic rationale and failure mode>",
    "example": "<Concrete UI implementation or component before/after>",
    "confidence": "<high|medium|low>"
  }
]
Only output valid JSON. No conversational filler or markdown fences outside the JSON.
"""

EXTRACTION_PROMPT_HASH = hashlib.sha256(EXTRACTION_BATCH_SYSTEM_PROMPT.strip().encode("utf-8")).hexdigest()[:12]


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def call_llm_for_extraction(text: str, categories: list = None, system_prompt: str = None) -> tuple:
    """
    Call an available LLM API (Anthropic, OpenAI, Gemini, Groq, or OpenAI-compatible endpoint).
    Returns (list_of_principles, provider_info_dict).
    Raises RuntimeError if no LLM API key/endpoint is configured.
    """
    active_prompt = system_prompt or EXTRACTION_SYSTEM_PROMPT
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY")
    groq_key = os.environ.get("GROQ_API_KEY")
    openai_base = os.environ.get("OPENAI_BASE_URL")
    attempt_errors = []

    # 1. Anthropic Claude
    if anthropic_key:
        try:
            model = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
            req_data = {
                "model": model,
                "max_tokens": 2500,
                "system": active_prompt,
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
                "max_tokens": 2500,
                "messages": [
                    {"role": "system", "content": active_prompt},
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
                "max_tokens": 2500,
                "messages": [
                    {"role": "system", "content": active_prompt},
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
        preferred_model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
        models_to_try = [preferred_model, "gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-2.5-flash", "gemini-flash-latest"]
        seen_models = set()
        models = [m for m in models_to_try if m and not (m in seen_models or seen_models.add(m))]

        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            req_data = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"{active_prompt}\n\nCreator Content to Analyze:\n{text}"}
                        ]
                    }
                ],
                "generationConfig": {"temperature": 0.1}
            }

            success = False
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
                        clean_text = re.sub(r"^```(?:json)?\s*", "", reply_text.strip(), flags=re.MULTILINE)
                        clean_text = re.sub(r"\s*```$", "", clean_text.strip(), flags=re.MULTILINE)
                        match = re.search(r"\[.*\]", clean_text, re.DOTALL)
                        if match:
                            return json.loads(match.group(0)), {"provider": "gemini", "model": model}
                        elif clean_text.startswith("[") and clean_text.endswith("]"):
                            return json.loads(clean_text), {"provider": "gemini", "model": model}
                        return [], {"provider": "gemini", "model": model}
                except urllib.error.HTTPError as e:
                    if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                        wait_time = (attempt + 1) * 3
                        logger.warning(f"Gemini API transient {e.code} error on {model}. Retrying in {wait_time}s (attempt {attempt + 1}/3)...")
                        import time
                        time.sleep(wait_time)
                    else:
                        logger.warning(f"Gemini API HTTP Error {e.code} on model {model}: {e}")
                        attempt_errors.append(f"Gemini ({model}): HTTP {e.code} - {e}")
                        break
                except Exception as e:
                    if attempt < 3:
                        wait_time = (attempt + 1) * 3
                        logger.warning(f"Gemini network error ({e}). Retrying in {wait_time}s...")
                        import time
                        time.sleep(wait_time)
                    else:
                        logger.warning(f"Gemini API extraction error on {model}: {e}")
                        attempt_errors.append(f"Gemini ({model}): {e}")
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


def extract_principles_batch(
    batch_items: list,
    allowed_categories: list
) -> tuple:
    """
    Extract structured principles across a batch of posts using LLM analysis.
    Each item in batch_items must be a dict:
      {"shortcode": str, "handle": str, "date": str, "url": str, "text": str}
    Returns (dict_of_shortcode_to_principles, provider_info).
    """
    if not batch_items:
        return {}, {"provider": "none", "model": "none"}

    formatted_blocks = []
    for item in batch_items:
        sc = item.get("shortcode", "")
        author = item.get("handle", "")
        date = item.get("date", "")
        text = item.get("text", "")
        formatted_blocks.append(
            f"--- POST START ---\n"
            f"Shortcode: {sc}\n"
            f"Author: @{author}\n"
            f"Date: {date}\n"
            f"Content:\n{text}\n"
            f"--- POST END ---"
        )
    combined_text = "\n\n".join(formatted_blocks)

    extracted, info = call_llm_for_extraction(
        combined_text,
        categories=allowed_categories,
        system_prompt=EXTRACTION_BATCH_SYSTEM_PROMPT
    )

    results_by_shortcode = {item.get("shortcode"): [] for item in batch_items if item.get("shortcode")}
    lookup = {item.get("shortcode"): item for item in batch_items if item.get("shortcode")}

    for p in extracted:
        if not isinstance(p, dict):
            continue
        sc = p.get("shortcode")
        if sc not in results_by_shortcode:
            if len(batch_items) == 1:
                sc = batch_items[0].get("shortcode")
            else:
                logger.warning(
                    f"LLM returned principle '{p.get('principle')}' with missing or unmatched shortcode '{sc}' "
                    f"in batch of {len(batch_items)} posts. Skipping principle to prevent misattribution."
                )
                continue

        meta = lookup.get(sc, {})
        cat = (p.get("category") or "layout").lower()
        if allowed_categories and cat not in allowed_categories:
            cat = "layout"

        p_name = (p.get("principle") or "Design Principle").strip()
        do_this = (p.get("do_this") or "").strip()
        dont_do_this = (p.get("dont_do_this") or p.get("anti_pattern") or "").strip()
        trigger_context = (p.get("trigger_context") or "").strip()
        rule = (p.get("rule") or do_this or "").strip()
        if not do_this and rule:
            do_this = rule
        why = (p.get("why") or "").strip()
        example = (p.get("example") or "None specified").strip()
        if example == "None specified" and do_this and dont_do_this:
            example = f"Before: {dont_do_this}\nAfter: {do_this}"
        confidence = (p.get("confidence") or "medium").lower()

        if not p_name or not rule:
            continue

        results_by_shortcode[sc].append({
            "principle": p_name,
            "category": cat,
            "trigger_context": trigger_context,
            "do_this": do_this,
            "dont_do_this": dont_do_this,
            "rule": rule,
            "why": why,
            "example": example,
            "confidence": confidence,
            "sources": [{
                "handle": meta.get("handle", ""),
                "date": meta.get("date", ""),
                "url": meta.get("url", "")
            }]
        })

    return results_by_shortcode, info


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
        do_this = (item.get("do_this") or "").strip()
        dont_do_this = (item.get("dont_do_this") or item.get("anti_pattern") or "").strip()
        trigger_context = (item.get("trigger_context") or "").strip()
        rule = (item.get("rule") or do_this or "").strip()
        if not do_this and rule:
            do_this = rule
        why = (item.get("why") or "").strip()
        example = (item.get("example") or "None specified").strip()
        if example == "None specified" and do_this and dont_do_this:
            example = f"Before: {dont_do_this}\nAfter: {do_this}"
        confidence = (item.get("confidence") or "medium").lower()

        if not p_name or not rule:
            continue

        valid_principles.append({
            "principle": p_name,
            "category": cat,
            "trigger_context": trigger_context,
            "do_this": do_this,
            "dont_do_this": dont_do_this,
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
    config_path: str = "config.yaml",
    refresh: bool = False,
    refresh_low_confidence: bool = False
) -> list:
    """
    Load classified & transcribed posts, extract principles via LLM analysis,
    and save creator-isolated output.
    Supports granular refresh: full refresh, low-confidence re-extraction, or automatic prompt-hash update.
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

    posts_to_analyze = []
    for post in posts:
        has_principles = post.get("principles") is not None and len(post.get("principles", [])) > 0
        current_meta = post.get("extraction_metadata", {})
        saved_hash = current_meta.get("prompt_hash")
        has_low_conf = any(p.get("confidence") == "low" for p in post.get("principles", []))

        if refresh:
            should_extract = True
        elif refresh_low_confidence:
            should_extract = (not has_principles) or has_low_conf
        else:
            if has_principles and saved_hash and saved_hash != EXTRACTION_PROMPT_HASH:
                logger.info(f"Post {post.get('shortcode')}: System prompt updated ({saved_hash} -> {EXTRACTION_PROMPT_HASH}). Re-extracting...")
                should_extract = True
            elif has_principles:
                should_extract = False
            else:
                should_extract = True

        if not should_extract:
            continue

        classification = post.get("classification", {})
        shortcode = post.get("shortcode")
        url = post.get("url")
        date = post.get("date")
        author = post.get("owner_username") or handle

        transcript = (post.get("transcript") or "").strip()
        caption = (post.get("caption") or "").strip()

        # Combine transcript and caption context if both exist, so creator caption specs aren't lost
        if transcript and caption and len(caption.split()) >= 15:
            source_text = f"Spoken Video Transcript:\n{transcript}\n\nPost Caption:\n{caption}"
        elif transcript:
            source_text = transcript
        elif caption and (classification.get("has_rich_caption") or "caption" in classification.get("paths", [classification.get("path")])):
            source_text = caption
        elif caption and len(caption.split()) >= 25:
            source_text = caption
        else:
            source_text = ""

        if not source_text or len(source_text.strip().split()) < 6:
            if "principles" not in post:
                post["principles"] = []
            continue

        posts_to_analyze.append({
            "post_ref": post,
            "shortcode": shortcode,
            "handle": author,
            "date": date,
            "url": url,
            "text": source_text
        })

    logger.info(f"Queued {len(posts_to_analyze)} posts with sufficient text for LLM principle extraction.")

    # Batch process in chunks (default 1 for maximum fidelity and zero cross-post contamination)
    batch_size = max(1, int(extract_cfg.get("batch_size", 1)))
    if batch_size > 1:
        logger.warning(
            f"Batch size is {batch_size} > 1. Multi-post LLM batching carries risk of post attribution drift. "
            f"Set batch_size: 1 in config.yaml for strictly isolated post analysis."
        )

    for i in range(0, len(posts_to_analyze), batch_size):
        batch = posts_to_analyze[i:i + batch_size]
        batch_codes = [b["shortcode"] for b in batch]
        logger.info(
            f"Extracting principles via LLM batch [{i + 1}-{min(i + batch_size, len(posts_to_analyze))}/{len(posts_to_analyze)}]: "
            f"{', '.join(batch_codes)}..."
        )

        try:
            batch_results, info = extract_principles_batch(batch, allowed_categories=allowed_cats)
            provider_used = f"{info.get('provider')}:{info.get('model')}"
            extraction_stats["llm_calls"] += 1
            extraction_stats["posts_analyzed"] += len(batch)

            for item in batch:
                post = item["post_ref"]
                sc = item["shortcode"]
                p_list = batch_results.get(sc, [])
                post["principles"] = p_list
                post["extraction_metadata"] = {
                    "method": "llm_batch",
                    "provider": info.get("provider"),
                    "model": info.get("model"),
                    "principles_count": len(p_list),
                    "prompt_hash": EXTRACTION_PROMPT_HASH
                }
                extraction_stats["principles_found"] += len(p_list)
                all_extracted.extend(p_list)
                logger.info(f"  -> Extracted {len(p_list)} principle(s) from {sc} ({provider_used})")

        except Exception as e:
            logger.warning(f"Batch LLM extraction failed ({e}). Falling back to single-post extraction for this batch...")
            for item in batch:
                post = item["post_ref"]
                sc = item["shortcode"]
                extraction_stats["posts_analyzed"] += 1
                try:
                    p_list, info = extract_principles_from_text(
                        item["text"],
                        handle=item["handle"],
                        date=item["date"],
                        url=item["url"],
                        allowed_categories=allowed_cats
                    )
                    provider_used = f"{info.get('provider')}:{info.get('model')}"
                    extraction_stats["llm_calls"] += 1
                    post["principles"] = p_list
                    post["extraction_metadata"] = {
                        "method": "llm",
                        "provider": info.get("provider"),
                        "model": info.get("model"),
                        "principles_count": len(p_list)
                    }
                    extraction_stats["principles_found"] += len(p_list)
                    all_extracted.extend(p_list)
                    logger.info(f"  -> Extracted {len(p_list)} principle(s) from {sc} ({provider_used})")
                except Exception as sub_e:
                    logger.error(f"Fallback extraction failed for {sc}: {sub_e}")
                    post["principles"] = []
                    post["extraction_metadata"] = {"method": "error", "error": str(sub_e)}

        # Incremental write
        for pfile in [out_posts_file, raw_posts_file]:
            pfile.parent.mkdir(parents=True, exist_ok=True)
            with open(pfile, "w", encoding="utf-8") as f:
                json.dump(posts, f, indent=2, ensure_ascii=False)

    # If posts were analyzed but all LLM calls failed, alert loudly
    if extraction_stats["posts_analyzed"] > 0 and extraction_stats["llm_calls"] == 0:
        raise RuntimeError("All attempted LLM calls failed. Please check your API key, network, or provider status.")

    # Gather all principles across all posts for full source-of-truth integrity
    full_principles_list = []
    for post in posts:
        for p in (post.get("principles", []) or post.get("extracted_principles", [])):
            full_principles_list.append(p)

    # Note: principles.json is strictly derived in Stage 5 (merge_skill.py)
    # posts.json is the single source of truth for extracted post principles.

    logger.info(
        f"Extraction complete for @{handle}: {len(all_extracted)} new principle(s) extracted "
        f"({len(full_principles_list)} total across {len(posts)} posts, Provider: {provider_used})."
    )
    return full_principles_list


def main():
    parser = argparse.ArgumentParser(description="Extract design principles via LLM analysis")
    parser.add_argument("--handle", required=True, help="Instagram handle (without @)")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--refresh", action="store_true", help="Re-extract principles even if already extracted")
    parser.add_argument("--refresh-low-confidence", action="store_true", help="Re-extract principles for posts with missing or low-confidence principles")

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    extract_principles(
        args.handle,
        config_path=args.config,
        refresh=args.refresh,
        refresh_low_confidence=args.refresh_low_confidence
    )


if __name__ == "__main__":
    main()
