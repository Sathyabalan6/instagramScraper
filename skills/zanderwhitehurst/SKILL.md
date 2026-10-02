---
name: zanderwhitehurst
description: "Actionable UI/UX design heuristics distilled from zanderwhitehurst."
---

# UI/UX Design System & Heuristics

Actionable, production-grade UI/UX design heuristics synthesized from leading design engineers and creators.
Reference these principles when architecting screens, refining typographic rhythm, calibrating negative space, or conducting design reviews.

## Pre-Flight UI/UX Audit Checklist

Before finalizing any interface layout or component hierarchy, audit against these verified fundamentals:

- [ ] **Confirmation Modal Structure and Text Alignment**: Organize confirmation modals into three distinct content blocks with left-aligned text to optimize scannability and readability?
- [ ] **Action-Oriented Modal Copywriting**: Replace vague interrogative titles with a direct verb-noun pairing (e.g., 'Delete folder') and clarify consequences using concise factual statements?
- [ ] **Modal Action Button Labeling and Hierarchy**: Implement exactly two distinct actions using uncapitalized simple verb text for the primary confirm button and 'Cancel' for the secondary action?
- [ ] **Left-Aligned Typography for Single Alignment Anchors**: Left-align multi-line blocks of text and UI elements to establish a single vertical alignment anchor instead of using center-aligned text?
- [ ] **Whitespace Over Line Borders for Layout Separation**: Eliminate structural border lines between content containers and rely exclusively on negative space to establish grouping and hierarchy?

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

### Typography

#### Action-Oriented Modal Copywriting
- **Rule**: Replace vague interrogative titles with a direct verb-noun pairing (e.g., 'Delete folder') and clarify consequences using concise factual statements.
- **Rationale**: Explicit verb-noun headings and direct statements eliminate ambiguity about the exact system state change and its irreversibility.
- **Implementation Pattern**: Changing a modal header from 'Are you sure?' to 'Delete folder' accompanied by a subtext stating 'This action is irreversible.'
- **Status**: Single-Source Guideline (@zanderwhitehurst)
- **Sources**: 1 citation(s) (latest: 2024-09-23) — [@zanderwhitehurst](https://www.instagram.com/p/DAQf2QEAT7Z/)

### Hierarchy

#### Modal Action Button Labeling and Hierarchy
- **Rule**: Implement exactly two distinct actions using uncapitalized simple verb text for the primary confirm button and 'Cancel' for the secondary action.
- **Rationale**: Clear, standard button labels reduce cognitive load and prevent accidental destructive inputs by establishing unambiguous pathways to proceed or abort.
- **Implementation Pattern**: A button group featuring a solid-fill primary button labeled 'delete' next to an outline or ghost secondary button labeled 'cancel'.
- **Status**: Single-Source Guideline (@zanderwhitehurst)
- **Sources**: 1 citation(s) (latest: 2024-09-23) — [@zanderwhitehurst](https://www.instagram.com/p/DAQf2QEAT7Z/)

### Layout

#### Confirmation Modal Structure and Text Alignment
- **Rule**: Organize confirmation modals into three distinct content blocks with left-aligned text to optimize scannability and readability.
- **Rationale**: Left-aligned text patterns align with natural reading habits, allowing users to process critical warning and action details faster than centered layouts.
- **Implementation Pattern**: A deletion warning modal structured with a top header containing a close icon, a left-aligned body containing a concise warning, and a bottom row for primary and secondary actions.
- **Status**: Single-Source Guideline (@zanderwhitehurst)
- **Sources**: 1 citation(s) (latest: 2024-09-23) — [@zanderwhitehurst](https://www.instagram.com/p/DAQf2QEAT7Z/)

#### Left-Aligned Typography for Single Alignment Anchors
- **Rule**: Left-align multi-line blocks of text and UI elements to establish a single vertical alignment anchor instead of using center-aligned text.
- **Rationale**: Center-aligned text creates multiple shifting alignment anchors across lines, forcing the user's eye to jump horizontally and increasing cognitive load during reading.
- **Implementation Pattern**: A product card featuring a center-aligned title, description, and price is updated to have all text elements left-aligned to a single vertical margin.
- **Status**: Single-Source Guideline (@zanderwhitehurst)
- **Sources**: 1 citation(s) (latest: 2026-08-19) — [@zanderwhitehurst](https://www.instagram.com/p/DcN2nJEu9L2/)

#### Whitespace Over Line Borders for Layout Separation
- **Rule**: Eliminate structural border lines between content containers and rely exclusively on negative space to establish grouping and hierarchy.
- **Rationale**: Removing visual clutter prevents interfaces from looking overly dense or resembling spreadsheets, reducing cognitive load and improving scannability.
- **Implementation Pattern**: Replacing card component borders and internal divider lines with uniform padding and generous margins.
- **Status**: Single-Source Guideline (@zanderwhitehurst)
- **Sources**: 1 citation(s) (latest: 2026-07-21) — [@zanderwhitehurst](https://www.instagram.com/p/DbDaptQscRR/)
