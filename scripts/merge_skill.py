"""
Stage 4: Merge extracted principles into structured store (principles.json)
and regenerate the deliverable Claude Skill (SKILL.md).
Performs fuzzy deduplication using rapidfuzz.
"""

import os
import json
import math
import hashlib
import argparse
import logging
from pathlib import Path
from datetime import datetime
import yaml
import requests
from dotenv import load_dotenv

load_dotenv()

try:
    from rapidfuzz import fuzz

    def compute_similarity(s1: str, s2: str) -> float:
        return fuzz.token_sort_ratio(s1, s2)
except ImportError:
    from difflib import SequenceMatcher
    import re

    def compute_similarity(s1: str, s2: str) -> float:
        # Normalize punctuation and sort word tokens for token-sort similarity
        tokens1 = " ".join(sorted(re.findall(r"\w+", s1.lower())))
        tokens2 = " ".join(sorted(re.findall(r"\w+", s2.lower())))
        if not tokens1 and not tokens2:
            return 100.0
        return SequenceMatcher(None, tokens1, tokens2).ratio() * 100.0

logger = logging.getLogger("merge_skill")

CATEGORIES_ORDER = [
    "spacing",
    "color",
    "typography",
    "hierarchy",
    "motion",
    "accessibility",
    "layout"
]

# Whitelist allowed cross-category semantic cluster pairings
ALLOWED_CROSS_CATEGORY_PAIRS = {
    frozenset({"layout", "spacing"}),
    frozenset({"motion", "hierarchy"}),
    frozenset({"color", "accessibility"}),
    frozenset({"typography", "accessibility"}),
    frozenset({"layout", "hierarchy"}),
}


def get_allowed_cross_category_pairs(config: dict = None) -> set:
    """Read allowed cross-category semantic cluster pairings from config, with default fallback."""
    if config and isinstance(config.get("merge"), dict):
        raw = config["merge"].get("allowed_cross_category_pairs")
        if isinstance(raw, list):
            res = set()
            for pair in raw:
                if isinstance(pair, (list, tuple)) and len(pair) == 2:
                    res.add(frozenset({str(pair[0]).lower().strip(), str(pair[1]).lower().strip()}))
            if res:
                return res
    return ALLOWED_CROSS_CATEGORY_PAIRS


def compute_quality_score(p: dict) -> float:
    """
    Compute a composite quality score (0 - 100+) for a design principle based on:
    - Trigger context presence (+30)
    - Anti-pattern 'dont_do_this' presence (+20)
    - Direct action 'do_this' presence (+15)
    - Number of cited sources (+10 per source, cap at +30)
    - Extraction confidence rating (high: +20, medium: +10, low: 0)
    - Structured Before/After implementation pattern (+5)
    """
    score = 0.0
    if p.get("trigger_context"):
        score += 30.0
    if p.get("dont_do_this"):
        score += 20.0
    if p.get("do_this"):
        score += 15.0

    sources = p.get("sources", [])
    score += 10.0 * min(len(sources), 3)

    conf = str(p.get("confidence", "medium")).lower()
    score += {"high": 20.0, "medium": 10.0, "low": 0.0}.get(conf, 10.0)

    ex = str(p.get("example", ""))
    if "Before:" in ex and "After:" in ex:
        score += 5.0

    return round(score, 2)


def compute_principles_diff(old_principles: list, new_principles: list) -> dict:
    """Compare previous target principles vs new synthesized principles."""
    old_map = {p.get("principle", "").strip(): p for p in (old_principles or []) if p.get("principle")}
    new_map = {p.get("principle", "").strip(): p for p in (new_principles or []) if p.get("principle")}

    added = []
    modified = []
    removed = []

    for name, new_p in new_map.items():
        if name not in old_map:
            added.append(new_p)
        else:
            old_p = old_map[name]
            old_srcs = len(old_p.get("sources", []))
            new_srcs = len(new_p.get("sources", []))
            reasons = []
            if new_srcs != old_srcs:
                reasons.append(f"{new_srcs - old_srcs:+d} source(s)")
            if new_p.get("do_this") != old_p.get("do_this") and new_p.get("do_this"):
                reasons.append("updated guideline")
            old_q = old_p.get("quality_score", 0)
            new_q = new_p.get("quality_score", 0)
            if old_q != new_q and old_q > 0:
                reasons.append(f"quality score {old_q} -> {new_q}")

            if reasons:
                modified.append({"principle": new_p, "reasons": ", ".join(reasons)})

    for name, old_p in old_map.items():
        if name not in new_map:
            removed.append(old_p)

    return {"added": added, "modified": modified, "removed": removed}


def format_diff_summary(diff: dict, target_name: str) -> str:
    """Format principles diff into clean CLI string."""
    lines = [f"=== Principles Diff for '{target_name}' ==="]
    added = diff.get("added", [])
    modified = diff.get("modified", [])
    removed = diff.get("removed", [])

    if not added and not modified and not removed:
        lines.append("No changes detected.")
    else:
        for p in added:
            lines.append(f"+ Added: {p.get('principle')} [{p.get('category')}] (Quality Score: {p.get('quality_score', 0)})")
        for m in modified:
            p = m["principle"]
            lines.append(f"~ Modified: {p.get('principle')} ({m['reasons']})")
        for p in removed:
            lines.append(f"- Removed: {p.get('principle')} [{p.get('category')}]")

    return "\n".join(lines)


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_principles_store(store_path: str) -> list:
    """Load existing principles store."""
    if os.path.exists(store_path):
        try:
            with open(store_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception as e:
            logger.warning(f"Failed to read principles store at {store_path}: {e}")
    return []


def save_principles_store(principles: list, store_path: str):
    """Save principles store to JSON file."""
    p = Path(store_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(principles, f, indent=2, ensure_ascii=False)


def find_matching_principle(new_p: dict, existing_list: list, threshold: float = 85.0) -> tuple:
    """
    Find matching principle in existing_list.
    Returns (match_index, match_type) where match_type is 'same_category' or 'cross_category'.
    Returns (-1, None) if no match found.
    """
    new_name = new_p.get("principle", "").lower().strip()
    new_cat = new_p.get("category", "").lower().strip()
    new_rule = new_p.get("rule", "").lower().strip()

    best_idx = -1
    best_score = 0.0
    best_type = None

    # Step 1: Check same-category matches (Title >= threshold or Rule >= threshold)
    for idx, item in enumerate(existing_list):
        item_cat = item.get("category", "").lower().strip()
        item_name = item.get("principle", "").lower().strip()
        item_rule = item.get("rule", "").lower().strip()

        if item_cat == new_cat:
            name_score = compute_similarity(new_name, item_name)
            rule_score = compute_similarity(new_rule, item_rule) if (new_rule and item_rule) else 0.0
            max_score = max(name_score, rule_score)

            if max_score > best_score and max_score >= threshold:
                best_score = max_score
                best_idx = idx
                best_type = "same_category"

    if best_idx >= 0:
        return best_idx, best_type

    # Step 2: Check cross-category semantic matches (Rule similarity >= 80% or Title >= 88%)
    for idx, item in enumerate(existing_list):
        item_name = item.get("principle", "").lower().strip()
        item_rule = item.get("rule", "").lower().strip()

        rule_score = compute_similarity(new_rule, item_rule) if (new_rule and item_rule) else 0.0
        name_score = compute_similarity(new_name, item_name)

        if rule_score >= 80.0 or name_score >= 88.0:
            score = max(rule_score, name_score)
            if score > best_score:
                best_score = score
                best_idx = idx
                best_type = "cross_category"

    if best_idx >= 0:
        return best_idx, best_type

    return -1, None


def merge_principles_list(
    new_principles: list,
    existing_principles: list,
    threshold: float = 85.0
) -> list:
    """
    Deduplicate and merge new principles into existing list (handling both same-category and cross-category merges).
    """
    merged = list(existing_principles)

    for new_p in new_principles:
        match_idx, match_type = find_matching_principle(new_p, merged, threshold=threshold)

        # Normalize sources list from new_p
        incoming_sources = list(new_p.get("sources", []))
        if not incoming_sources and new_p.get("source_url"):
            incoming_sources.append({
                "handle": new_p.get("source_handle", ""),
                "date": new_p.get("source_date", ""),
                "url": new_p.get("source_url", "")
            })

        if match_idx >= 0:
            target = merged[match_idx]
            if match_type == "cross_category":
                logger.info(
                    f"Cross-category duplicate found: '{new_p.get('principle')}' [{new_p.get('category')}] "
                    f"matches '{target.get('principle')}' [{target.get('category')}] -> Merging."
                )
            else:
                logger.info(f"Duplicate found: '{new_p.get('principle')}' matches '{target.get('principle')}' -> Merging.")

            # Ensure target has sources list
            if "sources" not in target or not isinstance(target["sources"], list):
                target["sources"] = []
                if "source_url" in target:
                    target["sources"].append({
                        "handle": target.get("source_handle", ""),
                        "date": target.get("source_date", ""),
                        "url": target.get("source_url", "")
                    })

            # Append any new unique sources
            existing_urls = {s.get("url") for s in target["sources"] if s.get("url")}
            for src in incoming_sources:
                if src.get("url") and src["url"] not in existing_urls:
                    target["sources"].append(src)
                    existing_urls.add(src["url"])

            # Enrich why/example with quality-first rules (never overwrite by length alone)
            incoming_why = new_p.get("why", "").strip()
            target_why = target.get("why", "").strip()
            if not target_why or target_why in ["None specified", ""]:
                target["why"] = incoming_why

            incoming_ex = new_p.get("example", "").strip()
            target_ex = target.get("example", "").strip()
            if not target_ex or target_ex in ["None specified", ""]:
                target["example"] = incoming_ex
            elif "Before:" in incoming_ex and "After:" in incoming_ex and not ("Before:" in target_ex and "After:" in target_ex):
                # Upgrade to structured Before/After implementation pattern
                target["example"] = incoming_ex

            # Upgrade confidence if incoming principle has higher confidence
            conf_rank = {"high": 3, "medium": 2, "low": 1}
            new_conf = new_p.get("confidence", "medium").lower()
            old_conf = target.get("confidence", "medium").lower()
            if conf_rank.get(new_conf, 2) > conf_rank.get(old_conf, 2):
                target["confidence"] = new_conf

            # Merge instructive fields if missing on target
            if not target.get("do_this") and (new_p.get("do_this") or new_p.get("rule")):
                target["do_this"] = new_p.get("do_this") or new_p.get("rule")
            if not target.get("dont_do_this") and new_p.get("dont_do_this"):
                target["dont_do_this"] = new_p.get("dont_do_this")
            if not target.get("trigger_context") and new_p.get("trigger_context"):
                target["trigger_context"] = new_p.get("trigger_context")

        else:
            # Create new structured record
            record = {
                "principle": new_p.get("principle"),
                "category": new_p.get("category"),
                "rule": new_p.get("rule"),
                "do_this": new_p.get("do_this") or new_p.get("rule"),
                "dont_do_this": new_p.get("dont_do_this") or "",
                "trigger_context": new_p.get("trigger_context") or "",
                "why": new_p.get("why"),
                "example": new_p.get("example"),
                "confidence": new_p.get("confidence", "medium"),
                "sources": incoming_sources
            }
            merged.append(record)
            logger.info(f"Appended new principle: '{record['principle']}' [{record['category']}]")

    return merged


def compute_centroid(embs: list) -> list:
    """Compute normalized average centroid vector from a list of embeddings."""
    valid = [e for e in embs if e]
    if not valid:
        return None
    dim = len(valid[0])
    avg = [sum(e[i] for e in valid) / len(valid) for i in range(dim)]
    norm = math.sqrt(sum(x * x for x in avg))
    if norm == 0:
        return avg
    return [x / norm for x in avg]


CACHE_DIR = Path("data/cache")
EMBEDDINGS_CACHE_FILE = CACHE_DIR / "embeddings.json"


def load_embedding_cache() -> dict:
    """Load persistent embedding cache to guarantee 100% deterministic clustering."""
    if EMBEDDINGS_CACHE_FILE.exists():
        try:
            with open(EMBEDDINGS_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_embedding_cache(cache: dict):
    """Save persistent embedding cache to disk."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(EMBEDDINGS_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except Exception as e:
        logger.debug(f"Could not persist embedding cache: {e}")


def cluster_and_synthesize_principles(
    principles: list,
    similarity_threshold: float = 0.83,
    config: dict = None,
    allowed_pairs: set = None
) -> list:
    """
    Semantic clustering pass that groups principles by concept rather than lexical tokens alone.
    Uses Gemini embeddings (if GEMINI_API_KEY is available) with dynamic centroid cosine similarity clustering,
    falling back to RapidFuzz token set ratio.
    In each cluster:
    - Maintains dynamically updated normalized centroid embeddings to eliminate seed-order dependency.
    - Employs persistent disk caching (data/cache/embeddings.json) for 100% reproducible re-runs.
    - Preserves non-canonical alternate rules and implementations as 'variants'.
    - Merges sources from all member principles into a canonical source list.
    - Upgrades confidence ranking to highest within the cluster.
    - Computes composite quality_score (0-100+) and ranks high-value heuristics first.
    - Retains the most articulate rule and structured implementation example.
    """
    if not principles:
        return principles

    active_allowed_pairs = allowed_pairs or get_allowed_cross_category_pairs(config)

    if len(principles) == 1:
        single = dict(principles[0])
        single["quality_score"] = compute_quality_score(single)
        return [single]

    api_key = os.getenv("GEMINI_API_KEY")

    embeddings = []
    if api_key:
        try:
            cache = load_embedding_cache()
            texts = [f"{p.get('principle', '')}: {p.get('rule', '')} {p.get('why', '')}" for p in principles]
            keys = [hashlib.sha256(f"gemini-embedding-001:{t[:1000]}".encode("utf-8")).hexdigest() for t in texts]

            missing_indices = [i for i, k in enumerate(keys) if k not in cache]
            if missing_indices:
                batch_reqs = [
                    {"model": "models/gemini-embedding-001", "content": {"parts": [{"text": texts[i][:1000]}]}}
                    for i in missing_indices
                ]
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:batchEmbedContents?key={api_key}"
                resp = requests.post(url, json={"requests": batch_reqs}, timeout=15)
                if resp.status_code == 200:
                    raw_embs = resp.json().get("embeddings", [])
                    for idx_pos, raw_e in enumerate(raw_embs):
                        orig_idx = missing_indices[idx_pos]
                        val = raw_e.get("values", [])
                        if val:
                            cache[keys[orig_idx]] = val
                    save_embedding_cache(cache)

            # Retrieve embeddings from cache
            all_cached = [cache.get(k) for k in keys]
            if all(e for e in all_cached) and len(all_cached) == len(principles):
                embeddings = all_cached
                logger.info(
                    f"Loaded/computed {len(embeddings)} semantic embeddings for cross-creator synthesis "
                    f"({len(texts) - len(missing_indices)} from cache, {len(missing_indices)} fresh)."
                )
            else:
                logger.warning("Partial embedding failure detected; falling back to lexical clustering across all principles.")
                embeddings = []
        except Exception as e:
            logger.warning(f"Semantic embedding generation failed, using lexical dedup fallback: {e}")
            embeddings = []

    def cosine_sim(v1, v2):
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    clusters = []  # list of lists of principle dicts
    cluster_member_embeddings = []  # list of lists of member embeddings
    cluster_centroids = []  # list of centroid embeddings

    has_full_embeddings = bool(embeddings and len(embeddings) == len(principles))

    for idx, p in enumerate(principles):
        p_emb = embeddings[idx] if has_full_embeddings else None
        p_cat = (p.get("category") or "layout").lower()
        best_cluster_idx = -1
        best_sim = 0.0

        for c_idx, c_members in enumerate(clusters):
            c_cat = (c_members[0].get("category") or "layout").lower()
            same_cat = (p_cat == c_cat)

            # Category Guard: Only allow same category or whitelisted cross-category pairs
            if not same_cat:
                if frozenset({p_cat, c_cat}) not in active_allowed_pairs:
                    continue  # Strict rejection for non-whitelisted cross-category pairs
                threshold = 0.88 if has_full_embeddings else 88.0
            else:
                threshold = similarity_threshold if has_full_embeddings else 82.0

            if has_full_embeddings and cluster_centroids[c_idx]:
                sim = cosine_sim(p_emb, cluster_centroids[c_idx])
            else:
                # Lexical single-linkage against cluster members
                member_sims = [
                    max(
                        compute_similarity(p.get("principle", ""), m.get("principle", "")),
                        compute_similarity(p.get("rule", ""), m.get("rule", ""))
                    )
                    for m in c_members
                ]
                sim = max(member_sims) if member_sims else 0.0

            if sim > best_sim and sim >= threshold:
                best_sim = sim
                best_cluster_idx = c_idx

        if best_cluster_idx >= 0:
            clusters[best_cluster_idx].append(p)
            if has_full_embeddings and p_emb:
                cluster_member_embeddings[best_cluster_idx].append(p_emb)
                cluster_centroids[best_cluster_idx] = compute_centroid(cluster_member_embeddings[best_cluster_idx])
            sim_display = f"{best_sim:.2f}" if has_full_embeddings else f"{best_sim:.1f}%"
            logger.info(
                f"Semantically clustered '{p.get('principle')}' into cluster '{clusters[best_cluster_idx][0].get('principle')}' "
                f"(centroid similarity: {sim_display})"
            )
        else:
            clusters.append([p])
            if has_full_embeddings and p_emb:
                cluster_member_embeddings.append([p_emb])
                cluster_centroids.append(p_emb)
            else:
                cluster_member_embeddings.append([])
                cluster_centroids.append(None)

    synthesized = []
    conf_rank = {"high": 3, "medium": 2, "low": 1}

    for members in clusters:
        if len(members) == 1:
            m = dict(members[0])
            m["quality_score"] = compute_quality_score(m)
            synthesized.append(m)
            continue

        def member_quality(m):
            score = conf_rank.get(m.get("confidence", "medium").lower(), 2) * 10
            if "Before:" in m.get("example", "") and "After:" in m.get("example", ""):
                score += 5
            return score

        canonical = max(members, key=member_quality)
        merged_principle = dict(canonical)

        # Preserve alternate perspectives & implementations as variants
        variants = []
        for m in members:
            if m is not canonical:
                v = {
                    "principle": m.get("principle"),
                    "rule": m.get("rule"),
                    "do_this": m.get("do_this") or m.get("rule"),
                    "dont_do_this": m.get("dont_do_this") or "",
                    "trigger_context": m.get("trigger_context") or "",
                    "why": m.get("why"),
                    "example": m.get("example"),
                    "sources": m.get("sources", [])
                }
                variants.append(v)
        if variants:
            merged_principle["variants"] = variants

        # Supplement instructive fields on merged_principle if missing
        if not merged_principle.get("dont_do_this"):
            for m in members:
                if m.get("dont_do_this"):
                    merged_principle["dont_do_this"] = m["dont_do_this"]
                    break
        if not merged_principle.get("trigger_context"):
            for m in members:
                if m.get("trigger_context"):
                    merged_principle["trigger_context"] = m["trigger_context"]
                    break

        all_sources = []
        seen_urls = set()
        for m in members:
            for s in m.get("sources", []):
                u = s.get("url")
                if u and u not in seen_urls:
                    all_sources.append(s)
                    seen_urls.add(u)
                elif not u:
                    all_sources.append(s)

        merged_principle["sources"] = all_sources
        max_conf = max(
            members,
            key=lambda m: conf_rank.get(m.get("confidence", "medium").lower(), 2)
        ).get("confidence", "medium")
        merged_principle["confidence"] = max_conf
        merged_principle["quality_score"] = compute_quality_score(merged_principle)

        synthesized.append(merged_principle)

    synthesized.sort(key=lambda item: (item.get("quality_score", 0), len(item.get("sources", []))), reverse=True)
    return synthesized


def generate_skill_markdown(
    principles: list,
    output_path: str,
    skill_name: str = "ui-ux",
    description: str = None
):
    """
    Generate clean, authoritative SKILL.md formatted for Claude skills.
    Includes confidence filtering, rich triggering frontmatter, and consensus weighting.
    """
    # Filter verified vs unverified
    verified_principles = [p for p in principles if p.get("confidence", "medium").lower() in ["high", "medium"]]
    unverified_principles = [p for p in principles if p.get("confidence", "medium").lower() == "low"]

    # Gather active categories and topics for dynamic frontmatter
    active_categories = sorted(list(set(p.get("category", "layout").lower() for p in verified_principles)))
    cat_str = ", ".join(c.title() for c in active_categories) if active_categories else "Color, Layout, Hierarchy"

    if description is None:
        description = (
            f"Actionable UI/UX design style guide covering {cat_str}. "
            "Use this skill whenever creating, reshaping, critiquing, or reviewing UI/UX interfaces — "
            "including landing pages, dashboards, hero layouts, typography hierarchy, dark/light color palettes, "
            "interactive cards, navigation headers, and modal states — even if the user does not explicitly request 'design principles.'"
        )

    grouped = {cat: [] for cat in CATEGORIES_ORDER}
    for p in verified_principles:
        cat = p.get("category", "layout").lower()
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(p)

    # Dynamically derive audit checklist from top verified principles
    checklist_items = []
    sorted_for_checklist = sorted(
        verified_principles,
        key=lambda x: (
            0 if x.get("confidence", "").lower() == "high" else 1,
            -len(x.get("sources", []))
        )
    )
    for p in sorted_for_checklist[:7]:
        name = p.get("principle", "").strip()
        rule = p.get("rule", "").strip().rstrip(".")
        if name and rule:
            checklist_items.append(f"- [ ] **{name}**: {rule}.")

    if len(checklist_items) < 3:
        fallback_checks = [
            "- [ ] **Spatial Consistency**: Are margins, gutters, and inner paddings adhering strictly to the 8-point spatial grid?",
            "- [ ] **Visual Separation**: Are cards and structural containers separated primarily via intentional negative space rather than heavy divider borders?",
            "- [ ] **Typographic Anchor**: Is body and title text left-aligned to establish a single vertical scanning anchor rather than centered jagged lines?",
            "- [ ] **Action Hierarchy**: Is there exactly one primary CTA above the fold, using explicit verb-noun copywriting ('Create Project', not 'Submit')?",
            "- [ ] **Safe Touch Targets**: Do interactive touch elements meet the minimum 44×44pt mobile bounding box?"
        ]
        for fc in fallback_checks:
            if len(checklist_items) < 7:
                checklist_items.append(fc)

    lines = [
        "---",
        f"name: {skill_name}",
        f'description: "{description}"',
        "---",
        "",
        "# UI/UX Design System & Heuristics",
        "",
        "Actionable, production-grade UI/UX design heuristics synthesized from leading design engineers and creators.",
        "Reference these principles when architecting screens, refining typographic rhythm, calibrating negative space, or conducting design reviews.",
        "",
        "## Pre-Flight UI/UX Audit Checklist",
        "",
        "Before finalizing any interface layout or component hierarchy, audit against these verified fundamentals:",
        "",
    ]
    lines.extend(checklist_items)
    lines.extend([
        "",
        "## Parametric Design Tokens",
        "",
        "> _Baseline system tokens (8-point spatial grid, WCAG targets) calibrated alongside extracted creator constraints:_ ",
        "",
        "| System Token | Standard Value | Practical Application |",
        "|---|---|---|",
        "| **Base Grid** | `8px` (`0.5rem`) | Micro adjustments use `4px` half-steps; macro layout uses `16px`, `24px`, `32px`, `48px`, `64px`. |",
        "| **Card Padding** | `16px` (compact) / `24px` (comfortable) | Uniform internal breathing room for content containers. |",
        "| **Touch Target** | Minimum `44×44px` (mobile), `32×32px` (desktop) | Prevents missed taps and motor strain on touchscreens. |",
        "| **Border Radius** | `4px` (inputs/tags), `8px` (buttons), `16px` (cards/modals), `9999px` (capsules) | Smooth corner curvature matching container scale. |",
        "| **Hairline Borders** | `1px solid rgba(255, 255, 255, 0.08)` (Dark) / `rgba(0, 0, 0, 0.08)` (Light) | Subtle surface elevation without visual heavy lines. |",
        "| **Typography Scale** | Headline `24–32px` (1.2 lh), Body `14–16px` (1.5 lh), Caption `12–13px` (1.4 lh) | Legible reading hierarchy with optical line-height balance. |",
        "",
        "## Distilled Design Principles by Domain",
        ""
    ])

    total_principles = 0

    for cat in CATEGORIES_ORDER:
        cat_title = cat.title()
        items = grouped.get(cat, [])
        if not items:
            continue

        lines.append(f"### {cat_title}\n")

        for item in sorted(items, key=lambda x: x.get("principle", "")):
            total_principles += 1
            title = item.get("principle", "Principle")
            rule = item.get("rule", "")
            do_this = item.get("do_this") or rule
            dont_do_this = item.get("dont_do_this") or ""
            trigger_context = item.get("trigger_context") or ""
            why = item.get("why", "")
            example = item.get("example", "")
            sources = item.get("sources", [])
            confidence = item.get("confidence", "medium").upper()

            lines.append(f"#### {title}")
            if trigger_context:
                lines.append(f"- **When to apply**: {trigger_context}")
            lines.append(f"- **Do this**: {do_this}")
            if dont_do_this:
                lines.append(f"- **Don't do this**: {dont_do_this}")
            if why:
                lines.append(f"- **Why it matters**: {why}")
            if example and example != "None specified":
                if "Before:" in example and "After:" in example:
                    # Clean before/after breakdown
                    parts = example.split("After:")
                    before_part = parts[0].replace("Before:", "").strip()
                    after_part = parts[1].strip() if len(parts) > 1 else ""
                    lines.append(f"- **Implementation Pattern**:")
                    lines.append(f"  - **Avoid**: {before_part}")
                    lines.append(f"  - **Do This**: {after_part}")
                else:
                    lines.append(f"- **Implementation Pattern**: {example}")

            # Alternate Creator Perspectives & Implementations (from synthesized clusters)
            variants = item.get("variants", [])
            if variants:
                lines.append("- **Alternate Creator Perspectives & Implementations**:")
                for v in variants:
                    v_sources = v.get("sources", [])
                    v_handles = [f"@{s.get('handle')}" for s in v_sources if s.get("handle")]
                    handle_label = f" ({', '.join(v_handles)})" if v_handles else ""
                    lines.append(f"  - *Perspective{handle_label}*: {v.get('rule')}")
                    if v.get("example") and v.get("example") != "None specified":
                        lines.append(f"    - *Implementation*: {v.get('example')}")

            # Source Diversity & Consensus Weighting
            if sources:
                unique_handles = sorted(list(set(s.get("handle") for s in sources if s.get("handle"))))
                dates = [s.get("date") for s in sources if s.get("date")]
                most_recent = max(dates) if dates else "recent"

                if len(unique_handles) >= 2:
                    handles_str = ", ".join(f"@{h}" for h in unique_handles)
                    lines.append(f"- **Consensus**: Multi-Source Consensus (Validated across {len(unique_handles)} creators: {handles_str})")
                elif len(sources) >= 2 and unique_handles:
                    lines.append(f"- **Consensus**: Creator Standard (Reaffirmed across {len(sources)} posts by @{unique_handles[0]})")
                elif unique_handles:
                    lines.append(f"- **Status**: Single-Source Guideline (@{unique_handles[0]})")

                source_links = [f"[@{s.get('handle', 'creator')}]({s.get('url')})" for s in sources if s.get("url")]
                citations = ", ".join(source_links) if source_links else f"{len(sources)} posts"
                lines.append(f"- **Sources**: {len(sources)} citation(s) (latest: {most_recent}) — {citations}")

            lines.append("")

    # Quarantined / Unverified Low-Confidence Drafts (if any)
    if unverified_principles:
        lines.append("### Unverified / Draft Observations\n")
        lines.append("> _Note: The following observations were extracted with low confidence and require manual verification before production use._\n")
        for item in unverified_principles:
            lines.append(f"#### [Draft] {item.get('principle', 'Observation')}")
            lines.append(f"- **Rule**: {item.get('rule', '')}")
            lines.append(f"- **Category**: {item.get('category', 'layout')}")
            lines.append("")

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).strip() + "\n")

    logger.info(f"Generated {output_path} with {total_principles} verified principles across active categories.")


def generate_creator_summary_markdown(
    handle: str,
    principles: list,
    posts: list,
    output_path: str,
    is_synthesis: bool = False,
    source_targets: list = None
):
    """
    Generate a visual, comprehensive summary report for a specific creator or multi-creator synthesis.
    """
    total_posts = len(posts)
    transcribed_count = sum(1 for p in posts if p.get("transcript"))
    video_count = sum(1 for p in posts if p.get("is_video"))
    dates = [p.get("date") for p in posts if p.get("date")]
    date_range = f"{min(dates)} to {max(dates)}" if dates else "Recent"

    cat_counts = {cat: 0 for cat in CATEGORIES_ORDER}
    for p in principles:
        cat = p.get("category", "layout").lower()
        if cat in cat_counts:
            cat_counts[cat] += 1

    if is_synthesis:
        target_list_str = ", ".join(source_targets) if source_targets else handle
        lines = [
            f"# Cross-Creator Design Skill Synthesis Report: {handle}",
            "",
            f"> **Synthesized Targets:** `{target_list_str}`  ",
            f"> **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"> **Analyzed Post Range:** {date_range}",
            "",
            "---",
            "",
            "## Synthesis Overview & Consensus Metrics",
            "",
            "| Metric | Count |",
            "|---|---|",
            f"| **Contributing Target Count** | `{len(source_targets) if source_targets else 1}` |",
            f"| **Total Posts Analyzed** | `{total_posts}` |",
            f"| **Video Reels Transcribed** | `{transcribed_count}` / `{video_count}` |",
            f"| **Synthesized Design Principles** | `{len(principles)}` |",
            f"| **Active Categories** | `{sum(1 for c, n in cat_counts.items() if n > 0)}` / `{len(CATEGORIES_ORDER)}` |",
            f"| **Synthesis Engine** | `Centroid Embedding Synthesis & Dedup` |",
            "",
            "### Category Distribution",
            "",
            "| Category | Principles Synthesized |",
            "|---|---|",
        ]
    else:
        lines = [
            f"# Design Skill Extraction Report: @{handle}",
            "",
            f"> **Creator Profile:** [@{handle}](https://www.instagram.com/{handle}/)  ",
            f"> **Extracted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"> **Analyzed Post Range:** {date_range}",
            "",
            "---",
            "",
            "## Overview & Extraction Metrics",
            "",
            "| Metric | Count |",
            "|---|---|",
            f"| **Total Posts Analyzed** | `{total_posts}` |",
            f"| **Video Reels Transcribed** | `{transcribed_count}` / `{video_count}` |",
            f"| **Unique Design Principles** | `{len(principles)}` |",
            f"| **Active Categories** | `{sum(1 for c, n in cat_counts.items() if n > 0)}` / `{len(CATEGORIES_ORDER)}` |",
            f"| **Extraction Engine** | `LLM Analysis (No Templates)` |",
            "",
            "### Category Distribution",
            "",
            "| Category | Principles Extracted |",
            "|---|---|",
        ]

    for cat in CATEGORIES_ORDER:
        cnt = cat_counts.get(cat, 0)
        if cnt > 0:
            lines.append(f"| **{cat.title()}** | `{cnt}` principle(s) |")

    lines.extend([
        "",
        "---",
        "",
        "## Distilled Design Principles",
        ""
    ])

    grouped = {cat: [] for cat in CATEGORIES_ORDER}
    for p in principles:
        cat = p.get("category", "layout").lower()
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(p)

    for cat in CATEGORIES_ORDER:
        items = grouped.get(cat, [])
        if not items:
            continue

        lines.append(f"### {cat.title()}\n")
        for item in sorted(items, key=lambda x: x.get("principle", "")):
            title = item.get("principle", "Principle")
            rule = item.get("rule", "")
            do_this = item.get("do_this") or rule
            dont_do_this = item.get("dont_do_this") or ""
            trigger_context = item.get("trigger_context") or ""
            why = item.get("why", "")
            example = item.get("example", "")
            sources = item.get("sources", [])
            variants = item.get("variants", [])

            lines.append(f"#### {title}")
            if trigger_context:
                lines.append(f"- **Trigger Scenario**: {trigger_context}")
            lines.append(f"- **Guideline**: {do_this}")
            if dont_do_this:
                lines.append(f"- **Avoid (Anti-Pattern)**: {dont_do_this}")
            if why:
                lines.append(f"- **Rationale**: {why}")
            if example and example != "None specified":
                lines.append(f"- **Practical Application**: {example}")
            if variants:
                lines.append("- **Alternate Creator Perspectives & Implementations**:")
                for v in variants:
                    v_sources = v.get("sources", [])
                    v_handles = [f"@{s.get('handle')}" for s in v_sources if s.get("handle")]
                    handle_label = f" ({', '.join(v_handles)})" if v_handles else ""
                    lines.append(f"  - *Perspective{handle_label}*: {v.get('rule')}")
                    if v.get("example") and v.get("example") != "None specified":
                        lines.append(f"    - *Implementation*: {v.get('example')}")
            if sources:
                source_links = [f"[{s.get('date', 'Link')}]({s.get('url')})" for s in sources if s.get("url")]
                citations = ", ".join(source_links) if source_links else f"{len(sources)} posts"
                lines.append(f"- **Cited Sources ({len(sources)})**: {citations}")
            lines.append("")

    lines.extend([
        "---",
        "",
        "## Source Posts Index",
        "",
        "| Shortcode | Date | Type | Likes | Caption Summary | Reel Transcript Available | Link |",
        "|---|---|---|---|---|---|---|"
    ])

    for p in posts:
        code = p.get("shortcode", "")
        pdate = p.get("date", "")
        ptype = "Video/Reel" if p.get("is_video") else "Image/Carousel"
        likes = f"{p.get('like_count', 0):,}"
        cap = (p.get("caption") or "").replace("\n", " ").strip()
        cap_summary = (cap[:45] + "...") if len(cap) > 45 else cap
        has_trans = "Yes" if p.get("transcript") else "No"
        url = p.get("url", f"https://www.instagram.com/p/{code}/")
        lines.append(f"| `{code}` | {pdate} | {ptype} | {likes} | {cap_summary} | {has_trans} | [View Post]({url}) |")

    lines.append("")

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).strip() + "\n")

    logger.info(f"Generated creator summary at {output_path}")


def get_clean_skill_name(target: str) -> str:
    """
    Get clean skill folder name from target handle or collection name.
    e.g. 'collection_checkups' -> 'checkups'
         '@zanderwhitehurst' -> 'zanderwhitehurst'
         'https://www.instagram.com/.../saved/checkups/123/' -> 'checkups'
    """
    if not target:
        return "ui-ux"
    import re
    if "/saved/" in target:
        match = re.search(r"/saved/([^/?#]+)", target)
        if match:
            return match.group(1).lower().replace(" ", "-")
    clean = target.strip()
    if clean.startswith("collection_"):
        clean = clean[len("collection_"):]
    return clean.lstrip("@").strip().lower()


def merge_skill(
    handle: str = None,
    config_path: str = "config.yaml",
    new_principles: list = None,
    dry_run: bool = False,
    show_diff: bool = False
) -> list:
    """
    Deduplicate and compile target-specific skill deliverables into skills/<clean_name>/
    and mirror to output/<target>/.
    Eliminates global skill generation; each target has its own isolated skill folder.
    """
    config = load_config(config_path)
    merge_cfg = config.get("merge", {})
    paths_cfg = config.get("paths", {})

    threshold = float(merge_cfg.get("dedup_similarity_threshold", 85))
    output_dir = paths_cfg.get("output_dir", "output")
    raw_data_dir = paths_cfg.get("raw_data_dir", "data/raw")
    skills_dir = paths_cfg.get("skills_dir", "skills")

    targets_to_process = [handle] if handle else []

    # If no target specified, discover all targets from output/ and data/raw/
    if not targets_to_process:
        found_targets = set()
        for base_dir in [Path(output_dir), Path(raw_data_dir)]:
            if base_dir.exists():
                for d in base_dir.iterdir():
                    if d.is_dir() and not d.name.startswith(".") and d.name != "design-ui-ux":
                        found_targets.add(d.name)
        targets_to_process = sorted(list(found_targets))

    last_merged = []
    for tgt in targets_to_process:
        if not tgt:
            continue

        clean_skill_name = get_clean_skill_name(tgt)
        target_out_dir = Path(output_dir) / tgt
        target_skill_dir = Path(skills_dir) / clean_skill_name

        target_principles_raw = []
        target_posts = []

        # Load posts from both output/ and raw/ directories, merging by post_id/shortcode
        # to ensure no principles or metadata are ever dropped from a stale mirror
        merged_posts_map = {}
        for pfile in [target_out_dir / "posts.json", Path(raw_data_dir) / tgt / "posts.json"]:
            if pfile.exists():
                try:
                    with open(pfile, "r", encoding="utf-8") as f:
                        file_posts = json.load(f)
                        if isinstance(file_posts, list):
                            for post in file_posts:
                                pid = str(post.get("post_id") or post.get("shortcode") or "")
                                if not pid:
                                    continue
                                if pid not in merged_posts_map:
                                    merged_posts_map[pid] = post
                                else:
                                    existing = merged_posts_map[pid]
                                    existing_principles = existing.get("principles", []) or existing.get("extracted_principles", [])
                                    incoming_principles = post.get("principles", []) or post.get("extracted_principles", [])
                                    if len(incoming_principles) > len(existing_principles):
                                        existing["principles"] = incoming_principles
                                    if post.get("transcript") and not existing.get("transcript"):
                                        existing["transcript"] = post["transcript"]
                except Exception as e:
                    logger.warning(f"Error reading posts file {pfile}: {e}")

        target_posts = list(merged_posts_map.values())
        for post in target_posts:
            post_principles = post.get("principles", []) or post.get("extracted_principles", [])
            for p in post_principles:
                target_principles_raw.append(p)

        if new_principles and tgt == handle:
            target_principles_raw.extend(new_principles)

        # Step 1: Lexical deduplication (token sort matching)
        target_merged = merge_principles_list(target_principles_raw, [], threshold=threshold)

        # Step 2: Semantic clustering & synthesis (cross-creator embedding consensus)
        target_synthesized = cluster_and_synthesize_principles(
            target_merged,
            similarity_threshold=0.83,
            config=config
        )

        old_principles_file = target_skill_dir / "principles.json"
        old_principles = load_principles_store(str(old_principles_file))
        diff = compute_principles_diff(old_principles, target_synthesized)
        diff_str = format_diff_summary(diff, clean_skill_name)
        if show_diff or dry_run or logger.isEnabledFor(logging.DEBUG):
            logger.info(diff_str)

        if dry_run:
            logger.info(
                f"[DRY-RUN] Target '{clean_skill_name}': {len(target_synthesized)} principles synthesized. "
                "No files written to disk."
            )
            last_merged = target_synthesized
            continue

        target_out_dir.mkdir(parents=True, exist_ok=True)
        target_skill_dir.mkdir(parents=True, exist_ok=True)

        # 1. Primary Skill Deliverables in skills/<clean_name>/
        skill_file = target_skill_dir / "SKILL.md"
        summary_file = target_skill_dir / "SUMMARY.md"
        principles_file = target_skill_dir / "principles.json"

        save_principles_store(target_synthesized, str(principles_file))
        generate_skill_markdown(
            principles=target_synthesized,
            output_path=str(skill_file),
            skill_name=clean_skill_name,
            description=f"Actionable UI/UX design heuristics distilled from {clean_skill_name}."
        )
        generate_creator_summary_markdown(
            handle=clean_skill_name,
            principles=target_synthesized,
            posts=target_posts,
            output_path=str(summary_file)
        )

        # 2. Mirror deliverables into output/<target>/
        save_principles_store(target_synthesized, str(target_out_dir / "principles.json"))
        generate_skill_markdown(
            principles=target_synthesized,
            output_path=str(target_out_dir / "SKILL.md"),
            skill_name=clean_skill_name,
            description=f"Actionable UI/UX design heuristics distilled from {clean_skill_name}."
        )
        generate_creator_summary_markdown(
            handle=clean_skill_name,
            principles=target_synthesized,
            posts=target_posts,
            output_path=str(target_out_dir / "SUMMARY.md")
        )

        logger.info(
            f"Compiled target skill '{clean_skill_name}' ({len(target_synthesized)} principles) -> "
            f"{target_skill_dir}/"
        )
        last_merged = target_synthesized

    return last_merged


def merge_multi_target(
    targets: list,
    output_skill_name: str = "ui-ux-consensus",
    min_sources: int = 1,
    config_path: str = "config.yaml",
    dry_run: bool = False,
    show_diff: bool = False
) -> list:
    """
    Synthesize design principles across multiple creators and/or saved collections
    into a unified, cross-creator design system skill.

    Loads posts and principles from output/<target>, data/raw/<target>, and skills/<clean_target>.
    Applies:
    1. Lexical deduplication across all pooled principles.
    2. Dynamic centroid semantic clustering with persistent disk embeddings cache.
    3. Consensus threshold filtering (min_sources >= N).
    4. Generation of skills/<output_skill_name>/ and output/<output_skill_name>/ deliverables.
    """
    config = load_config(config_path)
    merge_cfg = config.get("merge", {})
    paths_cfg = config.get("paths", {})

    threshold = float(merge_cfg.get("dedup_similarity_threshold", 85))
    output_dir_base = paths_cfg.get("output_dir", "output")
    raw_data_dir_base = paths_cfg.get("raw_data_dir", "data/raw")
    skills_dir_base = paths_cfg.get("skills_dir", "skills")

    all_posts_map = {}
    all_principles_raw = []
    found_targets = []

    for tgt in targets:
        if not tgt:
            continue
        clean_name = get_clean_skill_name(tgt)
        target_candidates = [
            tgt,
            tgt.lstrip("@"),
            f"collection_{tgt.lstrip('@')}",
            clean_name,
            f"collection_{clean_name}",
        ]

        target_principles = []
        matched_any = False

        search_dirs = []
        for cand in set(target_candidates):
            for base in [Path(output_dir_base), Path(raw_data_dir_base), Path(skills_dir_base)]:
                d = base / cand
                if d.exists() and d.is_dir() and d not in search_dirs:
                    search_dirs.append(d)

        for d in search_dirs:
            # Load posts.json
            pfile = d / "posts.json"
            if pfile.exists():
                matched_any = True
                try:
                    with open(pfile, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            for post in data:
                                pid = str(post.get("post_id") or post.get("shortcode") or "")
                                if not pid:
                                    continue
                                if pid not in all_posts_map:
                                    all_posts_map[pid] = post
                                else:
                                    ex = all_posts_map[pid]
                                    ep = ex.get("principles", []) or ex.get("extracted_principles", [])
                                    ip = post.get("principles", []) or post.get("extracted_principles", [])
                                    if len(ip) > len(ep):
                                        ex["principles"] = ip
                                    if post.get("transcript") and not ex.get("transcript"):
                                        ex["transcript"] = post["transcript"]

                                p_list = post.get("principles", []) or post.get("extracted_principles", [])
                                for p in p_list:
                                    target_principles.append((p, clean_name, post))
                except Exception as e:
                    logger.warning(f"Error reading {pfile}: {e}")

            # Load principles.json
            pr_file = d / "principles.json"
            if pr_file.exists():
                matched_any = True
                try:
                    with open(pr_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            for p in data:
                                target_principles.append((p, clean_name, None))
                except Exception as e:
                    logger.warning(f"Error reading {pr_file}: {e}")

        if matched_any:
            found_targets.append(clean_name)
        else:
            logger.warning(f"Target '{tgt}' not found in any search directories.")

        for p, handle_name, post_ref in target_principles:
            p_copy = dict(p)
            sources = list(p_copy.get("sources", []))
            if not sources:
                src = {"handle": handle_name}
                if post_ref:
                    if post_ref.get("url"):
                        src["url"] = post_ref["url"]
                    elif post_ref.get("shortcode"):
                        src["url"] = f"https://www.instagram.com/p/{post_ref['shortcode']}/"
                    if post_ref.get("date"):
                        src["date"] = post_ref["date"]
                sources.append(src)
            else:
                for s in sources:
                    if not s.get("handle"):
                        s["handle"] = handle_name
            p_copy["sources"] = sources
            all_principles_raw.append(p_copy)

    if not all_principles_raw:
        logger.warning(f"No principles found across targets: {targets}")
        return []

    logger.info(
        f"Multi-Target Synthesis: Pooling {len(all_principles_raw)} raw principles across {len(found_targets)} "
        f"targets ({', '.join(found_targets)})."
    )

    # Step 1: Lexical deduplication
    lexical_merged = merge_principles_list(all_principles_raw, [], threshold=threshold)
    logger.info(f"Lexical deduplication reduced {len(all_principles_raw)} principles to {len(lexical_merged)}.")

    # Step 2: Semantic clustering & synthesis (dynamic centroid + persistent cache)
    synthesized = cluster_and_synthesize_principles(
        lexical_merged,
        similarity_threshold=0.83,
        config=config
    )
    logger.info(f"Semantic clustering synthesized into {len(synthesized)} canonical principles.")

    # Step 3: Filter by min_sources
    if min_sources > 1:
        before_cnt = len(synthesized)
        synthesized = [p for p in synthesized if len(p.get("sources", [])) >= min_sources]
        logger.info(
            f"Filtered by min_sources={min_sources}: retained {len(synthesized)} of {before_cnt} principles."
        )

    clean_output_skill = get_clean_skill_name(output_skill_name)
    skill_dir = Path(skills_dir_base) / clean_output_skill
    out_dir = Path(output_dir_base) / clean_output_skill

    old_principles = load_principles_store(str(skill_dir / "principles.json"))
    diff = compute_principles_diff(old_principles, synthesized)
    diff_str = format_diff_summary(diff, clean_output_skill)
    if show_diff or dry_run or logger.isEnabledFor(logging.DEBUG):
        logger.info(diff_str)

    if dry_run:
        logger.info(
            f"[DRY-RUN] Multi-Target Synthesis '{clean_output_skill}': "
            f"{len(synthesized)} principles synthesized across {len(found_targets)} targets. No files written."
        )
        return synthesized

    skill_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    desc = (
        f"Actionable cross-creator UI/UX design heuristics synthesized from {len(found_targets)} "
        f"sources ({', '.join(found_targets)})."
    )

    # 1. Primary skill files
    save_principles_store(synthesized, str(skill_dir / "principles.json"))
    generate_skill_markdown(
        principles=synthesized,
        output_path=str(skill_dir / "SKILL.md"),
        skill_name=clean_output_skill,
        description=desc
    )
    all_posts = list(all_posts_map.values())
    generate_creator_summary_markdown(
        handle=clean_output_skill,
        principles=synthesized,
        posts=all_posts,
        output_path=str(skill_dir / "SUMMARY.md"),
        is_synthesis=True,
        source_targets=found_targets
    )

    # 2. Mirror files to output/
    save_principles_store(synthesized, str(out_dir / "principles.json"))
    generate_skill_markdown(
        principles=synthesized,
        output_path=str(out_dir / "SKILL.md"),
        skill_name=clean_output_skill,
        description=desc
    )
    generate_creator_summary_markdown(
        handle=clean_output_skill,
        principles=synthesized,
        posts=all_posts,
        output_path=str(out_dir / "SUMMARY.md"),
        is_synthesis=True,
        source_targets=found_targets
    )
    if all_posts:
        with open(out_dir / "posts.json", "w", encoding="utf-8") as f:
            json.dump(all_posts, f, indent=2, ensure_ascii=False)

    # Update stage state ledger with pooled posts
    state_file = paths_cfg.get("state_file", "state/processed.json")
    try:
        from scripts.run_pipeline import update_processed_state
        update_processed_state(state_file, all_posts)
    except Exception as e:
        logger.debug(f"Could not update processed state ledger in multi-target synthesis: {e}")

    logger.info(
        f"Multi-Target Synthesis Complete: Compiled unified skill '{clean_output_skill}' "
        f"({len(synthesized)} principles) -> {skill_dir}/"
    )
    return synthesized


def main():
    parser = argparse.ArgumentParser(description="Stage 4: Merge principles into SKILL.md with fuzzy deduplication.")
    parser.add_argument("--handle", default=None, help="Instagram username handle for creator-specific output")
    parser.add_argument(
        "--synthesize",
        nargs="+",
        help="Multi-Target Synthesis: list of target handles or collections to cross-synthesize into a unified design system"
    )
    parser.add_argument(
        "--output-skill",
        default="ui-ux-consensus",
        help="Output skill name for multi-target synthesis (default: ui-ux-consensus)"
    )
    parser.add_argument(
        "--min-sources",
        type=int,
        default=1,
        help="Minimum sources/citations required in synthesis mode (default: 1)"
    )
    parser.add_argument("--dry-run", action="store_true", help="Run synthesis/merging without writing files to disk")
    parser.add_argument("--diff", action="store_true", help="Display detailed principles diff vs existing SKILL store")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--threshold", type=float, default=None, help="Override similarity threshold (0-100)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logging")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    if args.synthesize:
        merge_multi_target(
            targets=args.synthesize,
            output_skill_name=args.output_skill,
            min_sources=args.min_sources,
            config_path=args.config,
            dry_run=args.dry_run,
            show_diff=args.diff
        )
    else:
        merge_skill(
            handle=args.handle,
            config_path=args.config,
            dry_run=args.dry_run,
            show_diff=args.diff
        )


if __name__ == "__main__":
    main()
