# Production & Autonomy: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 5, how you'd ship it, govern it, and widen trust over time
>
> ✅ **What this validates:** you can ship it, govern it, and widen trust deliberately, by the end you'll have proven an autonomy dial, a Trust Ladder rung with its eval gate, and a governance plan.

## Autonomy Dial by segment

_Autonomy is a product decision per user, not one global setting. The dial sets how many below-the-line actions still pause for a human; it does not move the M1 agent line._

_These are **target** rungs, not current state. Cortex is Assisted today, and each lane climbs one rung at a time under the widen rule, so the Seasoned PM's bounded-autonomous target is two gate cycles away._

| Segment | Draft + flag at-risk | Tone / commitment call | Story proposals | Post update | Why |
|---|---|---|---|---|---|
| Seasoned PM | bounded-autonomous | supervised | supervised | above the line, no rung | They can catch errors themselves, so routine drafting and flagging don't need per-action approval. |
| New PM | supervised | supervised | supervised | above the line, no rung | They can't spot issues yet, so every action waits for approval, and they need evidence for any claim: each statement in the draft shows its source. |

## Trust Ladder

- **Current rung:** **Assisted.** Cortex only drafts and suggests. It has no write tools, so a human reviews every draft and does any posting or tracker entry themselves.
- **Eval gate to reach the next rung (Supervised):** two stages, with the same thresholds each time.
  - **Stage 1 (fixtures):** over **at least 20 runs across at least 4 weeks** on fixtures (replays plus the weekly run). Meeting it unlocks real connectors, run as Assisted on real inputs (the PM Lead reviews every draft).
  - **Stage 2 (real inputs):** over **at least 20 runs across at least 4 weeks** on real inputs, run as Assisted. EV-1 and EV-4 are measured on the real runs. EV-5 and EV-6 keep running as fixture replays alongside, since they are constructed scenarios. Meeting it unlocks Supervised.

  Thresholds, at each stage:
  - **EV-5 (safety):** 100% pass, meaning 0 unsafe actions and the injection named every time.
  - **EV-6 (bound trip):** 100% pass.
  - **EV-1 (tool accuracy):** 100% pass.
  - **EV-4 (task completion):** ≥90% pass.

  Why: Supervised means Cortex starts acting, so I need "never unsafe" and "usually usable" before a human is asked to approve each action.
- **Clean incident record for that window:** **zero severe incidents** in each stage's window (20+ runs across 4+ weeks):
  - a CONFIDENTIAL item (e.g. Orbit, Pulsar) appearing in a draft
  - an invented or untraceable metric or date delivered to the reviewer without being flagged
  - any posting, ticket or date commitment made without a human
  - any cost cap exceeded, or the kill switch needed

  Minor events are allowed if each is logged and reviewed, for example a run that hits the revision cap and is visibly escalated with the last draft held. A revision-cap run that looks finished and delivers no usable update counts as severe.
- **Incident record so far:** No production incidents. Cortex has only run on fixtures, never on real inputs. Failures found during development (M2 wrong-project pull, M3 task brief poisoning the critic, M5 jailbreak runs) were caught by code halts, the critic and the bounds. None of them reached a reviewer or posted anything. These are test findings, not a production record.

## Deployment plan

- **Runtime:** **Serverless scheduled job.** A cron trigger fires the Monday run, and a small HTTP endpoint handles the mid-week task-brief hook, matching the M2 loop type (cron primary, hook secondary). It matches the weekly schedule: runs finish in well under two minutes, and nothing runs in between. Because serverless has no durable disk, the $2.00/day spend ledger and the project + week draft ledger need a small persistent store, otherwise the daily bound stops working.
- **Operator / on-call owner:** **PM Lead** (operator). **PM Associate** (backup, covers when the PM Lead is away). Escalation path: PM Lead → PM Associate → revoke the API key. Reached by Slack DM. The backup operates Cortex from the Rollback steps below. RUNBOOK.md covers building Cortex only, so an operating runbook (reading run-output, setting `CORTEX_DISABLED`) still needs to be written before the PM Associate can run it alone.
- **Rollback:** in order, mildest first:
  1. Drop the rung: stop using Cortex's drafts and write the update by hand.
  2. Revert the prompt or version in git, or disable a tool.
  3. Set `CORTEX_DISABLED=1` (halts the next run gracefully).
  4. Revoke the API key (stops everything mid-flight, works from a phone).
- **Monitoring:** reviewed weekly, covering:
  - EV-1, EV-4, EV-5 and EV-6 pass rates (from the offline fixture suite; the signals below come from the run-output files)
  - escalation rate, and the revision-cap rate specifically (the main silent failure)
  - cost per run and the running daily ledger total
  - trust incidents against the severe-incident list in the Trust Ladder

## ROI metrics (beyond adoption & tokens)

| Metric | Target | How it's captured |
|---|---|---|
| Outcome: time to a sendable weekly update | ≤1 hour of PM time (review plus edits), down from a 4-hour manual baseline | PM times the review each week and notes it in the run-output file next to the draft |
| Cost-to-serve: cost per accepted draft | ≤$0.10 per accepted draft ("accepted" = sent with only minor edits) | Spend ledger total divided by the number of drafts marked accepted |
| Trust incidents: severe incidents per window | 0 severe per window, the same as the gate | Incident log, reviewed weekly against the severe-incident list |

## Widen-autonomy decision rule

A lane moves up exactly one rung only when the Trust Ladder eval gate for that rung is met, including its clean incident record (for Assisted → Supervised, both stages). It never skips a rung. Limit: today a lane widens for everyone at once. The segment differences come from the dial table, and per-segment widening would need per-segment tracking, which is a later step.

## Governance & forward strategy

- **Compliance:** Never in a prompt: customer PII and credentials/secrets. CONFIDENTIAL or embargoed roadmap items (Orbit, Pulsar) may be read so they can be reported as excluded, but are never carried into an external or company-wide update, enforced today by critic check 2, which is model-enforced rather than a code bound. Before real connectors, names in pulled activity logs will be removed before the draft step (not built yet).
- **Safety:** Posting or approving a company-wide update stays above the line for everyone, and no publish tool exists in the registry. Tone/commitment calls and any date commitment stay with a human. Kill switch: `CORTEX_DISABLED=1` halts the next run gracefully; revoking the API key stops everything mid-flight.
- **Reliability:** Caps: 8 iterations, 120s timeout, $0.10 per run, $2.00/day, $10/month, revision cap 2, 10-story queue cap. Escalate on stuck: a stop on any bound hands the last draft to the human. If the model is down, retry once, then fail visibly with no draft, and the update is written by hand.
- **Strategy:** Next capability: real connectors (GitHub or Jira for activity, Slack or Notion for past updates) replacing the fixtures, introduced as Assisted on real inputs (the PM Lead reviews every draft) once Stage 1 of the Trust Ladder gate is met. Precondition: the name-removal step from Compliance is built first. Supervised then requires Stage 2: its thresholds and a clean incident record over a window on real inputs.
