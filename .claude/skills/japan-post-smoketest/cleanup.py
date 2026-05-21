#!/usr/bin/env python3
"""
Japan trip site — smoke test cleanup.

Removes test.html (created by post.py), commits the removal, and tries to push.
If the sandbox lacks GitHub auth, prints the exact Terminal command to run
from Justin's Mac to complete the push.

Usage:
    python3 cleanup.py
"""

import subprocess
from pathlib import Path

# Skill lives at: <repo>/.claude/skills/japan-post-smoketest/cleanup.py
SITE_DIR = Path(__file__).resolve().parent.parent.parent.parent
TEST_HTML = SITE_DIR / "test.html"


def run(cmd, cwd=None):
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, shell=isinstance(cmd, str)
    )
    return result.returncode, result.stdout, result.stderr


def main():
    if not TEST_HTML.exists():
        print(f"test.html not found at {TEST_HTML} — nothing to clean up.")
        # Still check git in case it's already-deleted-but-not-committed
        rc, out, err = run(["git", "status", "--porcelain", "test.html"], cwd=SITE_DIR)
        if not out.strip():
            print("Working tree is clean for test.html. Done.")
            return

    # Remove the file (use git rm so the deletion is staged)
    rc, out, err = run(["git", "rm", "-f", "test.html"], cwd=SITE_DIR)
    if rc != 0:
        # Fall back to plain rm if git rm fails (e.g., file was already deleted)
        if TEST_HTML.exists():
            TEST_HTML.unlink()
        run(["git", "add", "-A", "test.html"], cwd=SITE_DIR)
    print("Removed test.html and staged the deletion.")

    # Commit
    rc, out, err = run(
        ["git", "commit", "-m", "Smoke test: remove test.html"], cwd=SITE_DIR
    )
    if rc != 0:
        if "nothing to commit" in (out + err):
            print("Nothing to commit.")
        else:
            print(f"ERROR: git commit failed: {err}")
            return
    else:
        print("Committed removal locally.")

    # Push
    print("Attempting git push origin main ...")
    rc, out, err = run(["git", "push", "origin", "main"], cwd=SITE_DIR)
    push_ok = (rc == 0)

    print("")
    print("=" * 72)
    if push_ok:
        print("PUSH SUCCEEDED. GitHub Pages will redeploy in ~30-60 seconds.")
        print("japan.jconstant.com/test.html will return 404. Cleanup complete.")
    else:
        print("PUSH FAILED (expected — sandbox has no GitHub auth).")
        print("")
        print("The deletion is committed locally. To finish cleanup, open Terminal:")
        print("")
        mac_path = "~/Claude/Cowork\\ Projects/Summer\\ Plans/japan-trip-site"
        print(f"    cd {mac_path}")
        print(f"    git push origin main")
        print("")
        print("(git error was: %s)" % (err.strip().splitlines()[-1] if err.strip() else "unknown"))
    print("=" * 72)


if __name__ == "__main__":
    main()
