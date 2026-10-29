# Mermaid Preview — CLAUDE.md

## Project overview

Zero-build, single-page Mermaid previewer for pasting diagrams from LLM output — see [README.md](README.md) for what it does, the architecture diagram and directory layout.

## Architecture

App code lives in `index.html`; tests in `tests/`:
- **CSS** — Apple design system styling (SF Pro fonts, `#f5f5f7` backgrounds, dark glass nav)
- **HTML** — split-pane layout: editor (40%) + preview (60%)
- **JS** — preprocess → render → zoom/pan

## Key behaviors

### Preprocessor (`preprocess()`)
Runs before every Mermaid render. Current fixes:
- Every literal `\n` inside a single-line `[...]` label → `<br/>` (`{}` / `()` labels are not touched)
- Unquoted single-line `{labels with (parens)}` → `{"labels with (parens)"}` to prevent stadium-token parse error (multi-line classDiagram bodies are left alone)
- Unquoted `[labels with (parens)]` → `["labels with (parens)"]` for same reason; skips `[[subroutine]]`, cylinder `[(...)]` and trapezoid `[/...]` / `[\...]` shapes

When adding new preprocessing rules, keep them in this function and add a comment explaining what input pattern it fixes.

### Mermaid theme
Uses `theme: 'base'` with custom `themeVariables`. Color palette is Apple system colors:
- Primary: `#0071e3` (Apple Blue)
- Accents: `#ff3b30`, `#ff9f0a`, `#34c759`, `#5ac8fa`, `#af52de`, `#ff2d55`, `#30b0c7`
- Edge labels: `edgeLabelBackground: '#ffffff'` + CSS override forcing text to `#1d1d1f`

Do not switch away from `theme: 'base'` — other themes override `themeVariables`.

### Zoom + Pan
- State: `scale`, `tx`, `ty` — applied as `translate(tx, ty) scale(scale)` on `#diagram`
- Declared before `render()` (avoid TDZ); `resetView()` is shared by render and the Reset View button
- Scroll to zoom toward cursor (0.2x – 30x)
- Pointer drag to pan
- Reset on new render and on "Reset View" button click

## Design system

Design rules and the intentional deviations from Apple's spec are in [docs/design.md](docs/design.md) — don't "fix" the deviations back to the Apple spec.

## Tests / environment facts

How to install and run: see README "Tests". Constraints that matter when editing `index.html`:
- `tests/conftest.py` intercepts the Mermaid CDN request and serves `FAKE_MERMAID_JS` (records `window.__mermaid.initConfig` / `window.__mermaid.calls`); the clipboard is stubbed into `window.__copied`. No network needed.
- e2e tests rely on globals `preprocess`, `scale`, `tx`, `ty` (read and written directly) — keep them top-level, don't wrap them in a closure/module.
- e2e tests assert the text of `#status` ("Rendered OK" / "Parse error"), `#error-box` and `#copy-svg-btn` ("Copy SVG" / "Copied!").

## Status / next steps

- Status: live at the GitHub Pages URL in README; preprocess rules, zoom/pan and Copy SVG covered by tests.
- Next: possibly extend the `\n` → `<br/>` rule to `{}` / `()` labels (update README table and tests with it); add `:focus-visible` styles if keyboard focus states are wanted.

## What to avoid

- Do not add `htmlLabels: true` to the Mermaid flowchart config — it changes the DOM structure and breaks CSS selectors for edge labels
- Do not set background or padding on `.edgeLabel` via CSS — it hides the labels; only set `color`
- Do not switch `#preview-container` to `overflow: auto` — it breaks the zoom/pan behavior (must stay `overflow: hidden`)
- Do not add a build system or npm dependencies — the zero-install constraint is intentional
