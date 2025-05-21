#!/usr/bin/env python3
"""Remove local and remote branches that have already been merged.

Branches listed in ``PROTECTED_BRANCHES`` will never be deleted.
"""
import subprocess
import sys

PROTECTED_BRANCHES = {"main", "protected"}


def run(cmd):
    """Run a shell command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
    return result.stdout.strip()


def delete_local_branches():
    branches = run("git branch --merged").splitlines()
    for branch in branches:
        branch = branch.strip().lstrip('* ')
        if branch and branch not in PROTECTED_BRANCHES:
            subprocess.run(["git", "branch", "-d", branch], check=False)


def delete_remote_branches():
    branches = run("git branch -r").splitlines()
    for ref in branches:
        ref = ref.strip()
        if '/' not in ref:
            continue
        remote, name = ref.split('/', 1)
        if name and name not in PROTECTED_BRANCHES:
            subprocess.run(["git", "push", remote, "--delete", name], check=False)


if __name__ == "__main__":
    delete_local_branches()
    delete_remote_branches()
