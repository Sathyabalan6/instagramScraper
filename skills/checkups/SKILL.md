---
name: checkups
description: "Actionable UI/UX design heuristics distilled from checkups."
---

# UI/UX Design System & Heuristics

Actionable, production-grade UI/UX design heuristics synthesized from leading design engineers and creators.
Reference these principles when architecting screens, refining typographic rhythm, calibrating negative space, or conducting design reviews.

## Pre-Flight UI/UX Audit Checklist

Before finalizing any interface layout or component hierarchy, audit against these verified fundamentals:

- [ ] **Immediate Touch Feedback for Interactive Elements**: Trigger instant visual state changes (like scale or color shifts) on every tap, executing heavy tasks asynchronously.
- [ ] **Interactive Tap Debouncing**: Disable action triggers immediately upon activation to prevent duplicate submissions or purchases from rapid double-tapping.
- [ ] **User-Friendly Error Notification Toasts**: Replace raw technical error logs or undefined strings with contextual, human-readable notification toasts.
- [ ] **Viewport Auto-Scrolling for Active Inputs**: Ensure focused input fields automatically scroll into view above the software keyboard when the virtual keyboard expands.
- [ ] **Client-Side Input State Caching**: Persist form input states and user entries locally on page or route transitions so data is not lost when hitting the back button.
- [ ] **Skeleton Screen Content Placeholders**: Replace generic spinners with structural skeleton loaders that mimic the dimensions and layout of the incoming content.
- [ ] **Fixed Primary CTA Positioning in Stepper Flows**: Anchor the primary progression button (e.g., 'Continue') to the exact same screen coordinates across every step of an onboarding flow.

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

#### Theme State Persistence on Back Navigation
- **Rule**: Maintain consistent color token values and contrast ratios across dark and light mode transitions to prevent unreadable text states.
- **Rationale**: Abrupt theme switches can cause foreground text to blend into newly loaded backgrounds, breaking legibility.
- **Implementation Pattern**: Using dynamic CSS custom properties (e.g., var(--text-primary)) that update cleanly without orphan color dependencies.
- **Status**: Single-Source Guideline (@lincolndevine)
- **Sources**: 1 citation(s) (latest: 2026-09-30) — [@lincolndevine](https://www.instagram.com/p/Dd6TWQ0hpfH/)

### Hierarchy

#### Form Submission Feedback States
- **Rule**: Provide explicit, visible success and error messaging components immediately following user form interactions.
- **Rationale**: Prevents user confusion and uncertainty by confirming system status or clearly highlighting required corrections.
- **Implementation Pattern**:
  - **Avoid**: Form clears silently on error.
  - **Do This**: Inline red error alert displays above the submit button stating 'Please enter a valid email address.'
- **Status**: Single-Source Guideline (@yatesvids)
- **Sources**: 1 citation(s) (latest: 2026-08-18) — [@yatesvids](https://www.instagram.com/p/DcKiRe3TvdB/)

#### Single Primary Call-to-Action
- **Rule**: Designate one dominant, high-contrast visual action per view to guide user conversion and minimize cognitive load.
- **Rationale**: Multiple competing primary buttons cause decision fatigue and slow down user progression.
- **Implementation Pattern**: Style the primary 'Create Account' action as a filled solid brand button while secondary 'Sign In' is styled as a low-emphasis ghost button.
- **Status**: Single-Source Guideline (@millee.md)
- **Sources**: 1 citation(s) (latest: 2026-09-09) — [@millee.md](https://www.instagram.com/p/DdFJTtMganO/)

#### User-Friendly Error Notification Toasts
- **Rule**: Replace raw technical error logs or undefined strings with contextual, human-readable notification toasts.
- **Rationale**: Exposing raw database errors creates cognitive overload and damages product trust.
- **Implementation Pattern**: Displaying 'Something went wrong saving your changes. Try again.' instead of 'Error: TypeError: undefined at Object...'
- **Status**: Single-Source Guideline (@lincolndevine)
- **Sources**: 1 citation(s) (latest: 2026-09-30) — [@lincolndevine](https://www.instagram.com/p/Dd6TWQ0hpfH/)

### Motion

#### Immediate Touch Feedback for Interactive Elements
- **Rule**: Trigger instant visual state changes (like scale or color shifts) on every tap, executing heavy tasks asynchronously.
- **Rationale**: Immediate visual confirmation reassures the user that their input was registered, eliminating perceived lag.
- **Implementation Pattern**: An action button shows a pressed/active state instantly while the network request is handled in the background.
- **Alternate Creator Perspectives & Implementations**:
  - *Perspective (@julianxuofficial)*: Provide instantaneous visual and haptic feedback when a user touches or clicks an interactive surface.
    - *Implementation*: Scale a button down to 98% and trigger a light haptic pulse immediately upon touch down.
- **Consensus**: Multi-Source Consensus (Validated across 2 creators: @jploft.us, @julianxuofficial)
- **Sources**: 2 citation(s) (latest: 2026-09-16) — [@jploft.us](https://www.instagram.com/p/DdXFTBoPEHn/), [@julianxuofficial](https://www.instagram.com/p/DdQhclcxcL-/)

#### Interactive Tap Debouncing
- **Rule**: Disable action triggers immediately upon activation to prevent duplicate submissions or purchases from rapid double-tapping.
- **Rationale**: Rapid or impatient double-taps cause unintended duplicate requests, leading to user frustration and state corruption.
- **Implementation Pattern**: Button component enters a disabled loading state on first tap: onClick={() => { setLoading(true); submitForm(); }}
- **Status**: Single-Source Guideline (@lincolndevine)
- **Sources**: 1 citation(s) (latest: 2026-09-30) — [@lincolndevine](https://www.instagram.com/p/Dd6TWQ0hpfH/)

#### Low-Latency Interface Interaction Response
- **Rule**: Ensure all interactive UI feedback and state changes execute within 400 milliseconds.
- **Rationale**: Faster response times keep users feeling in control and prevent the application from feeling sluggish or unresponsive.
- **Implementation Pattern**: Button press triggers an immediate loading spinner or state change within 200ms rather than a delayed network block.
- **Status**: Single-Source Guideline (@adam_ha_yes)
- **Sources**: 1 citation(s) (latest: 2026-09-02) — [@adam_ha_yes](https://www.instagram.com/p/DcwkX6OyduT/)

#### Physics-Based Spring Animations
- **Rule**: Utilize spring physics curves instead of linear or basic ease-in-out transitions for UI state changes.
- **Rationale**: Spring animations mimic natural real-world physics, making interfaces feel tactile, responsive, and organic.
- **Implementation Pattern**: Apply a damping ratio of 0.8 and response time of 300ms to modal popups instead of a static linear fade.
- **Status**: Single-Source Guideline (@julianxuofficial)
- **Sources**: 1 citation(s) (latest: 2026-09-15) — [@julianxuofficial](https://www.instagram.com/p/DdQhclcxcL-/)

### Accessibility

#### Accessible Text Color Contrast
- **Rule**: Ensure all text elements meet minimum contrast ratios against their background to support users with visual impairments.
- **Rationale**: Sufficient contrast prevents eye strain and ensures content is legible for users with low vision or when viewing screens in bright sunlight.
- **Implementation Pattern**: Change secondary gray text from #A0A0A0 to #595959 on a white background to achieve a 4.5:1 contrast ratio.
- **Status**: Single-Source Guideline (@millee.md)
- **Sources**: 1 citation(s) (latest: 2026-09-09) — [@millee.md](https://www.instagram.com/p/DdFJTtMganO/)

#### Human-Readable Fallback Error States
- **Rule**: Intercept raw system exceptions (404, 500, stack traces) and display an actionable recovery message with clear next steps.
- **Rationale**: Technical error codes cause confusion and erode trust, whereas plain-language instructions guide the user toward recovery.
- **Implementation Pattern**: Instead of 'Error 500: SQL Timeout', show 'We're having trouble connecting. Try again in a moment.' with a retry button.
- **Status**: Single-Source Guideline (@jploft.us)
- **Sources**: 1 citation(s) (latest: 2026-09-16) — [@jploft.us](https://www.instagram.com/p/DdXFTBoPEHn/)

#### Informative Image Alternative Text
- **Rule**: Provide descriptive alt attributes for all meaningful images to support screen reader users.
- **Rationale**: Screen readers rely on alt text to convey the content and function of images to users who cannot see them.
- **Implementation Pattern**: Update `<img src="avatar.png">` to `<img src="avatar.png" alt="Profile portrait of Jane Doe">`.
- **Status**: Single-Source Guideline (@millee.md)
- **Sources**: 1 citation(s) (latest: 2026-09-09) — [@millee.md](https://www.instagram.com/p/DdFJTtMganO/)

#### Interactive Contact Triggers
- **Rule**: Convert text-based phone numbers and email addresses into active tel: and mailto: hyperlinks to enable direct device action.
- **Rationale**: Reduces user friction by eliminating the need to manually copy and paste contact details into external applications on mobile devices.
- **Implementation Pattern**:
  - **Avoid**: <span>Call us at 555-0199</span>
  - **Do This**: <a href="tel:5550199">Call us at 555-0199</a>
- **Status**: Single-Source Guideline (@yatesvids)
- **Sources**: 1 citation(s) (latest: 2026-08-18) — [@yatesvids](https://www.instagram.com/p/DcKiRe3TvdB/)

#### Reduced Motion Preference Compliance
- **Rule**: Disable or substitute motion-heavy transitions when the operating system's reduced motion setting is enabled.
- **Rationale**: Abrupt or scaling animations can trigger vestibular disorders, dizziness, or nausea for sensitive users.
- **Implementation Pattern**: Wrap expansive zoom transitions in `@media (prefers-reduced-motion: no-preference)` queries.
- **Status**: Single-Source Guideline (@julianxuofficial)
- **Sources**: 1 citation(s) (latest: 2026-09-15) — [@julianxuofficial](https://www.instagram.com/p/DdQhclcxcL-/)

### Layout

#### Above-the-Fold Primary Call to Action
- **Rule**: Position the primary conversion action within the initial viewport so it is visible without requiring vertical scrolling.
- **Rationale**: Maximizes conversion potential by capturing immediate user intent before they scroll past the hero section.
- **Implementation Pattern**:
  - **Avoid**: CTA placed at the bottom of a long landing page hero.
  - **Do This**: Primary 'Get Started' button anchored directly beside the main hero headline inside the 100vh container.
- **Status**: Single-Source Guideline (@techbypriyanka)
- **Sources**: 1 citation(s) (latest: 2026-08-30) — [@techbypriyanka](https://www.instagram.com/p/DcEqXsySUaP/)

#### Client-Side Input State Caching
- **Rule**: Persist form input states and user entries locally on page or route transitions so data is not lost when hitting the back button.
- **Rationale**: Losing typed inputs upon navigating backward causes severe user friction and forces repetitive data entry.
- **Implementation Pattern**: Autosaving form state to sessionStorage or localStorage on input change events.
- **Status**: Single-Source Guideline (@lincolndevine)
- **Sources**: 1 citation(s) (latest: 2026-09-30) — [@lincolndevine](https://www.instagram.com/p/Dd6TWQ0hpfH/)

#### Dedicated 404 Error State Design
- **Rule**: Provide a fully styled, custom 404 error page complete with navigation pathways back to primary site sections rather than falling back to unstyled server defaults.
- **Rationale**: Prevents user disorientation and abandonment when encountering broken URLs or deprecated links by offering immediate re-engagement options.
- **Implementation Pattern**:
  - **Avoid**: Browser default white screen with 'Server Not Found'.
  - **Do This**: A branded illustration, search bar, and direct links to Home, Pricing, and Support.
- **Status**: Single-Source Guideline (@quentin_aimarketing)
- **Sources**: 1 citation(s) (latest: 2026-08-14) — [@quentin_aimarketing](https://www.instagram.com/p/DcBqrPsR6BB/)

#### Fixed Primary CTA Positioning in Stepper Flows
- **Rule**: Anchor the primary progression button (e.g., 'Continue') to the exact same screen coordinates across every step of an onboarding flow.
- **Rationale**: Maintaining spatial consistency builds muscle memory, allowing users to progress rapidly without visually searching for the button.
- **Implementation Pattern**: Pin the primary 'Next' button to the bottom sticky container across all 4 onboarding screens.
- **Status**: Single-Source Guideline (@jploft.us)
- **Sources**: 1 citation(s) (latest: 2026-09-16) — [@jploft.us](https://www.instagram.com/p/DdXFTBoPEHn/)

#### Persistent Mobile Conversion Anchor
- **Rule**: Implement a sticky bottom bar housing the primary conversion action on mobile viewports.
- **Rationale**: Keeps the primary conversion goal accessible at all times on small screens, preventing the user from needing to scroll back up to convert.
- **Implementation Pattern**:
  - **Avoid**: Static CTA that scrolls away with the content.
  - **Do This**: position: fixed; bottom: 0; width: 100%; z-index: 100; container holding a full-width purchase button.
- **Status**: Single-Source Guideline (@techbypriyanka)
- **Sources**: 1 citation(s) (latest: 2026-08-30) — [@techbypriyanka](https://www.instagram.com/p/DcEqXsySUaP/)

#### Skeleton Screen Content Placeholders
- **Rule**: Replace generic spinners with structural skeleton loaders that mimic the dimensions and layout of the incoming content.
- **Rationale**: Mimicking the final layout shape reduces perceived waiting time and prevents layout shifts when data resolves.
- **Implementation Pattern**: Instead of a centered spinner, display grey pulsing rectangular blocks where cards or lists will load.
- **Status**: Single-Source Guideline (@jploft.us)
- **Sources**: 1 citation(s) (latest: 2026-09-16) — [@jploft.us](https://www.instagram.com/p/DdXFTBoPEHn/)

#### Viewport Auto-Scrolling for Active Inputs
- **Rule**: Ensure focused input fields automatically scroll into view above the software keyboard when the virtual keyboard expands.
- **Rationale**: When keyboards obscure input fields, users cannot see what they are typing, leading to input errors and abandonment.
- **Implementation Pattern**: Applying scrollIntoView({ behavior: 'smooth', block: 'center' }) on input focus events within mobile viewports.
- **Status**: Single-Source Guideline (@lincolndevine)
- **Sources**: 1 citation(s) (latest: 2026-09-30) — [@lincolndevine](https://www.instagram.com/p/Dd6TWQ0hpfH/)
