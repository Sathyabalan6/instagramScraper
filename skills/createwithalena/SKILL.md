---
name: createwithalena
description: "Actionable UI/UX design heuristics distilled from createwithalena."
---

# UI/UX Design System & Heuristics

Actionable, production-grade UI/UX design heuristics synthesized from leading design engineers and creators.
Reference these principles when architecting screens, refining typographic rhythm, calibrating negative space, or conducting design reviews.

## Pre-Flight UI/UX Audit Checklist

Before finalizing any interface layout or component hierarchy, audit against these verified fundamentals:

- [ ] **Earthy Olive and Tomato Red Contrast**: Pair muted olive green backgrounds or structural elements with high-saturation tomato red accents for focal elements.
- [ ] **Espresso and Baby Pink Palette Pairing**: Combine deep espresso brown neutrals with soft, desaturated baby pink for balanced surface-to-content contrast.
- [ ] **Bright Yellow and Royal Blue Complementary Pairing**: Pair high-luminance bright yellow alongside deep royal blue to maximize chromatic contrast and visual impact.

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

### Color

#### Bright Yellow and Royal Blue Complementary Pairing
- **Do this**: Pair high-luminance bright yellow alongside deep royal blue to maximize chromatic contrast and visual impact.
- **Why it matters**: Leverages opposing chromatic temperatures and extreme value differences to create energetic, highly memorable focal zones.
- **Implementation Pattern**: Highlighting key notification badges in bright yellow against a solid royal blue navigation bar.
- **Status**: Single-Source Guideline (@createwithalena)
- **Sources**: 1 citation(s) (latest: 2026-08-18) — [@createwithalena](https://www.instagram.com/p/DcLuspGxuR0/)

#### Earthy Olive and Tomato Red Contrast
- **Do this**: Pair muted olive green backgrounds or structural elements with high-saturation tomato red accents for focal elements.
- **Why it matters**: Balances a grounded, natural neutral tone with a vibrant, high-attention chromatic pop to direct user focus effectively.
- **Implementation Pattern**: Using an olive green interface background with tomato red primary CTA buttons.
- **Status**: Single-Source Guideline (@createwithalena)
- **Sources**: 1 citation(s) (latest: 2026-08-18) — [@createwithalena](https://www.instagram.com/p/DcLuspGxuR0/)

#### Espresso and Baby Pink Palette Pairing
- **Do this**: Combine deep espresso brown neutrals with soft, desaturated baby pink for balanced surface-to-content contrast.
- **Why it matters**: Provides a high-contrast dark foundation while utilizing a delicate pastel accent to maintain visual softness and legibility.
- **Implementation Pattern**: Applying an espresso brown container background with baby pink typography or badge elements.
- **Status**: Single-Source Guideline (@createwithalena)
- **Sources**: 1 citation(s) (latest: 2026-08-18) — [@createwithalena](https://www.instagram.com/p/DcLuspGxuR0/)
