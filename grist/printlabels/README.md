# Print Labels (A4 fork)

Fork of the Grist Labs "Print labels" custom widget, adapted for A4-based
label sheets (French/EU market) in addition to the original US Letter sheets.

- Original source: https://github.com/gristlabs/grist-widget/blob/master/printlabels/printlabels.js
- Original widget doc: https://github.com/gristlabs/grist-widget/tree/master/printlabels

## Changes from upstream

- Added a new template, `labels21a4`, for 21 labels per A4 sheet
  (63.5 x 38.1 mm), matching the Avery L7160 layout
  (ref: https://www.avery.fr/modele-l7160). Also cross-compatible with
  HERMA 4677 and APLI 01992 sheets.
- Made page size (`--page-width` / `--page-height`) configurable per
  template via CSS custom properties, defaulting to A4 (`210mm` x `297mm`).
  The original US Letter templates (`labels8`, `labels10`, `labels20`,
  `labels30`, `labels60`, `labels80`) now explicitly override these back to
  `8.5in` x `11in`, so they keep working unchanged.
- `labels21a4` is now the default template (previously `labels30`).
- Fixed `updateSize()` in `printlabels.js` to recompute the page width on
  every resize/render instead of caching it once. This was needed because
  page width can now differ between templates (A4 vs. Letter); the old
  cached value would go stale after switching template.
- Added a "Print label border" checkbox to the options popup (gear icon),
  next to "Leave initial blanks". Previously the label outline was only a
  screen guide and was always stripped at print time (`--label-outline:
  none` in `@media print`); this option is unchecked by default to preserve
  that original behavior, and when checked the outline is printed too.
  The outline itself was switched from `box-shadow` to a real `border` on
  `.label`, since `box-shadow` is treated as a background/decoration effect
  by some browsers' print engines (observed in Firefox print-to-PDF: no
  border printed even with "print background colors" enabled) and isn't
  reliably printed, while `border` is real box content and always is.

## Deployment

Grist cannot accept custom label dimensions from the widget's options
panel; the dropdown list of templates is hard-coded in `printlabels.js`,
and their sizes/margins in `printlabels.css`. To use this fork, host these
files somewhere static (e.g. GitHub Pages) and point the Custom Widget URL
in Grist at your hosted `index.html`.
