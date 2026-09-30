# Agent Line Map: Cortex PM Chief-of-Staff Agent

> Module 1 · The Agent Line
>
> ✅ **What this validates:** every risky action has a clear owner, by the end you'll have proven an above/below-the-line map with HITL checkpoints, scored on reversibility, blast radius, and measurability.

## The workflow, decision by decision

List every discrete decision or action in your agent's workflow, then score each one and place it **above** the line (a human owns it) or **below** (the agent owns it). Borderline calls get an HITL checkpoint.

| Decision / action | Reversibility (H/M/L) | Blast radius (H/M/L) | Measurability (H/M/L) | Above / Below | HITL? |
|---|---|---|---|---|---|
| Pull project state + recent activity | H | L | H | Below | — |
| Decide relevant context | H | L | L | HITL | scope pre-approved; draft lists exclusions |
| Draft the weekly leadership status update | H | L | M | Below | spot-check at review |
| Decide tone / commitment level | M | H | M | HITL | proposed with evidence; contested calls escalated |
| Flag at-risk / escalation | H | L | M | Below | spot-check at review |
| Choose what to escalate | H | L | H | Below | — |
| Propose next sprint's stories (within cap) | H | L | M | Below | required before anything enters the tracker |
| Post the update / approve a company-wide one | L | H | M | Above | required |

## Agent anatomy (sketch)

- **Model:** `gpt-4o-mini` as the default drafter, cheap and fast. The **critic runs on a
  stronger model** (`gpt-4o`, via `CORTEX_CRITIC_MODEL`), implemented in M2 after the cheap
  validator misquoted the team norms, missed a fabricated date, and then rejected correct
  drafts while restating the very rule it was misapplying. The drafter stays cheap because
  my review catches wording; it is the independent check that has to be right. A full run
  went from ≈ $0.005 to ≈ $0.02, well inside the cost cap.
- **Tools:** project lookup · recent engineering activity · past-update search · roadmap
  (confidential items flagged) · team norms · capped story proposal. *Absent by design:*
  no publish, no ticket create/close/merge, no date commit, no launch-gate tool.
- **Memory:** persists across runs, the team norms, roadmap, past updates, decision log,
  and the standing scope rule behind my context checkpoint. Per-run only, the source log
  and the draft; nothing else carries between runs today.
- **Loop:** placeholder, defined in M2 loop-spec.md
- **Bounds:** placeholder, defined in M5 bounds-and-evals.md
- **Evals:** placeholder, defined in M5 bounds-and-evals.md

## The golden rule, applied

1. **Pull project state + activity, below.** Easy to reverse, reads without changing anything, and I can tell whether the projects and activity exist. *Deciding axis: measurability.*
2. **Decide relevant context, HITL.** Easy to reverse and it only affects the draft, but I can't see what it chose to leave out, so I set the scope in advance and require the draft to report its exclusions. *Deciding axis: measurability.*
3. **Draft the update, below, spot-checked.** Easy to reverse and held for review, but a plausible fabrication can slip past a quick read. *Deciding axis: reversibility.*
4. **Decide tone / commitment, HITL.** Reversible while it is still a draft, but once leadership acts on a date or a status call the damage is wide, and I can't rely on AI here since it may not have all the day-to-day context. So Cortex proposes a status with the evidence behind it and I confirm or override it; on contested calls (open Sev-1, `launch_hold`) it proposes nothing and escalates the go/no-go. *Deciding axis: blast radius.*
5. **Flag at-risk / escalation, below, spot-checked.** Easy to reverse with a low blast radius, and I can check the risks it surfaced before anything is released, though not the ones it stayed silent about. *Deciding axis: blast radius.*
6. **Choose what to escalate, below.** Reversible, and reliable after setting the rules to escalate; an escalation is loud, the run halts and states why. *Deciding axis: reversibility.*
7. **Propose next sprint's stories, below, approval required.** A queue creates nothing in the tracker, the cap is enforced outside the model, and I read every story before approving. *Deciding axis: reversibility.*
8. **Post / approve company-wide, above.** Can't be undone once sent, and it reaches everyone who reads it. *Deciding axis: reversibility.*

## Hardest call

**Choosing what to escalate (action 6).** I first placed it above the line, using the same
reasoning as tone and commitment: Cortex may not have all the day-to-day context. Instead of
settling it I asked for concrete cases, a prompt-injection attempt, a demand for a firm GA
date, a story batch over the cap, and a project that doesn't exist. Those moved me: it's
reversible, and reliable after setting the rules to escalate. **Deciding axis: reversibility.**
