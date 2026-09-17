---
name: align-language
description: "Called in interactive design or planning when a term is new, load-bearing, and carries established meanings in two or more of the domains the work touches, or when the user's usage of a term contradicts your own understanding of it. Settles the meaning in at most three questions and writes it to CONTEXT.md. Never runs during implementation or inside a subagent."
---

# Align Language

A word that means two things is a design fork nobody noticed. Caught in conversation it costs three questions. Caught after the code exists it costs a rewrite, because the disagreement is now spread across an interface, a schema, and a suite of tests that all assert the wrong reading confidently.

## Scope

**Interactive design and planning with the user, and nowhere else.** Never during implementation, never inside a subagent, never inside the build orchestrator. Those readers have no user to ask and no authority to change the glossary: they read `CONTEXT.md` exactly as it stands, and language is never a reason for them to stop.

If a `grilling` or `domain-modeling` session is already under way, stay quiet. `domain-modeling` already challenges terms against the glossary and writes them down as they land, and two skills asking the same question in the same round is noise.

## Trigger A: a new term that is load-bearing and overloaded

All three conditions hold, or this is not a trigger.

1. **New**: not in `CONTEXT.md`, and not already settled earlier in this session.
2. **Load-bearing**: what gets built changes with the meaning. It names a module, an entity, a state, a rule, or something a test asserts on.
3. **Overloaded across domains**: it has distinct, established meanings in two or more of the fields this work touches. "Session" (auth, analytics, an agent run), "event", "account", "job", "model", "context", "run", "policy". Vagueness inside one domain is not this: that is a question to ask in passing, not a fork.

## Trigger B: your reading and the user's have come apart

Any term, new or not. The signals:

- their usage contradicts `CONTEXT.md`, the code, or their own earlier usage this session,
- they correct your paraphrase of a term.

To catch this early, **state your reading the first time you act on a load-bearing term**, inline and in a few words: "treating *session* as the auth session". Free when it is right. When it is wrong it fires this trigger while the design is still a sentence, rather than after it is a module.

## Not a trigger

General programming terms with one meaning in context. Terms the user is already using exactly as `CONTEXT.md` defines them. Wording preferences. Ambiguity that would not change the design: if both readings build the same thing, pick one, say which, and move on.

## When it fires

Stop before designing or coding any further. Ask **at most three numbered questions**, in the `grilling` format:

```
❓ **Q1** - **<the term>**: <the question>

➡️ <your recommended answer>
```

For trigger A, each question carries both readings in the caller's terms, one concrete scenario the two would handle differently, and your recommended answer. The scenario is what does the work: two definitions sound compatible until a case has to go one way or the other.

For trigger B, state the mismatch plainly before the question:

```
Your usage: ...
My understanding: ...
Source: CONTEXT.md / the code at <path> / earlier in this session
```

Naming the source is not bookkeeping. It tells the user whether they are correcting you or contradicting something they wrote themselves, and those need different answers.

## Write it down as it lands

The moment the answer arrives, add the term to `CONTEXT.md`, with the readings you ruled out under `_Avoid_`:

```md
**Session**:
The authenticated period between a user signing in and signing out.
_Avoid_: analytics session, agent run
```

Immediately, not at the end of the session. An answer that only exists in the conversation is gone the next time context is compacted, and the same three questions get asked again next week.

For anything past a glossary entry (an ADR, a multi-context repo, the full format), call the Skill tool with `domain-modeling`.

## Escalate only when the answer opens a fork

If settling the word settles the design, you are done: carry on with what you were doing. If the answer turns out to open a real design fork, two builds rather than two words, stop and call the Skill tool with `grilling`. Three questions is this skill's ceiling by design. A fork needs rounds, and rounds are what `grilling` is for.
