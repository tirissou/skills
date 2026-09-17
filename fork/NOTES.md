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
6. **Issue tracker: GitHub issues, not local files** (decided 2026-09-16,
   amending the strategy's decision table). `/setup-matt-pocock-skills`
   configured GitHub, the remote is real (`tirissou/_edna`) and `gh` is
   authenticated, so the configuration works as written.

   What it changes downstream:

   - **Stage 4b** commits the spec, `decisions.md`, `CONTEXT.md` and ADRs to
     the feature branch as planned, but not the tickets: those are issues.
     Implementer worktrees read design artifacts from disk and tickets over
     the network.
   - **Stage 5's frontier** can use GitHub's native issue dependencies rather
     than a hand-rolled blocker list. `docs/agents/issue-tracker.md` already
     spells out the frontier query: open children of the map issue, minus any
     with `issue_dependencies_summary.blocked_by > 0` or an assignee. This is
     the real gain over local files.
   - **Modules touched** (the plan's Stage 4b field, which drives parallelism)
     becomes a line in the issue body rather than a field in a local template.
   - Every implementer and reviewer subagent now needs `gh` on its PATH and a
     live network. A `gh` outage stops the Build phase, where local files
     would not have.
   - The ledger stays local at `.scratch/<feature>/ledger.md`. It records this
     run's state, not the tickets, and it must survive without the network.
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
- **`write-docs` lost nothing.** The three-tier documentation convention it
  encoded (`CLAUDE.md` at 50 to 150 lines, `README.md` for callers, `docs/`
  for theory) is already documented at length in the repo's own
  `CONTRIBUTING.md`, including the STOP checklist and the CLAUDE.md template.
  The skill was a second copy of a rule that has a home.

## Stage 2 notes

- **`skills/personal/evaluate-output/`**: `SKILL.md`, `page-shell.html`,
  `build-page.py` and a vendored `assets/mermaid.min.js`.
- **The Mermaid bundle is vendored, 3.4 MB.** "Inline the library so it opens
  offline" cannot be done by an agent writing the page: no agent can carry
  3.4 MB through its context. `build-page.py` splices the vendored copy into
  the shell instead, and only when the fragment actually contains a
  `class="mermaid"` block, so evals without diagrams stay small.
- **Verified by rendering, not by reading.** Headless Chrome was pointed at the
  finished page from a `file://` URL: two flowcharts rendered
  (`aria-roledescription="flowchart-v2"`), zero error SVGs, and the shell
  references no external stylesheet, script or font.
- **`skills/personal/README.md`** added, per the repo convention that every
  bucket lists its skills. The plan's "don't edit" list covers upstream's
  publishing files, and this is a new file in a new bucket.
- The always-on rules in `~/.claude/CLAUDE.md` now carry three bullets. The two
  remaining ones land with their skills in Stage 3.

## The worktree provisioning problem (found running the Stage 2 eval)

Running `uv run pytest` in the fresh `garment-pocock` worktree **fails at
collection**: 13 errors, no tests run. Two causes, both untracked and
worktree-local, so a new worktree never receives them:

1. `MEDIAPIPE_LANDMARKER_MODEL_URI` is set by `.envrc` through direnv, and is
   read at **module import** by `src/edna/landmark/joints_in_image.py:29`
   behind a bare `assert`. Unset, it takes out 7 test modules.
2. `corpora/body0_pencil_v1` is cited by a ledger claim's `depends_on`, and
   `edna.verify.ledger` raises `LedgerSchemaError` at import when it is
   missing. That takes out the other 6.

Supply both and the suite is green: **2055 passed, 20 skipped, 1 xfailed, in
258.67s**. The code is fine; the worktree was unprovisioned.

**This is a direct threat to Stage 5**, which runs every ticket in its own
fresh worktree and gates each merge on a green suite there. As things stand
every such worktree starts red for reasons unrelated to its ticket. Options,
cheapest first: have the orchestrator link `corpora/` and export the model URI
when it creates a worktree; commit a small fixture corpus so `depends_on`
resolves from the tree; or make the ledger degrade instead of raising at
import. Decide before Stage 5, not during it.

Two lesser findings from the same run: `mypy src/edna` reports **760 errors in
140 files**, so the typecheck currently cannot prove anything about a change,
and a stale committed `.codegraphcontext/db/falkordb.settings` (pointing at a
worktree named `comfort-ease-replumb` that no longer exists) was deleted by
something during the session and restored.

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
