#!/usr/bin/env python3
import subprocess
from collections import Counter, defaultdict
from datetime import datetime

def run_git_command(args):
    """Run a git command and return output lines."""
    result = subprocess.run(
        ["git"] + args, capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Error:", result.stderr.strip())
        exit(1)
    return result.stdout.strip().split("\n")

def stats():
    commits = run_git_command(["rev-list", "--all", "--count"])[0]
    authors = run_git_command(["log", "--pretty=format:%an"])
    unique_authors = set(authors)
    print("=== Repository Stats ===")
    print(f"Total commits: {commits}")
    print(f"Unique authors: {len(unique_authors)}")

def top_contributors(n=5):
    authors = run_git_command(["log", "--pretty=format:%an"])
    counts = Counter(authors)
    print(f"\n=== Top {n} Contributors ===")
    for author, count in counts.most_common(n):
        print(f"{author:20} {count}")

def top_files(n=5):
    numstat = run_git_command(["log", "--numstat", "--pretty=format:"])
    file_changes = Counter()
    for line in numstat:
        parts = line.split()
        if len(parts) == 3:
            _, _, filename = parts
            file_changes[filename] += 1
    print(f"\n=== Top {n} Modified Files ===")
    for fname, count in file_changes.most_common(n):
        print(f"{fname:40} {count}")

def timeline():
    dates = run_git_command(["log", "--date=short", "--pretty=format:%ad"])
    weeks = defaultdict(int)
    for d in dates:
        if not d.strip():
            continue
        dt = datetime.strptime(d, "%Y-%m-%d")
        year_week = f"{dt.year}-W{dt.isocalendar().week}"
        weeks[year_week] += 1
    print("\n=== Commits per Week ===")
    for week, count in sorted(weeks.items()):
        bar = "█" * (count // 2 + 1)  # 1 block per ~2 commits
        print(f"{week}: {count:3} {bar}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python inspector.py [stats|top|files|timeline]")
        exit(1)

    cmd = sys.argv[1]
    if cmd == "stats":
        stats()
    elif cmd == "top":
        top_contributors()
    elif cmd == "files":
        top_files()
    elif cmd == "timeline":
        timeline()
    else:
        print("Unknown command:", cmd)

