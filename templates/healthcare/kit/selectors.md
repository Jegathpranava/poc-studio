# healthcare kit: selector and anchor guide

Rules the Prototype Builder follows when it writes screens from this kit.

## Scoping

- Every screen fragment is rooted at `<div class="hlx">`. The assembler wraps it in `.pf`.
- Product CSS lives under `.pf .hlx`. New rules added for a screen use the same prefix.
- Step-state CSS is written as `.pf.sl-<screen-id>[data-step="N"] .hlx <selector>` and nothing else.
- Use only classes defined in `product.css` and `icons.css`. Do not add inline styles or external URLs.
- Icons are `<span class="ic ic-<name>"></span>`. Available: `layout-dashboard`, `search`, `bell`, `plus`, `check`, `clock`, `user`, `file-text`, `settings`, `chevron-right`, `triangle-alert`, `heart-pulse`, `stethoscope`, `calendar`, `pill`.
- Widths for meters use the `.w-5` to `.w-100` classes, in steps of 5.

## Component classes

- Shell: `shell`, `rail`, `rail-brand`, `brand-mark`, `rail-link` (`is-active`), `main`, `topbar`, `topbar-title`, `topbar-search`, `topbar-actions`, `icon-btn`, `avatar`, `page`, `page-head`, `page-title`, `page-sub`.
- Layout: `grid` with `cols-2`, `cols-3`, `cols-4` or `split`; `stack`, `row`, `row-between`, `spacer`.
- Cards: `card`, `card-head`, `card-title`, `card-body`, `card-foot`.
- Stats: `stat`, `stat-label`, `stat-value`, `stat-delta` (`up`, `down`).
- Tables: `table-wrap`, `table`, `num` on cells, `is-selected` on rows.
- Forms: `form`, `field`, `label`, `input`, `textarea` (`is-error`), `hint`, `error-text`, `check-row`, `check` (`is-on`), `form-actions`.
- Buttons: `btn`, `btn-primary`, `btn-ghost`, `btn-sm`.
- Chips and pills: `chip` (`is-on`), `pill` with `pill-ok`, `pill-warn`, `pill-bad`, `pill-info`, `pill-muted`.
- Lists and progress: `list`, `list-item`, `list-icon`, `list-main`, `list-title`, `meter`, `meter-fill`, `steps`, `step` (`is-done`, `is-current`), `kv`.
- States: `empty`, `empty-icon`, `empty-title`, `toast`, `toast-title`, `toast-text`.
- Text: `muted`, `mono`, `strong`.

## Anchors

Anchors are spotlight targets for the deck tour. Mark an element with `data-anchor="<name>"` and select it with `[data-anchor="<name>"]`.

- Names are lowercase, dash separated, and describe the thing, not the position (`kpis`, `recent-table`, `submit`).
- Every screen exposes 3 to 8 anchors. Each anchor must match at least one element in its fragment.
- Anchor the container a viewer should look at (a table wrapper, a card, a form), not a single text node.
- `nav-active` marks the current navigation item.
- Names are unique within a screen. Keep the anchors listed in `kit.json` when reusing an example screen.

## Example screens

- `screens/dashboard.html` (Dashboard): `alerts`, `kpis`, `nav-active`, `primary-action`, `recent-table`
- `screens/list-detail.html` (Patients list and detail): `detail`, `detail-action`, `filters`, `list-table`, `nav-active`
- `screens/form.html` (Book appointment): `form`, `key-field`, `nav-active`, `steps`, `submit`, `toast`
