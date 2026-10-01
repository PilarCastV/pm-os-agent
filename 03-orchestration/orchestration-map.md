# Orchestration Map: Cortex PM Chief-of-Staff Agent

> Module 3 · Orchestration & Subagents, ★ Deliverable 3
>
> ✅ **What this validates:** nothing advances unchecked, by the end you'll have proven a justified topology, a roster, and a validator with a defined fail action.
>
> Builds on your M2 Loop Spec. Only split one agent into a team when there's a real reason, coordination has a cost.

## 1. Why split? (or why not)

**Cortex splits because it needs an independent critic to validate the draft before it
reaches the user.** That is the only reason that holds. The other three do not:

| Reason | Applies? | Why |
|---|---|---|
| Separation of concerns | No | Pulling, drafting and proposing stories are one coherent job. The only real separation is drafting vs checking, which is the validator reason. |
| Parallelism | No | The run is weekly, takes under a minute and costs about two cents. Nothing waits on anything, and Cortex already batches its five data pulls into one step. |
| **Independent validation** | **Yes** | Cortex cannot grade its own draft. Evidence from M2: the critic caught a draft that included P-VEGA after declaring it excluded, and a weaker critic let a fabricated date ("July 6, 2026") reach the final update. |
| Context-window pressure | No | The fixtures are a few KB and a run uses at most 8 iterations. This would change with real Jira and GitHub volumes, but not today. |

## 2. Topology

**Pattern:** single + subagents

```
[Monday cron]  or  [inbound PM task brief]
        │
        ▼
[Cortex] applies the scope rule, pulls project · activity · past updates ·
         roadmap · norms, drafts the update, proposes a status, queues stories
        │
        ├──► project_not_found ──► HARD STOP, escalate   (enforced in agent.py)
        │
        ▼
[Validator] independent call, stronger model, the five checks
        │
   fail ├──► back to Cortex with reasons ──► max 2 revisions ──► escalate, draft held
        │
   pass ▼
[PM review checkpoint] update + queued stories, held for my approval
        │
        ▼
   nothing posted — there is no publish tool
```

## 3. Roster

| Agent / subagent | Responsibility | Runs which Loop Spec |
|---|---|---|
| **Cortex** (chief-of-staff) | Applies the scope rule, pulls data, drafts the update, proposes a status with evidence, queues stories within the cap | M2 `loop-spec.md`, cron + hook trigger, DONE / ESCALATE exits |
| **Validator** (`critic.py`) | Independently checks the draft against the five rules before the PM sees it | Validation loop: one call in, pass/fail JSON out, no tools, no memory |

No research subagent and no separate GitHub/Jira reader: §1 records why neither is justified yet.

## 4. Communication & hand-offs

- **Cortex → Validator:** the proposed draft plus the source log, every tool call and its
  result as text. A plain in-process Python call (`review()` in `critic.py`), no network
  between them.
- **Validator → Cortex:** strict JSON, `{"verdict": "pass"|"fail", "reasons": [...]}`. On a
  fail the reasons are appended to Cortex's history as a new instruction.
- **Cortex → PM:** the final draft printed to the trace and saved to
  `run-output/status-update-<task>.md`, with the queued stories.
- **No MCP, no A2A.** Both run in one Python process against one client. A protocol would only
  matter if the validator moved out of process.

## 5. The validator

**What the critic checks** (five rules, each checkable against the pulled data):

1. **Grounded** — the update names the correct project and real PR/issue IDs, and every figure
   *and date* traces to pulled activity. A date appearing nowhere in the source data is an
   automatic fail.
2. **Nothing committed or sent** — no post, no ticket created/closed/merged, no ship date
   committed, no launch gate marked, no CONFIDENTIAL item in an external or company-wide update.
3. **Scope reported** — the update ends with a Sources used / Excluded block naming what was
   pulled and what was deliberately left out, with reasons.
4. **Status handled** — the status is marked as a proposal carrying its evidence; where a real
   Sev-1 or `launch_hold` exists, no status is proposed and the go/no-go is escalated instead.
5. **Escalation is valid** — a refusal, or an action a tool rejected (e.g.
   `batch_exceeds_queue_cap`), is a correct outcome, judged only on check 2.

**Fail action: revise.** The draft returns to Cortex with the critic's reasons attached, up to
**2 revisions**. On the third failure the run halts and escalates to me with the last draft held,
unposted. The cap is enforced in `agent.py` (`CORTEX_MAX_REVISIONS`), not left to the model.

**Pass action:** the draft advances to the PM review checkpoint, queued for my approval. It is
never sent: there is no publish tool, so passing the critic cannot post anything.

**Independence:** the critic is a separate model call that never sees Cortex's drafting context,
so it cannot inherit the drafter's blind spots. It deliberately runs on a stronger model than the
drafter (`CORTEX_CRITIC_MODEL`, default `gpt-4o`).

## 6. State: shared vs isolated

**Shared:** the source log (every tool call and its result) and the draft itself. The critic
needs both to check grounding, it cannot verify a figure it cannot see.

**Isolated:** the critic never sees Cortex's system prompt, its reasoning, or its message
history, so it cannot inherit the drafter's blind spots. Cortex never sees the critic's
reasoning either, only the verdict JSON.

**Each critic call is fresh.** The validator does not see its own previous verdicts when
checking a revision. That is deliberate: independence beats consistency here, because a critic
that remembers its last call can entrench a wrong rejection and spend both revisions defending
it. The known cost is the inconsistency observed in M2, where it rejected a draft on one ground
and rejected the revision on a contradictory one.

**Carried from M2 (loop-spec §4):** the standing scope rule persists across runs; the project +
week ledger is deferred; run internals, the source log, draft, iteration and cost counters, are
discarded when the run ends.

## 7. Cost & latency budget

**Extra model calls:** the validator adds exactly **one call per draft attempt**. Worst case is
`CORTEX_MAX_REVISIONS + 1 = 3` critic calls in a run.

**Measured on the same happy-path task (M3):**

| Configuration | Critic calls | Run cost |
|---|---|---|
| Cheap critic (`gpt-4o-mini`), passed first time | 1 | $0.0016 |
| Cheap critic, one revision | 2 | $0.0027 |
| Cheap critic, revision cap hit | 3 | $0.0054 |
| Strong critic (`gpt-4o`), one revision | 2 | $0.0207 |
| Strong critic, three calls (`stale-notes`) | 3 | $0.0298 |
| Strong critic, withheld-source probe (M4) | 3 | **$0.0437** |

**The validator is ~90% of the spend.** The drafter alone costs well under half a cent; the
check costs roughly twenty times the work it checks. That is the price of the independence in
§1, and it is worth paying, because the check is what stands between a fabricated figure and my
leadership update.

**At my cadence**, one project weekly, the worst case is about $1.50 a year; five projects
weekly is under $8. Cost is not the binding constraint at this scale, correctness is.

**Latency:** not precisely measured. Irrelevant on the cron path, where the draft is ready
before my sync; it would matter on the hook path, where someone is waiting on a reply.

**Bound set from this data (forward to M5):** per-run cost cap tightened from $0.50 to
**$0.10**. Loose enough never to trip on legitimate work, tight enough that a runaway halts
quickly. Revision cap stays at 2.

**Margin update (M4).** The cap was chosen as ~3x the then-worst run of $0.0298. The M4
withheld-source probe then cost **$0.0437**, so the real margin is **2.3x**, not 3x. It has
never tripped, but the headroom is thinner than when the bound was set, and a richer fixture
set or a longer brief would narrow it further. Revisit in M5 with the eval numbers.
