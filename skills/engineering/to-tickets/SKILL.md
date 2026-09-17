---
name: to-tickets
description: Break a plan, spec, or the current conversation into a set of tracer-bullet tickets, each declaring its blocking edges, published to the configured tracker (edges as text in one file per ticket locally, or native blocking links on a real tracker).
disable-model-invocation: true
---

# To Tickets

Break a plan, spec, or conversation into a set of **tickets**: tracer-bullet vertical slices, each declaring the tickets that **block** it.

The issue tracker and triage label vocabulary should have been provided to you. If not, tell the user to run `/setup-matt-pocock-skills`.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes a reference (a spec path, an issue number or URL) as an argument, fetch it and read its full body and comments.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Ticket titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

Look for opportunities to prefactor the code to make the implementation easier. "Make the change easy, then make the easy change."

### 3. Draft vertical slices

Break the work into **tracer bullet** tickets.

<vertical-slice-rules>

- Each slice cuts a narrow but COMPLETE path through every layer (schema, API, UI, tests): vertical, NOT a horizontal slice of one layer
- A completed slice is demoable or verifiable on its own
- Each slice is sized to fit in a single fresh context window
- Any prefactoring should be done first

</vertical-slice-rules>

Give each ticket its **blocking edges**: the other tickets that must complete before it can start. A ticket with no blockers can start immediately.

**Wide refactors are the exception to vertical slicing.** A **wide refactor** is one mechanical change (rename a column, retype a shared symbol) whose **blast radius** fans across the whole codebase, so a single edit breaks thousands of call sites at once and no vertical slice can land green. Don't force it into a tracer bullet; sequence it as **expand–contract**. First expand: add the new form beside the old so nothing breaks. Then migrate the call sites over in batches sized by blast radius (per package, per directory), each batch its own ticket blocked by the expand, keeping CI green batch to batch because the old form still exists. Finally contract: delete the old form once no caller remains, in a ticket blocked by every migrate batch. When even the batches can't stay green alone, keep the sequence but let them share an integration branch that all block a final integrate-and-verify ticket; green is promised only there.

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each ticket, show:

- **Title**: short descriptive name
- **Blocked by**: which other tickets (if any) must complete first
- **What it delivers**: the end-to-end behaviour this ticket makes work

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the blocking edges correct: does each ticket only depend on tickets that genuinely gate it?
- Should any tickets be merged or split further?

Iterate until the user approves the breakdown.

### 5. Publish the tickets to the configured tracker

Publish the approved tickets. **How** depends on the tracker `/setup-matt-pocock-skills` configured; the tickets are the same either way, only the shape of the blocking edges changes:

- **Local files** → write one file per ticket under `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01` in dependency order (blockers first). Each file's "Blocked by" lists the numbers/titles it depends on. Use the per-ticket file template below: one ticket per file, never a single combined file.
- **A real issue tracker (GitHub, Linear, …)** → publish one issue per ticket in dependency order (blockers first) so each ticket's blocking edges can reference real identifiers. Use the platform's native blocking / sub-issue relationship where it has one; otherwise set each ticket's "Blocked by" to the blocking issues. Apply the `ready-for-agent` triage label unless instructed otherwise; the tickets are agent-grabbable by construction.

Work the **frontier**: any ticket whose blockers are all done. For a purely linear chain that means top to bottom.

Do NOT close or modify any parent issue.

<local-ticket-template>

# <NN>: <Ticket title>

**What to build:** the end-to-end behaviour this ticket makes work, from the user's perspective, not a layer-by-layer implementation list.

**Blocked by:** the numbers/titles of the tickets that gate this one, or "None (can start immediately)".

**Status:** ready-for-agent

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2

</local-ticket-template>

<issue-template>

## Parent

A reference to the parent issue on the tracker (if the source was an existing issue, otherwise omit this section).

## What to build

The end-to-end behaviour this ticket makes work, from the user's perspective, not layer-by-layer implementation.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Blocked by

- A reference to each blocking ticket, or "None (can start immediately)".

</issue-template>

In either form, avoid specific file paths or code snippets: they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.


<!-- fork: start -->

## Modules touched

Each ticket declares the modules it touches, by name, from the spec's Module/Seam Diagram. Module names, never file paths: paths go stale within a ticket or two, and navigation is not what the field is for.

Add it to both templates, directly after **Blocked by**:

**Modules touched:** the modules from the spec's diagram that this ticket changes.

This is the field that makes parallelism safe. Two tickets whose blockers are all done can run at the same time only when their declared modules do not overlap; where they overlap they run one after the other, whatever the blocking edges say. Blocking edges record what must happen first, and that is a different question from what two agents can safely edit at once.

Two things the field surfaces while the breakdown is still cheap to change. A ticket that declares most of the diagram is not a vertical slice yet; split it. A ticket that has to touch a module the diagram does not have is a design question wearing a ticket's clothes; take it back to the spec rather than letting the implementer invent the module.

## Show the breakdown as a graph

Step 4 presents a numbered list. Draw it as well. A numbered list of fifteen tickets with blocking edges is a graph flattened into prose, and an accidental chain or a bottleneck is invisible in that form to the one person whose approval the step is asking for.

Write the body as an HTML fragment, then build the page with the shared shell:

```
python3 <skills-dir>/evaluate-output/build-page.py \
  --title "Tickets: <feature>" \
  --subtitle "<n> tickets - <date>" \
  --content <fragment>.html \
  --out .scratch/<feature-slug>/visuals/tickets.html
```

The fragment holds one `<pre class="mermaid">` block, never a `<div>`: both render locally, only the `<pre>` form also renders in a Claude Artifact, and before any script runs it still shows its own source. Inside it, a `flowchart LR` (`TD` once the longest chain passes four or so): one node per ticket labelled with its number and title, one edge per blocking edge drawn from blocker to blocked. Group the nodes by module with `subgraph`, or colour them by module with `classDef`, so overlap is something the reader sees rather than something they reconstruct by reading a field ticket by ticket. Under the diagram, the numbered list step 4 already asks for.

The shell provides `.panel`, `.grid`, `.scroll`, `.badge` and `.mermaid`; use them rather than inventing styles. Open the page if you are the session talking to the user and `open` is available, otherwise print the absolute path. Then ask step 4's questions against it, plus the two the graph makes askable at all: is anything a chain that does not need to be one, and do the modules spread widely enough for anything to run in parallel?

If the script is not installed, show the numbered list alone and say the page was skipped. This is worth a minute, not a detour.

## Commit the design artifacts before Build

Once the user approves the breakdown and the tickets are published, commit to the feature branch:

- `.scratch/<feature-slug>/spec.md`
- `.scratch/<feature-slug>/decisions.md`
- `CONTEXT.md`, and any ADR the design phase added or changed
- the ticket files, on a local-markdown tracker. On a real tracker the tickets are issues, read over the network, and there is nothing here to commit.

Build runs every ticket in a fresh git worktree cut from this branch, and a worktree holds committed files and nothing else. Anything left uncommitted is invisible to every implementer, and the failure mode is silent: no error, just a spec that is not there and an implementer that invents its own.

Where `.gitignore` covers `.scratch/`, force-add on this branch only, `git add -f .scratch/<feature-slug>/`. Do not edit `.gitignore` to make this work: the artifacts are wanted on one feature branch, not in every future one.

<!-- fork: end -->
