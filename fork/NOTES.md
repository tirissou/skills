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
3. **Pilot repo: `~/Projects/tailoring/backend/garment-pocock`, branch
   `pocock-pilot`** (moved there 2026-09-16, replacing an earlier choice of
   `backend/target-garment`). Note the shape: `tailoring` is a workspace, not a
   repo, and `backend/main`, `backend/encoder`, `backend/target-garment` and
   `backend/garment-pocock` are four **worktrees of one repository** whose
   common git dir is `backend/main/.git`. The pilot is therefore isolated by
   worktree and branch, not by repository, and Stage 5's ticket worktrees will
   be siblings of these.

   `pocock-pilot` was branched off the worktree's detached HEAD at `3f26fbbe`,
   17 commits behind `target-garment`'s tip. The pin moved from `8c069926` to
   `3f26fbbe` mid-setup, by a hand other than this session's, so if the base is
   wrong it is one `git reset --hard` away.
4. **`.scratch/` reaches worktrees by force-add on the feature branch**
   (`git add -f .scratch/<feature>/`). In the pilot repo this is a no-op:
   nothing in its `.gitignore` matches `.scratch`, so design artifacts commit
   normally. The decision stands for repos that do ignore it.
5. **`docs/superpowers/` in the pilot repo stays where it is** (decided
   2026-09-16, replacing plan Stage 0 task 6). The plugin and its SessionStart
   hook are already gone, so nothing re-activates that workflow, and the
   directory is now cited as evidence rather than read as current process:
   `CONTEXT.md:133`, four `[evidence](docs/superpowers/specs/...)` links in
   `docs/design_ledger.md` and two files under `docs/ledger/claims/drape-design/`
   all point into it. A `git mv` would break every one of them for no gain.

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

## Stage 1 notes

- **`tdd`**: one inline replacement (the "Refactoring is not part of the loop"
  rule, which now points at the between-slice check) plus one trailing fenced
  block holding "Name the break", "Between-slice design check" and "Seams
  already agreed in a spec".
- **`code-review`**: the "Duplicated Code" smell replaced in place by
  "Duplicated Knowledge", four book checks fenced onto the end of the smell
  baseline, and the Drift axis fenced onto the end of the file.
- `git diff upstream/main -- skills/engineering` removes exactly the two lines
  the plan names, and every added line sits inside a `fork:` fence. Checked
  mechanically, not by eye.
- **`~/.claude/CLAUDE.md` did not exist** and was created for the two rules
  that are live now (size the task, use the `codebase-design` vocabulary). The
  other three rules name skills that land in Stages 2 and 3, and get added with
  them.
- **The stale `~/.claude/skills/engineering/` bucket was deleted** (decided
  2026-09-16). Its unique skills (`to-issues`, `to-prd`, `zoom-out`) are
  recoverable from this repo's history at `386d4ff` and `e112a6b`.
- **The pilot repo's `.claude/skills/write-docs` was deleted** in its commit
  `c160f8bb`, leaving the other 41 modified files alone. It encoded a
  three-tier documentation convention (`CLAUDE.md` at 50 to 150 lines,
  `README.md` for callers, `docs/` for theory) that now has no home. Fold it
  into that repo's `CONTEXT.md` if it should still bind.

## Pilot repo notes

- **No superpowers references in the pilot repo's `CLAUDE.md`.** The matches
  are evidence paths (above) plus `.gitignore:217`, which ignores
  `.superpowers/`. Nothing there instructs an agent to use that workflow, so
  plan Stage 0 task 5 needed no edits.
- **`.superpowers/` still holds SDD ledgers on disk**, gitignored. Left alone.
- **`.claude/skills/write-docs` is deleted on both branches**: `target-garment`
  at `c160f8bb` and `pocock-pilot` at `2c90fbaa`. Project-level skills take
  precedence over user-level ones, so it would have shadowed the fork's.
- The pilot worktree is clean (0 modified files) and carries 346 test files,
  which is what the Stage 5 fix loop and the full-suite check after each merge
  will run against.

## Questions for Thibault

1. **Is `pocock-pilot`'s base right?** It sits at `3f26fbbe`, the worktree's
   detached HEAD at the moment the branch was cut, 17 commits behind
   `target-garment`. Reset it if you meant `8c069926` or the tip.
2. **Run `/setup-matt-pocock-skills` in `backend/garment-pocock`**
   (user-invoked, so it has to be typed by you), choosing the local-files
   tracker. It writes `docs/agents/issue-tracker.md`, which `code-review` and
   the Plan and Build phases read. Stage 1's dry run is waiting on it.
