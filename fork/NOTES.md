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

7. **The pilot base stays at `3f26fbbe`** (decided 2026-09-16, closing
   question 1). `8c069926` turned out to be *older* than the current base, so
   that option was never real. The live alternative was rebasing onto
   `target-garment`'s tip, which had moved 21 commits and +4180/-209 ahead the
   same day. Staying put keeps the pilot's diff clean and isolates it from work
   in flight; the cost is a larger merge at the end, and a Stage 5 green-suite
   gate measured against a 21-commit-old suite. Only `1b7aa294` (the agents
   config) is unique to `pocock-pilot`; its other commit, `2c90fbaa`, is the
   same patch as `c160f8bb` on `target-garment`.
8. **The Design phase gets no stated exit condition** (decided 2026-09-16,
   closing question 3). `STRATEGY.md` ends Design when seams are agreed, with
   where tests go and the dependency category behind each seam, but no skill
   says so and none will. Stage 4's `to-spec` diagram section carries the same
   information downstream. Revisit after the pilot if Design turns out to end
   ambiguously.

9. **`gh` is assumed always available** (decided 2026-09-16, after Stage 4).
   Decision 6 listed a `gh` outage as a hazard that local files would not have
   had. That hedge is dropped: treat `gh` as present on every PATH, with a live
   network, in every session and every subagent. Nothing in the skills or the
   orchestrator carries a fallback for its absence, and if it ever is absent
   the Build phase stops with a plain error rather than degrading.

   This removes one of the two reasons Stage 4 gave for keeping a copy of the
   spec on disk. The remaining one is the load-bearing one and does not depend
   on the network: the module/seam diagram has to be versioned with the code it
   describes, so a drift check measures against the diagram as of the commit it
   is reviewing.

10. **Ticket worktrees are provisioned by the repo's existing `post-checkout`
    hook** (decided 2026-09-16, closing the worktree provisioning problem that
    Stage 2 recorded and Stage 5 was blocked on). Drawn in
    `.scratch/fork/visuals/design-worktree-provisioning.html`.

    The first draft of this fork proposed a new convention, a
    `docs/agents/worktree-setup.sh` the orchestrator would call. Thibault
    pointed out the repo already provisions on checkout, and it does: a
    `post-checkout` hook creates the venv and runs `uv pip install -e '.[all]'`.
    `core.hooksPath` is set in the **shared** `main/.git/config` with
    `extensions.worktreeConfig` unset, so every worktree of the repo inherits
    it with no action from anyone. Adding a second mechanism beside it would
    have been duplicated knowledge with no rule saying which file gets the next
    dependency.

    The orchestrator therefore knows nothing about provisioning. It runs
    `git worktree add`, and three things follow:

    - **The hook supplies files.** Extended (2026-09-16) to copy `corpora/`,
      which is a git-ignored build artifact of
      `python -m edna.verify corpus <fixture_id>`. **Copied, not symlinked**,
      at Thibault's call: `settle_corpus` writes into `corpora/<fixture_id>/`,
      so a link would let one worktree write through into another's, and 3.3 MB
      is cheap insurance. **Not regenerated**, because
      `settle_corpus._assert_serial_context()` raises off the main thread, so
      parallel worktrees cannot rebuild concurrently even if the cost were
      acceptable.
    - **The orchestrator supplies the environment.** A hook is a subprocess of
      `git worktree add`; it exits, and cannot export into a process that
      starts later. The hook's `direnv allow` only whitelists `.envrc` for an
      interactive, direnv-hooked shell, and no agent shell is either. So the
      orchestrator sources the tracked `.envrc` itself before running anything.
      This is a bug that predates Stage 5: agents have never had these
      variables, in any worktree.
    - **The smoke check proves both.** `post-checkout` runs *after* the
      checkout, so a failing hook leaves a half-provisioned worktree and a
      nonzero exit. Nothing is handed to an implementer until a proving command
      passes in that worktree; a red one stops the run.

    Two findings from making the hook edit, both of which would have been
    silent failures:

    - **The copy source is not the primary worktree.** `main/corpora` does not
      exist; `target-garment` and `garment-pocock` have it. Copying "from the
      primary worktree" would have been a no-op for every ticket worktree. The
      hook now honours `EDNA_CORPORA_SRC` when the caller knows, and otherwise
      takes the first other worktree with a non-empty `corpora/`. All three
      paths were tested standalone before anything depended on them.
    - **`MEDIAPIPE_LANDMARKER_MODEL_URI` now resolves.** Thibault fixed the
      target: the 29 MB model file exists at the path `.envrc` names. The
      variable is still only defined in `.envrc` and there is no direnv hook in
      any rc file on this machine, so it remains unset in every agent shell.
      The fix means sourcing `.envrc` is now sufficient, with no validation
      logic needed.

    The hook is untracked, in `.git/hooks`, reached by an absolute
    `core.hooksPath`, so "the repo provisions itself" is really "this machine
    does". Backed up beside itself as `post-checkout.bak-2026-09-16` before
    editing. Not blocking, worth knowing.

    **Not yet observed:** that `post-checkout` fires on `git worktree add`. It
    is documented by git, asserted in the hook's own header, and corroborated
    by four worktrees whose `.venv` mtimes match their creation dates. The
    first real Stage 5 run is what will prove it.

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

### Stage 1's `code-review` dry run (2026-09-16)

Run against `6b833708` (`forward_map` trunk-contour lift hardening, 2 files,
+103/-19) in a detached worktree of the pilot repo, fixed point `6b833708~1`.
Spec source: the commit body's enumerated review-requested items, since no
tracked spec exists for that work.

- **Both axes reported, Drift skipped** with the one-line note the fence asks
  for. The plan's Stage 1 "done when" is met.
- **The rewritten duplication rule earned its keep.** Standards reported
  Duplicated Knowledge and explicitly moved the finding off the code that looks
  alike (the chord loop, which the commit had already collapsed) and onto the
  rule expressed twice (the scale-k computation). Under upstream's "the same
  logic shape appears in more than one hunk" wording the collapsed loop would
  have read as fixed and the live duplication would have been missed.
- **The book checks fired, and plausibly.** Feature Envy on validation that
  belongs to the dataclass's `__post_init__`, not the lift.
- **The two axes disagreed usefully.** Standards called the precision clause a
  documented-standard breach (`CLAUDE.md`: cite claim IDs, do not restate
  measurements); Spec called the same clause wrong on its facts (it cites a
  docstring stating ~0.85%, not the ~0.21% it claims). Neither would have found
  the other's version. That is the case the two-axis split exists for.
- **`docs/agents/issue-tracker.md` is absent from history before `1b7aa294`.**
  It lives only on `pocock-pilot`, so a worktree cut from an arbitrary historical
  commit leaves `code-review` without a tracker. Stage 5 always branches off the
  feature branch, so this is fine as designed, but it is worth not forgetting.
- **A concurrency hazard for Stage 5, found by accident.** The Spec sub-agent
  reported the test suite unverifiable because `open3d` failed to load a native
  dependency. Checked directly afterwards: `import open3d` succeeds. The failure
  was transient, caused by two sub-agents running `uv run` against one shared
  `.venv` at the same time, each triggering a resync that uninstalls and
  reinstalls packages under the other. **Stage 5 runs reviewers and implementers
  in parallel by design**, so either each worktree gets its own environment or
  nothing in a worktree may run `uv run` concurrently. Add it to the worktree
  provisioning problem recorded under Stage 2, which now has three parts:
  the model URI, the corpora, and this.

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

## Stage 3 notes

- **`skills/personal/align-language/`** and **`skills/personal/visual-design-review/`**,
  both model-invoked with narrow descriptions, plus one fenced append to
  `grill-with-docs` (decisions to disk, the two-prototype cap, design-it-twice
  into the review page). The always-on rules in `~/.claude/CLAUDE.md` are now
  complete at five bullets.
- **The page machinery stays in `evaluate-output` and is reached by path.** The
  plan left this open at Stage 2 ("reuse it by calling this skill's material
  through the Skill tool. If that turns out awkward, ask me"). It is awkward:
  the Skill tool's seam hands the caller a whole skill's instructions, and most
  of `evaluate-output`'s are about re-running proving commands over finished
  work, which a design review has none of. `visual-design-review` therefore
  calls `../evaluate-output/build-page.py` directly. The decision is drawn out
  in `.scratch/fork/visuals/design-page-machinery.html`, produced by the new
  skill on its own dependency question. **A third fragment author is the signal
  to move the script to its own folder**; that move is one `git mv` and two
  edited paths.
- **Sibling paths survive the install layout by accident, not design.**
  `~/.claude/skills/<name>` is a flat symlink into the repo, so
  `../evaluate-output/` resolves whether an agent treats its skill directory as
  the symlink or as the resolved path. Verified by running the build from
  `~/.claude/skills/visual-design-review`.
- **No cross-folder markdown links.** Nothing upstream links from one skill
  folder into another; every cross-skill reference is "call the Skill tool with
  X". The first draft of the `grill-with-docs` append linked
  `../codebase-design/DESIGN-IT-TWICE.md` and was rewritten to match.
- **Evidence** (all re-run at the end of the stage): both frontmatters parse and
  both skills are model-invoked; zero em-dashes in every changed file; the only
  lines removed from `skills/engineering` are still the two Stage 1 named, and
  everything added outside a `fork:` fence is a blank line; both skills linked
  into `~/.claude/skills` and `~/.agents/skills`; the design page built from the
  installed skill directory renders 3 of 3 diagrams headless with 0 error SVGs
  and 0 external references.
- **Eval**: `.scratch/fork/visuals/eval-2026-09-16-2200.html`. This repo has no
  `.scratch` entry in `.gitignore`, so the directory shows as untracked. Left
  that way: the pages are outputs, and `.gitignore` is upstream's file.
- **What this stage does not prove.** Nothing here shows the two skills fire at
  the right moment. That needs the plan's "done when": a real design
  conversation in the pilot repo.

## Stage 4 notes

- **Two fenced appends, no removals.** `to-spec` gains "Read the decision files",
  "The Module/Seam Diagram section" and "The spec also lives on disk";
  `to-tickets` gains "Modules touched", "Show the breakdown as a graph" and
  "Commit the design artifacts before Build". Checked mechanically: zero lines
  removed from either file against the base commit, and everything added
  outside a `fork:` fence is a blank separator line.
- **The diagram section is appended, not inserted into `<spec-template>`.** The
  plan's fence rule prefers a trailing block, so the template above it is
  untouched and the append opens by naming the step and the template it amends,
  the same shape Stage 1 used in `tdd`. The cost is real: an agent that reads
  `<spec-template>` as the whole answer can produce a spec with no diagram, and
  every drift check downstream then has nothing to measure against. Watch for
  it in the pilot; if it happens, the fix is a fenced insert inside the template
  tags and the merge risk is worth paying.
- **Two copies of the spec, and the disk copy wins.** With the GitHub tracker
  (decision 6) the spec is an issue, but Build reads design artifacts from a
  worktree, which holds committed files and nothing else. So `to-spec` now
  writes `.scratch/<feature-slug>/spec.md` as well and names it canonical: the
  issue is the copy people comment on, the file is the copy agents read. Each
  carries a pointer to the other. This is duplicated knowledge by construction,
  which the fork's own `code-review` rule would flag; it is accepted because the
  diagram has to be **versioned with the code it describes**. A drift check run
  on the diff at commit X has to measure against the diagram as it stood at
  commit X, and an issue body has one current version and no history tied to the
  branch. The mitigation is the stated winner plus "change the file first".
  (Availability of `gh` is not part of this argument: see decision 9.)
- **The third fragment author arrived and the script did not move.** Stage 3
  recorded that a third caller of `build-page.py` was the signal to move it out
  of `evaluate-output` into its own folder. `to-tickets` is that third caller,
  and the move turned out not to be the problem the note anticipated. What
  breaks across buckets is the *sibling* form `../evaluate-output/build-page.py`,
  which only resolves between two skills in `personal/`; the form actually
  documented in the command block, `<skills-dir>/evaluate-output/build-page.py`,
  resolves from any bucket because the install layout is flat. `to-tickets` uses
  that form and it was verified by running it. The sibling wording in
  `visual-design-review`'s prose is now the odd one out, not the script's
  location. Revisit only if a caller appears that cannot resolve `<skills-dir>`.
- **`to-spec` and `to-tickets` live in a promoted bucket**, so the repo's own
  `CLAUDE.md` would normally demand a re-synced docs page and an `ask-matt`
  update. The fork plan's ground rule 3 puts both out of scope, as it did for
  `tdd` and `code-review` in Stage 1. Unchanged, recorded again because it is
  the kind of thing a later reader reports as an omission.
- **Evidence** (re-run at the end of the stage): zero lines removed from the two
  files against the base; four lines added outside a fence, all blank; both
  fences balanced; both frontmatters intact and still user-invoked; zero em or
  en dashes in any line added; both skills symlinked into `~/.claude/skills` and
  `~/.agents/skills` and resolving into this repo. The graph instruction was run
  rather than read: a five-ticket sample built through
  `~/.claude/skills/evaluate-output/build-page.py` renders 1 of 1 diagram
  headless, 0 error SVGs, subgraph clusters drawn, all five ticket labels
  present, 0 external references, 3496 KB. Page:
  `.scratch/fork/visuals/tickets-sample.html`.
- **Eval**: `.scratch/fork/visuals/eval-2026-09-16-2320.html`, with the
  sample tickets graph it cites at `.scratch/fork/visuals/tickets-sample.html`.
- **What this stage does not prove.** The plan's "done when" is a real design
  conversation turned into a committed spec with a diagram and tickets with
  modules, with the dependency graph approved. That has not happened, and it
  cannot: Stage 3's "done when" is the same pilot conversation and is also still
  open. Both are waiting on one session in the pilot repo, not on more building.

## Stage 5 notes

- **`skills/personal/build/`**, user-invoked, copied from
  `skills/in-progress/implement-spec` at upstream `5b15a47` and then rewritten.
  The provenance comment sits at the top of the file. The original is
  byte-identical to the base commit and was not edited.
- **Written as one whole, not four increments.** The plan asks for 5a through 5d
  built in sequence, "each tried on the pilot tickets before the next". There
  are no pilot tickets: Stage 3's and Stage 4's "done when" are both the same
  unrun pilot design conversation. Writing four drafts of one file with nothing
  to try them against would have produced four unverified drafts instead of one.
  **The skill is untried.** Nothing below claims otherwise.
- **Upstream's exploration-subagent step was dropped.** `implement-spec` step 2
  spawns an explorer to save notes outside the repo for later implementers. The
  plan does not list it and ground rule 1 forbids extras, so it is gone.
  Recorded because it is a real capability, not an oversight: if implementers
  turn out to re-explore the same ground per ticket, this is the first thing to
  add back.
- **Provisioning is written generically**, per decision 10. The skill says a
  repo may provision itself on checkout and that this is the repo's business,
  names no hook, no path and no package manager, and requires the orchestrator
  to load the environment and smoke-check regardless. Nothing about the pilot
  repo leaked into a skill that has to work elsewhere.
- **Two rules carried in from findings rather than from the plan.** "One
  command-runner per ticket worktree at a time" comes from the Stage 1
  concurrency hazard. The clause on a typecheck that is already red at the base
  commit closes the second standing hazard: with 760 mypy errors in the pilot
  repo, a gate quoting that output would be theatre, so the skill says to
  declare it once and gate on the suite instead. Both are hazards this file
  already recorded as things Stage 5 depends on, not new scope.
- **Evidence**: plugin validate --strict passed; plugin version in sync;
  frontmatter and `agents/openai.yaml` agree that `build` is user-invoked; all
  three skills it calls (`code-review`, `tdd`, `evaluate-output`) are
  model-invoked and therefore actually reachable, which a user-invoked
  dependency would not have been; zero em-dashes; zero cross-folder markdown
  links; zero lines removed from `skills/engineering`; `implement-spec`
  byte-identical to base; `build` linked into both harness directories and
  readable through the symlink.
- **Eval**: `.scratch/fork/visuals/eval-2026-09-16-2355.html`. The fork it
  closed is drawn in `.scratch/fork/visuals/design-worktree-provisioning.html`.
- **What this stage does not prove.** That the orchestrator works. Every claim
  above is about the artifact, not its behaviour. The frontier query, the
  modules-overlap gate, the fix-loop cap, the merger's conflict judgement and
  the stop list have never run. So has the provisioning chain: that
  `post-checkout` fires on `git worktree add` is still documented and
  corroborated rather than observed.

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

None open. Question 1 (pilot base) and question 3 (the Design phase exit
condition) were closed by decisions 7 and 8. Question 2, Stage 1's `code-review`
dry run, ran on 2026-09-16; its result is under "Stage 1 notes".

The two standing hazards are not questions but work Stage 5 depends on: the
worktree provisioning problem (Stage 2 notes, now three parts) and the 760 mypy
errors that leave the typecheck unable to prove anything about a change.
