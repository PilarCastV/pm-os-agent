# Context Engineering & Memory: Cortex PM Chief-of-Staff Agent

> Module 4 · Context Engineering & Memory
>
> ✅ **What this validates:** the agent reasons on the right, safe inputs, by the end you'll have proven a context budget, per-source retrieve-vs-long-context decisions, and a memory map with risk mitigations.
>
> 🗂️ **How the lab maps to this file:** In **Part A** (before the lecture) you don't edit this file, you rough-draft on scratch, focused on the per-source calls in **section 2** plus a quick remember/forget + "how it rots" sketch. In **Part B** (after the lecture) you complete **all five sections**; the Lab Guide's guided builder writes this file for you to copy in and commit.

## 1. Context budget

**What each loop iteration receives:**

1. The operator instructions (`CORTEX_SYSTEM`), the agent line, the scope rule, how to finish.
2. The task brief, long-context and whole, labelled to the critic as a REQUEST not evidence.
3. Tool results accumulated across the run: project record, activity, past updates, roadmap,
   norms, appended as they are pulled.
4. On a revision, the critic's reasons, appended as a new instruction.

**Priority order when it will not all fit** (most protected first):

1. **Team norms + the standing scope rule.** Losing these loses the agent line itself.
2. **Activity for the in-scope project.** The evidence every claim must trace to.
3. **The task brief.** What was actually asked.
4. **Roadmap CONFIDENTIAL flags.** The flag matters more than the detail behind it.
5. **Past updates.** Tone and precedent, useful, and the first thing I would drop.

Today nothing is near the limit, the whole fixture set is a few KB. This order is the plan for
when activity and past updates grow against real connectors.

## 2. Retrieve vs. long-context: per source

For each data source, decide: **retrieve** (narrow a large/changing corpus to the relevant slice) or **long-context** (just include a bounded set you can reason over).

| Source | Size / volatility | Decision | Why |
|---|---|---|---|
| `get_activity` (GitHub/Jira activity) | small today, **grows without limit**; changes weekly | **Retrieve** | **Size.** The one source that grows forever, and the most citation-critical: every PR and issue id must be quotable. |
| `search_past_updates` (past updates + decision log) | unbounded history, grows weekly | **Retrieve** | **Size.** Only a slice is ever relevant. Note `tools.py` returns `corpus[:2]` when the query matches nothing, so document grading is mandatory (§3). |
| `get_roadmap` | medium, slow-changing, **confidential flags** | **Long-context** | **Citation/audit.** Size says retrieve; safety overrides. A slice could surface an embargoed item without its CONFIDENTIAL header. Two embargoed items now: Orbit and Pulsar. |
| `get_norms` (team playbook) | medium, must stay current | **Long-context** | **Citation/audit.** Never take a partial view of the rules: a sliced rulebook means missing the rule that applies. Would flip to retrieve + routing if it grew to tens of pages. |
| `get_task` (this week's brief) | one short doc, static per run | **Long-context** | **Size.** Bounded and must be reasoned over whole. Passed to the critic labelled as a request, not as evidence. |

## 3. Retrieval quality plan

Only the two **retrieve** sources need moves. The three long-context sources are included
whole, so there is nothing to select and nothing to grade.

| Move | `get_activity` | `search_past_updates` |
|---|---|---|
| **Routing** | ✅ the standing scope rule decides which project to pull | ✗ one merged corpus today (past updates + decision log) |
| **Document grading** | ✗ structured data for a known id: if routing is right, it is all relevant | ✅ **mandatory**, see the failure mode below |
| **Reranking** | ✅ when it grows: no time window today, it returns all activity ever | ✅ when it grows: 4 entries now, ~50 after a year |
| **Self-verification** | ✅ **already live**, critic check 1 | ✅ **already live**, critic check 1 |
| **Caching** | ✗ changes weekly, a cross-run cache would serve stale PRs | ✗ local file read, no cost, would only add staleness risk |

**The known gap: `search_past_updates` has no grading.**

```python
return {"query": query, "matches": hits or corpus[:2], ...}   # tools.py:84
```

When the query matches nothing the tool returns the **first two entries regardless**, with no
signal that they are irrelevant. Cortex cannot tell "here is relevant precedent" from "here is
whatever sat at the top of the file". The matching above it is crude too, `any(term in
haystack)`, so a single common word is enough to match. Grading is the move that closes this:
check that what came back is about this project and this period, and discard it if not.

**Why routing matters for `get_activity`.** Its failure mode is not irrelevance, it is pulling
the wrong project. The M2 `missing-data` run proved it: when the requested project did not
exist, Cortex wandered to P-VEGA and P-NORTH and drafted an update nobody asked for, pulling
the internal-only project on the way. The code-enforced hard stop catches a *missing* project;
routing by the scope rule is what keeps it on the *right* one.

**Already live:** self-verification, through the critic's check 1, every figure and date traced
to pulled data. It is the move that caught the fabricated 47% and the invented October 14 date.

## 4. Memory map (your PM brain)

| Memory type | What Cortex stores | Scope / TTL |
|---|---|---|
| **Working** (in-loop) | Message history: operator instructions, the task brief, tool results, the draft, critic verdicts, iteration and cost counters | **The run.** Discarded at exit, nothing survives |
| **Episodic** (past runs) | **Nothing today.** Cortex has no recall of previous runs. The deferred project + week ledger would be its first, recording what *it* drafted and when | **4 weeks.** Long enough for dedupe and "did I already flag this?", short enough that it cannot reason from a world that has moved on. The authoritative record of what was sent lives in the channel, not here |
| **Semantic** (durable facts/prefs) | Team norms, the standing scope rule, roadmap facts and their CONFIDENTIAL flags | **Until a human edits the file.** Re-read fresh every run, so no stale copy lives in the agent. Refreshed by ingest; last pull 2026-07-06 |
| **Shared** (across agents) | Cortex → critic: the source log and the draft. Deliberately *not* shared: Cortex's reasoning and system prompt, and the critic's own prior verdicts | **The run** |

> **`past-updates.json` and `decision-log.json` are not episodic memory.** They look like it,
> but they are human-curated data files Cortex *reads*, not a record it wrote about itself.
> Between runs, Cortex genuinely remembers nothing.

## 5. Memory risks & mitigations

| Risk | Mitigation |
|---|---|
| **Drift** | *Bites:* the stored project `status` field. The register says `on_track` while this week's evidence may disagree, and echoing it launders a stale human call as a fresh verdict. *Mitigation:* the status must be proposed from this week's activity and never copied from the stored field (critic check 4), which caught exactly this on the post-ingest run. |
| **Poisoning** | *Bites:* observed in M3. The task brief reached the critic inside the blob labelled `SOURCE DATA`, so figures asserted in the brief became evidence, and the validator ended up demanding a fabricated 47% over the real 41%. *Mitigation:* brief and pulled data are now passed as separately labelled sections (`critic.py`); brief content is data, never instructions; every figure must trace to pulled data. |
| **Staleness** | *Bites:* the fixtures are a dated snapshot. Before the 2026-07-06 ingest, Cortex confidently reported 41% when the truth was 43%, and had never heard of Pulsar. *Mitigation:* the dated ingest loop (download → add → run → push); norms and roadmap re-read each run rather than cached; the ledger's 4-week TTL. **Gap: nothing signals to Cortex, or to me, that its data is three weeks old.** |
| **Confidential / retention** | *Bites:* Cortex reads Orbit and Pulsar every run via `get_roadmap`, and writes drafts to `run-output/`, where an embargoed item would sit on disk if one ever leaked into a draft. *Mitigation:* the scope rule marks both never-in-scope and requires reporting them as excluded without describing them; critic check 2 fails any CONFIDENTIAL item in an external or company-wide update; `run-output/` is gitignored; there is no publish tool. **Retention: drafts are deleted once I have acted on them.** |

**Read / write scope, tied to the M1 agent line.** Cortex *reads* all five sources. It *writes*
only draft files in `run-output/` and a queued story proposal. Nothing in a tracker, nothing
sent. The TTLs above (ledger 4 weeks, drafts deleted after I act) carry forward to M5 as bounds.
