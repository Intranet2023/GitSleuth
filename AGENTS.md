# Automated Git Merge Conflict Resolution

These guidelines define how automation agents resolve merge conflicts in this repository.

## Environment Preparation
- Ensure the working directory is clean with `git status`.
- Pull the latest changes using `git pull` before starting a merge or rebase.

## Conflict Identification
- Conflicts will appear during `git merge` or `git rebase`.

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

```

After:
```
(Conflict markers removed completely, resulting in no changes)
```

### Line-Level Code Conflicts

- Automatically resolve by always accepting incoming changes (the new code) over existing code.
- Delete the conflicting local version so that only the latest incoming code remains.

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

# Automated Git Merge Conflict Resolution

This document provides detailed rules for automation agents (bots or AI scripts) to automatically resolve Git merge conflicts consistently and safely, prioritizing incoming changes.

## Conflict Resolution Workflow

### Environment Preparation
- Confirm working directory is clean (`git status`).
- Ensure local branch is up-to-date (`git pull`).


### Conflict Identification
- Detect conflicts using `git merge` or `git rebase`.

- If automated tests fail, post a comment in the PR with the failure details and tag the PR as "failing tests".
- If Dependabot detects security vulnerabilities in a PR, auto-close the PR and notify the submitter to address the security issues.

#### Whitespace and Formatting Conflicts
- Automatically resolve by accepting incoming changes.


#### Line-Level Code Conflicts
- **Do not** auto-merge conflicting code changes.
- Notify maintainers via email or Slack.
- Tag the pull request as `needs human review`.
- Delete feature branches automatically after merging into main.
- Do NOT delete branches labeled as "protected".

#### Deletion vs. Modification Conflicts
- If the incoming branch deleted a file or line, remove it from the target.
- If the incoming branch modified content deleted locally, restore and keep the incoming changes.

#### Concurrent Additions
- Preserve both incoming and local additions when independent, ordering incoming additions first.
- If duplicates or conflicts arise, prefer the incoming additions exclusively.

#### Binary or Unmergeable Files
- Always choose the incoming branch's version.

#### Other Complex Conflicts
- Default to incoming branch changes.
- If the conflict is overly complex (e.g., large code blocks), notify maintainers and tag the PR as `needs human review`.

### Pull Request Issues
- If automated tests fail on a pull request, post a comment detailing the failure and tag the PR as `failing tests`.
- If Dependabot reports security vulnerabilities, auto-close the PR and notify the submitter.

### Branch Management
- Delete feature branches automatically after merging into `main`.
- Do **not** delete branches labeled `protected`.

### Fallback Strategies
- Halt automation and alert maintainers when conflicts exceed complexity thresholds or resolution is uncertain.
- Log unresolved conflicts in detail for maintainers.

### Safety Precautions
- Record all decisions and actions.
- Verify removal of conflict markers.
- Check syntax or compile the code after resolving conflicts.
- Run available tests and abort the merge if validation fails, alerting maintainers immediately.

### Commit and Push Procedures
- Stage all resolved changes with `git add -A` and ensure no unresolved paths (`git status`).
- Commit with a clear message indicating automatic conflict resolution, e.g.,
  `Merge branch 'feature-branch' into 'main' (Auto-resolved conflicts)`.
- Push to the remote repository (`git push`) and monitor CI status, alerting maintainers of any issues immediately.

Following these rules ensures reliable automated merge conflict resolution, maintaining codebase integrity and consistency.
Automated Git Merge Conflict Resolution

This document provides detailed rules for automation agents managing repository operations and handling merge conflicts consistently and safely, prioritizing incoming changes.

Environment Preparation

Confirm the working directory is clean using git status.

Pull the latest changes with git pull to ensure the branch is up-to-date.

Conflict Identification

Detect conflicts using git merge or git rebase.

Resolution Rules

Whitespace and Formatting Conflicts

Automatically resolve by accepting incoming changes.

Empty and Trivial Conflict Blocks

Automatically resolve empty conflicts (no content between conflict markers) by removing conflict markers entirely.

Automatically resolve trivial conflicts containing only branch labels and no substantive content by removing conflict markers entirely.

Automatically resolve trivial conflicts involving only branch markers and whitespace or newline characters by removing conflict markers entirely and retaining clean formatting.

Example:

Before:


After:

(Conflict markers removed completely, resulting in no changes)

Line-Level Code Conflicts

Do NOT auto-merge conflicting code changes:

Notify maintainers via email or Slack.

Tag pull request as "needs human review".

Deletion vs. Modification Conflicts

If the incoming branch deleted a file or line, remove it from the target.

If the incoming branch modified content deleted locally, restore and keep the incoming changes.

Concurrent Additions

Preserve both incoming and local additions when independent, ordering incoming additions first.

If duplicates or conflicts arise, prefer the incoming additions exclusively.

Binary or Unmergeable Files

Always choose the incoming branch's version.

Other Complex Conflicts

Default to incoming changes.

If the conflict is overly complex, notify maintainers and tag the PR as "needs human review".

Pull Request Issues

If automated tests fail, post a comment in the PR with the failure details and tag the PR as "failing tests".

If Dependabot detects security vulnerabilities in a PR, auto-close the PR and notify the submitter to address the security issues.

Branch Management

Delete feature branches automatically after merging into main.

Do NOT delete branches labeled as "protected".

Fallback Strategies

Log unresolved conflicts in detail and halt automation if conflicts exceed complexity thresholds or resolutions are uncertain.

Clearly alert maintainers of these conflicts.

Safety Precautions

Record all decisions and actions in detail.

Verify removal of conflict markers and run available tests.

Abort the merge and alert maintainers if validation fails.

Commit and Push Procedures

Stage all resolved changes with git add -A and ensure there are no unresolved paths (git status).

Commit with a message indicating automatic conflict resolution.

Example: Merge branch 'feature-branch' into 'main' (Auto-resolved conflicts).

Push to the remote repository (git push) and monitor CI status, alerting maintainers of any issues immediately.

Following these rules ensures reliable automated merge conflict resolution, maintaining codebase integrity and consistency.


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

- **Whitespace or formatting only**: accept incoming changes.
- **Empty or trivial blocks**: remove conflict markers entirely.
- **Line-level code conflicts**: prefer the incoming version. Escalate and tag the pull request as `needs human review` if the conflict is complex.
- **Deletion vs. modification**:
  - If the incoming branch deleted lines, delete them.
  - If the incoming branch modified code that was deleted locally, keep the incoming changes.
- **Concurrent additions**: keep both sets when they do not overlap; otherwise prefer incoming changes.
- **Binary or unmergeable files**: choose the incoming version.

## Post-Resolution Steps
1. Stage all resolved files with `git add -A` and verify no conflict markers remain using `git diff --check`.
2. Run the available tests:
   ```bash
   python -m py_compile GitSleuth_GUI.py OAuth_Manager.py Token_Manager.py GitSleuth.py GitSleuth_API.py
   ```
3. Commit the resolution using a message such as `Merge branch 'feature-branch' into 'main' (Auto-resolved conflicts)`.

Following these rules helps keep merges consistent and reliable.

