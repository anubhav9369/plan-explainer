# plan-explainer

Plain-language explanations for inspectable agent plans — Week 1 of the
trustworthy-agentic-ai build (BITS–RMIT PhD project BRJP26100123:
*Building Trustworthy AI Systems through Explainability and Human-in-the-Loop Control*).

An agent plan is only inspectable if a human can read it in a minute and
spot what is risky. This tool renders an `InspectablePlan` (the JSON schema
in [trustworthy-agentic-ai](https://github.com/anubhav9369/trustworthy-agentic-ai))
as Markdown: the goal, every step with its reasoning and failure points,
the assumptions, constraints, and risks — with every permission-gated step
flagged. It also turns the plan into a review checklist: the questions a
human should answer before approving, rejecting, or refining it.

No LLM call — the explanation is deterministic rendering of what the plan
already declares, so it can never invent a justification the plan did not make.

## Usage

```bash
python3 explainer.py examples/summarise-paper-plan.json
python3 explainer.py examples/summarise-paper-plan.json --checklist
```

## Example

`examples/summarise-paper-plan.json` is the Week 1 example plan ("Summarise
this paper and email the summary to me"): 5 steps, 2 of them permission-gated
(confirming the recipient, then sending), decision still `pending`.

## Tests

```bash
python3 -m pytest tests/ -q
# or, stdlib only:
python3 -m unittest discover -s tests -v
```

## Next steps

- Week 2: feed the checklist answers back into the approve / reject / refine loop.
- Week 3: check the rendered constraints against policy before approval.
