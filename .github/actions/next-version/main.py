#!/usr/bin/env python3
import subprocess
import json

# --- helper to run shell commands ---
def run(cmd):
    return subprocess.check_output(cmd, shell=True, text=True).strip()

# --- 1. Get last tag ---
try:
    last_tag = run("git describe --tags --abbrev=0")
except subprocess.CalledProcessError:
    print("⚠️ No tags found, using 0.0.0 as base")
    last_tag = "0.0.0"
print(f"Last tag: {last_tag}")

# --- 2. Fetch merged PRs since last tag ---
prs_json = run(f"gh pr list --state merged --base main --search 'merged:>{last_tag}' --json number,labels")
prs = json.loads(prs_json)

# --- 3. Determine bump ---
bump = "patch"
for pr in prs:
    labels = [label["name"] for label in pr.get("labels", [])]
    if "type: major" in labels:
        bump = "major"
        break
    elif "type: minor" in labels and bump != "major":
        bump = "minor"

print(f"Determined bump: {bump}")

# --- 4. Compute next version ---
major, minor, patch = map(int, last_tag.split("."))
if bump == "major":
    major += 1
    minor = 0
    patch = 0
elif bump == "minor":
    minor += 1
    patch = 0
else:
    patch += 1

next_version = f"{major}.{minor}.{patch}"
print(f"Next version: {next_version}")

# --- 5. Write output for GitHub Actions ---
print(f"::set-output name=next-version::{next_version}")
