#!/usr/bin/env python3
"""
Japan trip site — end-to-end post smoke test.

Creates `test.html` at the site root with a real YouTube embed, sample caption,
and placeholder photo gallery. Commits it locally and tries to push to GitHub.
If the sandbox doesn't have GitHub auth (typical for Cowork), prints the exact
command Justin should run from his Mac Terminal to push.

Once Pages redeploys, the test is visible at:
    https://japan.jconstant.com/test.html

Run cleanup.py afterward to remove the test page.

Usage:
    python3 post.py                            # uses default Starship V3 video
    python3 post.py "<YOUTUBE_URL>"            # uses a specific URL
    python3 post.py "<11-char video ID>"       # raw ID also works
"""

import os
import re
import shlex
import subprocess
import sys
import urllib.parse as up
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Default smoke-test video — "Starship V3: Everything you need to know!" by Everyday Astronaut.
# Public, embeddable, family-safe, long enough to verify smooth playback.
DEFAULT_VIDEO_ID = "y_ecCDqTSJs"

# Skill lives at: <repo>/.claude/skills/japan-post-smoketest/post.py
# So the repo root is three parents up.
SITE_DIR = Path(__file__).resolve().parent.parent.parent.parent
INDEX_HTML = SITE_DIR / "index.html"
TEST_HTML = SITE_DIR / "test.html"

VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def parse_video_id(raw: str):
    """Pull the 11-character video ID out of any common YouTube URL shape."""
    raw = raw.strip()

    if VIDEO_ID_RE.match(raw):
        return raw

    parsed = urlparse(raw)
    host = (parsed.netloc or "").lower().lstrip("www.")
    path = parsed.path or ""

    if host == "youtu.be":
        candidate = path.lstrip("/").split("/")[0]
        return candidate if VIDEO_ID_RE.match(candidate) else None

    if host.endswith("youtube.com"):
        if path == "/watch":
            v = parse_qs(parsed.query).get("v", [""])[0]
            return v if VIDEO_ID_RE.match(v) else None
        for prefix in ("/embed/", "/shorts/", "/v/"):
            if path.startswith(prefix):
                candidate = path[len(prefix):].split("/")[0]
                return candidate if VIDEO_ID_RE.match(candidate) else None

    return None


def extract_css() -> str:
    text = INDEX_HTML.read_text(encoding="utf-8")
    m = re.search(r"<style>(.*?)</style>", text, re.DOTALL)
    if not m:
        raise RuntimeError(f"Could not find <style> block in {INDEX_HTML}")
    return m.group(1)


def render_test_page(video_id: str) -> str:
    css = extract_css()

    swatches = ["#ff385c", "#4ea8de", "#f9a03f", "#5eaa5e"]
    sample_imgs = []
    for i, color in enumerate(swatches, start=1):
        svg = (
            f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200'>"
            f"<rect width='200' height='200' fill='{color}'/>"
            f"<text x='100' y='110' text-anchor='middle' font-family='sans-serif' "
            f"font-size='28' fill='white'>Photo {i}</text></svg>"
        )
        data_uri = "data:image/svg+xml;utf8," + up.quote(svg)
        sample_imgs.append(f'<img src="{data_uri}" alt="">')
    gallery_html = "\n        ".join(sample_imgs)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow, noarchive, nosnippet">
<meta name="googlebot" content="noindex, nofollow, noarchive, nosnippet">
<title>Japan 2026 — Smoke Test</title>
<style>{css}
  /* Smoke-test only — clearly marks this page as not real */
  .smoke-banner {{
    background: #fff8e1;
    border-bottom: 1px solid #f0d97a;
    padding: 10px 64px;
    font-size: 13px;
    color: #7a5d00;
  }}
  .smoke-banner code {{
    background: rgba(0,0,0,0.05);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
  }}
</style>
</head>
<body>

<div class="smoke-banner">
  <strong>End-to-end smoke test.</strong> This page is not part of the real trip journal.
  Video ID: <code>{video_id}</code>
</div>

<div class="hero">
  <h1><span class="flag">🇯🇵</span>Japan 2026 — Smoke Test</h1>
  <div class="hero-meta">Verifying the daily-update flow works end-to-end</div>
</div>

<div class="main">

<div class="day-card complete" id="day-0">
  <div class="day-header">
    <div class="day-badge" style="background:var(--tokyo)">D0</div>
    <div class="day-titles">
      <h2>Smoke Test<span class="recap-pill">&#10003; Recap</span></h2>
      <div class="day-date">End-to-end test of the post flow</div>
    </div>
    <div class="day-city-tag" style="background:var(--tokyo)">Test</div>
  </div>
  <div class="day-body">
    <div class="timeline">
      <div class="tl-item highlight"><div class="tl-time">Morning</div><div class="tl-desc"><strong>Sample timeline item</strong> &middot; placed here so the journal sits in its real context</div></div>
      <div class="tl-item"><div class="tl-time">Afternoon</div><div class="tl-desc">Second timeline item to verify spacing</div></div>
    </div>
    <div class="journal">
      <p class="entry">If you can see this page on japan.jconstant.com/test.html, the publish pipeline works. If the video below plays cleanly and the photo placeholders sit beneath it with the right spacing, the daily-update flow is ready for the trip.</p>
      <p class="entry">Second paragraph to verify multi-paragraph captions render with the tighter spacing rule between entries.</p>
      <div class="video-embed">
        <iframe src="https://www.youtube-nocookie.com/embed/{video_id}"
                title="Smoke test recap"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                referrerpolicy="strict-origin-when-cross-origin"
                allowfullscreen></iframe>
      </div>
      <div class="gallery">
        {gallery_html}
      </div>
    </div>
  </div>
</div>

</div>

<div style="text-align: center; padding: 32px 16px 48px; color: #929292; font-size: 12px;">
  Generated by <code>japan-post-smoketest</code>. After verification, run <code>cleanup.py</code> to remove this page.
</div>

<!-- LIGHTBOX (mirrors index.html so click-to-zoom matches the live site) -->
<div class="lightbox" id="lightbox" aria-hidden="true">
  <img src="" alt="">
</div>

<script>
  const lb = document.getElementById('lightbox');
  const lbImg = lb.querySelector('img');
  document.addEventListener('click', (e) => {{
    if (e.target.matches('.gallery img')) {{
      lbImg.src = e.target.src;
      lb.classList.add('open');
    }} else if (e.target === lb || e.target === lbImg) {{
      lb.classList.remove('open');
      lbImg.src = '';
    }}
  }});
  document.addEventListener('keydown', (e) => {{
    if (e.key === 'Escape') {{ lb.classList.remove('open'); lbImg.src = ''; }}
  }});
</script>

</body>
</html>
"""


def run(cmd, cwd=None):
    """Run a shell command, returning (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, shell=isinstance(cmd, str)
    )
    return result.returncode, result.stdout, result.stderr


def main():
    if len(sys.argv) > 1 and sys.argv[1].strip():
        raw = sys.argv[1]
        video_id = parse_video_id(raw)
        if not video_id:
            print(f"ERROR: Could not parse a YouTube video ID from: {raw}", file=sys.stderr)
            sys.exit(2)
        print(f"Parsed video ID: {video_id} (from: {raw})")
    else:
        video_id = DEFAULT_VIDEO_ID
        print(f"No URL provided — using default test ID: {video_id}")

    # 1. Generate test.html
    html = render_test_page(video_id)
    TEST_HTML.write_text(html, encoding="utf-8")
    print(f"Wrote: {TEST_HTML}")

    # 2. Stage + commit locally
    rc, out, err = run(["git", "add", "test.html"], cwd=SITE_DIR)
    if rc != 0:
        print(f"ERROR: git add failed: {err}", file=sys.stderr)
        sys.exit(3)

    rc, out, err = run(
        ["git", "commit", "-m", "Smoke test: add test.html with video embed"],
        cwd=SITE_DIR,
    )
    if rc != 0:
        if "nothing to commit" in (out + err):
            print("No changes to commit (test.html already matches current commit).")
        else:
            print(f"ERROR: git commit failed: {err}", file=sys.stderr)
            sys.exit(4)
    else:
        print("Committed test.html locally.")

    # 3. Attempt push
    print("Attempting git push origin main ...")
    rc, out, err = run(["git", "push", "origin", "main"], cwd=SITE_DIR)
    push_ok = (rc == 0)

    print("")
    print("=" * 72)
    if push_ok:
        print("PUSH SUCCEEDED. GitHub Pages should deploy in ~30-60 seconds.")
        print("")
        print("Visit:  https://japan.jconstant.com/test.html")
        print("")
        print("If the video plays inline and the layout looks right, the smoke")
        print("test passed. Then run cleanup.py to remove test.html.")
    else:
        print("PUSH FAILED (expected — sandbox has no GitHub auth).")
        print("")
        print("test.html is committed locally. To push, open Terminal on your Mac:")
        print("")
        mac_path = "~/Claude/Cowork\\ Projects/Summer\\ Plans/japan-trip-site"
        print(f"    cd {mac_path}")
        print(f"    git push origin main")
        print("")
        print("Then wait ~30-60s for Pages to deploy and visit:")
        print("    https://japan.jconstant.com/test.html")
        print("")
        print("(git error was: %s)" % (err.strip().splitlines()[-1] if err.strip() else "unknown"))
    print("=" * 72)


if __name__ == "__main__":
    main()
