---
name: checkups
description: "Actionable UI/UX design heuristics distilled from checkups."
---

# UI/UX Design System & Heuristics

Actionable, production-grade UI/UX design heuristics synthesized from leading design engineers and creators.
Reference these principles when architecting screens, refining typographic rhythm, calibrating negative space, or conducting design reviews.

## Pre-Flight UI/UX Audit Checklist

Before finalizing any interface layout or component hierarchy, audit against these verified fundamentals:

- [ ] **Interactive Tap Debouncing**: Debounce all interactive triggers to prevent double submissions from rapid tapping.
- [ ] **User-Friendly Error Presentation**: Display human-readable toast notifications for errors instead of raw system output.
- [ ] **Dynamic Viewport Keyboard Padding**: Pad or scroll viewports dynamically so the virtual keyboard never obscures active input fields.
- [ ] **Theme Contrast Verification**: Verify accessible contrast ratios for all elements across both light and dark theme toggles.
- [ ] **Form State Persistence**: Persist form input state locally so user entries are preserved when navigating backward.
- [ ] **Hero Section Background Differentiation**: Avoid generic dark slate and centered purple blur hero backgrounds in favor of unique brand-aligned surface treatments.
- [ ] **Feature List Icon Container Design**: Eliminate redundant rounded square icon containers for feature bullet points.

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

#### Hero Section Background Differentiation
- **When to apply**: The primary landing page hero section background layer
- **Do this**: Utilize bespoke, context-driven surface treatments, custom brand palette pairings, or subtle mesh gradients instead of defaulting to a dark slate background with a centered generic purple radial blur.
- **Don't do this**: Default to Tailwind slate-900 combined with a centralized, blurred purple radial gradient orb.
- **Why it matters**: Relying on default AI-generated background aesthetics immediately signals uninspired template creation, eroding user trust before they read the value proposition.
- **Implementation Pattern**:
  - **Avoid**: Slate-900 canvas with an obnoxious fuchsia center blob.
  - **Do This**: Deep charcoal textured surface paired with subtle, asymmetric contextual illumination.
- **Status**: Single-Source Guideline (@murphmaxxing)
- **Sources**: 1 citation(s) (latest: 2026-09-18) — [@murphmaxxing](https://www.instagram.com/p/DdcIywaBDtY/)

#### Primary Call-to-Action Color Focus
- **When to apply**: Landing pages, conversion funnels, and primary interaction screens
- **Do this**: Designate a single, highly distinct accent color dedicated exclusively to the primary conversion action on the screen
- **Don't do this**: Use multiple competing saturated colors for primary actions, which dilutes visual hierarchy and user focus
- **Why it matters**: Multiple competing primary colors create cognitive load and paralyze decision-making, lowering conversion rates.
- **Implementation Pattern**:
  - **Avoid**: Multiple vibrant blue and orange buttons in the hero section.
  - **Do This**: One prominent emerald green primary button with secondary actions styled as ghost buttons.
- **Status**: Single-Source Guideline (@millee.md)
- **Sources**: 1 citation(s) (latest: 2026-09-09) — [@millee.md](https://www.instagram.com/p/DdFJTtMganO/)

#### Theme Contrast Verification
- **When to apply**: UI components, text, and icons that dynamically switch between dark and light themes
- **Do this**: Audit all token values across both dark and light modes to maintain WCAG compliant contrast ratios in every state
- **Don't do this**: Hardcode color values or rely on inversion algorithms that result in unreadable low-contrast text
- **Why it matters**: Unverified theme switching causes text to blend into backgrounds, rendering the interface completely unreadable.
- **Implementation Pattern**:
  - **Avoid**: Gray text remains dark gray when switching to dark mode, disappearing into the background.
  - **Do This**: Text tokens dynamically switch to light gray for high contrast.
- **Status**: Single-Source Guideline (@lincolndevine)
- **Sources**: 1 citation(s) (latest: 2026-09-30) — [@lincolndevine](https://www.instagram.com/p/Dd6TWQ0hpfH/)

### Hierarchy

#### Form Submission Feedback States
- **When to apply**: Interactive forms, newsletter signups, or contact modals handling user submissions
- **Do this**: Provide immediate, visually distinct success messages upon completion and explicit error messages for failed submissions.
- **Don't do this**: Leave the interface completely static or silent after a user submits a form, causing uncertainty.
- **Why it matters**: Users require explicit system feedback to confirm whether their action was successfully processed or requires correction.
- **Implementation Pattern**:
  - **Avoid**: Form clears silently on submit with no confirmation.
  - **Do This**: Form renders an inline green success banner stating 'Message sent successfully!'.
- **Status**: Single-Source Guideline (@yatesvids)
- **Sources**: 1 citation(s) (latest: 2026-08-18) — [@yatesvids](https://www.instagram.com/p/DcKiRe3TvdB/)

#### Immediate Value Onboarding Path
- **When to apply**: first-time user authentication and post-signup application entry flows
- **Do this**: Guide the user directly to a single, high-value primary action that immediately demonstrates the core utility of the application.
- **Don't do this**: Drop unguided new users into an empty state or generic dashboard without clear direction toward the primary value proposition.
- **Why it matters**: Unguided initial states cause high abandonment rates because users fail to discover the core product utility.
- **Implementation Pattern**: Presenting a prominent prompt to create a first project instantly upon logging in rather than showing a blank dashboard.
- **Status**: Single-Source Guideline (@danielwelsh_routiq)
- **Sources**: 1 citation(s) (latest: 2026-08-14) — [@danielwelsh_routiq](https://www.instagram.com/p/DcAKm8HBpCy/)

#### Inline Form Validation and Error States
- **When to apply**: Any user input form, multi-step checkout flow, or interactive data submission interface.
- **Do this**: Design explicit, contextual error states with clear recovery instructions directly adjacent to invalid form fields.
- **Don't do this**: Rely solely on generic, unhelpful system alerts or leave fields unstyled when validation fails.
- **Why it matters**: Vague or absent error states cause user confusion, form abandonment, and high cognitive load during data entry.
- **Implementation Pattern**: Highlighting an invalid email input field with a distinct red border and explanatory text reading 'Please enter a valid email format' below it.
- **Status**: Single-Source Guideline (@techbypriyanka)
- **Sources**: 1 citation(s) (latest: 2026-08-30) — [@techbypriyanka](https://www.instagram.com/p/DcEqXsySUaP/)

#### Pricing Tier Card Elevation & Sizing
- **When to apply**: Multi-tier product pricing matrix components
- **Do this**: Establish emphasis through thoughtful hierarchy, explicit value propositions, clean typography, and restrained badge placement rather than arbitrary dimensional scaling and glowing outlines.
- **Don't do this**: Scale the featured pricing card to be precisely 10 pixels taller and wrap it in an artificial glowing border.
- **Why it matters**: Literal height offsets and glowing borders look gimmicky and distract from evaluating actual plan features and pricing metrics.
- **Implementation Pattern**:
  - **Avoid**: Middle pricing card scaled up +10px with a neon border.
  - **Do This**: Subtle shadow elevation, distinct surface tint, and a clean 'Recommended' badge.
- **Status**: Single-Source Guideline (@murphmaxxing)
- **Sources**: 1 citation(s) (latest: 2026-09-18) — [@murphmaxxing](https://www.instagram.com/p/DdcIywaBDtY/)

#### User-Friendly Error Presentation
- **When to apply**: Any component handling API errors, network failures, or validation exceptions
- **Do this**: Display contextual toast notifications or inline banners containing human-readable error messages
- **Don't do this**: Expose raw database exceptions, stack traces, or variable values like undefined directly to the UI
- **Why it matters**: Raw technical errors confuse users, break visual polish, and erode trust in the application stability.
- **Implementation Pattern**:
  - **Avoid**: Screen displays 'TypeError: undefined is not a function'.
  - **Do This**: Toast displays 'Unable to save changes. Please try again.'
- **Status**: Single-Source Guideline (@lincolndevine)
- **Sources**: 1 citation(s) (latest: 2026-09-30) — [@lincolndevine](https://www.instagram.com/p/Dd6TWQ0hpfH/)

### Motion

#### Comprehensive Asynchronous Loading States
- **When to apply**: Any interface component, button, or container that fetches asynchronous data or submits a network request.
- **Do this**: Provide dedicated visual indicators, skeleton screens, or spinners for all pending asynchronous actions and data loads.
- **Don't do this**: Leave the interface completely static and unresponsive while network requests or background data fetches are processing.
- **Why it matters**: Without visual feedback during latency spikes, users assume the system froze and will repeatedly tap or abandon the interface.
- **Implementation Pattern**: Transforming a button into a spinner state immediately upon tap while network requests resolve.
- **Status**: Single-Source Guideline (@techbypriyanka)
- **Sources**: 1 citation(s) (latest: 2026-08-30) — [@techbypriyanka](https://www.instagram.com/p/DcEqXsySUaP/)

#### Instant Touch Feedback and Optimistic UI
- **When to apply**: Any interactive button or touch target that fires a network request or heavy background task
- **Do this**: Acknowledge every user tap immediately with visual state changes, executing heavy processes asynchronously in the background.
- **Don't do this**: Leave the UI frozen or unresponsive during network latency while waiting for server confirmation.
- **Why it matters**: Unresponsive interfaces break the illusion of direct manipulation and make the application feel broken or sluggish.
- **Implementation Pattern**:
  - **Avoid**: Button hangs with no state change for 3 seconds during upload.
  - **Do This**: Button instantly transitions to a loading/success state while the upload runs asynchronously.
- **Status**: Single-Source Guideline (@jploft.us)
- **Sources**: 1 citation(s) (latest: 2026-09-16) — [@jploft.us](https://www.instagram.com/p/DdXFTBoPEHn/)

#### Low-Latency Interface Interactions
- **When to apply**: any interactive UI component responding to user input, such as button taps, form submissions, or state transitions
- **Do this**: Execute state updates and feedback animations within a 400-millisecond window to ensure perceived system instantaneousness.
- **Don't do this**: Allow interaction response times or transition delays to exceed 400 milliseconds, which degrades user engagement and creates perceived sluggishness.
- **Why it matters**: Delays exceeding 400ms disrupt the user's flow state and reduce the perceived responsiveness and quality of the software application.
- **Implementation Pattern**: A button tap triggers an immediate visual feedback state change and loader within 200ms, followed by network resolution.
- **Status**: Single-Source Guideline (@adam_ha_yes)
- **Sources**: 1 citation(s) (latest: 2026-09-02) — [@adam_ha_yes](https://www.instagram.com/p/DcwkX6OyduT/)

#### Native Motion System Integration
- **When to apply**: interactive touch targets, modal sheets, and page transitions in mobile applications
- **Do this**: Implement physics-based spring animations and match OS-native navigation transitions while respecting user reduced-motion accessibility preferences
- **Don't do this**: Use generic, web-style linear or ease-in-out easing curves that feel disconnected from the platform's native feel
- **Why it matters**: Web-styled motion feels sluggish and unpolished on native hardware, violating user expectations for fluid, tactile feedback and causing cognitive friction.
- **Implementation Pattern**:
  - **Avoid**: A modal slides up using a standard linear ease.
  - **Do This**: A modal uses a damped spring animation that responds to a swipe-to-dismiss gesture with matching velocity.
- **Status**: Single-Source Guideline (@julianxuofficial)
- **Sources**: 1 citation(s) (latest: 2026-09-15) — [@julianxuofficial](https://www.instagram.com/p/DdQhclcxcL-/)

#### Perspectives & Transforms on Product Mockups
- **When to apply**: Hero dashboard previews and application UI mockups
- **Do this**: Render product interfaces flat or at clean, readable isometric angles with soft, physically plausible ambient drop shadows.
- **Don't do this**: Tilt dashboard preview mockups at an extreme 15-degree 3D perspective paired with heavy 40-pixel blurred drop shadows.
- **Why it matters**: Exaggerated perspective distortion sacrifices legibility of the actual interface content just for cheap visual flair.
- **Implementation Pattern**:
  - **Avoid**: Dashboard preview skewed at a steep 15-degree angle with a blown-out dark drop shadow.
  - **Do This**: Clean, front-facing UI shot with crisp edge rendering.
- **Status**: Single-Source Guideline (@murphmaxxing)
- **Sources**: 1 citation(s) (latest: 2026-09-18) — [@murphmaxxing](https://www.instagram.com/p/DdcIywaBDtY/)

### Accessibility

#### Accessible Color Contrast Enforcement
- **When to apply**: Any web page or UI component containing text displayed over background surfaces
- **Do this**: Verify and adjust all text-to-background color combinations to meet or exceed WCAG minimum contrast ratio thresholds
- **Don't do this**: Deploy low-contrast color pairings that cause readability strain for users with visual impairments
- **Why it matters**: Insufficient contrast makes text unreadable for users with low vision or when viewing displays under high ambient lighting, causing abandonment.
- **Implementation Pattern**:
  - **Avoid**: Light gray text on a white background (#CCCCCC on #FFFFFF).
  - **Do This**: Dark slate text on a white background (#333333 on #FFFFFF).
- **Status**: Single-Source Guideline (@millee.md)
- **Sources**: 1 citation(s) (latest: 2026-09-09) — [@millee.md](https://www.instagram.com/p/DdFJTtMganO/)

#### Interactive Contact Information Styling
- **When to apply**: Phone numbers and email addresses displayed in headers, footers, or contact sections
- **Do this**: Wrap phone numbers in 'tel:' anchors and email addresses in 'mailto:' anchors with clear interactive affordances.
- **Don't do this**: Render phone numbers and email addresses as static, unlinked plain text.
- **Why it matters**: Users on mobile devices expect touch targets to immediately initiate phone calls or open their default email client.
- **Implementation Pattern**:
  - **Avoid**: Plain text string '+1 (555) 019-2834'.
  - **Do This**: An interactive anchor tag `<a href="tel:+15550192834">+1 (555) 019-2834</a>`.
- **Status**: Single-Source Guideline (@yatesvids)
- **Sources**: 1 citation(s) (latest: 2026-08-18) — [@yatesvids](https://www.instagram.com/p/DcKiRe3TvdB/)

#### Interactive Tap Debouncing
- **When to apply**: Any primary action button or interactive element that triggers a mutation or network request
- **Do this**: Debounce tap handlers or immediately disable interactive elements upon first trigger until the asynchronous action resolves
- **Don't do this**: Allow rapid successive taps to fire duplicate network requests or trigger redundant actions
- **Why it matters**: Rapid double-tapping causes duplicate transactions, double data saves, and severe user frustration.
- **Implementation Pattern**:
  - **Avoid**: Button fires purchase API on every click.
  - **Do This**: Button enters loading state and disables on first click.
- **Status**: Single-Source Guideline (@lincolndevine)
- **Sources**: 1 citation(s) (latest: 2026-09-30) — [@lincolndevine](https://www.instagram.com/p/Dd6TWQ0hpfH/)

#### Subscription Cancellation Asymmetry Prevention
- **When to apply**: Account settings, billing dashboards, or subscription management interfaces where users attempt to downgrade or terminate a paid plan.
- **Do this**: Provide a direct, single-action cancellation path that requires equal or fewer interaction steps than the initial subscription onboarding flow.
- **Don't do this**: Bury the cancellation trigger behind multi-step confirmation screens, deceptive dark patterns, retention questionnaires, or hidden navigation paths.
- **Why it matters**: Making cancellation unnecessarily arduous creates cognitive friction and violates consumer protection standards, leading to severe legal penalties and severe brand erosion.
- **Implementation Pattern**:
  - **Avoid**: Requiring a 5-step retention survey, chat with support, and two confirmation pages to cancel.
  - **Do This**: A single 'Cancel Subscription' button in billing settings that processes immediately with one confirmation dialog.
- **Status**: Single-Source Guideline (@murphmaxxing)
- **Sources**: 1 citation(s) (latest: 2026-09-10) — [@murphmaxxing](https://www.instagram.com/p/Dcq_kZlpGsQ/)

### Layout

#### Above-the-Fold Primary Conversion Anchor
- **When to apply**: Any landing page, marketing site, or conversion-focused web view viewport initialization.
- **Do this**: Position the primary conversion trigger or call-to-action within the initial viewport before any vertical scrolling is required.
- **Don't do this**: Bury the primary conversion action below secondary content blocks or deep down the page layout.
- **Why it matters**: Users evaluate page value within seconds of arrival; hiding primary actions below the fold drastically increases bounce rates and reduces conversion velocity.
- **Implementation Pattern**: Hero section featuring a prominent primary 'Get Started' button visible immediately without scrolling versus a hero section showing only text where the button sits far down.
- **Status**: Single-Source Guideline (@techbypriyanka)
- **Sources**: 1 citation(s) (latest: 2026-08-30) — [@techbypriyanka](https://www.instagram.com/p/DcEqXsySUaP/)

#### Avoid Overused AI-Generated UI Tropes and Generic Layout Patterns
- **When to apply**: marketing landing pages, feature grids, and pricing sections generated via AI tools
- **Do this**: design bespoke layouts with purpose-driven typography, authentic content, and restrained visual styling tailored to the specific product identity
- **Don't do this**: rely on cliché AI styling tropes such as default bento grids, liquid glass effects, random sparkle icons, neon-on-dark palettes, and generic three-tier pricing cards without actual product differentiation
- **Why it matters**: Overused aesthetic tropes create visual fatigue, reduce brand trust, and make interfaces look indistinguishable from low-effort automated clones.
- **Implementation Pattern**:
  - **Avoid**: A dark mode landing page featuring purple glow effects, floating dot grids, terminal windows, and floating checkmark bullets.
  - **Do This**: A clean, content-first layout with high-contrast neutral typography and contextual product screenshots.
- **Status**: Single-Source Guideline (@aj.on.ai)
- **Sources**: 1 citation(s) (latest: 2026-08-15) — [@aj.on.ai](https://www.instagram.com/p/DcEJDHBTyPY/)

#### Bento Grid Content Density
- **When to apply**: Marketing bento grid layouts and feature showcases
- **Do this**: Populate grid cells with authentic product data, real-time metrics, actual code snippets, or functional UI widgets.
- **Don't do this**: Construct empty bento grid cards containing purely decorative static CSS charts and pointless bouncing toggles.
- **Why it matters**: Empty placeholder metrics and looping mock animations degrade user confidence by exposing a lack of substantive product depth.
- **Implementation Pattern**:
  - **Avoid**: Bento card with a static bar chart and an idle looping toggle.
  - **Do This**: Bento card showing live API latency metrics and functional telemetry graphs.
- **Status**: Single-Source Guideline (@murphmaxxing)
- **Sources**: 1 citation(s) (latest: 2026-09-18) — [@murphmaxxing](https://www.instagram.com/p/DdcIywaBDtY/)

#### Complete Application Edge States and Flows
- **When to apply**: Any application pre-launch checklist or production readiness audit for a new software interface.
- **Do this**: Implement explicit UI screens and feedback mechanisms for asynchronous data fetching, data-absent conditions, and failure states before considering a product finished.
- **Don't do this**: Assume an interface is complete when happy-path layouts function correctly without handling empty, loading, and error states.
- **Why it matters**: Failing to account for non-ideal states results in broken layouts, blank screens, and user confusion when network latency or empty databases occur.
- **Implementation Pattern**:
  - **Avoid**: A dashboard displaying blank white space when no data exists.
  - **Do This**: An empty state component featuring custom illustration, explanatory microcopy, and a clear call-to-action button to create the first item.
- **Status**: Single-Source Guideline (@corecodevibes)
- **Sources**: 1 citation(s) (latest: 2026-08-15) — [@corecodevibes](https://www.instagram.com/p/DcCS0Z6oNfW/)

#### Consistent Primary Action Placement in Flows
- **When to apply**: Multi-step onboarding flows, checkout wizards, or sequential form screens
- **Do this**: Anchor the primary continue or advance action button to the exact same screen coordinate across every step of the flow.
- **Don't do this**: Shift primary action buttons to different vertical or horizontal positions between sequential screens.
- **Why it matters**: Shifting buttons forces users to visually hunt for the target on every step, breaking muscle memory and increasing cognitive load.
- **Implementation Pattern**:
  - **Avoid**: Continue button is at the bottom in step one and in the middle in step two.
  - **Do This**: Continue button remains pinned to the bottom-fixed action bar across all steps.
- **Status**: Single-Source Guideline (@jploft.us)
- **Sources**: 1 citation(s) (latest: 2026-09-16) — [@jploft.us](https://www.instagram.com/p/DdXFTBoPEHn/)

#### Dynamic Viewport Keyboard Padding
- **When to apply**: Form inputs, textareas, and chat inputs positioned near the bottom of mobile viewports
- **Do this**: Adjust container padding or scroll the active input into view dynamically when the software keyboard appears
- **Don't do this**: Let the software keyboard obscure the active input field entirely
- **Why it matters**: Obscuring the input field prevents users from seeing what they are typing, leading to input abandonment.
- **Implementation Pattern**:
  - **Avoid**: Bottom input field is hidden beneath the OS keyboard.
  - **Do This**: Form scrolls up automatically to keep the focused input visible.
- **Status**: Single-Source Guideline (@lincolndevine)
- **Sources**: 1 citation(s) (latest: 2026-09-30) — [@lincolndevine](https://www.instagram.com/p/Dd6TWQ0hpfH/)

#### Feature List Icon Container Design
- **When to apply**: Feature checklist or benefit bullet-point lists utilizing icons
- **Do this**: Pair standalone icons directly with typography, use minimalist inline indicators, or design purpose-built structured containers that match the exact visual weight of the accompanying text.
- **Don't do this**: Enclose every single feature list icon inside an identical, generic rounded square background badge.
- **Why it matters**: Enclosing every single icon in an identical container creates visual noise and repetitive chunking that reduces scannability.
- **Implementation Pattern**:
  - **Avoid**: Every bullet point features a standalone icon inside a rounded grey container box.
  - **Do This**: Clean typographic hierarchy with minimal inline vector glyphs.
- **Status**: Single-Source Guideline (@murphmaxxing)
- **Sources**: 1 citation(s) (latest: 2026-09-18) — [@murphmaxxing](https://www.instagram.com/p/DdcIywaBDtY/)

#### Form State Persistence
- **When to apply**: Multi-step workflows, forms, and input screens where a user might navigate backward
- **Do this**: Persist user input state in local storage, route state, or form management stores across navigation events
- **Don't do this**: Clear input values or unmount state when a user hits the back button
- **Why it matters**: Losing typed data upon hitting the back button destroys user effort and causes extreme friction.
- **Implementation Pattern**:
  - **Avoid**: Hitting back clears all entered form fields.
  - **Do This**: Returning to the form restores previously typed inputs from state cache.
- **Status**: Single-Source Guideline (@lincolndevine)
- **Sources**: 1 citation(s) (latest: 2026-09-30) — [@lincolndevine](https://www.instagram.com/p/Dd6TWQ0hpfH/)

#### Mobile Viewport Overflow Prevention
- **When to apply**: Responsive web layouts viewed on mobile devices with constrained viewport widths
- **Do this**: Audit and eliminate any elements or layout containers that extend horizontally beyond the primary viewport boundary.
- **Don't do this**: Allow wide content blocks, unconstrained images, or fixed-width containers to force horizontal scrolling on mobile viewports.
- **Why it matters**: Horizontal scrolling on mobile creates a broken, jarring user experience and indicates layout containment failure.
- **Implementation Pattern**:
  - **Avoid**: A fixed-width data table causing horizontal page panning.
  - **Do This**: A responsive container with CSS overflow handling or stacked mobile representation.
- **Status**: Single-Source Guideline (@yatesvids)
- **Sources**: 1 citation(s) (latest: 2026-08-18) — [@yatesvids](https://www.instagram.com/p/DcKiRe3TvdB/)

#### Non-UI Content Filtering
- **When to apply**: Any unstructured content intake or social media corpus ingestion pipeline
- **Do this**: Filter out promotional creator metadata, personal branding hooks, and off-topic social captions that contain no interface design instructions.
- **Don't do this**: Process non-design text, general marketing copy, or personal introduction statements through design rule extraction engines.
- **Why it matters**: Ingesting non-design content contaminates design system guidelines with irrelevant noise, reducing the precision and reliability of the synthesized skill set.
- **Implementation Pattern**:
  - **Avoid**: Extracting principles from a general bio.
  - **Do This**: Returning an empty array `[]` when no design context is present.
- **Status**: Single-Source Guideline (@shubhamnalingupta)
- **Sources**: 1 citation(s) (latest: 2026-09-03) — [@shubhamnalingupta](https://www.instagram.com/p/Dc0ZxxvzdE8/)

#### OpenGraph Link Preview Asset Implementation
- **When to apply**: any web application URL or product link shared across social media or messaging platforms
- **Do this**: Define explicit OpenGraph and Twitter card image metadata tags accompanied by a descriptive title and subtitle so shared links render a rich visual card instead of a generic placeholder frame.
- **Don't do this**: Leave link metadata unconfigured, resulting in a fallback blank grey box or missing thumbnail when users share the application URL.
- **Why it matters**: Missing link previews diminish perceived professional quality and reduce click-through rates on external platforms.
- **Implementation Pattern**: Adding og:image, og:title, and twitter:image tags to the document head of the landing page.
- **Status**: Single-Source Guideline (@danielwelsh_routiq)
- **Sources**: 1 citation(s) (latest: 2026-08-14) — [@danielwelsh_routiq](https://www.instagram.com/p/DcAKm8HBpCy/)

#### Persistent Mobile Conversion Action Bar
- **When to apply**: Mobile web layouts and responsive viewports where vertical scrolling spans multiple content sections.
- **Do this**: Implement a pinned or sticky bottom action bar containing the primary conversion trigger on mobile viewports.
- **Don't do this**: Force mobile users to scroll back to the top of long-form pages or hunt through navigation menus to complete a conversion action.
- **Why it matters**: Mobile viewports have restricted vertical space; keeping the conversion trigger persistently accessible reduces interaction cost and friction.
- **Implementation Pattern**: A sticky bottom bar featuring a 'Buy Now' button that remains anchored while scrolling through product details.
- **Status**: Single-Source Guideline (@techbypriyanka)
- **Sources**: 1 citation(s) (latest: 2026-08-30) — [@techbypriyanka](https://www.instagram.com/p/DcEqXsySUaP/)

#### Skeleton Loaders for Perceived Performance
- **When to apply**: Any asynchronous content fetching or data-loading screen state
- **Do this**: Replace generic spinning loaders with structural skeleton loaders that mirror the layout and dimensions of the incoming content.
- **Don't do this**: Use generic spinning indicators or blank white screens for predictable layout content fetches.
- **Why it matters**: Spinners create a sense of stalling and disconnect user focus, whereas structural skeletons provide a spatial preview that tricks the brain into perceiving faster load times.
- **Implementation Pattern**:
  - **Avoid**: Centered spinner icon.
  - **Do This**: Gray pulsing placeholder blocks matching cards and text lines.
- **Status**: Single-Source Guideline (@jploft.us)
- **Sources**: 1 citation(s) (latest: 2026-09-16) — [@jploft.us](https://www.instagram.com/p/DdXFTBoPEHn/)
