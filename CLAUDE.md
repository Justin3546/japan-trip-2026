# Trip Journal Update Guide

This is a public single-page site for friends/family to follow our June 2026 Japan trip. During the trip, Justin will send photos and a short text recap for each day; you (Claude) update `index.html` so the day flips from "upcoming" to "recap."

## What you do when Justin sends a day's update

1. **Identify the day** by date (e.g., "we just landed in Tokyo" → Day 2). Day numbers and dates are fixed in `index.html`.
2. **Save photos** to `photos/dayN/` (create the directory). Name them `img1.jpg`, `img2.jpg`, ... in the order he sent them. Convert HEIC to JPEG with `sips -s format jpeg input.heic --out output.jpg`. Don't crop, rotate, or compress.
3. **Mark the day complete** in `index.html` — three coordinated edits below.
4. **Move the `.now-divider`** so it sits right before the first upcoming day.
5. **Update the footer date** to today's date (Central Time): `TZ=America/Chicago date "+%B %d, %Y"`.
6. **Commit and push.** Pages rebuilds automatically.

## The three coordinated edits to mark Day N complete

### A. The summary pill at the top

Change:
```html
<a class="summary-item" href="#day-N">...</a>
```
to:
```html
<a class="summary-item complete" href="#day-N">...</a>
```

### B. The day card header

Change:
```html
<div class="day-card" id="day-N">
  <div class="day-header">
    ...
    <div class="day-titles">
      <h2>Title</h2>
```
to:
```html
<div class="day-card complete" id="day-N">
  <div class="day-header">
    ...
    <div class="day-titles">
      <h2>Title<span class="recap-pill">&#10003; Recap</span></h2>
```

### C. The journal block

Replace:
```html
<div class="journal"><!-- JOURNAL --></div>
```
with:
```html
<div class="journal">
  <p class="entry">[Justin's text — see tone notes below]</p>
  <div class="gallery">
    <img src="photos/dayN/img1.jpg" alt="">
    <img src="photos/dayN/img2.jpg" alt="">
    <img src="photos/dayN/img3.jpg" alt="">
  </div>
</div>
```

For 1–4 photos, default `class="gallery"` (square crop, ~140px min). For mostly landscape shots or fewer photos, use `class="gallery wide"` (4:3 crop, ~220px min).

## The "Upcoming" divider

There's exactly one `.now-divider` on the page. It sits between the last completed day and the first upcoming day:

```html
<div class="now-divider"><span class="label">Upcoming</span></div>
```

After marking a day complete, cut and paste this divider so it appears right BEFORE the first upcoming day's `<!-- DAY N+1 -->` comment. If every day is complete (end of trip), delete the divider entirely. If no day is complete yet, the divider sits before Day 1 — but in practice, by the time you're updating, at least one day is done.

## Tone for journal entries

- Keep Justin's voice. Light copy edits only — typos, capitalization, replacing em-dashes with " — " or commas. No double-hyphens.
- Don't add commentary, embellishment, or speculation beyond what he wrote.
- Don't add emoji unless he used them.
- Keep paragraphs short. If he sends multiple distinct thoughts, use multiple `<p class="entry">` blocks.
- First names (Ricky, Cora) are fine. **Never** include the surname "Constant" or kids' ages.

## Things you must NOT change

- The pre-trip plans inside each day's `<div class="timeline">`. Those reflect what was planned, not what actually happened. Keep them even when the day reality diverged.
- Day numbering, dates, or order.
- Colors, layout, or any global CSS.
- Hotels — never mention them anywhere on the page.
- The noindex meta tags or `robots.txt`.

## Commit message format

```
Day N journal: [3–5 word summary]
```
Examples: `Day 1 journal: flight out, salmon hit`, `Day 6 journal: USJ start to finish`.

## Quick checklist before pushing

- [ ] Photos saved to `photos/dayN/` and committed
- [ ] Summary pill has `complete` class
- [ ] Day card has `complete` class
- [ ] Recap pill added next to title
- [ ] Journal block populated with caption + gallery
- [ ] `.now-divider` moved to before the next upcoming day
- [ ] Footer date updated
- [ ] `git push` ran cleanly
