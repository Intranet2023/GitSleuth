# Automated Git Merge Conflict Resolution

These guidelines define how automation agents resolve merge conflicts in this repository.

## Environment Preparation
- Ensure the working directory is clean with `git status`.
- Pull the latest changes using `git pull` before starting a merge or rebase.

## Conflict Identification
- Conflicts will appear during `git merge` or `git rebase`.

## Resolution Rules
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
