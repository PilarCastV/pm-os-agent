# Build Insights: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 4, what you learned building it
>
> ✅ **What this validates:** you can reflect on what building it taught you, by the end you'll have proven the friction, the learning, and the aha that changes how you'd design your next agent.

## Friction

The validator was wrong, repeatedly. The cheap validator misquoted the norms, missed a fabricated date, and then rejected correct drafts. I found the root cause, and I could tell it was wrong only because I knew the data. It is dangerous if you don't have a clue about the data, because you would trust it.

The second fight was a withheld source. When I removed `get_activity`, the drafter substituted another source and never mentioned the downgrade. It should have told me the source was incomplete or missing. That matters because quietly using a weaker source creates hallucination risk, and that drives inaccuracy.

## Learning

Before this course, I thought of guardrails mainly as rules about what an agent must not do. Now I see that guardrails for what it should do matter just as much: that it does the job completely and honestly, for example by telling me when a source is missing.

Nondeterministic tools can't be proven with one good run. I have to test the same case several times before I trust it, and keep testing after it's deployed.

## Aha moment

The agent's silence is the failure. A loud stop is fine, and a quiet substitution is what hurts. In my next agent I would design the "I can't do this" path first: if a required source is missing, it stops and tells me, rather than quietly using a weaker one.

## What you'd do differently

If I rebuilt Cortex from scratch, I would start with the change from my aha: when a required source is missing, Cortex stops and tells me, rather than quietly using a weaker one. It already does this for a missing project, but not yet for a missing tool or source.
