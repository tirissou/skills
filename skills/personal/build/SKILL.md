---
name: build
description: "Run a spec's tickets through to a finished feature branch: frontier, a fresh implementer per ticket, review after each, merge and verify."
disable-model-invocation: true
---

# Build

Turn a spec and its tickets into a reviewed feature branch. You are the orchestrator: you do not write the feature code. You decide what runs next, you hold the state, you rule on small calls, and you stop and come to the user on the big ones.

<!--
Copied from skills/in-progress/implement-spec at upstream 5b15a47, then rewritten.
Do not edit the original. When upstream promotes or rewrites implement-spec, diff
against 5b15a47 and port deliberately rather than merging.
-->

## Before anything starts

Four things must already exist. If one is missing, say which and stop; none of them is yours to invent.

- **A spec carrying a Module/Seam Diagram.** Committed on the feature branch at `.scratch/<feature>/spec.md`. The diagram is what every drift check measures against, and without it the Drift axis cannot run.
- **Tickets, each declaring Modules touched.** Module names from that diagram. This drives parallelism, so a ticket without the field cannot be scheduled safely.
- **The design artifacts committed to the feature branch**: the spec, `decisions.md`, `CONTEXT.md`, and any ADRs. A ticket worktree holds committed files and nothing else, so an uncommitted artifact is invisible to every implementer, and the failure is silent.
- **A clean feature branch.** Uncommitted changes in the feature worktree do not reach ticket worktrees and will surprise you at merge time.

Read the spec and enough of the tickets to see the shape of the graph. Do not read every ticket body now; implementers read their own.

## Vocabulary

A **ticket worktree** is the ephemeral git worktree this skill creates for one ticket and removes when that ticket merges. A repository may also have long-lived worktrees that people work in, which are branches, not tickets. **Never remove a worktree you did not create**, and never assume a worktree is yours because it is a worktree.

Use the project's own vocabulary from `CONTEXT.md` for everything else, and the `codebase-design` terms (module, interface, depth, seam, adapter, leverage, locality) exactly.

## The ledger

`.scratch/<feature>/ledger.md` is the run's memory. It exists because your context will be compacted mid-run, and a compacted orchestrator that has lost its place will cheerfully redo a finished ticket.

**Read it first, every time this skill starts.** If it has entries, you are resuming: pick up from the recorded state and never re-run a ticket marked merged. Write to it at every state change, not in a batch at the end.

```
## <NN> <ticket title>  (#<issue>)

Status:   ready | provisioning | running | in-review | fixing (round 1|2) | merged | stopped
Modules:  <from the ticket>
Worktree: <absolute path, or "removed">
Commits:  <sha> <subject>
Evidence: <command> -> <result>, run <when>
Rulings:
  - Ruling: <what was decided> | <why> | <cost if wrong>
Stops:
  - <what stopped it> | <how it resolved> | <what changed as a result>
```

## The frontier

A ticket is on the frontier when **every blocker is closed** and **no module it touches is claimed by a ticket currently running**.

The first half is the tracker's answer, not yours. Follow `docs/agents/issue-tracker.md` for how this repo represents blocking, and trust the tracker's own summary of open blockers rather than reading bodies and reasoning about them.

The second half is yours. Two tickets whose blockers are done may still not run together: blocking edges record what must happen **first**, which is a different question from what two agents can safely edit **at once**. Compare the Modules touched lists. Any overlap, and the later ticket waits, whatever the graph says.

Start every ticket on the frontier that passes both tests. When none passes, wait for a running ticket to merge, which changes both answers at once.

## A ticket worktree

Create it as a sibling of the repo's existing worktrees, branched from the feature branch:

```
git worktree add <sibling-dir>/<feature>-<NN> -b <feature>/<NN>-<slug> <feature-branch>
```

**Siblings, not a temp directory.** A repository's `.envrc` may reach a parent directory outside the repo, and a worktree created elsewhere loses it silently. Temp directories also do not survive, and a run that outlives its worktrees has no evidence left.

Then three things, in order:

1. **Let the repo provision itself.** Many repos provision on checkout through a `post-checkout` hook, which `git worktree add` fires. That is the repo's business, not yours: you do not read a provisioning config, and you do not know what the repo needs. Check the exit status. A hook runs **after** the checkout, so a failed hook leaves a worktree that exists and does not work.
2. **Load the environment yourself.** If the repo has a tracked env file, source it into your own environment and pass that to every subagent: `set -a; source .envrc; set +a`. Tools like direnv hook interactive shells, and no agent shell is one, so an agent never receives these variables by default. This is usually invisible until a suite fails at import for reasons that have nothing to do with any ticket.
3. **Smoke check before handing it over.** Run the repo's fastest proving command in the new worktree. Green, and the worktree is ready. Red, and the run stops here: an implementer handed a broken worktree will spend the ticket debugging the environment and blaming its own change.

**One command-runner per ticket worktree at a time.** Separate worktrees are safe to run in parallel; two subagents inside one worktree are not, because package managers resync a shared environment underneath each other and the failures look like flaky tests.

Remove the worktree when its ticket merges, and only then.

## The implementer

One fresh subagent per ticket, in that ticket's worktree.

**Pass pointers, not content.** Give it the path to the spec, the ticket reference, `CONTEXT.md`, the relevant ADRs, and its worktree path. Do not paste the spec into the prompt: it is already on disk in that worktree, and a copy in a prompt is a copy that can go stale.

Tell it to call the Skill tool with `tdd` and work at the seams the spec's diagram already names. Those seams are agreed: the implementer does not re-ask the user to confirm them. A seam the diagram does not cover is a signal that the ticket has outgrown its spec, and that comes back to you.

**Evidence before done.** An implementer has not finished until it reports the output of the command it just ran that proves the ticket works. A report without fresh output is not a report; send it back.

## Review, after every ticket

Call the Skill tool with `code-review`, giving it the ticket's diff range and the spec, so it does not stop to ask the user for either. Three axes:

- **Spec**: does it do what the ticket asked, and no more? This axis re-runs the proving command itself rather than trusting the implementer's report.
- **Standards**: the repo's documented standards, the smell baseline, and the book checks.
- **Drift**: does the diff still match the spec's Module/Seam Diagram? This runs because the spec has a diagram.

For a small ticket, one module and a small diff, Spec and Standards may share one sub-agent. Drift stays separate: it answers a different question and merging it lets a clean-code verdict bury a moved seam.

**The fix loop is capped at two rounds.** Round one, send the findings back to a fresh implementer in the same worktree. Round two, the same. After that, stop and come to the user. A third round means the ticket is wrong, not the code.

## Rulings and stops

**Rule on small implementation calls and keep going.** Log each one in the ledger as `Ruling: <what> | <why> | <cost if wrong>`. The cost field is the point: it is what the end-of-build eval sorts by, and a ruling whose cost you cannot state in a few words is probably a stop.

**Stop that ticket and come to the user** for any of these:

- a design fork, two real options where the right answer is not yours to pick
- a drift finding that changes a seam
- a ticket that turns out to be architectural
- a fix loop that ran out of rounds
- a merge conflict where two tickets' intents clash, rather than their text
- anything irreversible, destructive, security-sensitive, or reaching outside the ticket worktree

**Language is never a reason to stop.** Use `CONTEXT.md` as it stands. Do not ask about terminology, do not state readings, and never write to `CONTEXT.md` during a build. Alignment is a design-phase activity with the user, and a build that stops on vocabulary will stop constantly.

**While a stop is open**, tickets already running finish their current review round and then hold. No new ticket starts. This bounds how much work is built on an assumption the user is about to overturn.

**When the user approves a seam change**, update the spec's Module/Seam Diagram, write an ADR if the decision is hard to reverse, surprising without context, and a real trade-off, and **commit both before resuming**. An approved change that never reaches the diagram makes every later drift check fire on the same settled deviation until the axis is worthless.

## Merge and verify

A merger subagent merges each finished, reviewed ticket into the feature branch.

- **Mechanical conflicts it resolves**: two tickets touching neighbouring lines, import ordering, a moved file.
- **Intent conflicts stop the run**: two tickets that solved overlapping problems in incompatible ways. That is a design question wearing a conflict's clothes, and it goes to the user.

After every merge, run the **full test suite and typecheck on the feature branch** before any dependent ticket starts. A red suite after a merge is treated exactly like a failed review: it opens a fix round against the ticket that turned it red.

Then remove that ticket's worktree and update the ledger.

**If the repo's typecheck is already failing at the base commit**, say so once at the start of the run and treat the suite as the gate instead. A check that was red before the branch existed cannot prove anything about the branch, and quoting its output as if it could is worse than admitting it.

## Close

When every ticket is merged:

1. Call the Skill tool with `code-review` over the whole branch, against the merge base. Ticket-level review sees one diff at a time; some findings only exist across the whole change.
2. Call the Skill tool with `evaluate-output` for the build eval: the intended module/seam diagram beside what was actually built, which seams have tests and at what level, deviations, open questions, and every ruling from the ledger sorted by cost if wrong.
3. **Stop.** Leave a finished, reviewed feature branch. Do not open a pull request and do not merge. That decision is the user's.
