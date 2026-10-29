# Mermaid Preview — CLAUDE.md

## Project overview

Single-file (`index.html`) browser app for previewing Mermaid diagrams. No build step, no dependencies beyond Mermaid.js loaded from CDN. Designed for pasting diagrams directly from LLM responses, which often contain subtle syntax errors.

## Architecture

Everything lives in `index.html`:
- **CSS** — Apple design system styling (SF Pro fonts, `#f5f5f7` backgrounds, dark glass nav)
- **HTML** — split-pane layout: editor (40%) + preview (60%)
- **JS** — preprocess → render → zoom/pan

## Key behaviors

### Preprocessor (`preprocess()`)
Runs before every Mermaid render. Current fixes:
- Literal `\n` inside node labels → `<br/>`
- Unquoted `{labels with (parens)}` → `{"labels with (parens)"}` to prevent stadium-token parse error
- Unquoted `[labels with (parens)]` → `["labels with (parens)"]` for same reason

When adding new preprocessing rules, keep them in this function and add a comment explaining what input pattern it fixes.

### Mermaid theme
Uses `theme: 'base'` with custom `themeVariables`. Color palette is Apple system colors:
- Primary: `#0071e3` (Apple Blue)
- Accents: `#ff3b30`, `#ff9f0a`, `#34c759`, `#5ac8fa`, `#af52de`, `#ff2d55`, `#30b0c7`
- Edge labels: `edgeLabelBackground: '#ffffff'` + CSS override forcing text to `#1d1d1f`

Do not switch away from `theme: 'base'` — other themes override `themeVariables`.

### Zoom + Pan
- State: `scale`, `tx`, `ty` — applied as `translate(tx, ty) scale(scale)` on `#diagram`
- Scroll to zoom toward cursor (0.2x – 30x)
- Pointer drag to pan
- Reset on new render and on "Reset View" button click

## Design system

UI references the Apple design system (summary in README "Design trade-offs", details in [docs/design.md](docs/design.md)), with some deliberate deviations. Key rules:
- Header: `rgba(0,0,0,0.8)` + `backdrop-filter: saturate(180%) blur(20px)`, 48px height
- Backgrounds: `#f5f5f7` (page/pane), `#ffffff` (toolbars/labels)
- Typography: SF Pro Display (headings) / SF Pro Text (body), negative letter-spacing at all sizes
- Buttons: Apple Blue `#0071e3` (primary), `#1d1d1f` (secondary), 8px radius
- Borders: `rgba(0,0,0,0.08)` hairlines only — no solid borders
- Interactive elements use only `#0071e3`; status and error messages may use the system semantic colors `#34c759` / `#ff3b30`

Intentional deviations from Apple's generic spec — do not "fix" these to match it:
- Hairline dividers (`1px solid rgba(0,0,0,0.08)`) between panes and under the pane label/toolbar — an editor UI needs visible separation
- Red/green semantic colors on the status bar and error box — render status needs them
- Compact `.btn` (`padding: 5px 14px`, 13px) — toolbar buttons must fit the 36px toolbar
- Header `h1` is 17px SF Pro Display (spec says Display only at 20px+)
- `#diagram` has its own `drop-shadow` in addition to the error box's card shadow

## What to avoid

- Do not add `htmlLabels: true` to the Mermaid flowchart config — it changes the DOM structure and breaks CSS selectors for edge labels
- Do not set background or padding on `.edgeLabel` via CSS — it hides the labels; only set `color`
- Do not switch `#preview-container` to `overflow: auto` — it breaks the zoom/pan behavior (must stay `overflow: hidden`)
- Do not add a build system or npm dependencies — the zero-install constraint is intentional
