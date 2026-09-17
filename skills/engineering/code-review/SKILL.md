---
name: code-review
description: "Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes: Standards (does the code follow this repo's documented coding standards?) and Spec (does the code match what the originating issue/spec asked for?). Runs both reviews in parallel sub-agents and reports them side by side. Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to \"review since X\"."
---

Two-axis review of the diff between `HEAD` and a fixed point the user supplies:

- **Standards**: does the code conform to this repo's documented coding standards?
- **Spec**: does the code faithfully implement the originating issue / spec?

Both axes run as **parallel sub-agents** so they don't pollute each other's context, then this skill aggregates their findings.

The issue tracker should have been provided to you. If `docs/agents/issue-tracker.md` is missing, tell the user to run `/setup-matt-pocock-skills`.

## Process

### 1. Pin the fixed point

Whatever the user said is the fixed point (a commit SHA, branch name, tag, `main`, `HEAD~5`, etc.). If they didn't specify one, ask for it.

Capture the diff command once: `git diff <fixed-point>...HEAD` (three-dot, so the comparison is against the merge-base). Also note the list of commits via `git log <fixed-point>..HEAD --oneline`.

Before going further, confirm the fixed point resolves (`git rev-parse <fixed-point>`) and the diff is non-empty. A bad ref or empty diff should fail here, not inside two parallel sub-agents.

### 2. Identify the spec source

Look for the originating spec, in this order:

1. Issue references in the commit messages (`#123`, `Closes #45`, GitLab `!67`, etc.), fetched via the workflow in `docs/agents/issue-tracker.md`.
2. A path the user passed as an argument.
3. A spec file under `docs/`, `specs/`, or `.scratch/` matching the branch name or feature.
4. If nothing is found, ask the user where the spec is. If they say there isn't one, the **Spec** sub-agent will skip and report "no spec available".

### 3. Identify the standards sources

Anything in the repo that documents how code should be written, such as `CODING_STANDARDS.md` or `CONTRIBUTING.md`.

On top of whatever the repo documents, the Standards axis always carries the **smell baseline** below: a fixed set of Fowler code smells (_Refactoring_, ch.3) that applies even when a repo documents nothing. Two rules bind it:

- **The repo overrides.** A documented repo standard always wins; where it endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never a hard violation. Like any standard here, skip anything tooling already enforces.

Each smell reads *what it is* → *how to fix*; match it against the diff:

- **Mysterious Name**: a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
<!-- fork: start -->
- **Duplicated Knowledge**: the same business rule or decision is expressed in two or more places in the change, so changing the rule would mean editing each of them. Code that merely looks alike is not this smell. → give the rule one home, call it from both.
<!-- fork: end -->
- **Feature Envy**: a method that reaches into another object's data more than its own. → move the method onto the data it envies.
- **Data Clumps**: the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
- **Primitive Obsession**: a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches**: the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery**: one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
- **Divergent Change**: one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
- **Speculative Generality**: abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
- **Message Chains**: long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
- **Middle Man**: a class or function that mostly just delegates onward. → cut it, call the real target direct.
- **Refused Bequest**: a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.

<!-- fork: start -->

Four further checks close the baseline, in the same format and with the same judgement-call status, drawn from _A Philosophy of Software Design_ and _The Pragmatic Programmer_:

- **Information Leakage**: one design decision (a format, a schema, an ordering, a wire protocol) is known to two or more modules in the change, so changing it means changing all of them. → give the decision a single owner, and let everyone else reach it through that interface.
- **Complexity Pushed Up**: a module hands its callers work it could have done itself: configuration they must assemble, errors they must interpret, steps they must sequence correctly. → pull the complexity down, so the interface stays simpler than the implementation.
- **Temporal Decomposition**: modules are split by when things happen (read, then validate, then write) rather than by what they know, so one piece of knowledge is smeared across every phase. → regroup by knowledge, not by order of execution.
- **Orthogonality Violation**: a change to one concern forced edits in an unrelated one, or a module knows about a concern that is none of its business (a data layer that knows HTTP status codes). → cut the link, so the two can change independently.

Reversibility is deliberately not here. It is a design-review question, asked before the code exists, and a diff cannot answer it.

<!-- fork: end -->

### 4. Spawn both sub-agents in parallel

**Standards sub-agent prompt** should include:

- The full diff command and commit list.
- The list of standards-source files you found in step 3, **plus the smell baseline from step 3** pasted in full (the sub-agent has no other access to it).
- The brief: "Report, per file/hunk where relevant, (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) any baseline smell you spot: name it and quote the hunk. Distinguish hard violations from judgement calls: documented-standard breaches can be hard, but baseline smells are always judgement calls, and a documented repo standard overrides the baseline. Skip anything tooling enforces. Under 400 words."

**Spec sub-agent prompt** should include:

- The diff command and commit list.
- The path or fetched contents of the spec.
- The brief: "Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong. Quote the spec line for each finding. Under 400 words."

If the spec is missing, skip the Spec sub-agent and note this in the final report.

### 5. Aggregate

Present the two reports under `## Standards` and `## Spec` headings, verbatim or lightly cleaned. Do **not** merge or rerank findings, because the two axes are deliberately separate (see _Why two axes_).

End with a one-line summary: total findings per axis, and the worst issue _within each axis_ (if any). Don't pick a single winner across axes: that's the reranking the separation exists to prevent.

## Why two axes

A change can pass one axis and fail the other:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the issue asked but breaks the project's conventions → **Spec pass, Standards fail.**

Reporting them separately stops one axis from masking the other.


<!-- fork: start -->

## Drift: the third axis

Runs **only** when the spec found in step 2 carries a module/seam diagram. Without one there is nothing to measure drift against: skip the axis and say so in one line in the final report.

When it runs, it is a third **parallel sub-agent**, spawned in step 4 alongside Standards and Spec.

**Drift sub-agent prompt** should include:

- The diff command and commit list.
- The spec's module/seam diagram, pasted in full (the sub-agent has no other access to it).
- The brief: "The diagram is what we agreed to build. Report every place the diff departs from it: a module that took on a responsibility the diagram gives to another, a call that crosses a boundary the diagram doesn't draw, a seam that moved, a seam that was never built, a module in the code that isn't in the diagram at all. For each, quote the code and state plainly whether it changes a seam or leaves the seams intact. Don't judge whether the code is good; only whether it matches the diagram. Under 400 words."

In step 5, report it under its own `## Drift` heading beside `## Standards` and `## Spec`, never merged into either. The axes answer different questions: a change can be clean code, faithful to the spec's prose, and still have moved a seam.

**A deviation that changes a seam is the finding that matters most.** It doesn't get fixed by the reviewer. It goes to the user, who either approves the new seam, in which case the spec's diagram is updated and committed before work resumes, or rejects it, in which case the code moves back. An approved seam change that never reaches the diagram makes every later drift check fire on the same, already-settled deviation.

<!-- fork: end -->
