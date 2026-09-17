---
name: grill-with-docs
description: A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go.
disable-model-invocation: true
---

Call the Skill tool twice, for "grilling" and "domain-modeling".

<!-- fork: start -->

## Decisions go to disk as they land

An ADR is for a decision that is hard to reverse, surprising without context, and the result of a real trade-off. Most of what a grilling session settles clears none of those bars and is still worth keeping: write it to `.scratch/<feature>/decisions.md` as it lands, one entry per decision, with the option chosen, the options rejected, and why.

`CONTEXT.md` and ADRs work exactly as `domain-modeling` describes. This file is the third tier under them, and it exists because a session's reasoning is gone the moment its context is compacted. `to-spec` reads it, so a spec written next week still knows why.

## When a fork's answer is unknown

Some questions cannot be answered by more interviewing, only by building the smallest thing that settles them. Call the Skill tool with `prototype`, then bring the answer back into the round it came from.

**At most two prototypes per question.** A third means the question is wrong or the answer is a preference: put it to the user directly and decide it in conversation.

## When a fork has two or more real options

Call the Skill tool with `codebase-design` and use its design-it-twice parallel sub-agent pattern, then call the Skill tool with `visual-design-review` to draw the options and compare them. Prose comparison of two shapes favours whichever was written more confidently.

<!-- fork: end -->
