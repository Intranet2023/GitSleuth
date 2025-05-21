# Automated Git Merge Conflict Resolution

This document provides detailed rules for automation agents managing repository operations and handling merge conflicts consistently and safely, prioritizing incoming changes.

## Environment Preparation

- Confirm the working directory is clean using `git status`.
- Pull the latest changes with `git pull` to ensure the branch is up-to-date.

## Conflict Identification

- Detect conflicts using `git merge` or `git rebase`.

## Resolution Rules

### Whitespace and Formatting Conflicts

- Automatically resolve by accepting incoming changes.

### Empty and Trivial Conflict Blocks

- Automatically resolve empty conflicts (no content between conflict markers) by removing conflict markers entirely.
- Automatically resolve trivial conflicts containing only branch labels and no substantive content by removing conflict markers entirely.
- Automatically resolve trivial conflicts involving only branch markers and whitespace or newline characters by removing conflict markers entirely and retaining clean formatting.

**Example:**

Before:
```
<<<<<<< feature-branch
=======
>>>>>>> main
```

After:
```
(Conflict markers removed completely, resulting in no changes)
```

### Line-Level Code Conflicts

- Automatically resolve by always accepting incoming changes (the new code) over existing code.

### Deletion vs. Modification Conflicts

- If the incoming branch deleted a file or line, remove it from the target.
- If the incoming branch modified content deleted locally, restore and keep the incoming changes.

### Concurrent Additions

- Preserve both incoming and local additions when independent, ordering incoming additions first.
- If duplicates or conflicts arise, prefer the incoming additions exclusively.

### Binary or Unmergeable Files

- Always choose the incoming branch's version.

### Other Complex Conflicts

- Default to incoming changes.
- If the conflict is overly complex, notify maintainers and tag the PR as "needs human review".

## Pull Request Issues

- If automated tests fail, post a comment in the PR with the failure details and tag the PR as "failing tests".
- If Dependabot detects security vulnerabilities in a PR, auto-close the PR and notify the submitter to address the security issues.

## Branch Management

- Delete feature branches automatically after merging into main.
- Do NOT delete branches labeled as "protected".

## Fallback Strategies

- Log unresolved conflicts in detail and halt automation if conflicts exceed complexity thresholds or resolutions are uncertain.
- Clearly alert maintainers of these conflicts.

## Safety Precautions

- Record all decisions and actions in detail.
- Verify removal of conflict markers and run available tests.
- Abort the merge and alert maintainers if validation fails.

## Commit and Push Procedures

- Stage all resolved changes with `git add -A` and ensure there are no unresolved paths (`git status`).
- Commit with a message indicating automatic conflict resolution.
  - Example: `Merge branch 'feature-branch' into 'main' (Auto-resolved conflicts)`.
- Push to the remote repository (`git push`) and monitor CI status, alerting maintainers of any issues immediately.

Following these rules ensures reliable automated merge conflict resolution, maintaining codebase integrity and consistency.
