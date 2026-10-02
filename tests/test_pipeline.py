"""
Unit and integration tests for the IG Design-Skill Extractor pipeline.
Validates configuration integrity, classification heuristics, deduplication,
FastAPI web endpoints, and safety constraints.
"""

import os
import sys
from pathlib import Path
import asyncio
import pytest

# Ensure root is in sys.path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import app
from scripts.classify_posts import classify_single_post, load_config
from scripts.merge_skill import find_matching_principle, merge_principles_list


def test_config_structure():
    """Verify config.yaml contains all required pipeline sections and categories."""
    config = load_config(str(_ROOT / "config.yaml"))
    assert "instagram" in config
    assert "classify" in config
    assert "transcription" in config
    assert "extraction" in config
    assert "merge" in config
    assert "paths" in config

    # Required categories
    categories = config["extraction"]["categories"]
    assert "typography" in categories
    assert "color" in categories
    assert "layout" in categories
    assert "accessibility" in categories


def test_classify_heuristic():
    """Test caption-vs-audio classification heuristic."""
    config = load_config(str(_ROOT / "config.yaml"))
    min_words = config.get("classify", {}).get("min_caption_words", 40)
    keywords = config.get("classify", {}).get("keywords", [])

    # Caption with design keywords and sufficient length -> caption path
    rich_caption = (
        "Here are 3 typography and spacing rules for UI cards. Always ensure sufficient contrast "
        "and hierarchy between headline and body text. Use an 8pt grid for consistent padding, "
        "margins, and alignment across all responsive breakpoints for better accessibility and ux."
    )
    caption_post = {
        "caption": rich_caption,
        "is_video": False
    }
    res_caption = classify_single_post(caption_post, min_words=min_words, keywords=keywords)
    assert res_caption["path"] == "caption"
    assert res_caption["has_rich_caption"] is True
    assert res_caption["has_substance"] is True
    assert "typography" in res_caption["matched_keywords"]
    assert "spacing" in res_caption["reason"]

    # Video post with short caption -> audio path
    video_post = {
        "caption": "New UI design tips! Link in bio. #design",
        "is_video": True
    }
    res_video = classify_single_post(video_post, min_words=min_words, keywords=keywords)
    assert res_video["path"] == "audio"
    assert res_video["has_rich_caption"] is False

    # Video post with rich caption -> audio path with has_rich_caption True
    video_rich_post = {
        "caption": rich_caption,
        "is_video": True
    }
    res_video_rich = classify_single_post(video_rich_post, min_words=min_words, keywords=keywords)
    assert res_video_rich["path"] == "audio"
    assert res_video_rich["has_rich_caption"] is True
    assert res_video_rich["has_substance"] is True


def test_deduplication_same_category():
    """Test fuzzy deduplication on matching principles within the same category."""
    existing = [
        {
            "principle": "Action-Oriented Modal Copywriting",
            "category": "typography",
            "rule": "Replace vague interrogative titles with a direct verb-noun pairing.",
            "why": "Eliminates ambiguity about system state.",
            "example": "Change 'Are you sure?' to 'Delete folder'.",
            "confidence": "medium",
            "sources": [{"handle": "creator1", "url": "https://instagram.com/p/1"}]
        }
    ]

    new_p = {
        "principle": "Action Oriented Modal Copywriting",
        "category": "typography",
        "rule": "Use direct verb-noun titles for confirmation modals instead of vague questions.",
        "why": "Clear verb-noun titles remove confusion on irreversible actions.",
        "example": "Delete folder modal",
        "confidence": "high",
        "sources": [{"handle": "creator2", "url": "https://instagram.com/p/2"}]
    }

    match_idx, match_type = find_matching_principle(new_p, existing, threshold=80.0)
    assert match_idx == 0
    assert match_type == "same_category"


def test_merge_skill_confidence_upgrade():
    """Test that merging a duplicate principle upgrades confidence and combines sources."""
    existing = [
        {
            "principle": "High Contrast Button Hierarchy",
            "category": "hierarchy",
            "rule": "Use solid filled buttons for primary actions and ghost buttons for secondary.",
            "why": "Guides visual attention directly to the primary action.",
            "example": "Save vs Cancel",
            "confidence": "low",
            "sources": [{"handle": "creator_a", "url": "https://instagram.com/p/a"}]
        }
    ]

    incoming = [
        {
            "principle": "High Contrast Button Hierarchy",
            "category": "hierarchy",
            "rule": "Use solid filled buttons for primary actions and ghost buttons for secondary.",
            "why": "Guides visual attention directly to the primary action.",
            "example": "Save vs Cancel",
            "confidence": "high",
            "sources": [{"handle": "creator_b", "url": "https://instagram.com/p/b"}]
        }
    ]

    merged = merge_principles_list(incoming, existing, threshold=85.0)
    assert len(merged) == 1
    # Confidence upgraded from low -> high
    assert merged[0]["confidence"] == "high"
    # Both sources preserved
    assert len(merged[0]["sources"]) == 2


def test_web_studio_dashboard_route():
    """Test that the Apple HIG web dashboard renders successfully."""
    response = asyncio.run(app.serve_dashboard())
    assert response.status_code == 200
    html_text = response.body.decode("utf-8")
    assert "Design Skill Studio" in html_text
    assert "Apple SF Pro typography" in html_text


def test_web_studio_api_status():
    """Test the API status health diagnostic endpoint."""
    data = asyncio.run(app.api_status())
    assert isinstance(data, dict)
    assert "cookies" in data
    assert "llm" in data
    assert "targets" in data


def test_web_studio_api_principles():
    """Test fetching distilled principles."""
    data = asyncio.run(app.get_principles(target="global"))
    assert isinstance(data, dict)
    assert "principles" in data
    assert "total" in data


def test_safety_constraints():
    """Ensure AGENTS.md Hard Rule 1: No persistent audio/video files remain."""
    tmp_audio = _ROOT / "data/tmp_audio"
    if tmp_audio.exists():
        files = list(tmp_audio.iterdir())
        assert len(files) == 0, f"data/tmp_audio should be empty, but found: {files}"

    # Verify no .mp4 files exist in data/
    data_dir = _ROOT / "data"
    if data_dir.exists():
        mp4_files = list(data_dir.rglob("*.mp4"))
        assert len(mp4_files) == 0, f"Found persisted video files: {mp4_files}"


def test_resolve_target():
    """Test smart target resolution across handles, URLs, and collections."""
    from scripts.run_pipeline import resolve_target

    # Plain handle
    h, c = resolve_target(target="zanderwhitehurst")
    assert h == "zanderwhitehurst" and c is None

    # Handle with @
    h, c = resolve_target(target="@designcode.io")
    assert h == "designcode.io" and c is None

    # Profile URL
    h, c = resolve_target(target="https://www.instagram.com/lincolndevine/")
    assert h == "lincolndevine" and c is None

    # Saved collection URL
    h, c = resolve_target(target="https://www.instagram.com/creator/saved/checkups/123456/")
    assert h is None and "saved/checkups" in c

    # Explicit collection override
    h, c = resolve_target(collection="my_collection")
    assert h is None and c == "my_collection"


def test_stage_ledger(tmp_path):
    """Test stage ledger migration and incremental stage updates."""
    from scripts.run_pipeline import update_processed_state
    import json

    state_file = tmp_path / "processed.json"

    # Seed with legacy flat list
    with open(state_file, "w") as f:
        json.dump(["1001", "1002"], f)

    # Update with new post objects
    new_posts = [
        {
            "post_id": "1003",
            "shortcode": "AbCdEf",
            "date": "2026-10-01",
            "is_video": True,
            "transcript": "Hello design world",
            "principles": [{"principle": "Rule 1", "category": "layout"}]
        }
    ]
    update_processed_state(str(state_file), new_posts)

    with open(state_file, "r") as f:
        data = json.load(f)

    assert data["version"] == "2.0"
    assert "1001" in data["posts"]
    assert "1003" in data["posts"]
    assert data["posts"]["1003"]["stages"]["transcribed"] is True
    assert data["posts"]["1003"]["stages"]["extracted"] is True


def test_skill_markdown_v2(tmp_path):
    """Test SKILL.md v2 generator produces pre-flight checklist, tokens, and zero emojis."""
    from scripts.merge_skill import generate_skill_markdown

    test_principles = [
        {
            "principle": "Left-Aligned Scanning Anchor",
            "category": "layout",
            "rule": "Left-align multi-line blocks of text to establish a single anchor.",
            "why": "Eliminates visual saccades and cognitive strain.",
            "example": "Before: Centered body text. After: Left-aligned paragraph with 1.5 line height.",
            "confidence": "high",
            "sources": [
                {"handle": "designerA", "url": "https://instagram.com/p/1"},
                {"handle": "designerB", "url": "https://instagram.com/p/2"}
            ]
        }
    ]

    out_file = tmp_path / "SKILL.md"
    generate_skill_markdown(test_principles, str(out_file))

    content = out_file.read_text(encoding="utf-8")

    assert "# UI/UX Design System & Heuristics" in content
    assert "## Pre-Flight UI/UX Audit Checklist" in content
    assert "## Parametric Design Tokens" in content
    assert "Multi-Source Consensus" in content
    assert "⭐" not in content
    assert "🎯" not in content
    assert "- **Avoid**: Centered body text." in content
    assert "- **Do This**: Left-aligned paragraph with 1.5 line height." in content


def test_clean_skill_name():
    """Verify target names are cleaned of collection_ prefixes and @ symbols."""
    from scripts.merge_skill import get_clean_skill_name

    assert get_clean_skill_name("collection_checkups") == "checkups"
    assert get_clean_skill_name("@zanderwhitehurst") == "zanderwhitehurst"
    assert get_clean_skill_name("https://www.instagram.com/sathyabalan6/saved/checkups/1950348122301909/") == "checkups"
    assert get_clean_skill_name("https://www.instagram.com/user/saved/social-media-post-improvement/12345/") == "social-media-post-improvement"
    assert get_clean_skill_name("designcode.io") == "designcode.io"
    assert get_clean_skill_name("") == "ui-ux"


def test_target_skill_folder_creation(tmp_path):
    """Verify merge_skill creates target-isolated folder under skills/<clean_name>/ and NOT global design-ui-ux."""
    from scripts.merge_skill import merge_skill
    import yaml

    # Create dummy config pointing to tmp_path
    cfg_data = {
        "merge": {"dedup_similarity_threshold": 85},
        "paths": {
            "output_dir": str(tmp_path / "output"),
            "raw_data_dir": str(tmp_path / "data/raw"),
            "skills_dir": str(tmp_path / "skills"),
        }
    }
    cfg_path = tmp_path / "config.yaml"
    with open(cfg_path, "w") as f:
        yaml.dump(cfg_data, f)

    test_principles = [
        {
            "principle": "High Contrast Button Hierarchy",
            "category": "hierarchy",
            "rule": "Use solid filled buttons for primary actions.",
            "why": "Guides visual attention directly to the primary action.",
            "example": "Save vs Cancel",
            "confidence": "high",
            "sources": [{"handle": "testcreator", "url": "https://instagram.com/p/test"}]
        }
    ]

    # Test collection target
    merge_skill(handle="collection_checkups", config_path=str(cfg_path), new_principles=test_principles)

    # Verify target skill folder exists in skills/checkups/
    checkups_skill_dir = tmp_path / "skills" / "checkups"
    assert checkups_skill_dir.exists()
    assert (checkups_skill_dir / "SKILL.md").exists()
    assert (checkups_skill_dir / "SUMMARY.md").exists()
    assert (checkups_skill_dir / "principles.json").exists()

    # Verify mirror exists in output/collection_checkups/
    checkups_out_dir = tmp_path / "output" / "collection_checkups"
    assert checkups_out_dir.exists()
    assert (checkups_out_dir / "SKILL.md").exists()

    # Verify global skill directory was NOT created
    global_dir = tmp_path / "skills" / "design-ui-ux"
    assert not global_dir.exists()


def test_enrichment_does_not_overwrite_by_length():
    """Verify that a concise, high-quality rationale is not overwritten by a rambling longer one."""
    existing = [
        {
            "principle": "Left-Aligned Scanning Anchor",
            "category": "layout",
            "rule": "Left-align multi-line blocks of text.",
            "why": "Eliminates visual saccades and cognitive strain.",
            "example": "Left-aligned paragraph",
            "confidence": "high",
            "sources": [{"handle": "creator1", "url": "https://instagram.com/p/1"}]
        }
    ]

    incoming = [
        {
            "principle": "Left-Aligned Scanning Anchor",
            "category": "layout",
            "rule": "Left-align multi-line blocks of text.",
            "why": "This is a much longer and more rambling text that goes on and on without adding any actual value or insight to the design rule.",
            "example": "Left-aligned paragraph",
            "confidence": "high",
            "sources": [{"handle": "creator2", "url": "https://instagram.com/p/2"}]
        }
    ]

    merged = merge_principles_list(incoming, existing, threshold=85.0)
    assert len(merged) == 1
    # Original concise why is preserved, NOT replaced by the longer one
    assert merged[0]["why"] == "Eliminates visual saccades and cognitive strain."


def test_honest_consensus_labeling(tmp_path):
    """Verify honest consensus labels: Multi-Source vs Single-Source."""
    from scripts.merge_skill import generate_skill_markdown

    single_source = [
        {
            "principle": "Single CTA Principle",
            "category": "hierarchy",
            "rule": "Only use one primary CTA.",
            "why": "Prevents decision fatigue.",
            "example": "Primary vs Secondary button",
            "confidence": "high",
            "sources": [{"handle": "creatorA", "url": "https://instagram.com/p/1"}]
        }
    ]

    out_file = tmp_path / "SINGLE_SKILL.md"
    generate_skill_markdown(single_source, str(out_file))
    content = out_file.read_text(encoding="utf-8")

    assert "- **Status**: Single-Source Guideline (@creatorA)" in content
    assert "Multi-Source Consensus" not in content



