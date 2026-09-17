#!/usr/bin/env bash
set -euo pipefail

# Fork-only script. Upstream's scripts/link-skills.sh installs every skill
# outside deprecated/ and misc/, which includes in-progress/ and a long tail
# this fork does not use. This one installs an explicit allowlist instead: the
# skills the personal workflow depends on (see fork/STRATEGY.md, "Build list"),
# plus every skill under skills/personal/.
#
# Everything is installed as a symlink into this repo, so a `git pull` keeps
# installed skills current.
#
# It also prunes, so that dropping a skill from the allowlist uninstalls it on
# the next run. A destination entry is removed only when it is provably this
# repo's: either a symlink resolving into the repo (or into the other
# destination), or a real directory byte-identical to a skill of the same name
# in the repo. Anything else, including skills installed from elsewhere, is
# reported and left alone.
#
# Destinations:
#   - ~/.claude/skills: Claude Code
#   - ~/.agents/skills: Codex and other Agent Skills-compatible harnesses

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DESTS=("$HOME/.claude/skills" "$HOME/.agents/skills")

# Allowlist: bucket-relative paths under skills/. Everything under personal/ is
# added automatically below.
ALLOWLIST=(
  engineering/codebase-design
  engineering/tdd
  engineering/domain-modeling
  engineering/grill-with-docs
  engineering/prototype
  engineering/improve-codebase-architecture
  engineering/code-review
  engineering/diagnosing-bugs
  engineering/to-spec
  engineering/to-tickets
  engineering/setup-matt-pocock-skills
  productivity/grilling
  productivity/grill-me
  productivity/wait-what
  productivity/handoff
)

names=()
srcs=()

add_skill() {
  local rel="$1"
  local src="$REPO/skills/$rel"
  if [ ! -f "$src/SKILL.md" ]; then
    echo "error: no SKILL.md at skills/$rel" >&2
    exit 1
  fi
  names+=("$(basename "$src")")
  srcs+=("$src")
}

for rel in "${ALLOWLIST[@]}"; do
  add_skill "$rel"
done

# Every skill under personal/, if the bucket exists yet.
if [ -d "$REPO/skills/personal" ]; then
  while IFS= read -r -d '' skill_md; do
    src="$(dirname "$skill_md")"
    add_skill "personal/$(basename "$src")"
  done < <(find "$REPO/skills/personal" -name SKILL.md -not -path '*/node_modules/*' -print0)
fi

is_allowed() {
  local candidate="$1"
  local name
  for name in "${names[@]}"; do
    [ "$name" = "$candidate" ] && return 0
  done
  return 1
}

# Path of the repo skill with this name, empty if the repo has no such skill.
# Matches on any bucket, and only on directories that are skills (they hold a
# SKILL.md), so a bucket directory called "engineering" never matches.
repo_skill_path() {
  local candidate="$1" dir
  for dir in "$REPO"/skills/*/"$candidate"; do
    [ -f "$dir/SKILL.md" ] && { echo "$dir"; return 0; }
  done
  return 0
}

# Guard: a destination that is itself a symlink into the repo would make the
# per-skill links land back inside the working copy.
for DEST in "${DESTS[@]}"; do
  if [ -L "$DEST" ]; then
    resolved="$(readlink -f "$DEST")"
    case "$resolved" in
      "$REPO"|"$REPO"/*)
        echo "error: $DEST is a symlink into this repo ($resolved)." >&2
        echo "Remove it (rm \"$DEST\") and re-run; the script will recreate it as a real dir." >&2
        exit 1
        ;;
    esac
  fi
  mkdir -p "$DEST"
done

# True when this destination entry is provably a copy or link of the repo's own
# skill of the same name, and so is ours to remove or replace.
is_ours() {
  local target="$1" name resolved repo_src other
  name="$(basename "$target")"

  if [ -L "$target" ]; then
    resolved="$(readlink -f "$target" 2>/dev/null || true)"
    case "$resolved" in
      "$REPO"/*) return 0 ;;
    esac
    for other in "${DESTS[@]}"; do
      case "$resolved" in
        "$other"/*) return 0 ;;
      esac
    done
    return 1
  fi

  [ -d "$target" ] || return 1
  repo_src="$(repo_skill_path "$name")"
  [ -n "$repo_src" ] || return 1
  diff -rq "$repo_src" "$target" >/dev/null 2>&1
}

# Pruning runs as its own pass over every destination before anything is
# removed: a link in ~/.claude/skills may point at ~/.agents/skills, and
# removing the agents entry first would leave the claude link dangling and no
# longer traceable to this repo.
prune=()
kept=()
for DEST in "${DESTS[@]}"; do
  for target in "$DEST"/*; do
    [ -e "$target" ] || [ -L "$target" ] || continue
    name="$(basename "$target")"
    is_allowed "$name" && continue
    if is_ours "$target"; then
      prune+=("$target")
    else
      kept+=("$target")
    fi
  done
done

for target in ${prune+"${prune[@]}"}; do
  rm -rf "$target"
  echo "uninstalled $(basename "$target") ($(dirname "$target"))"
done

for DEST in "${DESTS[@]}"; do
  for i in "${!names[@]}"; do
    name="${names[$i]}"
    src="${srcs[$i]}"
    target="$DEST/$name"

    # Replace an existing install only when it is ours. An unrelated skill of
    # the same name is left in place and reported, rather than overwritten.
    if [ -e "$target" ] && [ ! -L "$target" ]; then
      if is_ours "$target"; then
        rm -rf "$target"
      else
        echo "skipped $name ($DEST): not this repo's, left in place" >&2
        continue
      fi
    fi

    ln -sfn "$src" "$target"
    echo "linked $name -> ${src#"$REPO"/} ($DEST)"
  done
done

echo
echo "${#names[@]} skills linked into ${#DESTS[@]} destinations."
if [ "${#kept[@]}" -gt 0 ]; then
  echo "left alone (not this repo's):"
  for target in "${kept[@]}"; do
    echo "  $target"
  done
fi
