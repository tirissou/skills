---
name: visual-design-review
description: "Called when a design fork has two or more real options on the table, usually the ones design-it-twice just produced, to draw each option's modules and seams and compare them on one HTML page. Not a code review, and not an end-of-work eval."
---

# Visual Design Review

Two designs argued in prose read as two paragraphs of adjectives, and the user picks the one that was described more confidently. Drawn, the difference is a shape: which module knows what, where the seam sits, what a request has to touch on its way through. This skill turns a fork into one page.

## Draw it only when seeing beats reading

The options differ in **shape**, which modules exist, what each one knows, where the seams sit, how a flow moves through them, so draw them.

The options differ in a **value**, a library, a name, a threshold, an ordering, so write a paragraph and pick one. Two diagrams of the same boxes teach nobody anything, and a page produced out of habit trains the reader to skim the next one.

This gate is this skill's alone. The end-of-work eval (`evaluate-output`) is not gated: it always appears.

## What goes on the page

### One block per option

Each option gets, in this order:

1. **A module/seam diagram.** Mermaid. Modules as nodes, seams as the edges that cross them, labelled with what passes. Mark which seams are new.
2. **One key flow**, as a flowchart or a sequence diagram: the case that made this a fork in the first place, moving through that option's modules. This replaces pseudocode. Pseudocode in a design review is code written before the decision that would have shaped it.
3. **What sits behind each seam**, in a line or two: the implementation the interface hides, and the dependency category behind it.

Name modules with the project's own vocabulary from `CONTEXT.md`, and use `codebase-design` terms (module, interface, depth, seam, adapter, leverage, locality) exactly. An option that has to invent a word for one of its parts is telling you something: say so.

### One comparison table

Three columns, one row per option, judgements rather than restatements:

| | Depth | Locality | Seam placement |
|---|---|---|---|
| Option A | leverage a caller gets per unit of interface it has to learn | where a change to this concern lands, and how many places it touches | is the seam where something actually varies, and does one adapter or two sit at it |

One adapter means a hypothetical seam, two means a real one. An option whose seams all have exactly one adapter is paying for flexibility it has not been asked for.

### The book checks, per option

Each is a judgement call, answered in a line. They are the design-phase counterparts to the ones `code-review` runs on a diff, asked here while they are still cheap to act on:

- **Information leakage**: does one decision (a format, a schema, an ordering, a wire protocol) have to be known by two or more modules? Then changing it changes all of them.
- **Complexity pushed up**: does the interface hand callers work it could have done itself, configuration to assemble, errors to interpret, steps to sequence in the right order?
- **Temporal decomposition**: are modules split by when things happen (read, then validate, then write) rather than by what they know, so one piece of knowledge is smeared across every phase?
- **Orthogonality**: can each concern change without dragging an unrelated one with it, or does a module know about something that is none of its business?
- **Reversibility**: if this turns out wrong in three months, what does undoing it cost? This is the check a diff cannot answer, which is why `code-review` leaves it here.

### A recommendation

One option, named, with the reason in one or two sentences. If the best page is a hybrid, say which parts of which options and why. Be opinionated: the user wants a strong read, not a menu. They can overrule a recommendation in a sentence; they cannot overrule a shrug.

## Build the page

Write the body as an HTML fragment (the content that goes inside `<main>`), then splice it into the shared shell:

```
python3 <skills-dir>/evaluate-output/build-page.py \
  --title "Design: <the fork, in a few words>" \
  --subtitle "<date> - <n> options" \
  --content <fragment>.html \
  --out .scratch/<feature>/visuals/design-<topic>.html
```

The page machinery lives in the sibling `evaluate-output` skill, which vendors the Mermaid bundle, 3.4 MB that no agent can carry through its own context. Reach it by path, not by calling the Skill tool: that skill's instructions are about proving finished work with fresh command output, and there is no finished work here. The two skills install side by side, so `../evaluate-output/build-page.py` resolves both in the repo and under `~/.claude/skills`.

**Write every diagram as `<pre class="mermaid">`, never a `<div>`.** Both render locally; only the `<pre>` form also renders in a Claude Artifact, and before any script runs the block still shows its own source, which is a readable fallback.

The shell provides `.panel`, `.grid` (for option blocks side by side), `.scroll` around wide tables, `.badge` with `.pass`, `.fail` and `.warn`, and `.mermaid`. Use them instead of inventing styles.

Save under `.scratch/<feature>/visuals/`, beside the spec, tickets and evals for the same feature. Not the temp directory: it does not survive.

If the user wants the page on a phone or in someone else's hands, build it a second time with `--target artifact` and publish it; the same script handles it.

## Deliver it

Open it if you are the session talking to the user and `open` is available. Otherwise, and always from a subagent, print the absolute path and stop. Never report a path you have not just written.

## After the user picks

The page is the argument; it is not the record. Once the user chooses, write the choice, the options rejected, and why into `.scratch/<feature>/decisions.md`, and link the page. If the choice is hard to reverse, surprising without context, and the result of a real trade-off, it has earned an ADR: call the Skill tool with `domain-modeling`.

The chosen option's module/seam diagram is the one `to-spec` carries into the spec, where it becomes what every later drift check measures against.
