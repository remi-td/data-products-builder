# Styling & Theming

The skill ships with a Teradata-branded theme. Users can swap it in two
ways without forking the frontend.

## Theme model

Three layers, in order of precedence:

1. **Tokens** — CSS variables in `src/theme/brand.css`. Single source of
   truth for color, font stack, radius, spacing scale.
2. **Tailwind theme** — `tailwind.config.js` maps utility classes
   (`bg-brand-orange`) onto the tokens.
3. **Component classes** — components use only Tailwind utilities; they
   never hard-code hex values.

Because everything resolves through tokens, replacing `brand.css`
re-skins the whole app.

## How a user customizes

### Option A — drop-in stylesheet

The user provides a `brand.css` (or any name). Import it in
`src/main.tsx` *after* the default theme:

```tsx
import "./theme/brand.css";       // defaults
import "./theme/customer.css";    // overrides — last wins
```

The customer file only needs the variables it changes:

```css
:root {
  --brand-orange: #2563EB;        /* customer blue */
  --brand-navy:   #0F172A;
}
```

### Option B — token JSON

Agents can also be handed a JSON file:

```json
{
  "brand-orange": "#2563EB",
  "brand-navy":   "#0F172A",
  "font-sans":    "Inter, sans-serif"
}
```

The agent rewrites `brand.css` from the JSON. See `templates/frontend/`
for the `scripts/apply-theme.mjs` helper.

### Option C — guideline document

If the user uploads a brand PDF or guidelines doc, the agent extracts:
- primary / secondary colors (hex)
- accent / status colors
- font family (and fallback)
- corner radius style (sharp vs. rounded)

…and writes a `brand.css` accordingly. Confirm extracted values with
the user before applying.

## Teradata default tokens

| Token             | Value     | Use                                   |
|-------------------|-----------|---------------------------------------|
| `--brand-orange`  | `#FF5F02` | Primary CTA, focus, key chart series  |
| `--brand-navy`    | `#00233C` | Headings, sidebar, secondary chart    |
| `--brand-bg`      | `#FFFFFF` | Page background                       |
| `--brand-fg`      | `#00233C` | Body text                             |
| `--brand-muted`   | `#64748B` | Captions, secondary text              |
| Font              | `Inter`   | Body + UI; system-ui fallback         |

These match the `teradata-brand` skill. See that skill for logo files
and full guidelines.

## Chart palette

Use a **palette token array** for chart series, never raw hex:

```css
:root {
  --chart-1: var(--brand-orange);
  --chart-2: var(--brand-navy);
  --chart-3: #0EA5E9;
  --chart-4: #10B981;
  --chart-5: #A855F7;
}
```

```tsx
const PALETTE = ["var(--chart-1)","var(--chart-2)","var(--chart-3)","var(--chart-4)","var(--chart-5)"];
```

## Dark mode

Toggle via `class="dark"` on `<html>`. Tokens redefine under `.dark`:

```css
.dark {
  --brand-bg: #0B1320;
  --brand-fg: #F8FAFC;
  --brand-muted: #94A3B8;
}
```

## What not to do

- Don't import a UI framework with its own theme system (MUI, Chakra,
  Ant). They fight Tailwind tokens and bloat bundles.
- Don't inline styles (`style={{...}}`) except for dynamic positional
  values.
- Don't write component-scoped CSS modules. Tailwind utilities + tokens
  cover 99% of cases and keep agents productive.
