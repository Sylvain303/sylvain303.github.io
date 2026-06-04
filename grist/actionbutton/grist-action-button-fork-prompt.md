# Claude Code Prompt: Fork Grist Action Button Widget

## Goal

Fork the official Grist `actionbutton` widget to add **cursor navigation** after record creation. When the button creates a new record, the card view should automatically move to that new record.

Host the result as a static site on GitHub Pages so it can be referenced via a custom widget URL in Grist.

---

## Source Files to Fork

File already locally copied from  

`https://github.com/gristlabs/grist-widget/raw/refs/heads/master/actionbutton/`

---

## What the Widget Does (Current Behaviour)

The widget reads a formula column called `ActionButton` from the current Grist record. The column returns either a single dict or a list of dicts, each with the shape:

```python
{
  "button": "Label shown on button",
  "description": "Text shown below the button",
  "actions": [["AddRecord", "TableName", None, {"field": value}]]
}
```

The JS normalises single/multiple buttons into an array, renders them via Vue.js, and on click calls:

```javascript
await grist.docApi.applyUserActions(actions);
```

No navigation happens after the action.

---

## Required Change

In `actionbutton.js`, modify the `applyActions` function to navigate to the newly created record after `applyUserActions` resolves.

**Current code:**

```javascript
async function applyActions(actions) {
  data.results = "Working...";
  try {
    await grist.docApi.applyUserActions(actions);
    data.message = 'Done';
  } catch (e) {
    data.message = `Please grant full access for writing. (${e})`;
  }
}
```

**Target behaviour:**

```javascript
async function applyActions(actions) {
  data.results = "Working...";
  try {
    const result = await grist.docApi.applyUserActions(actions);
    // Navigate to the newly created record if an AddRecord action was used
    const newRowId = result?.retValues?.[0];
    if (newRowId) {
      await grist.setCursorPos({ rowId: newRowId });
    }
    data.message = 'Done';
  } catch (e) {
    data.message = `Please grant full access for writing. (${e})`;
  }
}
```

`grist.setCursorPos({ rowId })` is an officially supported API method in the Grist plugin API. `sectionId` is not needed (it is ignored by Grist).

---

## Grist Plugin API Reference

The widget communicates with Grist via the `grist` global object injected by `grist-plugin-api.js` (loaded in `index.html`). Relevant methods:

| Method | Description |
|---|---|
| `grist.ready(options)` | Declare widget ready, register column mappings |
| `grist.onRecord(fn)` | Subscribe to current row changes |
| `grist.mapColumnNames(row)` | Remap columns per creator panel config |
| `grist.docApi.applyUserActions(actions)` | Execute userActions, returns `{ retValues: [newRowId, ...] }` |
| `grist.setCursorPos({ rowId })` | Move cursor to a specific row (used for widget linking) |

---

## UserActions Format

Each action is an array:

```
["ActionName", "TableId", rowId_or_null, { field: value }]
```

Common actions:

```javascript
["AddRecord",    "TableName", null, { "Col": value }]   // create, returns new id
["UpdateRecord", "TableName", 42,   { "Col": value }]   // update by id
["RemoveRecord", "TableName", 42]                        // delete by id
```

Multiple actions can be batched in one `applyUserActions([...])` call.

---

## My Specific Use Case

I have a Grist document with two tables: **Compagny** and **Contact**.

- A `Contact` requires a linked `Compagny`.
- `Compagny` has a boolean field `physical_person`.
- When `physical_person = true`, the company is a placeholder used to represent an individual (no real company).
- I have a card view filtered on `physical_person = true`, showing both a Company widget and a Contact widget.
- The Action Button should create a new `Compagny` record with `physical_person = true`, then navigate the card view to that new record.

Example Python formula for the button column:

```python
actions = [["AddRecord", "Compagny", None, {"physical_person": True}]]
return {"actions": actions, "button": "Add person", "description": ""}
```



## Hosting

- Target: **GitHub Pages** (static hosting, no build step needed)
- The widget URL to enter in Grist will be: `https://<username>.github.io/<repo>/actionbutton/`
- No `manifest.json` needed since we are pointing to one widget directly via Custom Widget → URL field

---

## Constraints

- Keep Vue.js dependency (already used in the original)
- Keep full backward compatibility with the existing Python formula format (single dict or list of dicts)
- Do not break the multi-button rendering
- `setCursorPos` should only be called when `retValues[0]` exists (i.e. an `AddRecord` was the first action)
- Widget must request **Full document access** (already required by the original)
