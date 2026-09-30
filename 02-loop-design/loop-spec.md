# Loop Spec: Cortex PM Chief-of-Staff Agent

> Module 2 · Loop Engineering, ★ Deliverable 2
>
> ✅ **What this validates:** the agent knows when to run and when to stop, by the end you'll have proven a one-page Loop Spec with a trigger, a definition of "done," and explicit stop conditions.
>
> Your one-page blueprint for how the work you handed to the agent (M1) actually *runs*.
> An agent is just a prompt that fires itself, this spec says when it fires, what "done" means, and what it needs to do the job. Living document; refine as the course progresses.

## 1. Trigger & loop type

**Chosen type:** cron (primary) + hook (secondary)

Monday morning, early enough that the draft is waiting before my leadership sync, is the
primary trigger: the weekly leadership update is a calendar artifact, so a clock owns it.
A hook fires it as well when my product lead sends a task brief mid-week, which is the case
the happy-path fixture models. **Heartbeat, ruled out:** nothing needs reacting to between
weekly cycles, so it would spend money to discover there is no news. **Goal, ruled out:**
a human makes the final status call, so Cortex cannot validate its own finish.

**Dedupe / idempotency:** the artifact is identified by project + week. A second trigger for
a week that already has a draft updates that draft rather than creating a second one, which
covers both a hook firing twice and Monday's cron landing after a mid-week request.

## 2. Goal / definition of done

The loop is responsible for one artifact: this week's leadership status update for a
project, drafted and held for me.

**Done** = a draft built from my pre-approved scope, grounded in real pulled activity, that
reports what it used **and** what it deliberately left out, with risks flagged, next-sprint
stories queued for approval, and nothing sent or committed.

The draft carries a **proposed** red/yellow/green status, clearly marked as a proposal and
showing the evidence behind it, which I confirm or override. It is reasoned from this week's
activity, never copied from the project record's stored `status` field. Where the call is
contested, an open Sev-1 or a `launch_hold`, Cortex proposes nothing and escalates the
go/no-go to me, so it only ever anchors me where the evidence is unambiguous.

## 3. Stop conditions

| Condition | What it looks like | What happens |
|---|---|---|
| **Success** | Draft written from in-scope data, exclusions reported, risks flagged, stories queued, status line left for me | Critic returns `pass`; `propose_stories` returns `queued_for_approval`; draft saved to `run-output/` → HITL checkpoint, nothing posted |
| **Stuck / give up** | Cannot get the data, or cannot converge | `get_project` returns `project_not_found`; a claim cannot be traced to pulled data; critic returns `fail` twice (revision cap 2); 8 iterations reached; cost ≥ $0.50 → halt, log, hand over the last draft held |
| **Escalate to human** | A decision that is mine | Unconfirmed date demanded · open Sev-1 or `launch_hold` · `propose_stories` returns `batch_exceeds_queue_cap` · a CONFIDENTIAL item would appear · injection attempt in the brief · something relevant falls outside my pre-approved scope → `ESCALATE`, draft held, nothing posted |

## 4. State

**Persists across runs:** the standing scope rule (which projects and sources are in scope),
and a record of which project + week drafts already exist, required by the dedupe rule in §1.
The team norms, roadmap, past updates and decision log are read fresh each run rather than
carried in memory.

**Per-run only:** the source log, the draft, the critic's verdict, and the iteration and cost
counters, all discarded when the run ends.

**Scope boundary:** confidential items (Orbit) may be read but never carried into an external
or company-wide update; no cross-project leakage.

Note: the standing scope rule is implemented in `fixtures/team-norms.md` and read each run.
The project + week ledger is **deferred**: it needs memory that survives between runs, which
the build does not have yet. Until it exists, the dedupe rule in §1 is a design commitment
rather than an enforced one.

## 5. The five things a loop can lean on

_`state` is always-on. `connectors` only if you already have one wired (e.g. a Jira key or Google MCP), otherwise just note it as a plan. `skills`, `subagents`, `work tree` scale with autonomy; "not needed yet, because…" is a valid answer._

| Component | For Cortex |
|---|---|
| **Work tree** (isolated workspace per run, a git worktree) | Not needed yet: Cortex edits no code and writes one output file, and runs are weekly and sequential, so there is nothing to isolate. |
| **Skills** (reusable capabilities) | Not needed yet: the update format is a single prompt. If the house format hardens, or a second artifact type appears, it becomes one. |
| **Plugins / connectors** (tools & access, optional if you don't have one yet) | None wired; the build reads JSON fixtures in `00-build/fixtures/`. Planned: GitHub or Jira for activity, Slack or Notion for past updates, calendar for the sync time. |
| **Subagents** (independent check when the loop can't grade itself) | Already present: `critic.py` is an independent validator that never saw the drafting context, and it deliberately runs on a **stronger model than the drafter** (`CORTEX_CRITIC_MODEL`, default `gpt-4o`) because the check is the part that has to be right. Detail deferred to M3 orchestration-map.md. |
| **State tracking** | As §4: the standing scope rule and the project + week draft ledger persist; run internals are discarded. |

> Context plan (M4) and the hand-off to bounds & evals (M5) come in later modules, you'll add them to their own deliverables then, not here.

## Link to live loop

`00-build/agent.py` (loop + bounds) · `00-build/prompts.py` (definition of done, stop
conditions) · `00-build/fixtures/team-norms.md` (the standing scope rule)
