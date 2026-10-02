# Design Skill Extraction Report: @checkups

> **Creator Profile:** [@checkups](https://www.instagram.com/checkups/)  
> **Extracted:** 2026-10-02 17:41:11  
> **Analyzed Post Range:** 2026-03-12 to 2026-09-30

---

## Overview & Extraction Metrics

| Metric | Count |
|---|---|
| **Total Posts Analyzed** | `25` |
| **Video Reels Transcribed** | `24` / `25` |
| **Unique Design Principles** | `29` |
| **Active Categories** | `5` / `7` |
| **Extraction Engine** | `LLM Analysis (No Templates)` |

### Category Distribution

| Category | Principles Extracted |
|---|---|
| **Color** | `3` principle(s) |
| **Hierarchy** | `5` principle(s) |
| **Motion** | `5` principle(s) |
| **Accessibility** | `4` principle(s) |
| **Layout** | `12` principle(s) |

---

## Distilled Design Principles

### Color

#### Hero Section Background Differentiation
- **Trigger Scenario**: The primary landing page hero section background layer
- **Guideline**: Utilize bespoke, context-driven surface treatments, custom brand palette pairings, or subtle mesh gradients instead of defaulting to a dark slate background with a centered generic purple radial blur.
- **Avoid (Anti-Pattern)**: Default to Tailwind slate-900 combined with a centralized, blurred purple radial gradient orb.
- **Rationale**: Relying on default AI-generated background aesthetics immediately signals uninspired template creation, eroding user trust before they read the value proposition.
- **Practical Application**: Before: Slate-900 canvas with an obnoxious fuchsia center blob. After: Deep charcoal textured surface paired with subtle, asymmetric contextual illumination.
- **Cited Sources (1)**: [2026-09-18](https://www.instagram.com/p/DdcIywaBDtY/)

#### Primary Call-to-Action Color Focus
- **Trigger Scenario**: Landing pages, conversion funnels, and primary interaction screens
- **Guideline**: Designate a single, highly distinct accent color dedicated exclusively to the primary conversion action on the screen
- **Avoid (Anti-Pattern)**: Use multiple competing saturated colors for primary actions, which dilutes visual hierarchy and user focus
- **Rationale**: Multiple competing primary colors create cognitive load and paralyze decision-making, lowering conversion rates.
- **Practical Application**: Before: Multiple vibrant blue and orange buttons in the hero section. After: One prominent emerald green primary button with secondary actions styled as ghost buttons.
- **Cited Sources (1)**: [2026-09-09](https://www.instagram.com/p/DdFJTtMganO/)

#### Theme Contrast Verification
- **Trigger Scenario**: UI components, text, and icons that dynamically switch between dark and light themes
- **Guideline**: Audit all token values across both dark and light modes to maintain WCAG compliant contrast ratios in every state
- **Avoid (Anti-Pattern)**: Hardcode color values or rely on inversion algorithms that result in unreadable low-contrast text
- **Rationale**: Unverified theme switching causes text to blend into backgrounds, rendering the interface completely unreadable.
- **Practical Application**: Before: Gray text remains dark gray when switching to dark mode, disappearing into the background. After: Text tokens dynamically switch to light gray for high contrast.
- **Cited Sources (1)**: [2026-09-30](https://www.instagram.com/p/Dd6TWQ0hpfH/)

### Hierarchy

#### Form Submission Feedback States
- **Trigger Scenario**: Interactive forms, newsletter signups, or contact modals handling user submissions
- **Guideline**: Provide immediate, visually distinct success messages upon completion and explicit error messages for failed submissions.
- **Avoid (Anti-Pattern)**: Leave the interface completely static or silent after a user submits a form, causing uncertainty.
- **Rationale**: Users require explicit system feedback to confirm whether their action was successfully processed or requires correction.
- **Practical Application**: Before: Form clears silently on submit with no confirmation. After: Form renders an inline green success banner stating 'Message sent successfully!'.
- **Cited Sources (1)**: [2026-08-18](https://www.instagram.com/p/DcKiRe3TvdB/)

#### Immediate Value Onboarding Path
- **Trigger Scenario**: first-time user authentication and post-signup application entry flows
- **Guideline**: Guide the user directly to a single, high-value primary action that immediately demonstrates the core utility of the application.
- **Avoid (Anti-Pattern)**: Drop unguided new users into an empty state or generic dashboard without clear direction toward the primary value proposition.
- **Rationale**: Unguided initial states cause high abandonment rates because users fail to discover the core product utility.
- **Practical Application**: Presenting a prominent prompt to create a first project instantly upon logging in rather than showing a blank dashboard.
- **Cited Sources (1)**: [2026-08-14](https://www.instagram.com/p/DcAKm8HBpCy/)

#### Inline Form Validation and Error States
- **Trigger Scenario**: Any user input form, multi-step checkout flow, or interactive data submission interface.
- **Guideline**: Design explicit, contextual error states with clear recovery instructions directly adjacent to invalid form fields.
- **Avoid (Anti-Pattern)**: Rely solely on generic, unhelpful system alerts or leave fields unstyled when validation fails.
- **Rationale**: Vague or absent error states cause user confusion, form abandonment, and high cognitive load during data entry.
- **Practical Application**: Highlighting an invalid email input field with a distinct red border and explanatory text reading 'Please enter a valid email format' below it.
- **Cited Sources (1)**: [2026-08-30](https://www.instagram.com/p/DcEqXsySUaP/)

#### Pricing Tier Card Elevation & Sizing
- **Trigger Scenario**: Multi-tier product pricing matrix components
- **Guideline**: Establish emphasis through thoughtful hierarchy, explicit value propositions, clean typography, and restrained badge placement rather than arbitrary dimensional scaling and glowing outlines.
- **Avoid (Anti-Pattern)**: Scale the featured pricing card to be precisely 10 pixels taller and wrap it in an artificial glowing border.
- **Rationale**: Literal height offsets and glowing borders look gimmicky and distract from evaluating actual plan features and pricing metrics.
- **Practical Application**: Before: Middle pricing card scaled up +10px with a neon border. After: Subtle shadow elevation, distinct surface tint, and a clean 'Recommended' badge.
- **Cited Sources (1)**: [2026-09-18](https://www.instagram.com/p/DdcIywaBDtY/)

#### User-Friendly Error Presentation
- **Trigger Scenario**: Any component handling API errors, network failures, or validation exceptions
- **Guideline**: Display contextual toast notifications or inline banners containing human-readable error messages
- **Avoid (Anti-Pattern)**: Expose raw database exceptions, stack traces, or variable values like undefined directly to the UI
- **Rationale**: Raw technical errors confuse users, break visual polish, and erode trust in the application stability.
- **Practical Application**: Before: Screen displays 'TypeError: undefined is not a function'. After: Toast displays 'Unable to save changes. Please try again.'
- **Cited Sources (1)**: [2026-09-30](https://www.instagram.com/p/Dd6TWQ0hpfH/)

### Motion

#### Comprehensive Asynchronous Loading States
- **Trigger Scenario**: Any interface component, button, or container that fetches asynchronous data or submits a network request.
- **Guideline**: Provide dedicated visual indicators, skeleton screens, or spinners for all pending asynchronous actions and data loads.
- **Avoid (Anti-Pattern)**: Leave the interface completely static and unresponsive while network requests or background data fetches are processing.
- **Rationale**: Without visual feedback during latency spikes, users assume the system froze and will repeatedly tap or abandon the interface.
- **Practical Application**: Transforming a button into a spinner state immediately upon tap while network requests resolve.
- **Cited Sources (1)**: [2026-08-30](https://www.instagram.com/p/DcEqXsySUaP/)

#### Instant Touch Feedback and Optimistic UI
- **Trigger Scenario**: Any interactive button or touch target that fires a network request or heavy background task
- **Guideline**: Acknowledge every user tap immediately with visual state changes, executing heavy processes asynchronously in the background.
- **Avoid (Anti-Pattern)**: Leave the UI frozen or unresponsive during network latency while waiting for server confirmation.
- **Rationale**: Unresponsive interfaces break the illusion of direct manipulation and make the application feel broken or sluggish.
- **Practical Application**: Before: Button hangs with no state change for 3 seconds during upload. After: Button instantly transitions to a loading/success state while the upload runs asynchronously.
- **Cited Sources (1)**: [2026-09-16](https://www.instagram.com/p/DdXFTBoPEHn/)

#### Low-Latency Interface Interactions
- **Trigger Scenario**: any interactive UI component responding to user input, such as button taps, form submissions, or state transitions
- **Guideline**: Execute state updates and feedback animations within a 400-millisecond window to ensure perceived system instantaneousness.
- **Avoid (Anti-Pattern)**: Allow interaction response times or transition delays to exceed 400 milliseconds, which degrades user engagement and creates perceived sluggishness.
- **Rationale**: Delays exceeding 400ms disrupt the user's flow state and reduce the perceived responsiveness and quality of the software application.
- **Practical Application**: A button tap triggers an immediate visual feedback state change and loader within 200ms, followed by network resolution.
- **Cited Sources (1)**: [2026-09-02](https://www.instagram.com/p/DcwkX6OyduT/)

#### Native Motion System Integration
- **Trigger Scenario**: interactive touch targets, modal sheets, and page transitions in mobile applications
- **Guideline**: Implement physics-based spring animations and match OS-native navigation transitions while respecting user reduced-motion accessibility preferences
- **Avoid (Anti-Pattern)**: Use generic, web-style linear or ease-in-out easing curves that feel disconnected from the platform's native feel
- **Rationale**: Web-styled motion feels sluggish and unpolished on native hardware, violating user expectations for fluid, tactile feedback and causing cognitive friction.
- **Practical Application**: Before: A modal slides up using a standard linear ease. After: A modal uses a damped spring animation that responds to a swipe-to-dismiss gesture with matching velocity.
- **Cited Sources (1)**: [2026-09-15](https://www.instagram.com/p/DdQhclcxcL-/)

#### Perspectives & Transforms on Product Mockups
- **Trigger Scenario**: Hero dashboard previews and application UI mockups
- **Guideline**: Render product interfaces flat or at clean, readable isometric angles with soft, physically plausible ambient drop shadows.
- **Avoid (Anti-Pattern)**: Tilt dashboard preview mockups at an extreme 15-degree 3D perspective paired with heavy 40-pixel blurred drop shadows.
- **Rationale**: Exaggerated perspective distortion sacrifices legibility of the actual interface content just for cheap visual flair.
- **Practical Application**: Before: Dashboard preview skewed at a steep 15-degree angle with a blown-out dark drop shadow. After: Clean, front-facing UI shot with crisp edge rendering.
- **Cited Sources (1)**: [2026-09-18](https://www.instagram.com/p/DdcIywaBDtY/)

### Accessibility

#### Accessible Color Contrast Enforcement
- **Trigger Scenario**: Any web page or UI component containing text displayed over background surfaces
- **Guideline**: Verify and adjust all text-to-background color combinations to meet or exceed WCAG minimum contrast ratio thresholds
- **Avoid (Anti-Pattern)**: Deploy low-contrast color pairings that cause readability strain for users with visual impairments
- **Rationale**: Insufficient contrast makes text unreadable for users with low vision or when viewing displays under high ambient lighting, causing abandonment.
- **Practical Application**: Before: Light gray text on a white background (#CCCCCC on #FFFFFF). After: Dark slate text on a white background (#333333 on #FFFFFF).
- **Cited Sources (1)**: [2026-09-09](https://www.instagram.com/p/DdFJTtMganO/)

#### Interactive Contact Information Styling
- **Trigger Scenario**: Phone numbers and email addresses displayed in headers, footers, or contact sections
- **Guideline**: Wrap phone numbers in 'tel:' anchors and email addresses in 'mailto:' anchors with clear interactive affordances.
- **Avoid (Anti-Pattern)**: Render phone numbers and email addresses as static, unlinked plain text.
- **Rationale**: Users on mobile devices expect touch targets to immediately initiate phone calls or open their default email client.
- **Practical Application**: Before: Plain text string '+1 (555) 019-2834'. After: An interactive anchor tag `<a href="tel:+15550192834">+1 (555) 019-2834</a>`.
- **Cited Sources (1)**: [2026-08-18](https://www.instagram.com/p/DcKiRe3TvdB/)

#### Interactive Tap Debouncing
- **Trigger Scenario**: Any primary action button or interactive element that triggers a mutation or network request
- **Guideline**: Debounce tap handlers or immediately disable interactive elements upon first trigger until the asynchronous action resolves
- **Avoid (Anti-Pattern)**: Allow rapid successive taps to fire duplicate network requests or trigger redundant actions
- **Rationale**: Rapid double-tapping causes duplicate transactions, double data saves, and severe user frustration.
- **Practical Application**: Before: Button fires purchase API on every click. After: Button enters loading state and disables on first click.
- **Cited Sources (1)**: [2026-09-30](https://www.instagram.com/p/Dd6TWQ0hpfH/)

#### Subscription Cancellation Asymmetry Prevention
- **Trigger Scenario**: Account settings, billing dashboards, or subscription management interfaces where users attempt to downgrade or terminate a paid plan.
- **Guideline**: Provide a direct, single-action cancellation path that requires equal or fewer interaction steps than the initial subscription onboarding flow.
- **Avoid (Anti-Pattern)**: Bury the cancellation trigger behind multi-step confirmation screens, deceptive dark patterns, retention questionnaires, or hidden navigation paths.
- **Rationale**: Making cancellation unnecessarily arduous creates cognitive friction and violates consumer protection standards, leading to severe legal penalties and severe brand erosion.
- **Practical Application**: Before: Requiring a 5-step retention survey, chat with support, and two confirmation pages to cancel. After: A single 'Cancel Subscription' button in billing settings that processes immediately with one confirmation dialog.
- **Cited Sources (1)**: [2026-09-10](https://www.instagram.com/p/Dcq_kZlpGsQ/)

### Layout

#### Above-the-Fold Primary Conversion Anchor
- **Trigger Scenario**: Any landing page, marketing site, or conversion-focused web view viewport initialization.
- **Guideline**: Position the primary conversion trigger or call-to-action within the initial viewport before any vertical scrolling is required.
- **Avoid (Anti-Pattern)**: Bury the primary conversion action below secondary content blocks or deep down the page layout.
- **Rationale**: Users evaluate page value within seconds of arrival; hiding primary actions below the fold drastically increases bounce rates and reduces conversion velocity.
- **Practical Application**: Hero section featuring a prominent primary 'Get Started' button visible immediately without scrolling versus a hero section showing only text where the button sits far down.
- **Cited Sources (1)**: [2026-08-30](https://www.instagram.com/p/DcEqXsySUaP/)

#### Avoid Overused AI-Generated UI Tropes and Generic Layout Patterns
- **Trigger Scenario**: marketing landing pages, feature grids, and pricing sections generated via AI tools
- **Guideline**: design bespoke layouts with purpose-driven typography, authentic content, and restrained visual styling tailored to the specific product identity
- **Avoid (Anti-Pattern)**: rely on cliché AI styling tropes such as default bento grids, liquid glass effects, random sparkle icons, neon-on-dark palettes, and generic three-tier pricing cards without actual product differentiation
- **Rationale**: Overused aesthetic tropes create visual fatigue, reduce brand trust, and make interfaces look indistinguishable from low-effort automated clones.
- **Practical Application**: Before: A dark mode landing page featuring purple glow effects, floating dot grids, terminal windows, and floating checkmark bullets. After: A clean, content-first layout with high-contrast neutral typography and contextual product screenshots.
- **Cited Sources (1)**: [2026-08-15](https://www.instagram.com/p/DcEJDHBTyPY/)

#### Bento Grid Content Density
- **Trigger Scenario**: Marketing bento grid layouts and feature showcases
- **Guideline**: Populate grid cells with authentic product data, real-time metrics, actual code snippets, or functional UI widgets.
- **Avoid (Anti-Pattern)**: Construct empty bento grid cards containing purely decorative static CSS charts and pointless bouncing toggles.
- **Rationale**: Empty placeholder metrics and looping mock animations degrade user confidence by exposing a lack of substantive product depth.
- **Practical Application**: Before: Bento card with a static bar chart and an idle looping toggle. After: Bento card showing live API latency metrics and functional telemetry graphs.
- **Cited Sources (1)**: [2026-09-18](https://www.instagram.com/p/DdcIywaBDtY/)

#### Consistent Primary Action Placement in Flows
- **Trigger Scenario**: Multi-step onboarding flows, checkout wizards, or sequential form screens
- **Guideline**: Anchor the primary continue or advance action button to the exact same screen coordinate across every step of the flow.
- **Avoid (Anti-Pattern)**: Shift primary action buttons to different vertical or horizontal positions between sequential screens.
- **Rationale**: Shifting buttons forces users to visually hunt for the target on every step, breaking muscle memory and increasing cognitive load.
- **Practical Application**: Before: Continue button is at the bottom in step one and in the middle in step two. After: Continue button remains pinned to the bottom-fixed action bar across all steps.
- **Cited Sources (1)**: [2026-09-16](https://www.instagram.com/p/DdXFTBoPEHn/)

#### Dynamic Viewport Keyboard Padding
- **Trigger Scenario**: Form inputs, textareas, and chat inputs positioned near the bottom of mobile viewports
- **Guideline**: Adjust container padding or scroll the active input into view dynamically when the software keyboard appears
- **Avoid (Anti-Pattern)**: Let the software keyboard obscure the active input field entirely
- **Rationale**: Obscuring the input field prevents users from seeing what they are typing, leading to input abandonment.
- **Practical Application**: Before: Bottom input field is hidden beneath the OS keyboard. After: Form scrolls up automatically to keep the focused input visible.
- **Cited Sources (1)**: [2026-09-30](https://www.instagram.com/p/Dd6TWQ0hpfH/)

#### Feature List Icon Container Design
- **Trigger Scenario**: Feature checklist or benefit bullet-point lists utilizing icons
- **Guideline**: Pair standalone icons directly with typography, use minimalist inline indicators, or design purpose-built structured containers that match the exact visual weight of the accompanying text.
- **Avoid (Anti-Pattern)**: Enclose every single feature list icon inside an identical, generic rounded square background badge.
- **Rationale**: Enclosing every single icon in an identical container creates visual noise and repetitive chunking that reduces scannability.
- **Practical Application**: Before: Every bullet point features a standalone icon inside a rounded grey container box. After: Clean typographic hierarchy with minimal inline vector glyphs.
- **Cited Sources (1)**: [2026-09-18](https://www.instagram.com/p/DdcIywaBDtY/)

#### Form State Persistence
- **Trigger Scenario**: Multi-step workflows, forms, and input screens where a user might navigate backward
- **Guideline**: Persist user input state in local storage, route state, or form management stores across navigation events
- **Avoid (Anti-Pattern)**: Clear input values or unmount state when a user hits the back button
- **Rationale**: Losing typed data upon hitting the back button destroys user effort and causes extreme friction.
- **Practical Application**: Before: Hitting back clears all entered form fields. After: Returning to the form restores previously typed inputs from state cache.
- **Cited Sources (1)**: [2026-09-30](https://www.instagram.com/p/Dd6TWQ0hpfH/)

#### Mobile Viewport Overflow Prevention
- **Trigger Scenario**: Responsive web layouts viewed on mobile devices with constrained viewport widths
- **Guideline**: Audit and eliminate any elements or layout containers that extend horizontally beyond the primary viewport boundary.
- **Avoid (Anti-Pattern)**: Allow wide content blocks, unconstrained images, or fixed-width containers to force horizontal scrolling on mobile viewports.
- **Rationale**: Horizontal scrolling on mobile creates a broken, jarring user experience and indicates layout containment failure.
- **Practical Application**: Before: A fixed-width data table causing horizontal page panning. After: A responsive container with CSS overflow handling or stacked mobile representation.
- **Cited Sources (1)**: [2026-08-18](https://www.instagram.com/p/DcKiRe3TvdB/)

#### Non-UI Content Filtering
- **Trigger Scenario**: Any unstructured content intake or social media corpus ingestion pipeline
- **Guideline**: Filter out promotional creator metadata, personal branding hooks, and off-topic social captions that contain no interface design instructions.
- **Avoid (Anti-Pattern)**: Process non-design text, general marketing copy, or personal introduction statements through design rule extraction engines.
- **Rationale**: Ingesting non-design content contaminates design system guidelines with irrelevant noise, reducing the precision and reliability of the synthesized skill set.
- **Practical Application**: Before: Extracting principles from a general bio. After: Returning an empty array `[]` when no design context is present.
- **Cited Sources (1)**: [2026-09-03](https://www.instagram.com/p/Dc0ZxxvzdE8/)

#### OpenGraph Link Preview Asset Implementation
- **Trigger Scenario**: any web application URL or product link shared across social media or messaging platforms
- **Guideline**: Define explicit OpenGraph and Twitter card image metadata tags accompanied by a descriptive title and subtitle so shared links render a rich visual card instead of a generic placeholder frame.
- **Avoid (Anti-Pattern)**: Leave link metadata unconfigured, resulting in a fallback blank grey box or missing thumbnail when users share the application URL.
- **Rationale**: Missing link previews diminish perceived professional quality and reduce click-through rates on external platforms.
- **Practical Application**: Adding og:image, og:title, and twitter:image tags to the document head of the landing page.
- **Cited Sources (1)**: [2026-08-14](https://www.instagram.com/p/DcAKm8HBpCy/)

#### Persistent Mobile Conversion Action Bar
- **Trigger Scenario**: Mobile web layouts and responsive viewports where vertical scrolling spans multiple content sections.
- **Guideline**: Implement a pinned or sticky bottom action bar containing the primary conversion trigger on mobile viewports.
- **Avoid (Anti-Pattern)**: Force mobile users to scroll back to the top of long-form pages or hunt through navigation menus to complete a conversion action.
- **Rationale**: Mobile viewports have restricted vertical space; keeping the conversion trigger persistently accessible reduces interaction cost and friction.
- **Practical Application**: A sticky bottom bar featuring a 'Buy Now' button that remains anchored while scrolling through product details.
- **Cited Sources (1)**: [2026-08-30](https://www.instagram.com/p/DcEqXsySUaP/)

#### Skeleton Loaders for Perceived Performance
- **Trigger Scenario**: Any asynchronous content fetching or data-loading screen state
- **Guideline**: Replace generic spinning loaders with structural skeleton loaders that mirror the layout and dimensions of the incoming content.
- **Avoid (Anti-Pattern)**: Use generic spinning indicators or blank white screens for predictable layout content fetches.
- **Rationale**: Spinners create a sense of stalling and disconnect user focus, whereas structural skeletons provide a spatial preview that tricks the brain into perceiving faster load times.
- **Practical Application**: Before: Centered spinner icon. After: Gray pulsing placeholder blocks matching cards and text lines.
- **Cited Sources (1)**: [2026-09-16](https://www.instagram.com/p/DdXFTBoPEHn/)

---

## Source Posts Index

| Shortcode | Date | Type | Likes | Caption Summary | Reel Transcript Available | Link |
|---|---|---|---|---|---|---|
| `Dd6TWQ0hpfH` | 2026-09-30 | Video/Reel | 1,157 | Comment “POLISH” for the prompts + full 10+ i... | Yes | [View Post](https://www.instagram.com/p/Dd6TWQ0hpfH/) |
| `Ddv_d_sPx4l` | 2026-09-26 | Video/Reel | 4,345 | Do not publish your vibe coded website withou... | Yes | [View Post](https://www.instagram.com/p/Ddv_d_sPx4l/) |
| `DdfyNCptYtT` | 2026-09-20 | Video/Reel | 18 | You just vibe coded an app in 2 hours… but ca... | Yes | [View Post](https://www.instagram.com/p/DdfyNCptYtT/) |
| `DdcIywaBDtY` | 2026-09-18 | Video/Reel | 352 | Comment “DESIGN” to get the exact prompt rule... | Yes | [View Post](https://www.instagram.com/p/DdcIywaBDtY/) |
| `DdXFTBoPEHn` | 2026-09-16 | Video/Reel | 105 | 5 things you should be embarrassed to have in... | Yes | [View Post](https://www.instagram.com/p/DdXFTBoPEHn/) |
| `DcAKm8HBpCy` | 2026-08-14 | Video/Reel | 15 | Comment LAUNCH and I’ll send you my personal ... | Yes | [View Post](https://www.instagram.com/p/DcAKm8HBpCy/) |
| `DcCS0Z6oNfW` | 2026-08-15 | Video/Reel | 381 | Your vibe-coded app looks finished. It’s miss... | Yes | [View Post](https://www.instagram.com/p/DcCS0Z6oNfW/) |
| `DcEJDHBTyPY` | 2026-08-15 | Video/Reel | 84,093 | does your VIBECODED site have any of this ‼️🚨... | Yes | [View Post](https://www.instagram.com/p/DcEJDHBTyPY/) |
| `DcBqrPsR6BB` | 2026-08-14 | Video/Reel | 1,896 | Comment CHECK and I’ll DM you the 20 point ch... | No | [View Post](https://www.instagram.com/p/DcBqrPsR6BB/) |
| `DcC29Pdu02c` | 2026-08-15 | Video/Reel | 1,502 | Did I miss anything here?  #ai #vibecoding #b... | Yes | [View Post](https://www.instagram.com/p/DcC29Pdu02c/) |
| `DcCT3UfpFAn` | 2026-08-14 | Video/Reel | 2,735 | Am I missing anything this time?  P.S. This d... | Yes | [View Post](https://www.instagram.com/p/DcCT3UfpFAn/) |
| `DcEXXKGiIQ2` | 2026-08-15 | Video/Reel | 1,338 | Top 10 non negotiable things to add to your s... | Yes | [View Post](https://www.instagram.com/p/DcEXXKGiIQ2/) |
| `DcKiRe3TvdB` | 2026-08-18 | Video/Reel | 3,128 | 20 things to tell Claude to fix on your vibec... | Yes | [View Post](https://www.instagram.com/p/DcKiRe3TvdB/) |
| `DcDla-qRkoR` | 2026-08-15 | Video/Reel | 1,534 | Comment “checks” for the resource doc.  Promi... | Yes | [View Post](https://www.instagram.com/p/DcDla-qRkoR/) |
| `DcEqXsySUaP` | 2026-08-30 | Video/Reel | 1,713 | SAVE this checklist 🔖 + SHARE it with someone... | Yes | [View Post](https://www.instagram.com/p/DcEqXsySUaP/) |
| `DVyek2-kbZg` | 2026-03-12 | Video/Reel | 13,014 | Comment “website” and I’ll send you the promp... | Yes | [View Post](https://www.instagram.com/p/DVyek2-kbZg/) |
| `DcW5UU5SUaB` | 2026-08-22 | Video/Reel | 920 | If you find this useful please like and follo... | Yes | [View Post](https://www.instagram.com/p/DcW5UU5SUaB/) |
| `DctCXdSh0jc` | 2026-08-31 | Video/Reel | 2,209 | Comment “REJECTED” to get the full app launch... | Yes | [View Post](https://www.instagram.com/p/DctCXdSh0jc/) |
| `Dcq_kZlpGsQ` | 2026-09-10 | Video/Reel | 1,742 | Comment “Sued” for the full guide 🤝 #ai #clau... | Yes | [View Post](https://www.instagram.com/p/Dcq_kZlpGsQ/) |
| `DcwkX6OyduT` | 2026-09-02 | Video/Reel | 6,211 | Comment “UX” and follow for md instructions t... | Yes | [View Post](https://www.instagram.com/p/DcwkX6OyduT/) |
| `Dc0ZxxvzdE8` | 2026-09-03 | Video/Reel | 3,197 | Most people consume AI content.  I build with... | Yes | [View Post](https://www.instagram.com/p/Dc0ZxxvzdE8/) |
| `DdENScqokxH` | 2026-09-09 | Video/Reel | 541 | 20 hidden signs a website was vibecoded  1. v... | Yes | [View Post](https://www.instagram.com/p/DdENScqokxH/) |
| `DdP1ySxAsxT` | 2026-09-14 | Video/Reel | 6,821 | Vibe-coding is all fun and games until you ha... | Yes | [View Post](https://www.instagram.com/p/DdP1ySxAsxT/) |
| `DdFJTtMganO` | 2026-09-09 | Video/Reel | 2,636 | Did I miss anything? | Yes | [View Post](https://www.instagram.com/p/DdFJTtMganO/) |
| `DdQhclcxcL-` | 2026-09-15 | Video/Reel | 109 | Comment “Apple” for the full list 💬 | Yes | [View Post](https://www.instagram.com/p/DdQhclcxcL-/) |
