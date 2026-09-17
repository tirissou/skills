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
3. **Pilot repo: under `~/Projects/tailoring`, exact repo still to pick.**
   `tailoring` is a workspace, not a repo: it contains ten git repos
   (`edna-deepsdf`, `smpl`, `frontend/live`, `backend/main`, `backend/encoder`,
   `backend/target-garment`, `spikes/DiffCloth`, `spikes/Codim-IPC`,
   `external/DiffCloth`, `external/Codim-IPC`). Open question below.
4. **`.scratch/` reaches worktrees by force-add on the feature branch**
   (`git add -f .scratch/<feature>/`). The ignore rule stays intact elsewhere.
   No repo under `tailoring` currently ignores `scratch` at all, so this may
   turn out to be a no-op.

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

## Questions for Thibault

1. **Which repo under `~/Projects/tailoring` is the pilot?** It needs to be a
   single git repo, because Stage 5 runs each ticket in its own worktree off a
   feature branch. `backend/main` and `edna-deepsdf` look like the candidates
   with real application code, but pick the one whose next feature is
   architectural rather than bounded, since the pilot only exercises the
   workflow if it reaches Design it twice and the Build orchestrator.
