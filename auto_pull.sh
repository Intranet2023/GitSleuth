#!/bin/bash
# Pull latest changes and auto-resolve conflicts using 'theirs'.
set -e

current_branch=$(git rev-parse --abbrev-ref HEAD)

git pull || ./auto_resolve_conflicts.sh "$current_branch"

exit 0
