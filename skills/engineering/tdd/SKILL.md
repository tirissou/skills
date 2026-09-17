---
name: tdd
description: Test-driven development. Use when the user wants to build features or fix bugs test-first, mentions "red-green-refactor", or wants integration tests.
---

# Test-Driven Development

TDD is the red → green loop. This skill is the reference that makes that loop produce tests worth keeping: what a good test is, where tests go, the anti-patterns, and the rules of the loop. Every section applies on every cycle: consult them before and during the loop, not after.

When exploring the codebase, read `CONTEXT.md` (if it exists) so test names and interface vocabulary match the project's domain language, and respect ADRs in the area you're touching.

## What a good test is

Tests verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't. A good test reads like a specification: "user can checkout with valid cart" tells you exactly what capability exists, and it survives refactors because it doesn't care about internal structure.

See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking guidelines.

## Seams: where tests go

A **seam** is the public boundary you test at: the interface where you observe behavior without reaching inside. Tests live at seams, never against internals.

**Test only at pre-agreed seams.** Before writing any test, write down the seams under test and confirm them with the user. No test is written at an unconfirmed seam. You can't test everything, so agreeing the seams up front is how testing effort lands on the critical paths and complex logic instead of every edge case.

Ask: "What's the public interface, and which seams should we test?"

When the shape of that interface is itself in question (how deep the module is, where the seam belongs, what the interface should expose), call the Skill tool with "codebase-design" for the vocabulary. It is the shared source of the module, interface, depth, seam, adapter, leverage and locality terms, and it is a reference to consult, not a session to run.

## Anti-patterns

- **Implementation-coupled**: mocks internal collaborators, tests private methods, or verifies through a side channel (querying the database instead of using the interface). The tell: the test breaks when you refactor but behavior hasn't changed.
- **Tautological**: the assertion recomputes the expected value the way the code does (`expect(add(a, b)).toBe(a + b)`, a snapshot derived by hand the same way, a constant asserted equal to itself), so it passes by construction and can never disagree with the code. Expected values must come from an independent source of truth: a known-good literal, a worked example, the spec.
- **Horizontal slicing**: writing all tests first, then all implementation. Bulk tests verify _imagined_ behavior: you test the _shape_ of things rather than user-facing behavior, the tests go insensitive to real changes, and you commit to test structure before understanding the implementation. Work in **vertical slices** instead: one test → one implementation → repeat, each test a **tracer bullet** that responds to what the last cycle taught you.

## Rules of the loop

- **Red before green.** Write the failing test first, then only enough code to pass it. Don't anticipate future tests or add speculative features.
- **One slice at a time.** One seam, one test, one minimal implementation per cycle.
<!-- fork: start -->
- **Refactoring has two homes.** Small design refactors happen inside the loop, at the between-slice design check below. Larger ones belong to the review stage (see the `code-review` skill).
<!-- fork: end -->


<!-- fork: start -->

## Name the break

Every test says which production change would make it fail, in its name or in a one-line comment above it. "user can checkout with valid cart" names a break: remove the checkout path and it goes red. "renders correctly" names nothing, so nobody can tell later whether it still guards anything.

If the only edit that breaks a test is someone deliberately changing a decision (a constant's value, the wording of a message, the order of a list nobody depends on), the test is not written. It pins a choice instead of protecting behaviour, and it goes red on every intentional change while catching no regression.

## Between-slice design check

After each green slice, before starting the next, answer three questions in one or two lines each:

1. Did any interface get wider or shallower?
2. Is knowledge about one decision now in more than one module?
3. Does the code still sit on the agreed seams?

A "yes" is fixed with a refactor now, while the slice is small and the reasoning is fresh. If fixing it is out of scope for the current ticket, log it instead as a ruling: `Ruling: <what> | <why> | <cost if wrong>`.

The check is cheap because it runs over one slice's worth of change. Deferred to review, the same three questions have to be answered across a whole branch, where the fix is a rewrite rather than a rename.

## Seams already agreed in a spec

"Test only at pre-agreed seams" above asks you to confirm the seams with the user. When you are implementing from a spec that carries a module/seam diagram, that diagram **is** the confirmation: its seams are agreed, and asking again wastes the user's attention on a decision already made.

Ask only about a seam the diagram does not cover. Needing one is itself a signal: the ticket may have outgrown its spec.

<!-- fork: end -->
