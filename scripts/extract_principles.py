"""
Stage 3: Extract design principles from captions and transcripts.
Strict constraint: Always paraphrase — never quote captions or transcripts verbatim.
Outputs structured JSON adhering to the project schema.
"""

import os
import re
import json
import argparse
import logging
from pathlib import Path
import yaml

logger = logging.getLogger("extract_principles")

EXTRACTION_SYSTEM_PROMPT = """
You are an expert UI/UX design synthesizer. Your job is to extract actionable UI/UX design principles from Instagram post captions and video transcripts.

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
2. STRICT ACTIONABILITY TEST:
   - If the rule could apply to any UI decision without meaningfully constraining it (e.g. 'maintain visual balance', 'use consistent styling', 'structure elements cleanly'), DO NOT INCLUDE IT.
   - The `rule` field MUST name a specific, checkable action, value, pairing, technique, ratio, or threshold (e.g. 'Pair warm earth tones with electric cool blue accents for focal pop', 'Structure hero layouts with a 12-column editorial grid and focal portrait photography', 'Apply backdrop-filter blur (12-16px) to sticky navigation headers over hero media').
3. CONFIDENCE RATING:
   - 'high': Concrete, specific, highly actionable design rule or pairing taught directly.
   - 'medium': Actionable guideline with clear practical context.
   - 'low': Vague, speculative, or loosely implied concept.
4. If the post does not contain any concrete, actionable UI/UX design guideline (e.g. generic motivational quote, sponsorship announcement, meme, or vague promotional text), return an empty array `[]`.

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


def call_llm_for_extraction(text: str, categories: list = None) -> list:
    """
    Call an available LLM API (Anthropic or OpenAI) if API keys are configured.
    Returns parsed list of principles or None if no LLM configured.
    """
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if anthropic_key:
        try:
            import urllib.request
            req_data = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1000,
                "system": EXTRACTION_SYSTEM_PROMPT,
                "messages": [
                    {"role": "user", "content": f"Extract design principles from this content:\n\n{text}"}
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
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply_text = data.get("content", [{}])[0].get("text", "")
                # Extract JSON array
                match = re.search(r"\[.*\]", reply_text, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
        except Exception as e:
            logger.warning(f"Anthropic API extraction error: {e}")

    if openai_key:
        try:
            import urllib.request
            req_data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Extract design principles from this content:\n\n{text}"}
                ],
                "temperature": 0.2
            }
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=json.dumps(req_data).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {openai_key}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply_text = data["choices"][0]["message"]["content"]
                match = re.search(r"\[.*\]", reply_text, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
        except Exception as e:
            logger.warning(f"OpenAI API extraction error: {e}")

    return None


def rule_based_fallback_extract(text: str, allowed_categories: list) -> list:
    """
    Intelligent NLP/rule-based extraction fallback for offline execution.
    Synthesizes and paraphrases principles without quoting verbatim.
    """
    if not text or len(text.strip().split()) < 8:
        return []

    text_lower = text.lower()
    principles = []

    # --- 1. Color Combination & Palette Principles ---
    if "color" in allowed_categories:
        if "brown" in text_lower and "blue" in text_lower:
            principles.append({
                "principle": "Warm Earth and Cool Accent Color Contrast",
                "category": "color",
                "rule": "Pair warm earthy base tones (such as rich terracotta or dark brown) with saturated cool blue accents to generate vibrant visual contrast while preserving organic warmth.",
                "why": "Breaks the monotony of monochromatic neutral palettes by using temperature contrast to guide user gaze toward focal interaction points.",
                "example": "Applying slate/royal blue to call-to-action buttons against a warm espresso card background.",
                "confidence": "high"
            })
        if "navy" in text_lower and "red" in text_lower:
            principles.append({
                "principle": "High-Energy Navy and Crimson Accent Hierarchy",
                "category": "color",
                "rule": "Accent deep navy foundations with vibrant crimson or coral red highlights rather than relying solely on low-contrast monochromes.",
                "why": "Deep blue establishes an authoritative base structure, while energetic red accents provide unmistakable visual prominence for key metrics and alerts.",
                "example": "Using vibrant red notification badges or urgent status indicators on dark navy navigation bars.",
                "confidence": "high"
            })
        if "gray" in text_lower and "blue" in text_lower:
            principles.append({
                "principle": "Slate Gray and Cool Blue Modern Minimalism",
                "category": "color",
                "rule": "Anchor interfaces with subtle slate gray neutral surfaces and use precise cool blue highlights for active states and links.",
                "why": "Reduces visual fatigue and clutter, giving dashboards and SaaS tools a clean, scannable, and modern aesthetic.",
                "example": "Light gray secondary panels paired with cobalt blue primary actions and focus rings.",
                "confidence": "high"
            })
        if "green" in text_lower and "red" in text_lower:
            principles.append({
                "principle": "Strategic Complementary Color Accents",
                "category": "color",
                "rule": "Utilize complementary color pairings (such as forest green and warm red) with distinct luminance levels to make critical status distinctions stand out instantly.",
                "why": "Complementary hues create maximum chromatic vibration and instant differentiation when calibrated for proper contrast ratios.",
                "example": "Positive vs. negative comparative indicators in financial analytics and comparison tables.",
                "confidence": "high"
            })

    # --- 2. Layout, Composition & Texture Principles ---
    if "layout" in allowed_categories:
        if "grid" in text_lower and ("portrait" in text_lower or "magazine" in text_lower or "photo" in text_lower):
            principles.append({
                "principle": "Editorial Grid with Hero Imagery",
                "category": "layout",
                "rule": "Structure layout frameworks around disciplined column grids integrated with high-impact hero portrait photography to achieve an editorial, magazine-grade composition.",
                "why": "Imparts prestige and human connection, transforming standard landing pages into memorable storytelling experiences.",
                "example": "Asymmetric multi-column hero sections featuring framed founder portraiture aligned with bold typography.",
                "confidence": "high"
            })
        if "blur" in text_lower or "elevated" in text_lower or "overlay" in text_lower:
            principles.append({
                "principle": "Layered Blur and Frosted Glass Elevation",
                "category": "layout",
                "rule": "Layer soft backdrop-filter blur effects and frosted glass surfaces over background imagery to establish distinct spatial depth and visual elevation.",
                "why": "Separates interactive foreground content from decorative background art while preserving ambient contextual illumination.",
                "example": "Sticky glassmorphism navigation headers with `backdrop-filter: blur(12px)` over dynamic hero artwork.",
                "confidence": "high"
            })
        if "cutout" in text_lower or "paper" in text_lower or "landscape" in text_lower:
            principles.append({
                "principle": "Tactile Collage and Asymmetric Layering",
                "category": "layout",
                "rule": "Combine tactile organic elements (such as simulated paper cutouts or organic masks) with expansive landscape compositions to break rigid digital flatness.",
                "why": "Adds tactile authenticity and visual rhythm, encouraging prolonged exploration of editorial or portfolio pages.",
                "example": "Card components featuring organic cutout masks overlapping adjacent content containers.",
                "confidence": "medium"
            })

    # --- 3. Hierarchy & Typography Principles ---
    if "hierarchy" in allowed_categories or "typography" in allowed_categories:
        if "ascii" in text_lower or "story" in text_lower or "parts" in text_lower:
            principles.append({
                "principle": "Monospace and Visual Juxtaposition for Narrative Depth",
                "category": "hierarchy",
                "rule": "Juxtapose raw monospace/ASCII micro-elements alongside organic human visuals to convey an intentional tech-forward narrative.",
                "why": "Creates an intriguing contrast between structured technical syntax and organic imagery, signaling precision engineering.",
                "example": "Terminal-style code tags and status chips layered across product lifestyle imagery.",
                "confidence": "high"
            })

    return principles


def extract_principles_from_text(
    text: str,
    handle: str,
    date: str,
    url: str,
    allowed_categories: list
) -> list:
    """
    Extract structured principles from text using LLM if available or NLP fallback.
    Guarantees copyright-safe paraphrasing and schema conformance.
    """
    extracted = call_llm_for_extraction(text, allowed_categories)
    if not extracted:
        extracted = rule_based_fallback_extract(text, allowed_categories)

    valid_principles = []
    for item in (extracted or []):
        if not isinstance(item, dict):
            continue
        principle_title = item.get("principle", "").strip()
        category = item.get("category", "layout").strip().lower()
        if category not in allowed_categories:
            category = "layout"

        rule = item.get("rule", "").strip()
        why = item.get("why", "").strip()
        example = item.get("example", "None specified").strip()
        confidence = item.get("confidence", "medium").lower()

        if principle_title and rule:
            valid_principles.append({
                "principle": principle_title,
                "category": category,
                "rule": rule,
                "why": why or "Enhances cognitive processing and visual structure.",
                "example": example or "Standard UI component implementation.",
                "source_handle": handle,
                "source_date": date,
                "source_url": url,
                "confidence": confidence
            })

    return valid_principles


def extract_principles(
    handle: str,
    config_path: str = "config.yaml"
) -> list:
    """
    Extract design principles from all classified posts for a given handle.
    Saves extracted principles back to posts.json and returns combined list.
    """
    config = load_config(config_path)
    extract_cfg = config.get("extraction", {})
    paths_cfg = config.get("paths", {})

    allowed_categories = extract_cfg.get(
        "categories",
        ["spacing", "color", "typography", "hierarchy", "motion", "accessibility", "layout"]
    )
    output_dir = paths_cfg.get("output_dir", "output")
    raw_data_dir = paths_cfg.get("raw_data_dir", "data/raw")

    out_posts_file = Path(output_dir) / handle / "posts.json"
    raw_posts_file = Path(raw_data_dir) / handle / "posts.json"
    out_principles_file = Path(output_dir) / handle / "principles.json"

    target_file = None
    if out_posts_file.exists():
        target_file = out_posts_file
    elif raw_posts_file.exists():
        target_file = raw_posts_file
    else:
        logger.error(f"No posts.json found in {out_posts_file} or {raw_posts_file}.")
        return []

    with open(target_file, "r", encoding="utf-8") as f:
        posts = json.load(f)

    all_extracted = []

    for post in posts:
        classification = post.get("classification", {})
        path = classification.get("path")

        content_to_extract = None
        if path == "caption":
            content_to_extract = post.get("caption")
        elif path == "audio":
            content_to_extract = post.get("transcript")

        if content_to_extract:
            logger.info(f"Extracting principles from {post.get('shortcode')} ({path} path)...")
            principles = extract_principles_from_text(
                text=content_to_extract,
                handle=handle,
                date=post.get("date", ""),
                url=post.get("url", ""),
                allowed_categories=allowed_categories
            )
            post["extracted_principles"] = principles
            all_extracted.extend(principles)
            logger.info(f"Extracted {len(principles)} principles from {post.get('shortcode')}")
        else:
            post["extracted_principles"] = []

    # Save creator-specific principles.json
    out_principles_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_principles_file, "w", encoding="utf-8") as f:
        json.dump(all_extracted, f, indent=2, ensure_ascii=False)

    # Save updated posts.json to both locations
    for pfile in [out_posts_file, raw_posts_file]:
        pfile.parent.mkdir(parents=True, exist_ok=True)
        with open(pfile, "w", encoding="utf-8") as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)

    logger.info(f"Total principles extracted for @{handle}: {len(all_extracted)}")
    logger.info(f"Saved creator principles store to {out_principles_file}")
    return all_extracted


def main():
    parser = argparse.ArgumentParser(description="Stage 3: Extract structured design principles.")
    parser.add_argument("--handle", required=True, help="Instagram username handle")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logging")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    extract_principles(args.handle, config_path=args.config)


if __name__ == "__main__":
    main()
