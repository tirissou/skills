# Fork Notes

Working notes for the personal fork of `mattpocock/skills`. Companion to
[STRATEGY.md](./STRATEGY.md) and [fork-implementation-plan.md](./fork-implementation-plan.md).

## Base

| Item | Value |
|---|---|
| Fork origin | `git@github.com:tirissou/skills.git` |
| Upstream | `https://github.com/mattpocock/skills.git` |
| Base commit | `959a8e9f1edc3adbe2f7e3054bb6fbefa6696260` (2026-09-15, "Merge pull request #1083 from mattpocock/retro/deterministic-checks") |
| Plugin version at base | 1.2.3 |
| Divergence at Stage 0 | 0 ahead, 0 behind `upstream/main` |

The `v1.2.3` tag points at `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`, which is
behind the base commit: `main` carries commits past the tag under the same
version number. Diff against the base SHA, not the tag.

## Decisions (confirmed 2026-09-16, before Stage 0)

1. **Always-on rules live in user-level `~/.claude/CLAUDE.md`.** They apply in
   every repo rather than being copied per project.
2. **End of Build: feature branch only.** The orchestrator leaves a finished,
   reviewed feature branch. No draft PR. Thibault opens the PR and merges.
3. **Pilot repo: `~/Projects/tailoring/backend/target-garment`.** Note that
   `tailoring` is a workspace, not a repo: it holds ten git repos, and the
   pilot is one of them. It was picked as the most active (400 commits in the
   30 days to 2026-09-16, 1057 tracked files, 349 test files) and the one
   already carrying `CONTEXT.md`, a design ledger and its own
   `.claude/skills/write-docs`. It sits on branch `target-garment`.
4. **`.scratch/` reaches worktrees by force-add on the feature branch**
   (`git add -f .scratch/<feature>/`). In the pilot repo this is a no-op:
   nothing in its `.gitignore` matches `.scratch`, so design artifacts commit
   normally. The decision stands for repos that do ignore it.
5. **`docs/superpowers/` in the pilot repo stays where it is** (decided
   2026-09-16, replacing plan Stage 0 task 6). The plugin and its SessionStart
   hook are already gone, so nothing re-activates that workflow, and the
   directory is now cited as evidence rather than read as current process:
   `CONTEXT.md:133`, four `[evidence](docs/superpowers/specs/...)` links in
   `docs/design_ledger.md`, two files under `docs/ledger/claims/drape-design/`,
   and an exclusion in `.claude/skills/write-docs/SKILL.md` all point into it.
   A `git mv` would break every one of them, in a tree that currently has 41
   modified files and an in-flight SDD session. Revisit if the name itself
   starts to mislead.

## Stage 0 findings

- **The fork already existed** and was an exact copy of `upstream/main`. Stage 0
  task 1 reduced to adding the `upstream` remote.
- **Superpowers was already gone.** `~/.claude/plugins/installed_plugins.json`
  is empty, `enabledPlugins` in `~/.claude/settings.json` is `{}`, no
  `SessionStart` hook exists, nothing matching `*superpower*` is on disk under
  `~/.claude`, and `~/.claude/CLAUDE.md` has no reference to it. Plan tasks 4
  and 5 were no-ops on the user-level side.
- **The Pocock plugin was not installed either**, so skills were never loaded
  twice. They reach the harness only through `scripts/link-skills.sh` symlinks.
- **`STRATEGY.md` and `fork-implementation-plan.md` were moved, not copied,**
  from the repo root into `fork/`. A copy would have left two drifting sources
  of truth in a tree that has to merge cleanly with upstream.
- **The installed skills were copies, not links.** `~/.agents/skills/` held 37
  real directories (byte-identical to this repo at the base commit) and
  `~/.claude/skills/` symlinked to those copies. Nothing resolved into this
  repo, so no fork edit and no `git pull` would ever have reached the harness.
  `scripts/link-personal-skills.sh` now installs every allowlisted skill as a
  symlink straight into the repo, in both destinations.
- **Two installs under `~/.claude/skills` are not this repo's and were left
  alone:** `diagnose` (dated 2026-05-16, carries its own `scripts/`) and
  `engineering/` (dated 2026-05-18, a stale copy of a whole bucket holding
  `to-issues`, `to-prd` and `zoom-out`, none of which exist upstream any more).
  Worth deciding on separately: the stale bucket may still be loading old
  versions of skills the allowlist installs fresh.
- `.codegraphcontext/` sits untracked at the repo root. Left alone: not part of
  this plan.

## Pilot repo notes

- **No superpowers references in the pilot repo's `CLAUDE.md`.** The matches
  are evidence paths (above) plus `.gitignore:217`, which ignores
  `.superpowers/`. Nothing there instructs an agent to use that workflow, so
  plan Stage 0 task 5 needed no edits.
- **`.superpowers/` still holds SDD ledgers on disk**, gitignored, from a
  session that reads as unfinished. Left alone.
- **The repo has its own `.claude/skills/write-docs`.** Project-level skills
  take precedence over user-level ones, so watch for it competing with the
  fork's skills once `skills/personal/` lands.

## Questions for Thibault

1. **The stale `~/.claude/skills/engineering/` bucket** (2026-05-18) may be
   shadowing skills the allowlist now installs fresh. Delete it, or leave it?
2. **Run `/setup-matt-pocock-skills` in the pilot repo** (user-invoked, so it
   has to be typed by you), choosing the local-files tracker. It writes
   `docs/agents/issue-tracker.md`, which the Plan and Build phases read.
