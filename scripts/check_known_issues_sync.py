#!/usr/bin/env python3
"""
Checks that the README's "Known Issues" section only lists valid, open GitHub issues
and that each list item has a direct link matching the referenced issue number.

Exit codes:
- 0: OK
- 1: README not found or parsing error
- 2: One or more issues invalid (missing, closed, mismatched link)

Environment:
- GITHUB_TOKEN (optional locally, Actions provides this automatically)
- GITHUB_REPOSITORY (org/repo) used by default in Actions

Usage (local):
  export GITHUB_TOKEN=...  # with repo:read scope
  python scripts/check_known_issues_sync.py --repo athena-ceo/trusted-service
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import List, Tuple

import urllib.request

README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")
README_PATH = os.path.abspath(README_PATH)

KNOWN_ISSUES_HEADER = "## 🚧 Known Issues"

ISSUE_LINE_PATTERN = re.compile(r"^\s*-\s*#(?P<num>\d+):(?P<rest>.*?)(?P<link>https://github.com/[^\s]+/issues/(?P<linknum>\d+))\s*$")


def gh_api_get(url: str, token: str | None) -> tuple[int, str]:
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.getcode(), resp.read().decode("utf-8")
    except Exception as e:
        return 0, str(e)


def find_known_issues_lines(readme_text: str) -> List[str]:
    lines = readme_text.splitlines()
    try:
        start_idx = next(i for i, l in enumerate(lines) if l.strip() == KNOWN_ISSUES_HEADER)
    except StopIteration:
        return []

    # Scan until the next header (## ) or end of file, collect bullet lines that start with '- #'
    collected: List[str] = []
    for line in lines[start_idx + 1 :]:
        if line.startswith("## "):
            break
        if re.match(r"^\s*-\s*#\d+:", line):
            collected.append(line.rstrip())
    return collected


def parse_issue_line(line: str) -> Tuple[int, int]:
    """Return (issue_number, link_number) from a bullet line, or raise ValueError."""
    m = ISSUE_LINE_PATTERN.match(line)
    if not m:
        raise ValueError(f"Line does not match expected issue format: {line}")
    num = int(m.group("num"))
    linknum = int(m.group("linknum"))
    return num, linknum


def validate_issue_open(owner: str, repo: str, issue_number: int, token: str | None) -> Tuple[bool, str]:
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    code, text = gh_api_get(url, token)
    if code != 200:
        return False, f"GitHub API error for issue #{issue_number}: HTTP {code} {text}"
    try:
        data = json.loads(text)
    except Exception as e:
        return False, f"Invalid JSON for issue #{issue_number}: {e}"
    if data.get("state") != "open":
        return False, f"Issue #{issue_number} is not open (state={data.get('state')})"
    return True, ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=os.getenv("GITHUB_REPOSITORY", "athena-ceo/trusted-service"), help="owner/repo")
    parser.add_argument("--readme", default=README_PATH)
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")

    try:
        with open(args.readme, "r", encoding="utf-8") as f:
            readme = f.read()
    except Exception as e:
        print(f"ERROR: cannot read README at {args.readme}: {e}", file=sys.stderr)
        return 1

    issue_lines = find_known_issues_lines(readme)
    if not issue_lines:
        print("ERROR: Known Issues section not found or no issue entries.", file=sys.stderr)
        return 1

    owner, repo = args.repo.split("/", 1)

    errors: List[str] = []
    for line in issue_lines:
        try:
            num, linknum = parse_issue_line(line)
        except ValueError as e:
            errors.append(str(e))
            continue
        if num != linknum:
            errors.append(f"Mismatch between referenced issue #{num} and link issue #{linknum}: {line}")
            continue
        ok, msg = validate_issue_open(owner, repo, num, token)
        if not ok:
            errors.append(msg)

    if errors:
        print("Known Issues validation failed:")
        for err in errors:
            print(f" - {err}")
        return 2

    print("Known Issues validation passed: all referenced issues exist, are open, and links match.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
