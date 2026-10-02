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


def test_classify_paths_list():
    """Verify that classify_single_post outputs both path and paths list."""
    config = load_config(str(_ROOT / "config.yaml"))
    min_words = config.get("classify", {}).get("min_caption_words", 40)
    keywords = config.get("classify", {}).get("keywords", [])

    rich_caption = (
        "Here are spacing rules and typography guidelines for responsive cards with good accessibility. "
        "Always ensure sufficient contrast and hierarchy between headline and body text across all layouts."
    )
    # Video with rich caption -> both audio and caption in paths
    res_video_rich = classify_single_post({"caption": rich_caption, "is_video": True}, min_words=min_words, keywords=keywords)
    assert "audio" in res_video_rich["paths"]
    assert "caption" in res_video_rich["paths"]

    # Video with short caption -> only audio in paths
    res_video_short = classify_single_post({"caption": "Short caption", "is_video": True}, min_words=min_words, keywords=keywords)
    assert res_video_short["paths"] == ["audio"]


def test_centroid_clustering_and_variants(tmp_path):
    """Verify cluster_and_synthesize_principles uses centroids and preserves alternate variants."""
    from scripts.merge_skill import cluster_and_synthesize_principles, generate_skill_markdown

    principles = [
        {
            "principle": "Debounce Interactive Buttons",
            "category": "motion",
            "rule": "Disable action button triggers immediately on first tap.",
            "why": "Prevents accidental duplicate orders and form submissions.",
            "example": "Before: Button stays active. After: Button is disabled on click.",
            "confidence": "high",
            "sources": [{"handle": "creator1", "url": "https://instagram.com/p/1"}]
        },
        {
            "principle": "Debounce Interactive Buttons",
            "category": "motion",
            "rule": "Gate form submissions behind an immediate visual loading state.",
            "why": "Stops duplicate API requests and network spam.",
            "example": "Before: Rapid taps trigger multiple requests. After: Loading spinner activates.",
            "confidence": "medium",
            "sources": [{"handle": "creator2", "url": "https://instagram.com/p/2"}]
        }
    ]

    synthesized = cluster_and_synthesize_principles(principles)
    assert len(synthesized) == 1
    canonical = synthesized[0]
    assert canonical["confidence"] == "high"
    assert len(canonical["sources"]) == 2
    assert "variants" in canonical
    assert len(canonical["variants"]) == 1
    assert "Gate form submissions" in canonical["variants"][0]["rule"]

    # Verify rendering in SKILL.md
    out_file = tmp_path / "VARIANTS_SKILL.md"
    generate_skill_markdown(synthesized, str(out_file))
    content = out_file.read_text(encoding="utf-8")
    assert "- **Alternate Creator Perspectives & Implementations**:" in content
    assert "Gate form submissions" in content


def test_cross_category_guard():
    """Verify that non-whitelisted cross-category pairs are strictly rejected from clustering."""
    from scripts.merge_skill import cluster_and_synthesize_principles

    # Color and Spacing are NOT in ALLOWED_CROSS_CATEGORY_PAIRS
    color_p = {
        "principle": "High Contrast Ratio",
        "category": "color",
        "rule": "Maintain high contrast ratio between foreground and background.",
        "why": "Ensures readable text.",
        "example": "4.5:1 ratio",
        "confidence": "high",
        "sources": [{"handle": "c1", "url": "https://instagram.com/p/1"}]
    }
    spacing_p = {
        "principle": "High Contrast Ratio",
        "category": "spacing",
        "rule": "Maintain high contrast ratio between foreground and background.",
        "why": "Ensures readable text.",
        "example": "4.5:1 ratio",
        "confidence": "high",
        "sources": [{"handle": "c2", "url": "https://instagram.com/p/2"}]
    }

    synthesized = cluster_and_synthesize_principles([color_p, spacing_p])
    # Must NOT merge across forbidden categories despite identical wording
    assert len(synthesized) == 2


def test_instructive_directive_markdown_rendering(tmp_path):
    """Verify that SKILL.md and SUMMARY.md render instructive fields (When to apply, Do this, Don't do this)."""
    from scripts.merge_skill import generate_skill_markdown, generate_creator_summary_markdown

    principle = {
        "principle": "Predictable Primary Action Hierarchy",
        "category": "layout",
        "rule": "Maintain exactly one high-contrast primary CTA above the fold per view.",
        "do_this": "Anchor the primary CTA in the bottom-right or top-right visual scanning path.",
        "dont_do_this": "Place multiple competing high-saturation buttons in the same container.",
        "trigger_context": "Designing conversion-critical screens or modal confirmations.",
        "why": "Prevents decision paralysis by creating an unambiguous visual path.",
        "example": "Before: Side-by-side solid 'Save' and solid 'Cancel' buttons. After: Solid 'Save' paired with a ghost/text 'Cancel' button.",
        "confidence": "high",
        "sources": [{"handle": "design_lead", "url": "https://instagram.com/p/test123"}]
    }

    skill_file = tmp_path / "INSTRUCTIVE_SKILL.md"
    generate_skill_markdown([principle], str(skill_file), skill_name="instructive-test")
    skill_content = skill_file.read_text(encoding="utf-8")

    assert "- **When to apply**: Designing conversion-critical screens" in skill_content
    assert "- **Do this**: Anchor the primary CTA" in skill_content
    assert "- **Don't do this**: Place multiple competing high-saturation buttons" in skill_content
    assert "- **Why it matters**: Prevents decision paralysis" in skill_content
    assert "- **Implementation Pattern**:" in skill_content
    assert "- **Avoid**: Side-by-side solid" in skill_content
    assert "- **Do This**: Solid 'Save' paired with a ghost" in skill_content

    summary_file = tmp_path / "INSTRUCTIVE_SUMMARY.md"
    generate_creator_summary_markdown("design_lead", [principle], [], str(summary_file))
    summary_content = summary_file.read_text(encoding="utf-8")

    assert "- **Trigger Scenario**: Designing conversion-critical screens" in summary_content
    assert "- **Guideline**: Anchor the primary CTA" in summary_content
    assert "- **Avoid (Anti-Pattern)**: Place multiple competing" in summary_content
    assert "- **Rationale**: Prevents decision paralysis" in summary_content


def test_embedding_cache_disk_persistence(tmp_path, monkeypatch):
    """Verify that embedding cache reads and writes to disk seamlessly."""
    import scripts.merge_skill as ms

    test_cache_file = tmp_path / "cache" / "embeddings.json"
    monkeypatch.setattr(ms, "EMBEDDINGS_CACHE_FILE", test_cache_file)
    monkeypatch.setattr(ms, "CACHE_DIR", tmp_path / "cache")

    # Initial state -> empty cache
    assert ms.load_embedding_cache() == {}

    # Save dummy embeddings
    dummy_data = {
        "key1": [0.1, 0.2, 0.3],
        "key2": [-0.5, 0.0, 0.5]
    }
    ms.save_embedding_cache(dummy_data)
    assert test_cache_file.exists()

    # Reload and verify
    reloaded = ms.load_embedding_cache()
    assert reloaded == dummy_data


def test_multi_target_synthesis(tmp_path):
    """Verify pooling, deduplication, and cross-creator synthesis across multiple targets."""
    import json
    import yaml
    from scripts.merge_skill import merge_multi_target

    output_dir = tmp_path / "output"
    raw_dir = tmp_path / "data" / "raw"
    skills_dir = tmp_path / "skills"
    output_dir.mkdir(parents=True)
    raw_dir.mkdir(parents=True)
    skills_dir.mkdir(parents=True)

    config_data = {
        "instagram": {},
        "classify": {},
        "transcription": {},
        "extraction": {"categories": ["typography", "color", "layout", "accessibility", "spacing"]},
        "merge": {"dedup_similarity_threshold": 80.0},
        "paths": {
            "output_dir": str(output_dir),
            "raw_data_dir": str(raw_dir),
            "skills_dir": str(skills_dir)
        }
    }
    cfg_file = tmp_path / "config.yaml"
    with open(cfg_file, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f)

    # Target 1: creator_a with an 8pt spacing principle
    dir_a = output_dir / "creator_a"
    dir_a.mkdir()
    posts_a = [{
        "post_id": "1001",
        "shortcode": "CODE_A1",
        "date": "2026-09-01",
        "is_video": False,
        "like_count": 500,
        "principles": [{
            "principle": "8pt Spatial Grid System",
            "category": "layout",
            "rule": "Use strict 8pt grid increments for inner padding and margins.",
            "do_this": "Enforce 8px, 16px, 24px spacing.",
            "dont_do_this": "Use arbitrary 11px or 13px padding.",
            "trigger_context": "Container spacing",
            "why": "Ensures visual harmony.",
            "example": "Before: 13px padding. After: 16px padding.",
            "confidence": "high",
            "sources": [{"handle": "creator_a", "url": "https://instagram.com/p/CODE_A1/"}]
        }]
    }]
    with open(dir_a / "posts.json", "w", encoding="utf-8") as f:
        json.dump(posts_a, f)

    # Target 2: creator_b with a near-identical 8pt principle AND an accessibility principle
    dir_b = output_dir / "creator_b"
    dir_b.mkdir()
    posts_b = [{
        "post_id": "2001",
        "shortcode": "CODE_B1",
        "date": "2026-09-02",
        "is_video": True,
        "like_count": 1200,
        "principles": [
            {
                "principle": "8pt Grid Spatial Rhythm",
                "category": "layout",
                "rule": "Use strict 8pt grid increments for inner padding and layout margins.",
                "do_this": "Apply 8, 16, 24, 32 spatial tokens.",
                "dont_do_this": "Use uneven odd margins.",
                "trigger_context": "Component layout",
                "why": "Guarantees cross-screen consistency.",
                "example": "Before: 9px margin. After: 16px margin.",
                "confidence": "high",
                "sources": [{"handle": "creator_b", "url": "https://instagram.com/p/CODE_B1/"}]
            },
            {
                "principle": "Accessible Minimum Touch Target",
                "category": "accessibility",
                "rule": "Provide minimum 44x44pt bounding boxes for mobile touch targets.",
                "do_this": "Add touch hit slop of at least 44pt.",
                "dont_do_this": "Make buttons smaller than 44pt without hit expansion.",
                "trigger_context": "Mobile interactive components",
                "why": "Prevents mistaps per WCAG 2.2 AA.",
                "example": "Before: 28px icon button. After: 44px container padding.",
                "confidence": "high",
                "sources": [{"handle": "creator_b", "url": "https://instagram.com/p/CODE_B2/"}]
            }
        ]
    }]
    with open(dir_b / "posts.json", "w", encoding="utf-8") as f:
        json.dump(posts_b, f)

    # Run synthesis with min_sources=1 (should yield 2 principles: 1 merged layout + 1 accessibility)
    synth = merge_multi_target(
        targets=["creator_a", "creator_b"],
        output_skill_name="flagship-ui",
        min_sources=1,
        config_path=str(cfg_file)
    )
    assert len(synth) == 2

    # Verify that the layout principle merged sources and has consensus from both creators
    layout_p = next(p for p in synth if p.get("category") == "layout")
    assert len(layout_p.get("sources", [])) == 2
    handles = {s.get("handle") for s in layout_p.get("sources", [])}
    assert "creator_a" in handles
    assert "creator_b" in handles

    # Verify output skill files were generated
    skill_dir = skills_dir / "flagship-ui"
    assert (skill_dir / "SKILL.md").exists()
    assert (skill_dir / "SUMMARY.md").exists()
    assert (skill_dir / "principles.json").exists()

    skill_md = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    assert "Multi-Source Consensus (Validated across 2 creators: @creator_a, @creator_b)" in skill_md
    assert "- **When to apply**:" in skill_md
    assert "- **Do this**:" in skill_md
    assert "- **Don't do this**:" in skill_md

    summary_md = (skill_dir / "SUMMARY.md").read_text(encoding="utf-8")
    assert "Cross-Creator Design Skill Synthesis Report: flagship-ui" in summary_md
    assert "Contributing Target Count" in summary_md

    # Now test min_sources=2 filter (only the consensus principle should survive)
    synth_strict = merge_multi_target(
        targets=["creator_a", "creator_b"],
        output_skill_name="strict-consensus",
        min_sources=2,
        config_path=str(cfg_file)
    )
    assert len(synth_strict) == 1
    assert synth_strict[0].get("category") == "layout"


def test_quality_score_calculation_and_sorting():
    """Verify compute_quality_score weights directives, sources, and confidence, and sorts principles descending."""
    from scripts.merge_skill import compute_quality_score, cluster_and_synthesize_principles

    high_quality_p = {
        "principle": "High Quality Guideline",
        "category": "layout",
        "rule": "Enforce high quality.",
        "do_this": "Do exact positive action",
        "dont_do_this": "Avoid anti pattern",
        "trigger_context": "Layout design",
        "why": "Clear rationale",
        "example": "Before: Old. After: New.",
        "confidence": "high",
        "sources": [{"handle": "c1"}, {"handle": "c2"}, {"handle": "c3"}]
    }

    low_quality_p = {
        "principle": "Bare Guideline",
        "category": "layout",
        "rule": "Basic rule.",
        "confidence": "medium",
        "sources": [{"handle": "c1"}]
    }

    score_high = compute_quality_score(high_quality_p)
    score_low = compute_quality_score(low_quality_p)

    assert score_high > score_low
    assert score_high >= 110.0  # 30 (trigger) + 20 (dont) + 15 (do) + 30 (sources) + 20 (high conf) + 5 (ex)

    synthesized = cluster_and_synthesize_principles([low_quality_p, high_quality_p])
    assert synthesized[0]["principle"] == "High Quality Guideline"
    assert synthesized[0]["quality_score"] == score_high


def test_principles_diff_computation():
    """Verify compute_principles_diff detects added, modified, and removed principles."""
    from scripts.merge_skill import compute_principles_diff, format_diff_summary

    old_list = [
        {"principle": "Retained Rule", "category": "layout", "sources": [{"handle": "c1"}]},
        {"principle": "Obsolete Rule", "category": "color", "sources": [{"handle": "c1"}]}
    ]

    new_list = [
        {"principle": "Retained Rule", "category": "layout", "do_this": "Updated action", "sources": [{"handle": "c1"}, {"handle": "c2"}]},
        {"principle": "Fresh Rule", "category": "motion", "sources": [{"handle": "c2"}], "quality_score": 85.0}
    ]

    diff = compute_principles_diff(old_list, new_list)
    assert len(diff["added"]) == 1
    assert diff["added"][0]["principle"] == "Fresh Rule"
    assert len(diff["modified"]) == 1
    assert diff["modified"][0]["principle"]["principle"] == "Retained Rule"
    assert len(diff["removed"]) == 1
    assert diff["removed"][0]["principle"] == "Obsolete Rule"

    formatted = format_diff_summary(diff, "test-target")
    assert "+ Added: Fresh Rule" in formatted
    assert "~ Modified: Retained Rule" in formatted
    assert "- Removed: Obsolete Rule" in formatted


def test_custom_allowed_cross_category_pairs_from_config():
    """Verify loading allowed_cross_category_pairs from config overrides defaults."""
    from scripts.merge_skill import get_allowed_cross_category_pairs, cluster_and_synthesize_principles

    custom_cfg = {
        "merge": {
            "allowed_cross_category_pairs": [
                ["spacing", "typography"]
            ]
        }
    }

    pairs = get_allowed_cross_category_pairs(custom_cfg)
    assert frozenset({"spacing", "typography"}) in pairs
    assert frozenset({"layout", "spacing"}) not in pairs

    spacing_p = {
        "principle": "Consistent Line Spacing",
        "category": "spacing",
        "rule": "Maintain 1.5 line height for body paragraphs.",
        "confidence": "high",
        "sources": [{"handle": "c1"}]
    }

    typo_p = {
        "principle": "Consistent Line Spacing",
        "category": "typography",
        "rule": "Maintain 1.5 line height for body paragraphs.",
        "confidence": "high",
        "sources": [{"handle": "c2"}]
    }

    synthesized = cluster_and_synthesize_principles([spacing_p, typo_p], config=custom_cfg)
    # Since spacing ↔ typography is in custom config, they should cluster into 1 canonical principle!
    assert len(synthesized) == 1
    assert len(synthesized[0]["sources"]) == 2


def test_dry_run_mode(tmp_path):
    """Verify that --dry-run computes synthesis and diff without writing files to disk."""
    import json
    import yaml
    from scripts.merge_skill import merge_multi_target

    output_dir = tmp_path / "output"
    raw_dir = tmp_path / "data" / "raw"
    skills_dir = tmp_path / "skills"
    output_dir.mkdir(parents=True)
    raw_dir.mkdir(parents=True)
    skills_dir.mkdir(parents=True)

    config_data = {
        "merge": {"dedup_similarity_threshold": 80.0},
        "paths": {
            "output_dir": str(output_dir),
            "raw_data_dir": str(raw_dir),
            "skills_dir": str(skills_dir)
        }
    }
    cfg_file = tmp_path / "config.yaml"
    with open(cfg_file, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f)

    dir_a = output_dir / "creator_dry"
    dir_a.mkdir()
    posts_a = [{
        "post_id": "9001",
        "shortcode": "DRY_1",
        "principles": [{
            "principle": "Dry Run Spatial Rule",
            "category": "layout",
            "rule": "Use 8pt grid.",
            "confidence": "high",
            "sources": [{"handle": "creator_dry"}]
        }]
    }]
    with open(dir_a / "posts.json", "w", encoding="utf-8") as f:
        json.dump(posts_a, f)

    synth_dry = merge_multi_target(
        targets=["creator_dry"],
        output_skill_name="dry-skill",
        config_path=str(cfg_file),
        dry_run=True,
        show_diff=True
    )

    assert len(synth_dry) == 1
    # Verify NO files were created under skills/dry-skill or output/dry-skill
    assert not (skills_dir / "dry-skill").exists()
    assert not (output_dir / "dry-skill").exists()






