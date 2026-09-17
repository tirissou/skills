---
name: to-spec
description: "Turn the current conversation into a spec and publish it to the project issue tracker: no interview, just synthesis of what you've already discussed."
disable-model-invocation: true
---

This skill takes the current conversation context and codebase understanding and produces a spec. Do NOT interview the user; just synthesize what you already know.

The issue tracker and triage label vocabulary should have been provided to you. If not, tell the user to run `/setup-matt-pocock-skills`.

## Process

1. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the spec, and respect any ADRs in the area you're touching.

2. Sketch out the seams at which you're going to test the feature. Existing seams should be preferred to new ones. Use the highest seam possible. If new seams are needed, propose them at the highest point you can. The fewer seams across the codebase, the better - the ideal number is one.

Check with the user that these seams match their expectations.

3. Write the spec using the template below, then publish it to the project issue tracker. Apply the `ready-for-agent` triage label - no need for additional triage.

<spec-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this spec.

## Further Notes

Any further notes about the feature.

</spec-template>


<!-- fork: start -->

## Read the decision files, not just the conversation

"Synthesize what you already know" assumes the conversation that made the decisions is still in context. Often it is not: a compaction, a new session, or a week between design and planning each lose it. Before step 1, read what the design phase wrote to disk:

- `.scratch/<feature-slug>/decisions.md`: the choices that sat below the ADR bar, each with the option chosen, the options rejected, and why.
- `CONTEXT.md`: the domain glossary, including the `_Avoid_` synonyms. Use the resolved word throughout the spec and never one listed under `_Avoid_`.
- Any ADR covering the area being touched.

These files exist so the spec can be written without the conversation. Where one of them and your memory of the conversation disagree, the file is the record.

## The Module/Seam Diagram section

The template above gains one more section, between **Implementation Decisions** and **Testing Decisions**. Every spec carries it, and it is the most reused part of the spec: `to-tickets` reads the module names out of it, implementers read the seams instead of asking about them, and every drift check measures the diff against it.

<module-seam-diagram-template>

## Module/Seam Diagram

A Mermaid diagram (a ` ```mermaid ` fence) of the modules this feature touches and the seams between them: modules as nodes, seams as the edges that cross them, labelled with what passes. Mark which modules and which seams are new.

Then one line per seam:

- **<seam>**: its dependency category, what sits behind it, and where its tests go.

</module-seam-diagram-template>

The categories are the four in `codebase-design`'s `DEEPENING.md`: in-process, local-substitutable, remote but owned, true external. They are what decides how a seam is tested, so a seam recorded without one has left the test strategy undecided and the Testing Decisions section below it has nothing to stand on. Name modules with the project's own vocabulary from `CONTEXT.md`, and use the `codebase-design` terms exactly.

**This diagram is the reference for drift.** Every later check asks whether the code still matches it, so when the user approves a seam change mid-build, the diagram is updated and committed before work resumes. An approved change that never reaches the diagram makes every later drift check fire on the same, already-settled deviation until the reviewer learns to ignore the axis.

## The spec also lives on disk

Publish to the tracker as step 3 says. Then, whatever the tracker is, write the same spec to `.scratch/<feature-slug>/spec.md`. On a local-markdown tracker that is already the only copy and there is nothing further to do.

On a real tracker it is a second copy, and two copies drift, so say now which one wins: **the file on disk**. Build runs every ticket in a fresh git worktree cut from the feature branch, and a worktree holds committed files and nothing else. The file is what implementers and drift checks actually read; the issue is the copy people comment on. The deciding reason is versioning: a drift check reviewing the diff at one commit has to measure against the diagram as it stood at that commit, and an issue body has one current version and no history tied to the branch. Put the issue reference at the top of the file and the file's path in the issue body so neither copy is orphaned, and when the diagram changes, change the file first.

`to-tickets` commits it.

<!-- fork: end -->
