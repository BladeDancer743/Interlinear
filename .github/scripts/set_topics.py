#!/usr/bin/env python3
"""
Interlinear GitHub Topics Setter
--------------------------------
Uses GitHub REST API to set repository topics.
Requires: A GitHub Personal Access Token with repo scope.

Usage:
    python set_topics.py <token>
or:
    python set_topics.py          # prompts for token
"""

import urllib.request, urllib.error, json, sys, getpass

REPO_OWNER = "BladeDancer743"
REPO_NAME = "Interlinear"

TOPICS = [
    "claude-skills",
    "opencode-skills",
    "agent-skills",
    "llm-skills",
    "quantum-computing",
    "paper-reading",
    "chinese-translation",
    "academic-writing",
    "physics",
    "skill",
    "knowledge-base",
]

def set_topics(token):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/topics"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    body = json.dumps({"names": TOPICS}).encode("utf-8")

    req = urllib.request.Request(url, data=body, headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            names = result.get("names", [])
            print(f"[OK] Topics set successfully: {len(names)} tags")
            for t in names:
                print(f"     · {t}")
    except urllib.error.HTTPError as e:
        msg = e.read().decode()
        print(f"[ERR] HTTP {e.code}: {msg[:300]}")
        if e.code == 401:
            print("      Token is invalid or expired. Generate one at:")
            print("      https://github.com/settings/tokens")
    except Exception as e:
        print(f"[ERR] {e}")

def main():
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        token = getpass.getpass("GitHub Personal Access Token: ")

    if not token:
        print("[ERR] No token provided.")
        print("      Generate one at: https://github.com/settings/tokens")
        sys.exit(1)

    print(f"Setting topics for {REPO_OWNER}/{REPO_NAME}...")
    print(f"Topics: {', '.join(TOPICS)}")
    print()
    set_topics(token)

if __name__ == "__main__":
    main()
