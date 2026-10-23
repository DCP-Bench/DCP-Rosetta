# Standalone review

A solver skill must work outside this repository. `python -m generation.skills
rosetta-mentions <skill>` catches project names; this review catches a skill that teaches
this benchmark's way of submitting a model instead of the solver's own use. A release
needs a clean review (`python -m generation.release publish ... --review FILE`).

## Running it

1. **Take the digest** of what will be released. It covers git-tracked files only, so
   `git add` new files first (it warns about untracked ones).
   ```bash
   python -m generation.release digest <solver_id>   # prints "<skill> sha256:..."
   ```
2. **Give a fresh agent only the skill folder and this file**, not `CONTRACT.md`,
   `run.py` or an older skill: a reviewer who knows the harness reads it into the text.
   Without a fresh agent, review it yourself as `self`.
3. **On findings**, fix the skill, take a new digest and review again: a review covers
   exactly the digest it names.

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

## Output

Write one JSON object to a file **outside** the skill folder (inside, it changes the
digest):

```json
{
  "skill": "<skill name>",
  "source_digest": "<the digest from step 1>",
  "reviewer": "<agent and model, or 'self'>",
  "verdict": "standalone",
  "findings": []
}
```

`verdict` is `standalone` only with no findings, else `leaks`. Each finding:

```json
{"file": "SKILL.md", "line": 42, "quote": "<the text>", "category": "<a category above>", "why": "<one sentence>"}
```
