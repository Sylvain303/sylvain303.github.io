# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A static Grist Custom Widget that renders printable invoices. It has no build step, no bundler, and no test suite — it is plain HTML/CSS/JS served directly from the filesystem or a static host.

## Development

Open `index.html` directly in a browser, or use any static file server:

```sh
npx serve .
```

Preview modes (append to URL):

- `?demo=1` — renders a fully filled-out invoice using `exampleData.js`
- `?labels=1` — renders the invoice with field-name labels (shows column mapping)

When deployed as a Grist widget, it receives live data via `grist.onRecord()`.

## Architecture

The widget is three files that work together:

- **`invoice.js`** — all logic. Registers with the Grist Plugin API via `grist.ready()` and `grist.onRecord(updateInvoice)`. `updateInvoice()` normalizes the incoming row (expands a `References` column if present, auto-calculates `Subtotal`/`Total` from `Items` when absent, injects demo placeholders via `addDemo()`), then updates a global Vue 2 reactive `data` object.
- **`index.html`** — Vue 2 template bound to that `data` object. Renders the invoice or a status/guidance panel when data is missing.
- **`invoice.css`** — styles, including a `@media print` rule that hides the Print button.
- **`exampleData.js`** — hardcoded sample record used by `?demo=1`.

## Data contract (Grist columns → invoice fields)

The widget reads these column names from the selected Grist row:

| Column | Type | Notes |
|---|---|---|
| `Number` | any | Invoice number |
| `Issued` / `Due` | Unix timestamp (s) or date string | Formatted via moment.js |
| `Invoicer` | object or string | `{Name, Street1, Street2, City, State, Zip, Email, Phone, Website}` |
| `Client` | object or string | `{Name, Street1, Street2, City, State, Zip, Country}` |
| `Items` | array or string | Array: `[{Description, Price, Quantity, Total}]`; string: shown as single line |
| `Subtotal`, `Deduction`, `Taxes`, `Total` | number | Auto-calculated from Items if absent |
| `Note` | string | Free-text note at bottom |
| `Paid` | boolean | Shows a "PAID" stamp |
| `References` | object | If present, merged into the row via `Object.assign` (use Grist formula `RECORD(rec, expand_refs=1)`) |

When neither `Issued` nor `Due` is present, the widget shows a help panel that classifies each column as recognized / expected / ignored.

## Versioning

`index.html` uses query-string cache-busters on the script and stylesheet `<script src="invoice.js?ver=11">` / `<link href="invoice.css?ver=17">`. Increment these manually when deploying changes to those files.
