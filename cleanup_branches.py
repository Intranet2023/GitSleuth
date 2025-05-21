#!/usr/bin/env python3
"""Remove merged branches locally and remotely.

This script deletes branches that are already merged into `main`.
Branches named `main` or containing the word `protected` are skipped.
"""
import subprocess

KEEP = {"main"}
PROTECTED_KEYWORD = "protected"


def run(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, check=False)
    return result.stdout.strip().splitlines()


def cleanup_local():
    branches = run(["git", "branch", "--merged", "main"])
    for branch in branches:
        b = branch.strip().lstrip("* ")
        if not b or b in KEEP or PROTECTED_KEYWORD in b:
            continue
        subprocess.run(["git", "branch", "-d", b])


def cleanup_remote():
    branches = run(["git", "branch", "-r", "--merged", "origin/main"])
    for branch in branches:
        b = branch.strip()
        if not b.startswith("origin/"):
            continue
        name = b.split("/", 1)[1]
        if name in KEEP or PROTECTED_KEYWORD in name:
            continue
        subprocess.run(["git", "push", "origin", "--delete", name])


if __name__ == "__main__":
    cleanup_local()
    cleanup_remote()
