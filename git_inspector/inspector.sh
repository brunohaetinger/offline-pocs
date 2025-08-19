#!/bin/bash

cmd="$1"

if [ -z "$cmd" ]; then
  echo "Usage: ./inspector.sh [stats|top|files|timeline|days|hours]"
  exit 1
fi

stats() {
  echo "=== Repository Stats ==="
  echo "Total commits: $(git rev-list --all --count)"
  echo "Unique authors: $(git log --format='%an' | sort -u | wc -l)"
  echo "Project age: $(git log --reverse --format='%ad' | head -n1)"
}

top() {
  echo "=== Top Contributors ==="
  git log --format='%an' | sort | uniq -c | sort -nr | head -n 5
}

files() {
  echo "=== Top Modified Files ==="
  git log --numstat --format="" | awk '{print $3}' | sort | uniq -c | sort -nr | head -n 5
}

timeline() {
  echo "=== Commits per Week ==="
  git log --date=short --format="%ad" |
    awk -F"-" '{print $1"-W"strftime("%V", mktime($1" "$2" "$3" 0 0 0"))}' |
    sort | uniq -c
}

days() {
  echo "=== Commits per Day of Week ==="
  git log --date=format:'%A' --format='%ad' |
    sort | uniq -c | sort -nr
}

hours() {
  echo "=== Commits per Hour of Day ==="
  git log --date=format:'%H' --format='%ad' |
    sort | uniq -c | sort -n
}

case "$cmd" in
stats) stats ;;
top) top ;;
files) files ;;
timeline) timeline ;;
days) days ;;
hours) hours ;;
*) echo "Unknown command: $cmd" ;;
esac
