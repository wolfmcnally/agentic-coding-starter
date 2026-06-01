#!/usr/bin/env bash
#
# check-anonymization.sh — pre-publish guard against private-repo leaks.
#
# This repository is public (see policies/anonymize-log-references.md). No
# committed file may carry a private or external project's identity: a real
# absolute / home path, a commit SHA of an external repo, or a private
# project name. This script catches the two *mechanizable* classes —
# real paths and SHA-like tokens — across every tracked file, plus any
# terms listed in an optional, gitignored local denylist. The judgment
# part the patterns cannot catch (verbatim external project names framed in
# prose) stays a code-critic / human review call.
#
#   scripts/check-anonymization.sh          scan; exit 1 on findings
#   scripts/check-anonymization.sh --help   this text
#
# Local name denylist (optional, never committed): copy
# scripts/anonymization-denylist.local.example to
# scripts/anonymization-denylist.local and add one private project name or
# identifier per line. The .local file is gitignored so the names it lists
# are never themselves leaked into this public repo.
#
# Starter-only: NOT transferred by /starter or /teach to derived projects.
# A private downstream project has nothing to anonymize against itself.

set -euo pipefail

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  sed -n '2,/^set -euo/p' "$0" | sed 's/^# \{0,1\}//; $d'
  exit 0
fi

cd "$(git rev-parse --show-toplevel)"

SELF='scripts/check-anonymization.sh'
DENYLIST='scripts/anonymization-denylist.local'
status=0

report() {
  # $1 = section title, $2 = findings (empty if clean)
  if [[ -n "$2" ]]; then
    printf '\n✗ %s\n' "$1"
    printf '%s\n' "$2" | sed 's/^/    /'
    status=1
  fi
}

# --- 1. Real absolute / home paths -----------------------------------------
# Match /Users/<user>/, /home/<user>/, C:\Users\<user>\, and real ~/<homedir>.
# Illustrative placeholders are excluded by construction: a "<name>"-style
# token contains angle brackets, which fall outside [A-Za-z0-9._-], so it
# never matches; and the literal placeholder usernames (me, you, user, ...)
# are filtered out below. repo-relative-paths.md is excluded wholesale —
# that policy's entire purpose is to exhibit bad-path examples. The ~/<dir>
# branch lists personal-workspace roots only; conventional locations such
# as ~/Library and ~/.config are permitted by repo-relative-paths.md and
# are deliberately absent.
path_hits=$(
  git grep -nE \
    '(/Users/|/home/)[A-Za-z0-9._-]+/|C:\\Users\\[^\\ ]+|~/(Dropbox|DevProjects|Documents|Desktop|Downloads|Developer|Projects)' \
    -- . ":!$SELF" ":!$DENYLIST" ':!policies/repo-relative-paths.md' 2>/dev/null \
  | grep -vE '(/Users/|/home/)(me|you|user|username|name|example|\.\.\.)/|C:\\Users\\(\.\.\.|<)' \
  || true
)
report "Real absolute / home paths (policies/repo-relative-paths.md)" "$path_hits"

# --- 2. Commit-SHA-like tokens ---------------------------------------------
# Backtick-wrapped hex, "@ <sha>", or "commit <sha>" in prose. URLs, issue /
# PR refs, and sha256 digests are excluded.
sha_hits=$(
  git grep -nE '`[0-9a-f]{7,40}`|@ ?[0-9a-f]{7,40}([^0-9a-f]|$)|commit [0-9a-f]{7,40}([^0-9a-f]|$)' \
    -- '*.md' ":!$SELF" 2>/dev/null \
  | grep -vE 'github\.com|/issues/|/pull/|sha256|256:' \
  || true
)
report "Commit-SHA-like tokens (policies/anonymize-log-references.md)" "$sha_hits"

# --- 3. Local name denylist (optional) -------------------------------------
if [[ -f "$DENYLIST" ]]; then
  deny_hits=''
  while IFS= read -r term || [[ -n "$term" ]]; do
    term="${term%%#*}"                       # strip inline comments
    term="$(printf '%s' "$term" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')"
    [[ -z "$term" ]] && continue
    hits=$(git grep -niF -- "$term" . ":!$SELF" ":!$DENYLIST" 2>/dev/null || true)
    [[ -n "$hits" ]] && deny_hits+="$hits"$'\n'
  done < "$DENYLIST"
  report "Denylisted private names ($DENYLIST)" "${deny_hits%$'\n'}"
fi

if [[ "$status" -eq 0 ]]; then
  echo "✓ anonymization clean — no private-repo leaks in tracked files"
else
  echo
  echo "Anonymization check FAILED. Fix the references above before committing/pushing."
  echo "See policies/anonymize-log-references.md."
fi
exit "$status"
