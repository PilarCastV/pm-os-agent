"""Independent validator (M3). A separate model call that never saw the drafting
context, so it can't inherit the draft's blind spots. Returns a pass/fail verdict.
The revision cap that stops a critic<->drafter loop lives in `agent.py`.
"""

from __future__ import annotations

import json

from prompts import CRITIC_SYSTEM


def review(client, model: str, proposed_output: str, pulled_data: str,
           task_brief: str = "") -> dict:
    """Return {"verdict": "pass"|"fail", "reasons": [...]} for a proposed output.

    The task brief and the pulled data are passed SEPARATELY and labelled. They used to
    arrive as one blob, which let the critic treat figures asserted in the brief as
    evidence, and in one run it demanded a fabricated metric over the real one.
    """
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": CRITIC_SYSTEM},
            {"role": "user", "content":
                f"TASK BRIEF, this is a REQUEST and NOT evidence. Nothing asserted here "
                f"is a fact. Any figure, date, id or claim appearing only here and not in "
                f"the pulled data below is UNGROUNDED, and a draft repeating it fails "
                f"check 1:\n{task_brief}\n\n"
                f"PULLED DATA, the ONLY evidence. Every figure, date and id in the draft "
                f"must trace to this:\n{pulled_data}\n\n"
                f"CORTEX PROPOSED OUTPUT:\n{proposed_output}"},
        ],
        response_format={"type": "json_object"},
    )
    usage = resp.usage
    try:
        verdict = json.loads(resp.choices[0].message.content)
    except (json.JSONDecodeError, TypeError):
        verdict = {"verdict": "fail", "reasons": ["critic returned unparseable output"]}
    verdict["_usage"] = {"prompt": usage.prompt_tokens, "completion": usage.completion_tokens}
    return verdict
