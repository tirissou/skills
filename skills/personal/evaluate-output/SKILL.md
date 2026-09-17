---
name: evaluate-output
description: "Called at the end of a chunk of work that was sent out to be completed (a bounded change, a spike, or a full build) to re-run the commands that prove it works and turn the result into one self-contained HTML eval page. Not a code review, and not a comparison of design options."
---

# Evaluate Output

Every chunk of work ends here: a bounded change, a spike, or a full build. The eval answers two questions, in this order. Does it actually work, proved by a command run just now? And what does the result look like, shown rather than described?

## 1. Evidence first

Re-run the commands that prove the work. **Never reuse output from earlier in the session**, however recent: the point is evidence that survives everything that happened since.

Run three kinds:

- the test suite for the area touched,
- the typecheck or build, if the project has one,
- the specific command that demonstrates this change, not just the suite around it.

Report each as the command, verbatim, and its result. **If any command fails, the page leads with the failure** and says the work is not done. An eval that buries a red suite under a diagram is worthless.

If a command cannot be run, say which and why, in place. Absent evidence is reported as absent, never as success.

## 2. Size the eval

The size was already announced when the work started (spike, bounded, or architectural). Use it.

**Bounded**: what changed, the tests added and the break each one names, the fresh test output, and anything surprising.

**Spike**: the question the spike existed to answer, the answer, the evidence behind it, and where the prototype lives.

**Build**: the intended module/seam diagram beside a diagram of what was actually built, which seams have tests and at what level, deviations and open questions, and every ruling from `.scratch/<feature>/ledger.md` sorted by cost if wrong.

A build eval also states, plainly, **why** it works. Success nobody can explain is a finding: report it as one.

## 3. Build the page

Write the body as an HTML fragment (just the content that goes inside `<main>`), then splice it into the shared shell:

```
python3 <skill-dir>/build-page.py \
  --title "Eval: <what the work was>" \
  --subtitle "<date> - <evidence verdict in a few words>" \
  --content <fragment>.html \
  --out .scratch/<feature>/visuals/eval-<YYYY-MM-DD-HHMM>.html
```

`build-page.py` inlines the vendored Mermaid bundle when the fragment contains a `class="mermaid"` block, so the page renders with no network. Never paste the library yourself.

Save under `.scratch/<feature>/visuals/` when the work has a feature folder (the one holding its spec, tickets, and ledger). Bounded work with no feature folder goes to `.scratch/misc/visuals/`. Not the temp directory: it does not survive.

The shell provides: `.badge` with `.pass`, `.fail`, `.warn`; `.panel` and `.panel.alert`; `.grid` for diagrams side by side; `.scroll` around wide tables; and `.mermaid` for diagrams. Use them instead of inventing styles.

## 4. Deliver it

Open it if you are the session talking to the user and `open` is available. Otherwise, and always from a subagent, print the absolute path and stop. Never report a path you have not just written.

## Writing the page

**Diagrams carry the weight.** If a diagram needs a paragraph to explain it, redraw the diagram. Prose is for what a picture cannot hold: why it works, what is still open, what surprised you.

Two diagrams beat one table when the point is a shape that changed. A build eval's central image is the intended module/seam diagram beside the built one, in a `.grid`, so the difference is visible rather than asserted.

Report deviations in the reader's terms: what was agreed, what exists now, and whether it moved a seam.
