# Design — Apple design system, as applied to Mermaid Preview

The UI borrows from Apple's web design language: near-white neutrals, a single blue for interactive elements, SF Pro typography with tight tracking, and a dark translucent glass nav. This file keeps only the parts relevant to a single-page editor/preview tool (palette, typography, buttons, nav glass) and lists where `index.html` deliberately deviates. Hero sections, product imagery, breakpoints and pill CTAs from the generic Apple.com spec are intentionally left out — they don't apply here.

## 1. Color palette

### Neutrals
- **Light Gray** (`#f5f5f7`): page, editor and preview backgrounds. Not white — the slight blue-gray tint prevents sterility.
- **White** (`#ffffff`): toolbars, pane labels, status bar, error box; text on dark backgrounds and on blue/dark buttons.
- **Near Black** (`#1d1d1f`): primary text on light backgrounds, secondary (dark) button fill.
- **Black 48%** (`rgba(0, 0, 0, 0.48)`): tertiary text — pane labels, toolbar text, neutral status.

### Interactive
- **Apple Blue** (`#0071e3`): primary buttons. The only accent color for interactive elements.

### Semantic (status only — see deviations)
- **Green** (`#34c759`): "Rendered OK" status.
- **Red** (`#ff3b30`): parse-error status and the "Parse Error" heading in the error box.

### Shadow
- **Card Shadow** (`rgba(0, 0, 0, 0.22) 3px 5px 30px 0px`): soft, diffused elevation. Used on the error box.

## 2. Typography

### Font family
- **Display**: `SF Pro Display`, fallbacks `SF Pro Icons, Helvetica Neue, Helvetica, Arial, sans-serif`
- **Body**: `SF Pro Text`, fallbacks `SF Pro Icons, Helvetica Neue, Helvetica, Arial, sans-serif`
- **Editor**: `JetBrains Mono, Fira Code, Cascadia Code, monospace`
- Apple's rule: SF Pro Display at 20px and above, SF Pro Text at 19px and below.

### Sizes used in this tool

| Role | Font | Size | Weight | Letter Spacing |
|------|------|------|--------|----------------|
| Header title | SF Pro Display | 17px | 600 | -0.374px |
| Button | SF Pro Text | 13px | 400 | -0.224px |
| Error heading | SF Pro Text | 14px | 600 | -0.224px |
| Error body | SF Pro Text | 13px | 400 | -0.224px |
| Labels / toolbar / status / badge | SF Pro Text | 12px | 400 | -0.12px |

### Principles
- **Negative tracking at all sizes**: -0.374px at 17px, -0.224px at 13–14px, -0.12px at 12px.
- **Weight restraint**: 400 (regular) and 600 (semibold) only.

## 3. Buttons

**Primary Blue**
- Background: `#0071e3`, text `#ffffff`
- Radius: 8px, no border
- Hover: `brightness(1.1)`; active: `brightness(0.92)`

**Secondary Dark**
- Background: `#1d1d1f`, text `#ffffff`, otherwise same as primary

Apple's spec sizes these at `padding: 8px 15px`, 17px text; this tool uses a compact variant (see deviations).

## 4. Navigation glass

- Background: `rgba(0, 0, 0, 0.8)` with `backdrop-filter: saturate(180%) blur(20px)`
- Height: 48px
- Title in white; the "live" badge is a 980px-radius pill on `rgba(255, 255, 255, 0.12)` with `rgba(255, 255, 255, 0.72)` text
- The glass effect is essential — don't make the header opaque.

## 5. Deviations in this project (intentional)

These differ from Apple's generic spec on purpose. Don't "fix" them to match the spec.

| Apple spec says | `index.html` does | Why |
|---|---|---|
| No borders on cards or containers | `1px solid rgba(0,0,0,0.08)` hairlines between editor/preview and under the pane label and toolbar | An editor tool needs visible pane separation; hairlines only, no solid/heavy borders |
| Blue is the only accent color | Status bar and error box use `#34c759` / `#ff3b30` | Render status needs red/green semantics. Interactive elements still use only `#0071e3` |
| Buttons `padding 8px 15px`, 17px text | `.btn` is `padding: 5px 14px`, 13px | Toolbar buttons must fit a 36px-tall toolbar |
| SF Pro Display only at 20px+, never mix | Header `h1` is 17px SF Pro Display | Header title reads as a heading inside a compact 48px nav |
| One soft shadow or none | `#diagram` adds `drop-shadow(rgba(0,0,0,0.12) 0px 4px 24px)` besides the error box's card shadow | Lifts the rendered diagram off the `#f5f5f7` preview background |
