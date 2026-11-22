# Deck runtime (vendored)

Provenance
- Source: the owner's reference deck HTML under `reference/` (git-ignored; the exact file name is in the design spec, section 3 amendment 8, and is left out here so the brand-word check stays clean).
- Vendored on 2026-11-22. Spec section 3, amendment 9: the owner approved committing the engine to this public repo.

Included
- `chrome.css`: the presentation chrome only. That is the `:root{--dk-*}` tokens, `#dk-viewport`, `#dk-stage`, `.dk-*`,
  `.pf-canvas`, the base `.pf{position...}` rule, and the rotate and reduced-motion media rules.
- `runtime.js`: the deck runtime IIFE (reads `#dk-data`, mounts `<template id="tpl-ID">` into the 1280 px canvas, slides,
  steps, spotlight, deep links, keyboard, touch, fullscreen, count-ups, `window.__deck`).

Excluded
- All product CSS (`.pf{--...` tokens and every rule after the chrome), every icon mask, every product template,
  the `window.__dkScripts` bodies, the logo, images and video.

Re-vendoring
1. Strip base64 from a copy: `sed -E 's#data:[a-z/+]+;base64,[A-Za-z0-9+/=]+#DATA#g' ref.html > stripped.html`.
2. `chrome.css` = the `<style>` content from the first comment up to the line before the product rules begin.
3. `runtime.js` = the body of the last `<script>` (the one starting `/* Deck runtime embedded ...`).
4. Check: the brand-word grep from the Task 14 plan (the reference deck's product and brand words) must find nothing in this folder.
5. Run `uv run pytest tests/deck -q -m "browser or not browser"`.
