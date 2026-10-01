# Screenshots for prototype.md

Real terminal captures of Cortex running, one per required row. Transcripts of the same runs
are embedded in `../prototype.md`; these images are the visual evidence.

| File | Shows | Command |
|---|---|---|
| `01-happy-hitl.png` | HITL checkpoint + the drafted update, nothing posted | `python agent.py` |
| `02-critic-rejects.png` | The critic failing a draft built on ungrounded claims | `python agent.py stale-notes` |
| `03a-grounded.png` | The draft citing #820 / #823 / 43%, exclusions reported | same run as 01 |
| `03b-withheld-source.png` | `get_activity` withheld, the substitution caught | `CORTEX_WITHHOLD=get_activity python agent.py` |
| `04-jailbreak-refused.png` | Injection refused and escalated, nothing leaked | `python agent.py jailbreak` |
| `05-bound-trip.png` | The iteration cap halting a run with a good draft | `CORTEX_MAX_ITERATIONS=2 python agent.py happy` |
