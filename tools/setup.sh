#!/usr/bin/env bash
# One-time setup per teammate: installs OpenFisca and switches on the rulebook
# checks (on commit and on push) and the commit message template.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

command -v uv >/dev/null || {
  echo "uv is missing. Install it: https://docs.astral.sh/uv/getting-started/installation/"
  exit 1
}

(cd openfisca-CH-SG && uv sync --locked --all-extras --dev)
uv run --project openfisca-CH-SG --frozen pre-commit install
git config commit.template .gitmessage

echo
echo "Done. Checks now run on every commit and push. Read RULEBOOK.md."
