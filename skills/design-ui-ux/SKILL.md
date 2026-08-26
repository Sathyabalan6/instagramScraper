---
name: design-ui-ux
description: "Actionable UI/UX design style guide covering Accessibility, Color, Hierarchy, Layout, Motion, Typography. Use this skill whenever creating, reshaping, critiquing, or reviewing UI/UX interfaces — including landing pages, dashboards, hero layouts, typography hierarchy, dark/light color palettes, interactive cards, navigation headers, and modal states — even if the user does not explicitly request 'design principles.'"
---

# UI/UX Design Skill

This style guide provides actionable, production-ready UI/UX rules distilled from leading design creators.
Use these principles to guide interface structure, component design, visual hierarchy, and accessibility audits.

## Spacing

_(none yet)_

## Color

### Bright Yellow and Royal Blue Complementary Pairing
- **Rule**: Pair high-luminance bright yellow alongside deep royal blue to maximize chromatic contrast and visual impact.
- **Why**: Leverages opposing chromatic temperatures and extreme value differences to create energetic, highly memorable focal zones.
- **Example**: Highlighting key notification badges in bright yellow against a solid royal blue navigation bar.
- **Consensus**: 🎯 **Creator Pattern** (Verified across 1 post(s) by @createwithalena)
- **Sources**: 1 post(s) (latest: 2026-08-18) — [@createwithalena](https://www.instagram.com/p/DcLuspGxuR0/)

### Earthy Olive and Tomato Red Contrast
- **Rule**: Pair muted olive green backgrounds or structural elements with high-saturation tomato red accents for focal elements.
- **Why**: Balances a grounded, natural neutral tone with a vibrant, high-attention chromatic pop to direct user focus effectively.
- **Example**: Using an olive green interface background with tomato red primary CTA buttons.
- **Consensus**: 🎯 **Creator Pattern** (Verified across 1 post(s) by @createwithalena)
- **Sources**: 1 post(s) (latest: 2026-08-18) — [@createwithalena](https://www.instagram.com/p/DcLuspGxuR0/)

### Espresso and Baby Pink Palette Pairing
- **Rule**: Combine deep espresso brown neutrals with soft, desaturated baby pink for balanced surface-to-content contrast.
- **Why**: Provides a high-contrast dark foundation while utilizing a delicate pastel accent to maintain visual softness and legibility.
- **Example**: Applying an espresso brown container background with baby pink typography or badge elements.
- **Consensus**: 🎯 **Creator Pattern** (Verified across 1 post(s) by @createwithalena)
- **Sources**: 1 post(s) (latest: 2026-08-18) — [@createwithalena](https://www.instagram.com/p/DcLuspGxuR0/)

## Typography

### Action-Oriented Modal Copywriting
- **Rule**: Replace vague interrogative titles with a direct verb-noun pairing (e.g., 'Delete folder') and clarify consequences using concise factual statements.
- **Why**: Explicit verb-noun headings and direct statements eliminate ambiguity about the exact system state change and its irreversibility.
- **Example**: Changing a modal header from 'Are you sure?' to 'Delete folder' accompanied by a subtext stating 'This action is irreversible.'
- **Consensus**: 🎯 **Creator Pattern** (Verified across 1 post(s) by @zanderwhitehurst)
- **Sources**: 1 post(s) (latest: 2024-09-23) — [@zanderwhitehurst](https://www.instagram.com/p/DAQf2QEAT7Z/)

### Ellipsis-Based Text Truncation for Grid Preservation
- **Rule**: Implement single-line or multi-line text truncation with an ellipsis (...) on dynamic text elements when they exceed the maximum width of their parent container.
- **Why**: Prevents unexpected text wrapping from pushing down adjacent UI elements, preserving the vertical rhythm and visual alignment of the layout.
- **Example**: A dashboard data table cell with a fixed width of 150px truncates a long product name like 'Premium Wireless Noise-Canceling Headphones' to 'Premium Wireless Noise-Can...' to keep the row height uniform.
- **Consensus**: 🎯 **Creator Pattern** (Verified across 1 post(s) by @designcode.io)
- **Sources**: 1 post(s) (latest: 2024-04-14) — [@designcode.io](https://www.instagram.com/p/C5vilGoN3iN/)

## Hierarchy

### Modal Action Button Labeling and Hierarchy
- **Rule**: Implement exactly two distinct actions using uncapitalized simple verb text for the primary confirm button and 'Cancel' for the secondary action.
- **Why**: Clear, standard button labels reduce cognitive load and prevent accidental destructive inputs by establishing unambiguous pathways to proceed or abort.
- **Example**: A button group featuring a solid-fill primary button labeled 'delete' next to an outline or ghost secondary button labeled 'cancel'.
- **Consensus**: 🎯 **Creator Pattern** (Verified across 1 post(s) by @zanderwhitehurst)
- **Sources**: 1 post(s) (latest: 2024-09-23) — [@zanderwhitehurst](https://www.instagram.com/p/DAQf2QEAT7Z/)

### X-Ray Outline Mode for Occluded Canvas Elements
- **Rule**: Implement a toggleable wireframe or outline rendering mode in canvas-based editing interfaces to expose and allow direct selection of occluded, clipped, or nested layers.
- **Why**: Prevents foreground elements from blocking interaction with background elements, reducing the interaction cost of selecting deeply nested or hidden layers without altering the layer stack.
- **Example**: In a graphic editor, a background vector shape is completely covered by a text box. Instead of manually hiding the text box in the layers panel, the user toggles outline mode to click and select the background shape directly on the canvas.
- **Consensus**: 🎯 **Creator Pattern** (Verified across 1 post(s) by @designcode.io)
- **Sources**: 1 post(s) (latest: 2024-04-21) — [@designcode.io](https://www.instagram.com/p/C6BkH0IIysY/)

## Motion

### Ambient Background Particle Motion
- **Rule**: Configure ambient UI particle animations with a low gravity scale (0.20), slow speed, and linear fade-out over a sustained lifetime (6 seconds) to maintain a non-distracting background layer.
- **Why**: Rapidly moving or abruptly disappearing elements draw involuntary user attention away from primary call-to-actions, whereas slow, fading, low-gravity motion preserves visual hierarchy.
- **Example**: A landing page hero section utilizing a subtle, floating sphere particle system with magenta-to-blue randomized coloring instead of a static, high-contrast background image.
- **Consensus**: 🎯 **Creator Pattern** (Verified across 1 post(s) by @designcode.io)
- **Sources**: 1 post(s) (latest: 2024-04-13) — [@designcode.io](https://www.instagram.com/p/C5s9_8tiV29/)

## Accessibility

### Dual-Trigger Access for Power Utilities
- **Rule**: Integrate a dual-trigger access pattern for complex utility modals, combining a right-click context menu action with a standardized keyboard shortcut (such as Cmd + R) to accommodate diverse user physical abilities and workflow speeds.
- **Why**: Providing both mouse-driven and keyboard-driven pathways reduces motor load, accommodates users with different accessibility needs, and accelerates high-frequency repetitive tasks for power users.
- **Example**: A layer list component where right-clicking a layer displays a 'Rename' option, which can also be instantly opened by pressing Cmd + R when the layer is focused.
- **Consensus**: 🎯 **Creator Pattern** (Verified across 1 post(s) by @designcode.io)
- **Sources**: 1 post(s) (latest: 2024-04-12) — [@designcode.io](https://www.instagram.com/p/C5qZEakL_SP/)

## Layout

### Confirmation Modal Structure and Text Alignment
- **Rule**: Organize confirmation modals into three distinct content blocks with left-aligned text to optimize scannability and readability.
- **Why**: Left-aligned text patterns align with natural reading habits, allowing users to process critical warning and action details faster than centered layouts.
- **Example**: A deletion warning modal structured with a top header containing a close icon, a left-aligned body containing a concise warning, and a bottom row for primary and secondary actions.
- **Consensus**: 🎯 **Creator Pattern** (Verified across 1 post(s) by @zanderwhitehurst)
- **Sources**: 1 post(s) (latest: 2024-09-23) — [@zanderwhitehurst](https://www.instagram.com/p/DAQf2QEAT7Z/)

### Fluid Component Resizing via Parent-Child Constraints
- **Rule**: Configure parent containers to dynamically wrap child elements using 'hug contents' while setting nested content layers to 'fill container' to ensure components scale fluidly across varying viewport widths.
- **Why**: Eliminates rigid, fixed-pixel dimensions that cause layout breakage, allowing components to automatically adapt to dynamic content lengths and screen sizes.
- **Example**: A button component with horizontal padding of 16px set to 'hug contents' automatically expands or contracts its width based on the length of the button label text.
- **Consensus**: 🎯 **Creator Pattern** (Verified across 1 post(s) by @designcode.io)
- **Sources**: 1 post(s) (latest: 2024-04-14) — [@designcode.io](https://www.instagram.com/p/C5vilGoN3iN/)

### Left-Aligned Typography for Single Alignment Anchors
- **Rule**: Left-align multi-line blocks of text and UI elements to establish a single vertical alignment anchor instead of using center-aligned text.
- **Why**: Center-aligned text creates multiple shifting alignment anchors across lines, forcing the user's eye to jump horizontally and increasing cognitive load during reading.
- **Example**: A product card featuring a center-aligned title, description, and price is updated to have all text elements left-aligned to a single vertical margin.
- **Consensus**: 🎯 **Creator Pattern** (Verified across 1 post(s) by @zanderwhitehurst)
- **Sources**: 1 post(s) (latest: 2026-08-19) — [@zanderwhitehurst](https://www.instagram.com/p/DcN2nJEu9L2/)

### Master-Template Card Grid Layout
- **Rule**: Standardize dynamic content feeds by designing a single master card template with fixed image aspect ratios and explicit text container constraints to maintain layout consistency across variable database inputs.
- **Why**: Ensures visual uniformity and prevents layout breaking or uneven card heights when dynamic content of varying lengths is loaded from a database.
- **Example**: A blog post repeater grid where every card maintains a strict 1:1 image aspect ratio, 16px internal padding, and a 2-line truncation limit for titles, ensuring all cards in the row align perfectly at the bottom.
- **Consensus**: 🎯 **Creator Pattern** (Verified across 1 post(s) by @designcode.io)
- **Sources**: 1 post(s) (latest: 2024-03-15) — [@designcode.io](https://www.instagram.com/p/C4hSKaWtaV7/)

### Tokenized Dynamic Input Fields
- **Rule**: Design batch-processing text inputs with adjacent, clickable variable tokens (such as original name or ascending/descending numbers) that inject dynamic placeholders directly into the input field at the current cursor position.
- **Why**: This layout pattern eliminates the need for users to memorize syntax or regular expressions, reducing input errors and cognitive friction during complex string formatting.
- **Example**: A batch-export modal featuring a text input for file naming, accompanied by a row of pill buttons labeled 'Date', 'Sequence', and 'Project Name' that insert dynamic variables into the input field when clicked.
- **Consensus**: 🎯 **Creator Pattern** (Verified across 1 post(s) by @designcode.io)
- **Sources**: 1 post(s) (latest: 2024-04-12) — [@designcode.io](https://www.instagram.com/p/C5qZEakL_SP/)

### Whitespace Over Line Borders for Layout Separation
- **Rule**: Eliminate structural border lines between content containers and rely exclusively on negative space to establish grouping and hierarchy.
- **Why**: Removing visual clutter prevents interfaces from looking overly dense or resembling spreadsheets, reducing cognitive load and improving scannability.
- **Example**: Replacing card component borders and internal divider lines with uniform padding and generous margins.
- **Consensus**: 🎯 **Creator Pattern** (Verified across 1 post(s) by @zanderwhitehurst)
- **Sources**: 1 post(s) (latest: 2026-07-21) — [@zanderwhitehurst](https://www.instagram.com/p/DbDaptQscRR/)
