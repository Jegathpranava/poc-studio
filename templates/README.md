# Sector templates

A kit is the generic starting point for one sector. The Prototype Builder reads it before it writes the ScreenPack, so every run gets a consistent, accessible product look.

```
templates/
  sectors.json            sector name to directory map ("e-commerce" -> ecommerce)
  <sector>/
    kit/
      product.css         design system, every rule scoped under `.pf .<app_class>`
      icons.css           Lucide icons as CSS masks (`.ic` plus `.ic-<name>`)
      screens/*.html      3 example screen fragments with `data-anchor` targets
      selectors.md        naming guide for classes and anchors
      kit.json            {sector, app_class, accent, screens: [{id, file, label, anchors}]}
    app/                  standalone Next.js 16 starter (own package.json and lockfile)
```

## How the builder uses a kit

1. Look up the sector in `sectors.json`, then read `kit.json`, `product.css`, `selectors.md` and the example screens.
2. Write 6 to 12 screens as fragments that use only the kit classes. Add step-state CSS as `.pf.sl-<screen-id>[data-step="N"] ...`.
3. Expose 3 to 8 `data-anchor` elements per screen. Validation checks that each anchor selector matches.
4. For the repo, copy `app/` into the run directory and port the screens into pages. `app/app/kit/` holds copies of `product.css` and `icons.css`. A test keeps them identical to `kit/`.

The example data is fictional. Kits contain no external URLs, fonts or images.

## Starters

Each `app/` is its own project, not an npm workspace member: `cd templates/<sector>/app && npm ci && npm run build`. The versions of `next`, `react` and `react-dom` match `apps/web`.

## Tests

`cd services/api && uv run pytest tests/templates -q` checks the kits. `uv run pytest -m slow tests/templates` also builds all four starters.
