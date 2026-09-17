# Implementation Plan: Personal Skills Fork

This plan is for Claude Code, running on my machine. It implements `STRATEGY.md` (the "Design & Testing Workflow Strategy", v5), which sits beside this file. Read `STRATEGY.md` in full before starting. Where this plan and the strategy disagree, stop and ask me.

## Goal

Replace the `superpowers` plugin with a personal fork of `mattpocock/skills` (reviewed at v1.2.3), plus four new skills and a handful of small edits, so that my Claude Code workflow is Design → Plan → Build → Close as described in the strategy.

## Ground rules

1. **Build only what this plan lists.** No extra skills, no skills taken from upstream beyond the keep list, no "while I'm here" improvements. If something seems missing, write it under "Questions for Thibault" in `fork/NOTES.md` and ask at the next checkpoint.
2. **Work stage by stage.** Every stage ends with a checkpoint: stop, summarize what changed, show me the diff, and wait for my go-ahead before starting the next stage.
3. **Keep upstream merges clean.**
   - New skills live in a new bucket, `skills/personal/`. Upstream never touches it.
   - Edits to Pocock's skills are as small as possible and fenced with `<!-- fork: start -->` and `<!-- fork: end -->`. Prefer appending a fenced section at the end of the file. Where an existing line must change (listed explicitly below), replace only that line and fence the replacement.
   - Do not edit the repo's `README.md`, `CLAUDE.md`, `AGENTS.md`, `CHANGELOG.md`, `.claude-plugin/*`, `docs/` or `ask-matt`. The repo's publishing conventions (plugin manifest entries, docs pages, router updates, `agents/openai.yaml`) apply to upstream's promoted buckets, not to `skills/personal/`, and are out of scope for this fork.
   - Do follow the repo's writing conventions in new skills: no em-dashes, skill dependencies written as "Call the Skill tool with `<name>`", shared reference material kept inside the skill that owns it.
4. **Invocation rule (from the repo's `.agents/invocation.md`).** A skill with `disable-model-invocation: true` can only be typed by me; no other skill can call it. Therefore:
   - The build orchestrator is user-invoked.
   - `align-language`, `visual-design-review` and `evaluate-output` are model-invoked, because other skills and the orchestrator call them. Give them narrow, specific descriptions so they don't fire in the wrong moments.
5. **Evidence before claims** applies to this build too: don't report a stage done without showing the command output or file listing that proves it.

## Decisions to confirm with me before Stage 0

Ask these together, with a recommended answer for each:

1. **Where the always-on rules live:** user-level `~/.claude/CLAUDE.md` (applies to every repo) or each project's `CLAUDE.md`. Recommended: user-level.
2. **End of Build:** Pocock's `implement-spec` opens a draft PR. The strategy says "you merge". Should the orchestrator open a draft PR, or only leave a finished feature branch? Recommended: feature branch only.
3. **Pilot:** which repo and which feature to use for the pilot run.
4. **`.scratch/` in the pilot repo:** if it's gitignored, the design artifacts can't be committed for worktrees to see. Should `.scratch/<feature>/` be force-added on the feature branch, or un-ignored? Recommended: force-add on the feature branch only.

Record the answers in `fork/NOTES.md`.

---

## Stage 0: Fork, install, remove superpowers

**Tasks**

1. Fork `mattpocock/skills` to my GitHub account (use `gh repo fork mattpocock/skills --clone`), add `upstream` pointing at `mattpocock/skills`, and record the upstream commit SHA in `fork/NOTES.md`.
2. Copy `STRATEGY.md` and this plan into `fork/` in the fork, and commit.
3. Write `scripts/link-personal-skills.sh`: an explicit allowlist version of `scripts/link-skills.sh` that symlinks only these skills into `~/.claude/skills` (upstream's script links everything, including `in-progress/`, which we don't want):
   - `engineering/`: `codebase-design`, `tdd`, `domain-modeling`, `grill-with-docs`, `prototype`, `improve-codebase-architecture`, `code-review`, `diagnosing-bugs`, `to-spec`, `to-tickets`, `setup-matt-pocock-skills`
   - `productivity/`: `grilling`, `grill-me`, `wait-what`, `handoff`
   - every skill folder under `personal/` (none yet)
   The script must also remove any existing symlink in `~/.claude/skills` that points into this repo but is no longer on the allowlist.
4. Remove superpowers: list installed plugins, uninstall the superpowers plugin, and confirm its SessionStart hook no longer appears in settings. Do not uninstall anything else. If the Pocock plugin (`mattpocock-skills`) is installed, uninstall it too, so skills aren't loaded twice.
5. Search `~/.claude/CLAUDE.md` and the pilot repo's `CLAUDE.md` for superpowers references. Show me each one and remove them after I confirm.
6. In the pilot repo, move `docs/superpowers/` (if present) to `docs/archive/superpowers/` with `git mv`. Do not delete it.
7. Run `scripts/link-personal-skills.sh`.
8. In the pilot repo, tell me to run `/setup-matt-pocock-skills` myself (it's user-invoked), choosing the local-files tracker.

**Done when**

- `ls -la ~/.claude/skills` shows exactly the 15 allowlisted skills as symlinks into the fork, and nothing from superpowers.
- The plugin list no longer shows superpowers or `mattpocock-skills`.
- The pilot repo has `docs/agents/issue-tracker.md` configured for local files.

**Checkpoint.** I'll use plain Pocock for a few days before Stage 1.

---

## Stage 1: Edits aimed at the testing pain points

### 1a. `tdd`

- **Append** a fenced section "Name the break": every test must state, in its name or a one-line comment, which production change would make it fail. A test that only fails when someone changes a deliberate decision (a constant's value, message wording) is not written.
- **Append** a fenced section "Between-slice design check": after each green slice, answer three questions in one or two lines each:
  1. Did any interface get wider or shallower?
  2. Is knowledge about one decision now in more than one module?
  3. Does the code still sit on the agreed seams?
  A "yes" is fixed with a refactor before the next slice. If fixing it is out of scope for the current ticket, log it as a ruling (format in Stage 5).
- **Replace** the line "**Refactoring is not part of the loop.** It belongs to the review stage..." with a fenced line saying small design refactors happen at the between-slice design check, and larger ones belong to review.
- **Append** a fenced note: seams recorded in the spec's module/seam diagram count as confirmed, so an implementer working from a spec does not need to ask me to confirm them again.

### 1b. `code-review`

- **Replace** the "Duplicated Code" smell line with a fenced line: "**Duplicated Knowledge**: the same business rule or decision is expressed in two or more places in the change, so changing the rule would need edits in each. Code that merely looks alike is not this smell. → give the rule one home and call it from both."
- **Append** to the smell baseline (fenced) the book checks, each as a judgement call in the same "what it is → how to fix" format: information leakage, complexity pushed up to callers instead of pulled down, temporal decomposition, orthogonality violations. (Reversibility is a design-review check, not a code-review one.)
- **Append** a fenced third axis, **Drift**, run as its own parallel sub-agent only when the spec contains a module/seam diagram: does the diff still match the diagram's modules and seams? Report each deviation, and say whether it changes a seam. Present it under `## Drift`, not merged with the other two axes.

### 1c. Always-on rules

In the location chosen before Stage 0, add a short fenced block, no more than eight lines:

- Size every task as spike, bounded or architectural, and say which out loud. Only ever escalate.
- Use `codebase-design` vocabulary exactly.
- In interactive design and planning only, apply the language alignment triggers (call the Skill tool with `align-language`). Never during implementation or in subagents.
- Show design decisions with two or more options as diagrams (call the Skill tool with `visual-design-review`).
- End every chunk of work I send you out to complete with a visual eval backed by fresh evidence (call the Skill tool with `evaluate-output`).

These rules reference skills that don't exist until Stages 2 and 3. Add the first two bullets now and the rest when their skills land.

**Done when**

- `git diff upstream/main -- skills/engineering` shows only fenced changes.
- A dry run of `code-review` on any small branch in the pilot repo reports the Standards and Spec axes, and skips Drift because there is no diagram.

**Checkpoint.**

---

## Stage 2: `evaluate-output`

Create `skills/personal/evaluate-output/SKILL.md`. Model-invoked. Description, narrow: called at the end of a chunk of work (a bounded change, a spike, or a full build) to verify it with fresh evidence and produce a visual eval.

**Behaviour**

1. **Evidence first.** Re-run the proving commands (tests, typecheck, and the specific command that demonstrates the change). Never reuse earlier output. If a command fails, the eval reports the failure first.
2. **One self-contained HTML page**, saved to `.scratch/<feature>/visuals/eval-<timestamp>.html` (for bounded work with no feature folder, use `.scratch/misc/visuals/`). Inline the Mermaid library so it renders offline. Open it in the browser if one is available; otherwise print the path.
3. **Content scales with the work:**
   - *Bounded*: what changed, tests added and the break each one names, fresh test output, anything surprising.
   - *Spike*: the question, the answer, the evidence, and where the prototype lives.
   - *Build*: the intended module/seam diagram beside a diagram of what was actually built, which seams have tests and at what level, deviations and open questions, every ruling from the ledger sorted by cost if wrong, and a plain statement of why it works. Success without an explanation of why is reported as a finding.
4. **Diagrams carry the weight.** Keep prose minimal: if a diagram needs a paragraph, redraw it.

Put the HTML page structure (a shared shell with light/dark styles and inlined Mermaid) in a file inside this skill, e.g. `skills/personal/evaluate-output/page-shell.html`, so `visual-design-review` can reuse it by calling this skill's material through the Skill tool rather than a cross-folder link. If that turns out awkward, ask me.

Then add the `evaluate-output` rule to the always-on rules and re-run the link script.

**Done when** I've run it at the end of one real bounded task in the pilot repo and the page opens and renders its diagrams offline.

**Checkpoint.**

---

## Stage 3: Design phase

### 3a. `align-language`

Create `skills/personal/align-language/SKILL.md`. Model-invoked. Implement the "Language alignment triggers" section of `STRATEGY.md` verbatim in substance:

- Triggers A and B, the "not a trigger" list, and the response format (at most three numbered questions in the `grilling` format; for A both readings, one scenario, a recommended answer; for B "Your usage / My understanding / Source").
- "State your reading" on the first use of a load-bearing term.
- Write the resolved term to `CONTEXT.md` immediately, with other meanings under `_Avoid_`.
- Escalate to a full grilling session (call the Skill tool with `grilling`) only if the answer opens a real design fork.
- **Scope, stated at the top of the skill:** interactive design and planning with me only. It never runs during implementation, inside subagents, or inside the build orchestrator, and it never stops a build.

### 3b. `visual-design-review`

Create `skills/personal/visual-design-review/SKILL.md`. Model-invoked. Description, narrow: called when a design fork has two or more real options, after design-it-twice has produced them.

Produces one HTML page (same shell and save location as `evaluate-output`, under `visuals/design-<topic>.html`) with:

- A Mermaid module/seam diagram per option.
- Key flows as flowcharts or sequence diagrams, in place of pseudocode.
- A comparison table on depth, locality and seam placement.
- The book checks per option: information leakage, pulling complexity downward, temporal decomposition, orthogonality, reversibility.
- A recommended option, with the reason in one or two sentences.

### 3c. Decision capture and loop caps

Append a fenced section to `grill-with-docs`:

- As decisions land, record choices below the ADR bar in `.scratch/<feature>/decisions.md` (chosen option, rejected options, why). ADRs and `CONTEXT.md` updates work as before.
- When a fork's answer is unknown, use `prototype`, then return to grilling. At most two prototypes per question; after that, decide it with me directly.
- When a fork has two or more real options, run design it twice, then call the Skill tool with `visual-design-review`.

Add the remaining always-on rules and re-run the link script.

**Done when** one real design conversation in the pilot repo has produced a `decisions.md`, at least one `CONTEXT.md` entry from `align-language`, and (if a fork came up) a design review page. No code is written in this stage.

**Checkpoint.**

---

## Stage 4: Plan phase

### 4a. `to-spec`

Append fenced changes:

- Read `.scratch/<feature>/decisions.md`, `CONTEXT.md` and relevant ADRs as well as the conversation, so the spec survives context compaction.
- Add a "Module/Seam Diagram" section to the spec template: a Mermaid diagram of the chosen modules and seams, and for each seam, where tests go and the dependency category behind it. State that this diagram is the reference for drift checks and must be updated whenever I approve a seam change.
- With the local tracker, write the spec to `.scratch/<feature>/spec.md`.

### 4b. `to-tickets`

Append fenced changes:

- Each ticket declares **Modules touched**: module names from the spec's diagram, never file paths. Add the field to the local ticket template.
- In step 4 ("Quiz the user"), in addition to the numbered list, render the breakdown as a Mermaid dependency graph in an HTML page (same shell, `visuals/tickets.html`), with nodes labelled by ticket title and grouped or coloured by module.
- After I approve, commit the spec, tickets, `decisions.md`, `CONTEXT.md` and ADRs to the feature branch (following the `.scratch/` answer recorded in `fork/NOTES.md`), so worktrees can see them.

**Done when** the Stage 3 design conversation has been turned into a committed spec with a diagram and tickets with modules, and I've approved the dependency graph.

**Checkpoint.**

---

## Stage 5: Build orchestrator

Copy `skills/in-progress/implement-spec/` to `skills/personal/build/` (name it `build`, user-invoked). Record the upstream commit it was copied from at the top of the file. Do not edit the original. Then rewrite it to implement "3. Build" in `STRATEGY.md`. Build it in four increments, each tried on the pilot tickets before the next:

### 5a. Sequential, with a ledger

- Read the spec and tickets; work the frontier one ticket at a time.
- Keep `.scratch/<feature>/ledger.md`: ticket status, commits, rulings, stops. On start, read the ledger and resume; never redo a finished ticket.
- Fresh implementer subagent per ticket, given pointers (spec, ticket, `CONTEXT.md`, ADRs), not copied content. It calls the Skill tool with `tdd` and works at the ticket's seams.
- Evidence before done: the implementer must include the output of the command it just ran that proves the ticket works.
- Per the decision recorded before Stage 0: open a draft PR or not.

### 5b. Reviews and fix loop

- After each ticket, run `code-review` against the ticket's diff with the spec provided, so it does not ask me for the fixed point or spec. The Spec sub-agent re-runs the proving command itself. Drift runs because the spec has a diagram.
- For small tickets (one module, small diff), the Standards and Spec axes may run as one sub-agent.
- Fix loop: at most 2 rounds per ticket, then stop and come to me.

### 5c. Rulings and stops

- Small implementation calls are decided and logged in the ledger as `Ruling: <what> | <why> | <cost if wrong>`.
- **Stop that ticket and come to me** for: a design fork, a drift finding that changes a seam, a ticket that turns out to be architectural, a fix loop that ran out, a merge conflict where two tickets' intents clash, or anything irreversible, destructive, security-sensitive or outside the worktree. Language is never a reason to stop.
- While a stop is open: tickets already running finish their current review round; no new tickets start until I've resolved it.
- When I approve a seam change: update the spec's module/seam diagram (and an ADR if it meets the bar), commit, then resume.

### 5d. Parallel worktrees and merging

- Tickets whose blockers are done run in parallel only when their **Modules touched** don't overlap. Each gets its own git worktree off the feature branch.
- A merger subagent merges each finished, reviewed ticket into the feature branch. Mechanical conflicts are resolved; clashing intents stop (see 5c). After every merge, run the full test suite and typecheck on the feature branch before starting any ticket that depends on it. A red suite is treated as a failed review.
- Clean up worktrees when their ticket is merged.

### Close

When all tickets are merged: run `code-review` over the whole branch, then call the Skill tool with `evaluate-output` for the build eval. Then stop. I decide whether to merge.

**Done when** the pilot feature has run end to end.

**Checkpoint.** Then run the pilot review below.

---

## Pilot review

Write `fork/PILOT.md` with:

- **Design judgment:** design forks caught and drawn before code; drift findings that were real vs noise.
- **Mechanical testing:** count of mocks outside system boundaries and tests with no named break (target: zero of both).
- **Test strategy:** does every agreed seam have tests at the agreed level (from the build eval)?
- **Cost:** number of stops, fix rounds per ticket, and whether per-ticket review was worth it.
- A list of proposed changes. Do not make them; I'll decide.

## Out of scope

- Any skill not named in this plan, including other upstream skills.
- Changes to upstream's promoted-bucket publishing files (README, plugin manifest, docs pages, `ask-matt`).
- The strategy's deferred book gaps (comment-first interfaces, "define errors out of existence", design by contract, property-based testing, broken windows).
- Codex support (`agents/openai.yaml` files).
- Upstream syncing beyond recording the base SHA. After the pilot, I'll merge `upstream/main` by hand every few weeks.
