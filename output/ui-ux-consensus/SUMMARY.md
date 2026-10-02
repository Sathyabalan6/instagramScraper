# Design Skill Extraction Report: @ui-ux-consensus

> **Creator Profile:** [@ui-ux-consensus](https://www.instagram.com/ui-ux-consensus/)  
> **Extracted:** 2026-10-02 16:23:57  
> **Analyzed Post Range:** 2024-03-09 to 2026-09-30

---

## Overview & Extraction Metrics

| Metric | Count |
|---|---|
| **Total Posts Analyzed** | `55` |
| **Video Reels Transcribed** | `38` / `49` |
| **Unique Design Principles** | `30` |
| **Active Categories** | `6` / `7` |
| **Extraction Engine** | `LLM Analysis (No Templates)` |

### Category Distribution

| Category | Principles Extracted |
|---|---|
| **Color** | `4` principle(s) |
| **Typography** | `1` principle(s) |
| **Hierarchy** | `4` principle(s) |
| **Motion** | `5` principle(s) |
| **Accessibility** | `6` principle(s) |
| **Layout** | `10` principle(s) |

---

## Distilled Design Principles

### Color

#### Bright Yellow and Royal Blue Complementary Pairing
- **Guideline**: Pair high-luminance bright yellow alongside deep royal blue to maximize chromatic contrast and visual impact.
- **Rationale**: Leverages opposing chromatic temperatures and extreme value differences to create energetic, highly memorable focal zones.
- **Practical Application**: Highlighting key notification badges in bright yellow against a solid royal blue navigation bar.
- **Cited Sources (1)**: [2026-08-18](https://www.instagram.com/p/DcLuspGxuR0/)

#### Earthy Olive and Tomato Red Contrast
- **Guideline**: Pair muted olive green backgrounds or structural elements with high-saturation tomato red accents for focal elements.
- **Rationale**: Balances a grounded, natural neutral tone with a vibrant, high-attention chromatic pop to direct user focus effectively.
- **Practical Application**: Using an olive green interface background with tomato red primary CTA buttons.
- **Cited Sources (1)**: [2026-08-18](https://www.instagram.com/p/DcLuspGxuR0/)

#### Espresso and Baby Pink Palette Pairing
- **Guideline**: Combine deep espresso brown neutrals with soft, desaturated baby pink for balanced surface-to-content contrast.
- **Rationale**: Provides a high-contrast dark foundation while utilizing a delicate pastel accent to maintain visual softness and legibility.
- **Practical Application**: Applying an espresso brown container background with baby pink typography or badge elements.
- **Cited Sources (1)**: [2026-08-18](https://www.instagram.com/p/DcLuspGxuR0/)

#### Theme State Persistence on Back Navigation
- **Guideline**: Maintain consistent color token values and contrast ratios across dark and light mode transitions to prevent unreadable text states.
- **Rationale**: Abrupt theme switches can cause foreground text to blend into newly loaded backgrounds, breaking legibility.
- **Practical Application**: Using dynamic CSS custom properties (e.g., var(--text-primary)) that update cleanly without orphan color dependencies.
- **Cited Sources (1)**: [2026-09-30](https://www.instagram.com/p/Dd6TWQ0hpfH/)

### Typography

#### Ellipsis-Based Text Truncation for Grid Preservation
- **Guideline**: Implement single-line or multi-line text truncation with an ellipsis (...) on dynamic text elements when they exceed the maximum width of their parent container.
- **Rationale**: Prevents unexpected text wrapping from pushing down adjacent UI elements, preserving the vertical rhythm and visual alignment of the layout.
- **Practical Application**: A dashboard data table cell with a fixed width of 150px truncates a long product name like 'Premium Wireless Noise-Canceling Headphones' to 'Premium Wireless Noise-Can...' to keep the row height uniform.
- **Cited Sources (1)**: [2024-04-14](https://www.instagram.com/p/C5vilGoN3iN/)

### Hierarchy

#### Form Submission Feedback States
- **Guideline**: Provide explicit, visible success and error messaging components immediately following user form interactions.
- **Rationale**: Prevents user confusion and uncertainty by confirming system status or clearly highlighting required corrections.
- **Practical Application**: Before: Form clears silently on error.
After: Inline red error alert displays above the submit button stating 'Please enter a valid email address.'
- **Cited Sources (1)**: [2026-08-18](https://www.instagram.com/p/DcKiRe3TvdB/)

#### Single Primary Call-to-Action
- **Guideline**: Designate one dominant, high-contrast visual action per view to guide user conversion and minimize cognitive load.
- **Rationale**: Multiple competing primary buttons cause decision fatigue and slow down user progression.
- **Practical Application**: Style the primary 'Create Account' action as a filled solid brand button while secondary 'Sign In' is styled as a low-emphasis ghost button.
- **Cited Sources (1)**: [2026-09-09](https://www.instagram.com/p/DdFJTtMganO/)

#### User-Friendly Error Notification Toasts
- **Guideline**: Replace raw technical error logs or undefined strings with contextual, human-readable notification toasts.
- **Rationale**: Exposing raw database errors creates cognitive overload and damages product trust.
- **Practical Application**: Displaying 'Something went wrong saving your changes. Try again.' instead of 'Error: TypeError: undefined at Object...'
- **Cited Sources (1)**: [2026-09-30](https://www.instagram.com/p/Dd6TWQ0hpfH/)

#### X-Ray Outline Mode for Occluded Canvas Elements
- **Guideline**: Implement a toggleable wireframe or outline rendering mode in canvas-based editing interfaces to expose and allow direct selection of occluded, clipped, or nested layers.
- **Rationale**: Prevents foreground elements from blocking interaction with background elements, reducing the interaction cost of selecting deeply nested or hidden layers without altering the layer stack.
- **Practical Application**: In a graphic editor, a background vector shape is completely covered by a text box. Instead of manually hiding the text box in the layers panel, the user toggles outline mode to click and select the background shape directly on the canvas.
- **Cited Sources (1)**: [2024-04-21](https://www.instagram.com/p/C6BkH0IIysY/)

### Motion

#### Ambient Background Particle Motion
- **Guideline**: Configure ambient UI particle animations with a low gravity scale (0.20), slow speed, and linear fade-out over a sustained lifetime (6 seconds) to maintain a non-distracting background layer.
- **Rationale**: Rapidly moving or abruptly disappearing elements draw involuntary user attention away from primary call-to-actions, whereas slow, fading, low-gravity motion preserves visual hierarchy.
- **Practical Application**: A landing page hero section utilizing a subtle, floating sphere particle system with magenta-to-blue randomized coloring instead of a static, high-contrast background image.
- **Cited Sources (1)**: [2024-04-13](https://www.instagram.com/p/C5s9_8tiV29/)

#### Immediate Touch Feedback for Interactive Elements
- **Guideline**: Trigger instant visual state changes (like scale or color shifts) on every tap, executing heavy tasks asynchronously.
- **Rationale**: Immediate visual confirmation reassures the user that their input was registered, eliminating perceived lag.
- **Practical Application**: An action button shows a pressed/active state instantly while the network request is handled in the background.
- **Alternate Creator Perspectives & Implementations**:
  - *Perspective (@julianxuofficial)*: Provide instantaneous visual and haptic feedback when a user touches or clicks an interactive surface.
    - *Implementation*: Scale a button down to 98% and trigger a light haptic pulse immediately upon touch down.
- **Cited Sources (2)**: [2026-09-16](https://www.instagram.com/p/DdXFTBoPEHn/), [2026-09-15](https://www.instagram.com/p/DdQhclcxcL-/)

#### Interactive Tap Debouncing
- **Guideline**: Disable action triggers immediately upon activation to prevent duplicate submissions or purchases from rapid double-tapping.
- **Rationale**: Rapid or impatient double-taps cause unintended duplicate requests, leading to user frustration and state corruption.
- **Practical Application**: Button component enters a disabled loading state on first tap: onClick={() => { setLoading(true); submitForm(); }}
- **Cited Sources (1)**: [2026-09-30](https://www.instagram.com/p/Dd6TWQ0hpfH/)

#### Low-Latency Interface Interaction Response
- **Guideline**: Ensure all interactive UI feedback and state changes execute within 400 milliseconds.
- **Rationale**: Faster response times keep users feeling in control and prevent the application from feeling sluggish or unresponsive.
- **Practical Application**: Button press triggers an immediate loading spinner or state change within 200ms rather than a delayed network block.
- **Cited Sources (1)**: [2026-09-02](https://www.instagram.com/p/DcwkX6OyduT/)

#### Physics-Based Spring Animations
- **Guideline**: Utilize spring physics curves instead of linear or basic ease-in-out transitions for UI state changes.
- **Rationale**: Spring animations mimic natural real-world physics, making interfaces feel tactile, responsive, and organic.
- **Practical Application**: Apply a damping ratio of 0.8 and response time of 300ms to modal popups instead of a static linear fade.
- **Cited Sources (1)**: [2026-09-15](https://www.instagram.com/p/DdQhclcxcL-/)

### Accessibility

#### Accessible Text Color Contrast
- **Guideline**: Ensure all text elements meet minimum contrast ratios against their background to support users with visual impairments.
- **Rationale**: Sufficient contrast prevents eye strain and ensures content is legible for users with low vision or when viewing screens in bright sunlight.
- **Practical Application**: Change secondary gray text from #A0A0A0 to #595959 on a white background to achieve a 4.5:1 contrast ratio.
- **Cited Sources (1)**: [2026-09-09](https://www.instagram.com/p/DdFJTtMganO/)

#### Dual-Trigger Access for Power Utilities
- **Guideline**: Integrate a dual-trigger access pattern for complex utility modals, combining a right-click context menu action with a standardized keyboard shortcut (such as Cmd + R) to accommodate diverse user physical abilities and workflow speeds.
- **Rationale**: Providing both mouse-driven and keyboard-driven pathways reduces motor load, accommodates users with different accessibility needs, and accelerates high-frequency repetitive tasks for power users.
- **Practical Application**: A layer list component where right-clicking a layer displays a 'Rename' option, which can also be instantly opened by pressing Cmd + R when the layer is focused.
- **Cited Sources (1)**: [2024-04-12](https://www.instagram.com/p/C5qZEakL_SP/)

#### Human-Readable Fallback Error States
- **Guideline**: Intercept raw system exceptions (404, 500, stack traces) and display an actionable recovery message with clear next steps.
- **Rationale**: Technical error codes cause confusion and erode trust, whereas plain-language instructions guide the user toward recovery.
- **Practical Application**: Instead of 'Error 500: SQL Timeout', show 'We're having trouble connecting. Try again in a moment.' with a retry button.
- **Cited Sources (1)**: [2026-09-16](https://www.instagram.com/p/DdXFTBoPEHn/)

#### Informative Image Alternative Text
- **Guideline**: Provide descriptive alt attributes for all meaningful images to support screen reader users.
- **Rationale**: Screen readers rely on alt text to convey the content and function of images to users who cannot see them.
- **Practical Application**: Update `<img src="avatar.png">` to `<img src="avatar.png" alt="Profile portrait of Jane Doe">`.
- **Cited Sources (1)**: [2026-09-09](https://www.instagram.com/p/DdFJTtMganO/)

#### Interactive Contact Triggers
- **Guideline**: Convert text-based phone numbers and email addresses into active tel: and mailto: hyperlinks to enable direct device action.
- **Rationale**: Reduces user friction by eliminating the need to manually copy and paste contact details into external applications on mobile devices.
- **Practical Application**: Before: <span>Call us at 555-0199</span>
After: <a href="tel:5550199">Call us at 555-0199</a>
- **Cited Sources (1)**: [2026-08-18](https://www.instagram.com/p/DcKiRe3TvdB/)

#### Reduced Motion Preference Compliance
- **Guideline**: Disable or substitute motion-heavy transitions when the operating system's reduced motion setting is enabled.
- **Rationale**: Abrupt or scaling animations can trigger vestibular disorders, dizziness, or nausea for sensitive users.
- **Practical Application**: Wrap expansive zoom transitions in `@media (prefers-reduced-motion: no-preference)` queries.
- **Cited Sources (1)**: [2026-09-15](https://www.instagram.com/p/DdQhclcxcL-/)

### Layout

#### Above-the-Fold Primary Call to Action
- **Guideline**: Position the primary conversion action within the initial viewport so it is visible without requiring vertical scrolling.
- **Rationale**: Maximizes conversion potential by capturing immediate user intent before they scroll past the hero section.
- **Practical Application**: Before: CTA placed at the bottom of a long landing page hero.
After: Primary 'Get Started' button anchored directly beside the main hero headline inside the 100vh container.
- **Cited Sources (1)**: [2026-08-30](https://www.instagram.com/p/DcEqXsySUaP/)

#### Client-Side Input State Caching
- **Guideline**: Persist form input states and user entries locally on page or route transitions so data is not lost when hitting the back button.
- **Rationale**: Losing typed inputs upon navigating backward causes severe user friction and forces repetitive data entry.
- **Practical Application**: Autosaving form state to sessionStorage or localStorage on input change events.
- **Cited Sources (1)**: [2026-09-30](https://www.instagram.com/p/Dd6TWQ0hpfH/)

#### Dedicated 404 Error State Design
- **Guideline**: Provide a fully styled, custom 404 error page complete with navigation pathways back to primary site sections rather than falling back to unstyled server defaults.
- **Rationale**: Prevents user disorientation and abandonment when encountering broken URLs or deprecated links by offering immediate re-engagement options.
- **Practical Application**: Before: Browser default white screen with 'Server Not Found'. After: A branded illustration, search bar, and direct links to Home, Pricing, and Support.
- **Cited Sources (1)**: [2026-08-14](https://www.instagram.com/p/DcBqrPsR6BB/)

#### Fixed Primary CTA Positioning in Stepper Flows
- **Guideline**: Anchor the primary progression button (e.g., 'Continue') to the exact same screen coordinates across every step of an onboarding flow.
- **Rationale**: Maintaining spatial consistency builds muscle memory, allowing users to progress rapidly without visually searching for the button.
- **Practical Application**: Pin the primary 'Next' button to the bottom sticky container across all 4 onboarding screens.
- **Cited Sources (1)**: [2026-09-16](https://www.instagram.com/p/DdXFTBoPEHn/)

#### Fluid Component Resizing via Parent-Child Constraints
- **Guideline**: Configure parent containers to dynamically wrap child elements using 'hug contents' while setting nested content layers to 'fill container' to ensure components scale fluidly across varying viewport widths.
- **Rationale**: Eliminates rigid, fixed-pixel dimensions that cause layout breakage, allowing components to automatically adapt to dynamic content lengths and screen sizes.
- **Practical Application**: A button component with horizontal padding of 16px set to 'hug contents' automatically expands or contracts its width based on the length of the button label text.
- **Cited Sources (1)**: [2024-04-14](https://www.instagram.com/p/C5vilGoN3iN/)

#### Master-Template Card Grid Layout
- **Guideline**: Standardize dynamic content feeds by designing a single master card template with fixed image aspect ratios and explicit text container constraints to maintain layout consistency across variable database inputs.
- **Rationale**: Ensures visual uniformity and prevents layout breaking or uneven card heights when dynamic content of varying lengths is loaded from a database.
- **Practical Application**: A blog post repeater grid where every card maintains a strict 1:1 image aspect ratio, 16px internal padding, and a 2-line truncation limit for titles, ensuring all cards in the row align perfectly at the bottom.
- **Cited Sources (1)**: [2024-03-15](https://www.instagram.com/p/C4hSKaWtaV7/)

#### Persistent Mobile Conversion Anchor
- **Guideline**: Implement a sticky bottom bar housing the primary conversion action on mobile viewports.
- **Rationale**: Keeps the primary conversion goal accessible at all times on small screens, preventing the user from needing to scroll back up to convert.
- **Practical Application**: Before: Static CTA that scrolls away with the content.
After: position: fixed; bottom: 0; width: 100%; z-index: 100; container holding a full-width purchase button.
- **Cited Sources (1)**: [2026-08-30](https://www.instagram.com/p/DcEqXsySUaP/)

#### Skeleton Screen Content Placeholders
- **Guideline**: Replace generic spinners with structural skeleton loaders that mimic the dimensions and layout of the incoming content.
- **Rationale**: Mimicking the final layout shape reduces perceived waiting time and prevents layout shifts when data resolves.
- **Practical Application**: Instead of a centered spinner, display grey pulsing rectangular blocks where cards or lists will load.
- **Cited Sources (1)**: [2026-09-16](https://www.instagram.com/p/DdXFTBoPEHn/)

#### Tokenized Dynamic Input Fields
- **Guideline**: Design batch-processing text inputs with adjacent, clickable variable tokens (such as original name or ascending/descending numbers) that inject dynamic placeholders directly into the input field at the current cursor position.
- **Rationale**: This layout pattern eliminates the need for users to memorize syntax or regular expressions, reducing input errors and cognitive friction during complex string formatting.
- **Practical Application**: A batch-export modal featuring a text input for file naming, accompanied by a row of pill buttons labeled 'Date', 'Sequence', and 'Project Name' that insert dynamic variables into the input field when clicked.
- **Cited Sources (1)**: [2024-04-12](https://www.instagram.com/p/C5qZEakL_SP/)

#### Viewport Auto-Scrolling for Active Inputs
- **Guideline**: Ensure focused input fields automatically scroll into view above the software keyboard when the virtual keyboard expands.
- **Rationale**: When keyboards obscure input fields, users cannot see what they are typing, leading to input errors and abandonment.
- **Practical Application**: Applying scrollIntoView({ behavior: 'smooth', block: 'center' }) on input focus events within mobile viewports.
- **Cited Sources (1)**: [2026-09-30](https://www.instagram.com/p/Dd6TWQ0hpfH/)

---

## Source Posts Index

| Shortcode | Date | Type | Likes | Caption Summary | Reel Transcript Available | Link |
|---|---|---|---|---|---|---|
| `Dd6TWQ0hpfH` | 2026-09-30 | Video/Reel | 1,157 | Comment “POLISH” for the prompts + full 10+ i... | Yes | [View Post](https://www.instagram.com/p/Dd6TWQ0hpfH/) |
| `Ddv_d_sPx4l` | 2026-09-26 | Video/Reel | 4,345 | Do not publish your vibe coded website withou... | Yes | [View Post](https://www.instagram.com/p/Ddv_d_sPx4l/) |
| `DdfyNCptYtT` | 2026-09-20 | Video/Reel | 18 | You just vibe coded an app in 2 hours… but ca... | Yes | [View Post](https://www.instagram.com/p/DdfyNCptYtT/) |
| `DdcIywaBDtY` | 2026-09-18 | Video/Reel | 352 | Comment “DESIGN” to get the exact prompt rule... | No | [View Post](https://www.instagram.com/p/DdcIywaBDtY/) |
| `DdXFTBoPEHn` | 2026-09-16 | Video/Reel | 105 | 5 things you should be embarrassed to have in... | No | [View Post](https://www.instagram.com/p/DdXFTBoPEHn/) |
| `DcAKm8HBpCy` | 2026-08-14 | Video/Reel | 15 | Comment LAUNCH and I’ll send you my personal ... | Yes | [View Post](https://www.instagram.com/p/DcAKm8HBpCy/) |
| `DcCS0Z6oNfW` | 2026-08-15 | Video/Reel | 381 | Your vibe-coded app looks finished. It’s miss... | Yes | [View Post](https://www.instagram.com/p/DcCS0Z6oNfW/) |
| `DcEJDHBTyPY` | 2026-08-15 | Video/Reel | 84,093 | does your VIBECODED site have any of this ‼️🚨... | Yes | [View Post](https://www.instagram.com/p/DcEJDHBTyPY/) |
| `DcBqrPsR6BB` | 2026-08-14 | Video/Reel | 1,896 | Comment CHECK and I’ll DM you the 20 point ch... | No | [View Post](https://www.instagram.com/p/DcBqrPsR6BB/) |
| `DcC29Pdu02c` | 2026-08-15 | Video/Reel | 1,502 | Did I miss anything here?  #ai #vibecoding #b... | Yes | [View Post](https://www.instagram.com/p/DcC29Pdu02c/) |
| `DcCT3UfpFAn` | 2026-08-14 | Video/Reel | 2,735 | Am I missing anything this time?  P.S. This d... | Yes | [View Post](https://www.instagram.com/p/DcCT3UfpFAn/) |
| `DcEXXKGiIQ2` | 2026-08-15 | Video/Reel | 1,338 | Top 10 non negotiable things to add to your s... | Yes | [View Post](https://www.instagram.com/p/DcEXXKGiIQ2/) |
| `DcKiRe3TvdB` | 2026-08-18 | Video/Reel | 3,128 | 20 things to tell Claude to fix on your vibec... | Yes | [View Post](https://www.instagram.com/p/DcKiRe3TvdB/) |
| `DcDla-qRkoR` | 2026-08-15 | Video/Reel | 1,534 | Comment “checks” for the resource doc.  Promi... | Yes | [View Post](https://www.instagram.com/p/DcDla-qRkoR/) |
| `DcEqXsySUaP` | 2026-08-30 | Video/Reel | 1,713 | SAVE this checklist 🔖 + SHARE it with someone... | No | [View Post](https://www.instagram.com/p/DcEqXsySUaP/) |
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
| `DZGrND4MUnK` | 2026-06-03 | Video/Reel | 4,899 | Everything changed when I stopped treating my... | Yes | [View Post](https://www.instagram.com/p/DZGrND4MUnK/) |
| `DY9sP2mRaAC` | 2026-05-30 | Video/Reel | 63,443 | twenty browser tabs. three Pinterest boards. ... | Yes | [View Post](https://www.instagram.com/p/DY9sP2mRaAC/) |
| `DWhfBXjEiWw` | 2026-03-31 | Video/Reel | 81,838 | Student me was so rude. I would judge every b... | Yes | [View Post](https://www.instagram.com/p/DWhfBXjEiWw/) |
| `DcYkbAmxGO0` | 2026-08-23 | Video/Reel | 18,475 | Which design combo caught ur eye? My fav is c... | Yes | [View Post](https://www.instagram.com/p/DcYkbAmxGO0/) |
| `DcV-btTxYvs` | 2026-08-22 | Video/Reel | 8,079 | Which one was the reminder u needed? :) 4 des... | Yes | [View Post](https://www.instagram.com/p/DcV-btTxYvs/) |
| `DcTafpORYeq` | 2026-08-21 | Video/Reel | 2,135 | #ad Agent is in open beta and available on ev... | No | [View Post](https://www.instagram.com/p/DcTafpORYeq/) |
| `DcOTR60RuoI` | 2026-08-19 | Video/Reel | 711 | if you’ve scrolled all the way down ur font l... | Yes | [View Post](https://www.instagram.com/p/DcOTR60RuoI/) |
| `DcLuspGxuR0` | 2026-08-18 | Video/Reel | 7,699 | Have u tried any of these color combos before... | Yes | [View Post](https://www.instagram.com/p/DcLuspGxuR0/) |
| `DcJHlWIRerH` | 2026-08-17 | Video/Reel | 6,236 | Which one’s your fav? Patterns to use or spar... | Yes | [View Post](https://www.instagram.com/p/DcJHlWIRerH/) |
| `DcD9lX-RTNH` | 2026-08-15 | Video/Reel | 301 | I thought being a perfectionist meant I was a... | Yes | [View Post](https://www.instagram.com/p/DcD9lX-RTNH/) |
| `C6BkH0IIysY` | 2024-04-21 | Video/Reel | 25 | View Layout Outlines helps with the visual hi... | Yes | [View Post](https://www.instagram.com/p/C6BkH0IIysY/) |
| `C5yHa4ZtC6A` | 2024-04-15 | Video/Reel | 17 | Design tip: use placeholder UI and content ge... | Yes | [View Post](https://www.instagram.com/p/C5yHa4ZtC6A/) |
| `C5vilGoN3iN` | 2024-04-14 | Video/Reel | 12 | Hug content and resizing in Figma design tips... | Yes | [View Post](https://www.instagram.com/p/C5vilGoN3iN/) |
| `C5s9_8tiV29` | 2024-04-13 | Video/Reel | 14 | How to create particles in Spline tool   #3da... | Yes | [View Post](https://www.instagram.com/p/C5s9_8tiV29/) |
| `C5qZEakL_SP` | 2024-04-12 | Video/Reel | 10 | Rename all layers at once in Figma + tricks  ... | Yes | [View Post](https://www.instagram.com/p/C5qZEakL_SP/) |
| `C5lPdvIs__L` | 2024-04-10 | Image/Carousel | 15 | Using a design system can speed up your desig... | No | [View Post](https://www.instagram.com/p/C5lPdvIs__L/) |
| `C5hiW5lNM-n` | 2024-04-09 | Image/Carousel | 28 | Tesla desktop app concept 👀   #figmaappdesign... | No | [View Post](https://www.instagram.com/p/C5hiW5lNM-n/) |
| `C5du0TZs7W3` | 2024-04-07 | Image/Carousel | 35 | Spice up your designs with a dash of 3D eleme... | No | [View Post](https://www.instagram.com/p/C5du0TZs7W3/) |
| `C5AEBsNte9V` | 2024-03-27 | Video/Reel | 22 | Create this realistic UI from scratch in Figm... | No | [View Post](https://www.instagram.com/p/C5AEBsNte9V/) |
| `C4xZRqDMVPw` | 2024-03-21 | Image/Carousel | 15 | E-commerce web app design. Learn to design th... | No | [View Post](https://www.instagram.com/p/C4xZRqDMVPw/) |
| `C4uCdwnN53z` | 2024-03-20 | Image/Carousel | 14 | Midjourney UI design workflow. full course: h... | No | [View Post](https://www.instagram.com/p/C4uCdwnN53z/) |
| `C4sPrgWON95` | 2024-03-19 | Video/Reel | 16 | A very shiny card in SwiftUI  #appdevelopment... | Yes | [View Post](https://www.instagram.com/p/C4sPrgWON95/) |
| `C4rv-G8NyhZ` | 2024-03-19 | Video/Reel | 17 | I made a 3d card with a liquid action button ... | Yes | [View Post](https://www.instagram.com/p/C4rv-G8NyhZ/) |
| `C4rdqKGtYuS` | 2024-03-19 | Video/Reel | 14 | Translucent UI using the back camera #appdeve... | Yes | [View Post](https://www.instagram.com/p/C4rdqKGtYuS/) |
| `C4mLuJHqJlJ` | 2024-03-17 | Video/Reel | 17 | Will developers cry if we made this in Figma?... | No | [View Post](https://www.instagram.com/p/C4mLuJHqJlJ/) |
| `C4kBl_lydOk` | 2024-03-16 | Video/Reel | 34 | 🚀 Dive into web design with ZERO experience —... | No | [View Post](https://www.instagram.com/p/C4kBl_lydOk/) |
| `C4hSKaWtaV7` | 2024-03-15 | Video/Reel | 11 | Tired of designing the same layout over and o... | No | [View Post](https://www.instagram.com/p/C4hSKaWtaV7/) |
| `C4euDzYNphB` | 2024-03-14 | Video/Reel | 8 | Radial gradients are a powerful tool for crea... | No | [View Post](https://www.instagram.com/p/C4euDzYNphB/) |
| `C4dWIqbvi1g` | 2024-03-13 | Image/Carousel | 12 | how should we code this? 👀 #uidesign #figmade... | No | [View Post](https://www.instagram.com/p/C4dWIqbvi1g/) |
| `C4SMwwNrw29` | 2024-03-09 | Video/Reel | 8 | Design a heart icon using path and angular gr... | No | [View Post](https://www.instagram.com/p/C4SMwwNrw29/) |
