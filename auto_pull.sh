#!/bin/bash
# Pull latest changes and auto-resolve conflicts using the trusted local resolver.
set -euo pipefail

current_branch=$(git rev-parse --abbrev-ref HEAD)
trusted_resolver=$(mktemp)
trap 'rm -f "$trusted_resolver"' EXIT

git show HEAD:auto_resolve_conflicts.sh > "$trusted_resolver"
chmod +x "$trusted_resolver"

git pull || "$trusted_resolver" "$current_branch"

exit 0
