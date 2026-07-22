#!/bin/bash
set -euo pipefail

# Only run this in Claude Code on the web — local devs already get this via .devcontainer.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

# apt-get update is allowed to fail here (an unrelated third-party repo can be unsigned/blocked)
# as long as the Debian package lists it needs land — see .devcontainer/devcontainer.json.
sudo apt-get update || true
sudo apt-get install -y libgl1 openscad imagemagick xvfb

uv sync
pnpm install
uv run pre-commit install
