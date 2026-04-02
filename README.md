# Mermaid Preview

A fault-tolerant, browser-based Mermaid diagram previewer designed for pasting diagrams directly from LLM (ChatGPT, Claude, etc.) responses — without needing to manually fix common formatting issues.

## Live Demo

**[https://xiaokangs.github.io/mermaid-preview/](https://xiaokangs.github.io/mermaid-preview/)**

No install needed — open the link and start pasting.

## Why this exists

LLMs frequently generate Mermaid diagrams that look correct but fail to parse due to subtle issues:

- Literal `\n` characters inside node labels instead of actual line breaks
- Parentheses `()` inside diamond `{}` or box `[]` labels that confuse the parser
- Mixed-language labels (e.g. Chinese + English) that trigger unexpected token errors

This tool silently fixes those issues before rendering, so you can paste and preview immediately.

## Features

- **Live preview** — renders as you type, 300ms debounce
- **Fault-tolerant preprocessor** — auto-corrects common LLM output issues before passing to Mermaid
- **Zoom** — scroll to zoom in/out (up to 30x), zooms toward cursor
- **Pan** — click and drag to move around the diagram
- **Reset View** — one click to re-center and restore default zoom
- **Copy SVG** — copies the rendered diagram as SVG markup
- **No install, no build step** — single HTML file, open directly in a browser

## Usage

1. Open `index.html` in any modern browser
2. Paste your Mermaid code into the left editor pane
3. The diagram renders instantly on the right

## Preprocessing fixes applied

| Issue | Fix |
|---|---|
| `\n` inside node labels | Replaced with `<br/>` for line breaks |
| `(parens)` inside `{diamond}` nodes | Label auto-quoted to prevent stadium-token parse error |
| `(parens)` inside `[box]` nodes | Label auto-quoted for the same reason |

## Hosting

This is a static single-file app. Host it anywhere:

- **GitHub Pages** — free, push to a repo and enable Pages under Settings
- **Cloudflare Pages** — free CDN, connect your GitHub repo
- **AWS S3** — enable static website hosting on a bucket

## Tech

- [Mermaid.js](https://mermaid.js.org/) via CDN
- Vanilla HTML/CSS/JS — zero dependencies, zero build tooling
