#!/bin/bash
# Installs ImageMagick so HEIC/HEIF photos (iPhone default) can be converted to
# JPEG during a trip update. The cloud container is ephemeral and rebuilt each
# session, so this runs on every start. Most photos arrive as JPEG, so a failed
# install only disables the HEIC fallback — it never blocks a session.
set -uo pipefail

# Only relevant in Claude Code on the web; locally the user has their own tools.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Idempotent: nothing to do if a converter is already present.
if command -v magick >/dev/null 2>&1 || command -v convert >/dev/null 2>&1; then
  exit 0
fi

export DEBIAN_FRONTEND=noninteractive
if ! { apt-get update -qq && apt-get install -y -qq imagemagick libheif1; } \
     >/tmp/japan-session-start.log 2>&1; then
  echo "session-start: ImageMagick install failed; HEIC->JPEG fallback unavailable. See /tmp/japan-session-start.log" >&2
fi
