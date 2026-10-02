---
name: social-media-post-improvement
description: "Actionable UI/UX design heuristics distilled from social-media-post-improvement."
---

# UI/UX Design System & Heuristics

Actionable, production-grade UI/UX design heuristics synthesized from leading design engineers and creators.
Reference these principles when architecting screens, refining typographic rhythm, calibrating negative space, or conducting design reviews.

## Pre-Flight UI/UX Audit Checklist

Before finalizing any interface layout or component hierarchy, audit against these verified fundamentals:

- [ ] **Platform-Native Overlay Safe Zones**: Position all critical on-screen text and key visual elements strictly within safe zones that remain completely clear of native platform interactive overlays, such as like, comment, share, and profile buttons.
- [ ] **Frame-Accurate Kinetic Typography Synchronization**: Synchronize kinetic text animations to trigger precisely on the exact frame of the corresponding spoken word or audio beat, avoiding loose approximations.
- [ ] **Spatial Consistency**: Are margins, gutters, and inner paddings adhering strictly to the 8-point spatial grid?
- [ ] **Visual Separation**: Are cards and structural containers separated primarily via intentional negative space rather than heavy divider borders?
- [ ] **Typographic Anchor**: Is body and title text left-aligned to establish a single vertical scanning anchor rather than centered jagged lines?
- [ ] **Action Hierarchy**: Is there exactly one primary CTA above the fold, using explicit verb-noun copywriting ('Create Project', not 'Submit')?
- [ ] **Safe Touch Targets**: Do interactive touch elements meet the minimum 44×44pt mobile bounding box?

## Parametric Design Tokens

> _Baseline system tokens (8-point spatial grid, WCAG targets) calibrated alongside extracted creator constraints:_ 

| System Token | Standard Value | Practical Application |
|---|---|---|
| **Base Grid** | `8px` (`0.5rem`) | Micro adjustments use `4px` half-steps; macro layout uses `16px`, `24px`, `32px`, `48px`, `64px`. |
| **Card Padding** | `16px` (compact) / `24px` (comfortable) | Uniform internal breathing room for content containers. |
| **Touch Target** | Minimum `44×44px` (mobile), `32×32px` (desktop) | Prevents missed taps and motor strain on touchscreens. |
| **Border Radius** | `4px` (inputs/tags), `8px` (buttons), `16px` (cards/modals), `9999px` (capsules) | Smooth corner curvature matching container scale. |
| **Hairline Borders** | `1px solid rgba(255, 255, 255, 0.08)` (Dark) / `rgba(0, 0, 0, 0.08)` (Light) | Subtle surface elevation without visual heavy lines. |
| **Typography Scale** | Headline `24–32px` (1.2 lh), Body `14–16px` (1.5 lh), Caption `12–13px` (1.4 lh) | Legible reading hierarchy with optical line-height balance. |

## Distilled Design Principles by Domain

### Motion

#### Frame-Accurate Kinetic Typography Synchronization
- **Do this**: Synchronize kinetic text animations to trigger precisely on the exact frame of the corresponding spoken word or audio beat, avoiding loose approximations.
- **Why it matters**: Tight alignment between auditory and visual stimuli reduces cognitive processing lag, enhances reading comprehension, and creates a highly polished, immersive user experience.
- **Implementation Pattern**:
  - **Avoid**: Captions appearing with a loose delay after the speaker says a word, causing a jarring visual lag.
  - **Do This**: Captions rendering instantly on the exact frame the audio waveform peaks for each spoken word.
- **Status**: Single-Source Guideline (@daily.techtalks)
- **Sources**: 1 citation(s) (latest: 2026-08-28) — [@daily.techtalks](https://www.instagram.com/p/Dclzj_DRDUq/)

### Layout

#### Platform-Native Overlay Safe Zones
- **Do this**: Position all critical on-screen text and key visual elements strictly within safe zones that remain completely clear of native platform interactive overlays, such as like, comment, share, and profile buttons.
- **Why it matters**: Placing essential content beneath interactive platform elements causes visual clutter, renders text unreadable, and leads to accidental triggers of platform actions when users attempt to read or interact with the content.
- **Implementation Pattern**:
  - **Avoid**: Placing captions in the bottom-right corner of a vertical video where they are obscured by the Instagram 'Like' and 'Comment' icons.
  - **Do This**: Centering captions in the lower-middle third of the screen, leaving the right-hand margin and bottom edge completely clear of text.
- **Status**: Single-Source Guideline (@daily.techtalks)
- **Sources**: 1 citation(s) (latest: 2026-08-28) — [@daily.techtalks](https://www.instagram.com/p/Dclzj_DRDUq/)
