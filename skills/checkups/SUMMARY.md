# Design Skill Extraction Report: @checkups

> **Creator Profile:** [@checkups](https://www.instagram.com/checkups/)  
> **Extracted:** 2026-10-02 16:23:56  
> **Analyzed Post Range:** 2026-03-12 to 2026-09-30

---

## Overview & Extraction Metrics

| Metric | Count |
|---|---|
| **Total Posts Analyzed** | `25` |
| **Video Reels Transcribed** | `21` / `25` |
| **Unique Design Principles** | `20` |
| **Active Categories** | `5` / `7` |
| **Extraction Engine** | `LLM Analysis (No Templates)` |

### Category Distribution

| Category | Principles Extracted |
|---|---|
| **Color** | `1` principle(s) |
| **Hierarchy** | `3` principle(s) |
| **Motion** | `4` principle(s) |
| **Accessibility** | `5` principle(s) |
| **Layout** | `7` principle(s) |

---

## Distilled Design Principles

### Color

#### Theme State Persistence on Back Navigation
- **Guideline**: Maintain consistent color token values and contrast ratios across dark and light mode transitions to prevent unreadable text states.
- **Rationale**: Abrupt theme switches can cause foreground text to blend into newly loaded backgrounds, breaking legibility.
- **Practical Application**: Using dynamic CSS custom properties (e.g., var(--text-primary)) that update cleanly without orphan color dependencies.
- **Cited Sources (1)**: [2026-09-30](https://www.instagram.com/p/Dd6TWQ0hpfH/)

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

### Motion

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
