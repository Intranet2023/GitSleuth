# AGENTS.md – Automated Merge Conflict Resolution Policy

**Purpose:** This document defines the automation policy for Git merge conflict resolution by code agents (bots or AI scripts). It mandates a single, deterministic rule: **always resolve conflicts by accepting the incoming (new) code changes in their entirety**, discarding conflicting changes from the current branch. This approach applies to *all* types of merge conflicts and ensures merges are handled consistently and without manual intervention.

## Scope: All Merge Conflict Types

This policy applies universally to every kind of Git merge conflict, including but not limited to:

* **Line-by-line code conflicts:** Cases where both branches modify the same lines or sections of a file differently.
* **Concurrent additions:** Situations where both branches add new lines or blocks in the same location (e.g. both introduce different code or text at the same point).
* **Deletion vs. modification conflicts:** Scenarios where one branch deletes a file or code block that the other branch edits or retains.
* **Binary file conflicts:** Conflicts in non-text files (images, binaries, etc.) that were changed in both branches.
* **Trivial/whitespace conflicts:** Even conflicts that stem solely from whitespace or formatting differences (empty or trivial changes) are handled with the same rule.

## Conflict Resolution Procedure

When a merge conflict is detected, the agent will automatically resolve it by **keeping the incoming branch’s changes and discarding the current branch’s changes**. The process is as follows:

1. **Identify conflict regions:** For each conflicted file, locate the Git conflict markers:

   * `<<<<<<< HEAD` (marks the beginning of the current branch’s version)
   * `=======` (marks the separation between versions)
   * `>>>>>>> <branch-name>` (marks the end of the incoming branch’s version)
2. **Keep incoming content:** Remove the `<<<<<<< HEAD` marker and everything up to the `=======` line. This discards the current branch’s conflicting content. Also remove the `=======` and `>>>>>>> <branch-name>` markers, keeping only the code from the incoming branch between them.
3. **Apply to all conflicts:** Ensure that *every* conflict block in the file is handled by preserving only the incoming portion. No mixing or partial merges of content – the incoming side wholly replaces the conflicted section.
4. **Handle file-level conflicts:** If a file was deleted on the current branch but modified on the incoming branch (or vice versa), prefer the incoming branch’s outcome. For example:

   * If the incoming branch deleted the file, the file is deleted in the merge result.
   * If the incoming branch kept or modified the file while the current branch deleted it, the file remains (with the incoming branch’s changes) in the merge result.
5. **Resolve binary conflicts:** For a binary file conflict (which cannot be merged line-by-line), replace the current branch’s version of the file with the incoming branch’s version. Mark the file as resolved by using the incoming file without attempting to merge contents.
6. **Mark as resolved and commit:** After adjusting all conflicted files by accepting incoming changes, the agent marks them as resolved (e.g., via `git add`) and creates a merge commit. The resulting commit will contain only the incoming branch’s changes in conflict areas.

## Examples of Conflict Resolution

Below are examples of various conflict scenarios and how the agent applies the “accept incoming changes” rule to each. Conflict markers `<<<<<<<`, `=======`, `>>>>>>>` illustrate the state of a file during a merge conflict, and the resolution shows the file content after the agent’s automatic merge.

### Example: Conflicting Code Changes (both branches modified the same code)

Suppose two branches made different edits to the same line:

```
 <<<<<<< HEAD
int value = 1;
 =======
int value = 2;
 >>>>>>> feature-branch
```

In this conflict, the current branch (HEAD) defines `value` as 1, while the incoming `feature-branch` sets it to 2.

**Auto-resolved result (keeping incoming changes):**

```
int value = 2;
```

The agent drops the HEAD version and keeps the incoming branch’s code, resulting in `value` being 2.

### Example: Concurrent Additions (both branches added content in the same place)

Consider that both branches added a different line at the same location in a file:

```
 <<<<<<< HEAD
Added line from HEAD branch
 =======
Added line from incoming branch
 >>>>>>> other-branch
```

Here each branch introduced a new line with unique content.

**Auto-resolved result:**

```
Added line from incoming branch
```

Only the incoming branch’s new line is kept; the line added by HEAD is discarded.

### Example: Deletion vs. Modification Conflict

Imagine the current branch retained a piece of code that the incoming branch removed:

```
 <<<<<<< HEAD
Console.WriteLine("Debug info");
 =======
 >>>>>>> dev-branch
```

HEAD still has this line, but the incoming `dev-branch` deleted it (shown by an empty section after the `=======` line).

**Auto-resolved result:** *The line is removed*, because the incoming branch’s decision (to delete that code) is respected. The merged file will not contain `Console.WriteLine("Debug info");`.

Conversely, if the roles were reversed (the current branch deleted something that the incoming branch kept or changed), the incoming content would be restored in the merge. In all cases, the incoming branch’s version wins.

### Example: Binary File Conflict

If both branches edited a binary file (for example, a PDF report or an image), Git flags a conflict without inline markers:

```
CONFLICT (binary): Merge conflict in report.pdf
```

In this case, the agent will **take the incoming branch’s version** of *report.pdf* and use it in the merge result. The current branch’s version of the file is discarded. After copying the incoming file over, the conflict is marked resolved. No attempt is made to merge binary content; the incoming file simply replaces the current one.

*Note:* Even conflicts stemming from minor differences (like whitespace-only changes) are resolved in favor of the incoming side. The agent does not attempt to merge or reconcile such trivial differences – it will simply take the incoming version as-is.

## Unconditional Application (No Exceptions)

This “accept incoming changes” policy is applied **without exceptions**. The agent will not defer to manual review or use any alternate strategy regardless of conflict type or complexity. Previous guidelines that allowed for human intervention or special-case handling (for example, for binary files or extensive conflicts) are overridden by this update.

Every conflict, from simple line edits to complex merges and binary file divergences, is resolved automatically by this rule. The bot will consistently prefer incoming changes and finalize the merge. There is no fallback to a human or an alternate merge strategy; **all** conflicts are handled autonomously by accepting incoming code.

## Consistency, Determinism, and Repository Integrity

Adhering to a single resolution rule for all conflicts ensures the merge process is consistent and deterministic:

* **Consistent outcomes:** Every merge performed by an agent follows the same pattern, leading to uniform results. The policy doesn’t change based on file type or context – incoming changes are always chosen – so developers and tools can predict how conflicts will be resolved every time.
* **Deterministic merges:** Given the same two branches, this policy will produce the same merge result, no matter when or how often it’s applied. There’s no randomness or case-by-case judgment; the outcome is solely determined by the incoming branch’s content. This predictability simplifies automated workflows and testing.
* **Repository integrity:** By automatically resolving conflicts in a predefined way, the repository is kept in a valid state. There are no leftover conflict markers or half-resolved files, which means no broken builds due to unresolved merge artifacts. Each merge commit contains coherent file content (the incoming changes), preserving the integrity of the codebase. By avoiding manual edits, this approach also eliminates the risk of human error during conflict resolution.

This updated **AGENTS.md** policy serves as the authoritative guide for merge agents. All automated merge tools and AI assistants should follow these rules to ensure reliable, conflict-free integration of code changes by always accepting incoming modifications during merges.
