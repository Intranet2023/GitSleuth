Automated Git Merge Conflict Resolution

This document defines how automation agents (bots/scripts) resolve merge conflicts consistently in this repository. The policy strictly mandates always accepting incoming (new) changes, discarding conflicting changes from the current branch.

## Environment Preparation
- Ensure a clean working directory with `git status`.
- Pull the latest changes (`git pull`) before merging or rebasing.

## Conflict Identification and Resolution
When conflicts appear during `git merge` or `git rebase`:

Run the provided conflict resolution script:

```
./auto_resolve_conflicts.sh <branch>
```

This script resolves all conflicts by prioritizing incoming code.

## Resolution Rules
### General Rule
- Always accept incoming changes from the merged branch.
- Remove conflicting local changes entirely.

This applies to all conflict types, including:
- Line-level code conflicts
- Concurrent additions
- Deletion vs. modification
- Binary/unmergeable files
- Whitespace and formatting differences
- Empty/trivial conflict blocks

### Specific Conflict Handling Examples
#### Whitespace and Formatting Conflicts
Automatically resolve by accepting incoming changes.

#### Empty/Trivial Conflict Blocks
Remove conflict markers entirely.

Example:
```
 <<<<<<< feature-branch
 =======
 >>>>>>> main
```
After:
```
(No content, markers removed)
```

#### Line-Level Code Conflicts
Discard local changes and keep incoming.

Example:
```
 <<<<<<< HEAD
int value = 1;
 =======
int value = 2;
 >>>>>>> feature-branch
```
After:
```
int value = 2;
```

#### Deletion vs. Modification Conflicts
Always accept the incoming branch’s decision.

Example (incoming deletes line):
```
 <<<<<<< HEAD
Console.WriteLine("Debug info");
 =======
 >>>>>>> dev-branch
```
After:
(Line removed completely.)

#### Concurrent Additions
Prefer incoming additions exclusively.

Example:
```
 <<<<<<< HEAD
Local line added.
 =======
Incoming line added.
 >>>>>>> main
```
After:
```
Incoming line added.
```

#### Binary or Unmergeable Files
Replace the current branch’s file entirely with the incoming file version.

## Post-Resolution Steps
1. Stage resolved files:
   ```bash
   git add -A
   ```
2. Verify no conflict markers remain:
   ```bash
   git diff --check
   ```
3. Run validation tests:
   ```bash
   python -m py_compile GitSleuth_GUI.py OAuth_Manager.py Token_Manager.py GitSleuth.py GitSleuth_API.py
   ```
4. Commit with standardized message:
   ```
   Merge branch 'feature-branch' into 'main' (Auto-resolved conflicts)
   ```

## Policy Application: No Exceptions
This "accept incoming changes" rule applies universally without exceptions. Automation agents will never defer to manual review or alternative strategies, ensuring:
- **Consistency:** Identical merges produce identical results every time.
- **Determinism:** Results are predictable, simplifying automated workflows.
- **Repository Integrity:** Code remains coherent and immediately usable post-merge.
