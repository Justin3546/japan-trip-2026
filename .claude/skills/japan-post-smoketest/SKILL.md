---
name: japan-post-smoketest
description: End-to-end smoke test for the Japan trip site's daily-update flow. Generates a self-contained test.html page on the live japan.jconstant.com site with a real YouTube embed, sample caption, and placeholder photo gallery — then commits it and walks Justin through pushing to GitHub so he can verify on the live site that videos actually play, the CSS renders correctly, and the publish pipeline works before the June 2026 trip. Default video is "Starship V3" (y_ecCDqTSJs); accepts any YouTube URL as an argument. Has a separate cleanup phase that removes test.html when verification is done. Triggers on "smoke test the japan post", "test the daily update end to end", "post a test to japan.jconstant.com", "verify the live site embed", "run the japan smoke test", "test the live publish flow", or any variation. Use this skill — NOT a local preview — when the goal is to confirm the actual deployed page behaves correctly.
---

# Japan Trip End-to-End Post Smoke Test

## When to fire

Justin wants to verify the entire daily-update pipeline works on the live site, end-to-end, before the trip:

1. HTML gets generated with the right structure
2. Git commit + push to GitHub succeeds
3. GitHub Pages deploys
4. The video iframe actually plays at a real `https://` origin (no Error 153 etc.)
5. The CSS renders correctly in real browsers

The local preview approach (file:// HTML on his Mac) was abandoned because YouTube blocks playback from null origins. This skill exercises the actual production path instead.

Fire on phrases like:
- "smoke test the japan post"
- "run the end-to-end japan test"
- "post a test to japan.jconstant.com"
- "test the live publish flow"
- "verify the embed works on the live site"
- "run the japan smoke test"

Do NOT fire if Justin is asking to update a real day (Day 1–10). That goes through the main site CLAUDE.md flow.

## What the skill produces

A file at the site root called `test.html`. After push + Pages deploy, it's reachable at `https://japan.jconstant.com/test.html`.

The page contains exactly the same structure as a real journal entry on the live site:

- Hero header
- One `.day-card.complete` ("Day 0 — Smoke Test")
- Caption paragraph
- `.video-embed` iframe pointing at the test YouTube video (default: `y_ecCDqTSJs` — Starship V3)
- `.gallery` with four inline SVG swatches as placeholder photos
- The same `index.html` CSS, extracted at runtime so the test always matches what's actually deployed

The page is `noindex, nofollow` like the main site.

## How to invoke (post phase)

```bash
python3 "/Users/justin/Claude/Cowork Projects/Summer Plans/japan-trip-site/.claude/skills/japan-post-smoketest/post.py" [YOUTUBE_URL]
```

If no URL is provided, defaults to the Starship V3 video. URL parsing handles every common shape (youtu.be, watch?v=, embed/, shorts/, raw 11-char ID).

The script:
1. Generates `test.html` at the site root, using CSS extracted from the live `index.html`.
2. Runs `git add test.html` and commits with message `"Smoke test: add test.html with video embed"`.
3. Tries `git push origin main`. The Cowork sandbox typically has no GitHub auth, so this usually fails — in that case the script prints the exact one-liner Justin needs to run from his Mac Terminal (where his `gh` / SSH key is set up) to push.
4. Reports the live URL: `https://japan.jconstant.com/test.html`.

## Workflow when this skill runs

1. Acknowledge the request in one line.
2. Run `post.py`. Capture the output (especially whether push succeeded or needs manual completion).
3. Show Justin:
   - The video ID that got embedded.
   - The live URL.
   - If push succeeded: tell him to wait ~30–60 seconds for GitHub Pages to deploy, then open the URL.
   - If push failed: copy-paste the exact terminal command for him to run from `~/Claude/Cowork\ Projects/Summer\ Plans/japan-trip-site`.
4. Tell him three things to verify:
   - Video plays inline on `japan.jconstant.com/test.html`.
   - Page layout is correct (caption → video → photo grid below, day card has green top border and recap pill).
   - No console errors in DevTools.
5. After verification, remind him to run the cleanup phase (next section).

## Cleanup phase

After Justin confirms the test worked, run:

```bash
python3 "/Users/justin/Claude/Cowork Projects/Summer Plans/japan-trip-site/.claude/skills/japan-post-smoketest/cleanup.py"
```

The script:
1. Removes `test.html` from the site root.
2. Runs `git add -A` and commits `"Smoke test: remove test.html"`.
3. Tries to push, falling back to a printed command if no auth.

After Pages redeploys (~60s), `https://japan.jconstant.com/test.html` returns 404 and the site is back to its pre-test state. No real day data was touched.

## What NOT to do

- Do NOT modify `index.html`. The smoke test stays in `test.html` only.
- Do NOT touch any real day's photos, journal, or summary pill.
- Do NOT skip cleanup. Leaving `test.html` in production after verification is sloppy.
- Do NOT use a real day number (Day 1–10) as the test container. Always "Day 0 — Smoke Test."
- Do NOT auto-push if the user hasn't confirmed they want to commit to the live site. The script defaults to committing locally and reporting; pushing is gated on the manual Terminal command unless sandbox auth exists.

## Files

- `SKILL.md` — this file.
- `post.py` — runs the smoke test post.
- `cleanup.py` — removes the test page.
