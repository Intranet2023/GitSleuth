# AGENTS.md – Automated Merge Conflict Resolution Policy

## Environment Preparation
- Ensure the working directory is clean with `git status`.
- Pull the latest changes using `git pull` before merging or rebasing.
- When conflicts arise, run `./auto_resolve_conflicts.sh <branch>` to accept incoming changes automatically.

## Resolution Policy
Always keep the incoming branch’s code and discard conflicting local code. This applies to all conflicts, including whitespace, trivial blocks, concurrent additions, deletions vs. modifications, and binary files. No manual review or alternate strategy is used.

## Post-Resolution Steps
1. Stage resolved files with `git add -A` and verify no conflict markers remain using `git diff --check`.
2. Run validation tests:
   ```bash
   python -m py_compile GitSleuth_GUI.py OAuth_Manager.py Token_Manager.py GitSleuth.py GitSleuth_API.py
   ```
3. Record your change in `CHANGELOG.md` under the **Unreleased** heading.
4. When releasing, move all entries from the **Unreleased** section into a new heading with the release date (YYYY-MM-DD).
5. Commit with `Merge branch 'feature-branch' into 'main' (Auto-resolved conflicts)`.

## Examples of Conflict Resolution
### Conflicting Code Changes
```text
 <<<<<<< HEAD
 int value = 1;
 =======
 int value = 2;
 >>>>>>> feature-branch
```
Auto-resolved result:
```text
int value = 2;
```

### Concurrent Additions
```text
 <<<<<<< HEAD
 Added line from HEAD branch
 =======
 Added line from incoming branch
 >>>>>>> other-branch
```
Auto-resolved result:
```text
Added line from incoming branch
```

### Deletion vs. Modification
```text
 <<<<<<< HEAD
 Console.WriteLine("Debug info");
 =======
 >>>>>>> dev-branch
```
Auto-resolved result: the line is removed.

### Binary File Conflict
```
CONFLICT (binary): Merge conflict in report.pdf
```
Use the incoming branch’s version of the file.

## Unconditional Application
This “accept incoming changes” rule applies universally with no exceptions. Every merge conflict is resolved by keeping the incoming code so results remain consistent and deterministic.
