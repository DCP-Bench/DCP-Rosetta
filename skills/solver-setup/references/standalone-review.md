# Standalone review

A solver skill must work outside this repository. `python -m generation.skills
rosetta-mentions <skill>` catches project names; this review catches a skill that teaches
this benchmark's way of submitting a model instead of the solver's own use.

## Running it

1. **Give a fresh agent only the skill folder and this file**, not `CONTRACT.md`,
   `run.py` or an older skill: a reviewer who knows the harness reads it into the text.
   Without a fresh agent, review it yourself as `self`.
2. **On findings**, fix the skill and review again, until a review finds nothing.

## What counts as a leak

Read every file except `sources.md` and `evals/` (`rosetta-mentions` scans those).
Report a line that only makes sense to someone submitting a model to a benchmark runner:

| Category | Examples |
|---|---|
| `harness` | A model written as a function or predicate that something else calls (`build(instance)` returning a model and an outputs dictionary, `model/4` for a driver, `Build(json, builder, outputs)`), instead of a program that solves and prints |
| `runner` | Statements about "the runner", "the evaluator", "the driver", "the harness": what it proves, forces, enumerates, rejects or reports |
| `protocol` | Output dictionaries keyed by declared names for someone else to read, JSONL solution records, status strings such as `limit`, `complete`, `execution_error`, `invalid_output` |
| `benchmark` | Advice that only fits the benchmark: checking every instance, instance counts, declared outputs, references, warnings against hardcoded answers |
| `environment` | Facts about one particular container or test setup presented as the solver's: image names, `/opt/...` paths in that image, "inside the image" |

Not a leak: the solver's own API, statuses and parameters; reading a data file in a
program the user runs; enumeration in the user's own loop; timings; generic install
advice (containers, `PATH`, no network); a comment stating the problem atop a program
and one in the problem's words before each block of constraints.

## Shared claims

When the skill has `interfaces/`, also report under category `interface` any statement in
`SKILL.md` that one interface file or the interface table contradicts: a constraint,
option or status presented as general that a binding lacks or names differently. The
interface table is the only place where bindings may differ.

## Output

Write one JSON object to `solvers/<solver>/standalone-review.json` (the folder holding
`skills/dcp-<name>/`), outside the skill folder. It covers every interface:

```json
{
  "skill": "<skill name>",
  "reviewer": "<agent and model, or 'self'>",
  "verdict": "standalone",
  "findings": []
}
```

`verdict` is `standalone` only with no findings, else `leaks`. Each finding:

```json
{"file": "SKILL.md", "line": 42, "quote": "<the text>", "category": "<a category above>", "why": "<one sentence>"}
```
