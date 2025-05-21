# Automated Git Merge Conflict Resolution

This document provides detailed rules for automation agents (bots or AI scripts) to automatically resolve Git merge conflicts consistently and safely, prioritizing incoming changes.

## Conflict Resolution Workflow

### Environment Preparation
- Confirm working directory is clean (`git status`).
- Ensure local branch is up-to-date (`git pull`).

### Conflict Identification
- Detect conflicts using `git merge` or `git rebase`.

## Resolution Rules

### Whitespace and Formatting Conflicts
- Automatically resolve by accepting incoming changes.

### Empty Conflict Blocks
- Automatically resolve empty conflicts (no content between conflict markers) by removing conflict markers entirely.

### Line-Level Code Conflicts
- **Do NOT** auto-merge conflicting code changes:
  - Notify maintainers via email or Slack.
  - Tag pull request as "needs human review".

### Deletion vs. Modification Conflicts
- If the incoming branch deleted a file or line, respect the deletion and remove it from the target.
- If the incoming branch modified content deleted locally, restore and keep the incoming changes.

### Concurrent Additions
- Preserve both incoming and local additions when independent:
  - Order incoming additions first.
  - If conflicts or duplicates arise, prefer incoming additions exclusively.

### Binary or Unmergeable Files
- Always choose the incoming branch's version of the file.

### Other Complex Conflicts
- Default to incoming branch changes.
- If conflicts are overly complex (e.g., large code blocks), defer to human review:
  - Notify maintainers via email or Slack.
  - Tag pull request as "needs human review".

## Pull Request Issues
- If automated tests fail on a pull request:
  - Post a comment in the PR detailing the failure.
  - Tag the PR as "failing tests".
- If Dependabot detects security vulnerabilities in a PR:
  - Auto-close the PR.
  - Notify the submitter to address security issues first.

## Branch Management
- Delete feature branches automatically after merging into `main`.
- Do NOT delete branches labeled as "protected".

## Fallback Strategies
- Alert maintainers clearly and halt automation for conflicts:
  - Exceeding complexity thresholds (large chunks, multiple files).
  - Uncertain automatic resolutions.
- Log unresolved conflicts in detail for maintainers.

## Safety Precautions
- **Detailed Logging:** Record all decisions and actions.
- **Validation:**
  - Verify removal of conflict markers.
  - Check syntax or compile the code post-resolution.
  - Run available test suites.
  - Abort merge if validation fails and alert maintainers immediately.

## Commit and Push Procedures
- Stage all resolved changes (`git add -A`).
- Ensure no unresolved paths (`git status`).
- Commit clearly indicating automatic conflict resolution:
  - Example: `Merge branch 'feature-branch' into 'main' (Auto-resolved conflicts)`.
- Push merge to remote repository (`git push`).
- Monitor push success and CI pipeline status, alert maintainers of any issues immediately.

Following these rules ensures reliable automated merge conflict resolution, maintaining codebase integrity and consistency.
