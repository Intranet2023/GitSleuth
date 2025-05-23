#!/bin/bash
# Auto merge with incoming changes using 'theirs' strategy.
# Usage: ./auto_resolve_conflicts.sh <incoming-branch>

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <incoming-branch>" >&2
    exit 1
fi

incoming_branch="$1"

# Fetch latest changes from origin
if git remote get-url origin >/dev/null 2>&1; then
    git fetch origin "$incoming_branch"
fi

# Merge using theirs strategy to prefer incoming changes
if git merge -X theirs "origin/$incoming_branch"; then
    echo "Merged $incoming_branch with incoming changes prioritized."
else
    echo "Merge failed. Manual resolution may be required." >&2
    exit 1
fi

# Verify no conflict markers remain
if git diff --check | grep '<<<<' >/dev/null; then
    echo "Conflict markers remain. Please resolve manually." >&2
    exit 1
fi

exit 0
