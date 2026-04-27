# Trip Journal Update Guide

This is a public single-page site for friends/family to follow our June 2026 Japan trip. During the trip, Justin will send photos and a short text recap for each day; you (Claude) update `index.html` so the day flips from "upcoming" to "recap."

## Environment

You're running in a **Claude Code remote cloud session** bound to this repo, which Justin starts from the Claude app on his phone. The repo is already your working directory, git is configured, and `gh` is authenticated. The shell is Linux — no macOS-only tools (`sips`, etc.).

For HEIC → JPEG conversion (iPhone default format), use ImageMagick:
```
magick input.heic output.jpg
```
If `magick` isn't installed, fall back to `convert input.heic output.jpg`, or install with `sudo apt-get install -y imagemagick libheif1` if neither is present (the cloud sandbox usually needs this on first use). Most attached photos arrive as JPEG once iOS hands them through the Claude app, so check the media type before converting.

## Where Justin's photos actually are

When Justin attaches photos in the Claude mobile app, they do **not** appear as files on disk. They're embedded as base64 inside the session transcript JSONL at:

```
/root/.claude/projects/-home-user-japan-trip-2026/<session-uuid>.jsonl
```

(That path is `~/.claude/projects/` + the cwd with `/` replaced by `-`.) Each user message has a `.message.content` array containing `{type:"image", source:{type:"base64", media_type:"image/jpeg"|"image/heic", data:"..."}}` blocks in the order he sent them. There's typically one `.jsonl` per session — pick the newest in the directory.

To extract the photos from the most recent user message that has any images and save them with sequential names, run this from the repo root:

```bash
DAY=2  # set to the day number you're updating
DEST="photos/day${DAY}"
mkdir -p "$DEST"

TRANSCRIPT=$(ls -t /root/.claude/projects/-home-user-japan-trip-2026/*.jsonl | head -1)
TMP=$(mktemp -d)
jq -c 'select(.type=="user" and (.message.content | type=="array") and ([.message.content[] | select(.type=="image")] | length > 0))' "$TRANSCRIPT" \
  | tail -1 > "$TMP/msg.json"

N=$(jq '[.message.content[] | select(.type=="image")] | length' "$TMP/msg.json")
for i in $(seq 1 "$N"); do
  idx=$((i-1))
  mt=$(jq -r ".message.content | map(select(.type==\"image\")) | .[$idx].source.media_type" "$TMP/msg.json")
  ext=${mt#image/}; [ "$ext" = "jpeg" ] && ext=jpg
  jq -r ".message.content | map(select(.type==\"image\")) | .[$idx].source.data" "$TMP/msg.json" \
    | base64 -d > "$DEST/img${i}.${ext}"
done
rm -rf "$TMP"

# Convert any HEIC/HEIF to JPEG and drop the originals
for f in "$DEST"/*.heic "$DEST"/*.heif; do
  [ -f "$f" ] || continue
  convert "$f" "${f%.*}.jpg" && rm "$f"
done

ls -la "$DEST"
```

If Justin spreads photos across multiple messages in the same update ("oh, one more"), replace the `tail -1` with logic that takes every user message after the previous assistant turn — but his normal pattern is one message with all photos plus the caption.

## What you do when Justin sends a day's update

1. **Identify the day** by date (e.g., "we just landed in Tokyo" → Day 2). Day numbers and dates are fixed in `index.html`.
2. **Extract and save photos** to `photos/dayN/` using the snippet in the section above. Files land as `img1.jpg`, `img2.jpg`, ... in the order he sent them. Don't crop, rotate, or recompress.
3. **Mark the day complete** in `index.html` — three coordinated edits below.
4. **Move (or, on the first day, create) the `.now-divider`** so it sits right before the first upcoming day.
5. **Update the footer date** to today's date (Central Time): `TZ=America/Chicago date "+%B %d, %Y"`. Skip if the footer already shows today.
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

Once at least one day is complete there's exactly one `.now-divider` on the page. It sits between the last completed day and the first upcoming day:

```html
<div class="now-divider"><span class="label">Upcoming</span></div>
```

Pre-trip the divider doesn't exist. When marking the **first** day complete, add it right before the next day's `<!-- DAY N+1 -->` comment. For every day after that, cut and paste the existing one so it appears right BEFORE the first upcoming day's comment. If every day is complete (end of trip), delete the divider entirely.

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
