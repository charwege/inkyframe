# Plugin views

A plugin's `view(ctx, data)` turns its data into a plain dict of display-ready values. The studio
layouts in `inkyframe/layouts/<design>.py` draw only from this dict, so every design shows the same
facts. One file per plugin in this folder lists the fields with their sample values.

Rules for a view:
- display-ready: strings are already translated (`ctx.t`), dates/numbers already formatted with
  `ctx.date` / `ctx.num` – but also keep the raw numbers a chart or icon needs (e.g. `value: 776`,
  `value_text: "776 W"`).
- plain Python types only (str, int, float, bool, list, dict, `datetime`, PIL `Image` for pictures).
- everything the regular screen shows must be in it; nothing that needs another network call.
- states the regular screen handles with a message (not configured, nothing playing, no data) stay in
  the plugin *before* the hook – a layout is only called with a complete view.
