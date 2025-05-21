# AGENTS.md

This file provides instructions for automation agents (bots, scripts) managing repository operations.

## Merge Conflicts

If an agent encounters a merge conflict during an automated merge:

- **Check** if the conflict is only whitespace or formatting-related:
  - If so, auto-resolve by accepting the incoming changes.
- If code changes conflict:
  - Create a notification via email or Slack to the repository maintainer.
  - Do NOT auto-merge code changes.
  - Tag the PR as "needs human review".

## Pull Request Issues

- If a pull request fails automated tests:
  - Post a comment in the PR with the failure details.
  - Tag the PR as "failing tests".
- If the PR includes security vulnerabilities detected by Dependabot:
  - Auto-close PR and inform the submitter to address security concerns first.

## Branch Management

- Delete feature branches once merged into `main`.
- Do NOT delete branches labeled as "protected".

