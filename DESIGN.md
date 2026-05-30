# Design

## Color Palette

All colors in OKLCH. Theme: dark by default — engineers using a recruitment tool typically work in low-ambient-light environments; dark backgrounds reduce eye strain.

### Neutral Ramp
- `--color-background`: `oklch(0.12 0.01 240)` — deep near-black with faint blue tint
- `--color-surface`: `oklch(0.17 0.01 240)` — elevated cards, forms
- `--color-surface-2`: `oklch(0.22 0.01 240)` — secondary surfaces, search panel
- `--color-border`: `oklch(0.28 0.01 240)` — subtle dividers
- `--color-ink`: `oklch(0.94 0.005 240)` — primary text (4.7:1 contrast on background)
- `--color-muted`: `oklch(0.60 0.01 240)` — secondary text, labels (4.5:1 contrast on background)

### Semantic
- `--color-accent`: `oklch(0.72 0.16 195)` — sharp teal-cyan; CTAs, focus states, highlights
- `--color-score-high`: `oklch(0.75 0.14 155)` — green for fit ≥7
- `--color-score-mid`: `oklch(0.78 0.13 75)` — amber for fit 5–6
- `--color-score-low`: `oklch(0.65 0.16 25)` — red-orange for fit <5
- `--color-error`: `oklch(0.65 0.16 25)` — same as score-low, for error states
- `--color-focus`: `--color-accent` — keyboard focus ring

## Typography

### Font Families
- **Headings**: Geist Sans (system-default fallback: `-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`)
- **Body**: Same as headings, weight 400
- **Monospace**: Geist Mono, for outreach message previews

### Scale (px)
- `--font-size-xs`: 12
- `--font-size-sm`: 14
- `--font-size-base`: 16
- `--font-size-lg`: 20
- `--font-size-xl`: 28
- `--font-size-2xl`: 36

### Weight
- **Regular**: 400 (body, secondary text)
- **Medium**: 500 (buttons, labels, section eyebrows — use sparingly)
- **Semibold**: 600 (card titles, small headings)
- **Bold**: 700 (page titles, hero headings)

### Line Height
- Body: 1.5
- Headings: 1.2
- Monospace (code blocks): 1.6

## Spacing

4px base unit. Consistent multiples: 8, 12, 16, 24, 32, 48, 64.

- Card padding: 24px
- Form fields: 12px vertical, 16px horizontal
- Gap between sections: 32px
- Margin from viewport edge: 16px (mobile), 24px (desktop)

## Components

### Cards
- Background: `--color-surface`
- Border: 1px `--color-border`
- Radius: 6px
- Padding: 24px
- Shadow: none (use border + bg contrast)

### Form Inputs & Selects
- Background: `--color-surface-2`
- Border: 1px `--color-border`
- Text: `--color-ink`
- Placeholder: `--color-muted`
- Radius: 6px
- Padding: 12px 16px
- Focus: 2px `--color-accent` focus ring (offset 2px)

### Buttons
- Primary: background `--color-accent`, text `--color-background`, radius 6px, padding 12px 24px
- Secondary: background transparent, border 1px `--color-border`, text `--color-ink`, radius 6px, padding 12px 24px
- Disabled: opacity 0.5, cursor not-allowed
- Hover: slight background lightening (10% opacity increase)

### Badges (Score Pills)
- Radius: 20px (pill shape)
- Padding: 8px 12px
- Font size: 12px, weight 600
- Use score colors: green / amber / red-orange

### Links
- Color: `--color-accent`
- Underline on hover
- Focus ring: 2px `--color-accent` (offset 2px)

## Motion

### Entrance Animations
- Search results (cards streaming in): fade-in + slide-up, 200ms ease-out
- Form focus states: background and border color transition, 150ms ease-out
- Button hover: background transition, 150ms ease-out

### Reduced Motion
All animations → instant (no transition).

## Layout Breakpoints

- Mobile: <640px
- Tablet: 640px–1024px
- Desktop: >1024px

## Responsive Patterns

- Search form: full width on mobile (max-width 100%), centered 600px on tablet+
- Results grid: 1 column on mobile, 2 on tablet+, 3 on large desktop (use `repeat(auto-fit, minmax(300px, 1fr))`)
- Cards: stretch full width on all breakpoints (no fixed widths)

## Components & Patterns

### Search Form
- Fieldset with 4 inputs (Industry, Country, Stage, Role Interest)
- Stacked vertically, 24px gap between groups
- Submit button: full width, primary style

### Founder Card (Result)
- Rank # (top-left): small, muted text
- Fit score badge (top-right): semantic color pill
- Founder name + company: heading + subheading
- Fit explanation: body text, 2–3 lines
- Divider: 1px `--color-border`
- Outreach message section: bg `--color-surface-2`, monospace font, full width pre-wrap
- Copy button: secondary style, positioned bottom-right

### Progress Feed (Streaming State)
- Spinner or animation (show progress of API calls)
- Status message: 16px body text, centered
- Progress indicator: optional step counter (e.g. "Step 2 of 5")

### Error State
- Error banner: background `--color-score-low` at 10% opacity, border 1px `--color-score-low`, rounded 6px
- Icon: centered
- Error message + code: heading + body, centered
- Retry button: secondary style

## Design Tokens

Export as CSS variables in `globals.css`:

```css
/* Palette */
--color-background: oklch(0.12 0.01 240);
--color-surface: oklch(0.17 0.01 240);
--color-surface-2: oklch(0.22 0.01 240);
--color-border: oklch(0.28 0.01 240);
--color-ink: oklch(0.94 0.005 240);
--color-muted: oklch(0.60 0.01 240);
--color-accent: oklch(0.72 0.16 195);
--color-score-high: oklch(0.75 0.14 155);
--color-score-mid: oklch(0.78 0.13 75);
--color-score-low: oklch(0.65 0.16 25);

/* Typography */
--font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
--font-mono: "Geist Mono", monospace;
--font-size-xs: 0.75rem;
--font-size-sm: 0.875rem;
--font-size-base: 1rem;
--font-size-lg: 1.25rem;
--font-size-xl: 1.75rem;
--font-size-2xl: 2.25rem;

/* Spacing */
--space-xs: 0.5rem;
--space-sm: 0.75rem;
--space-md: 1rem;
--space-lg: 1.5rem;
--space-xl: 2rem;
--space-2xl: 3rem;
--space-3xl: 4rem;

/* Radius */
--radius: 6px;
--radius-pill: 20px;
```
