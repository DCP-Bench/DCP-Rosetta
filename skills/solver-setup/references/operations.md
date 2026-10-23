# Operations: evidence and skill changes

Recording a setup attempt, and changing a skill after a failure. Run the helpers from the repository root with its Python environment; syntax and schemas are in `generation/AGENTS.md`.

## Recording an attempt

1. **Open the attempt** before writing any file:
   ```bash
   python -m generation.manage setup-attempt --run RUN --solver ID --skill skills/solver-setup
   ```
   It freezes the setup skill (later edits do not apply to this attempt) and records the agent named in the run configuration. Use the path it returns.
2. **Keep the complete stdout and stderr** of every build and test, failed ones included,
   under `generation/runs/RUN/setup/ID/ATTEMPT/`.
3. **Close it** with an event pointing at the evidence:
   ```bash
   python -m generation.manage event --run RUN --kind setup_finished \
       --data '{"solver_id":"ID","evidence":"PATH"}'
   ```
   The kind is `setup_finished`, `setup_blocked` or `interrupted`.

## After a failure: what to fix

Diagnose first: a wrong runner gets a code repair with a regression test; a wrong solver skill or a misleading setup procedure gets a skill change (below). Not every failure is a skill bug: change instructions only for a lesson that holds beyond this case.

## Changing a skill

1. Record the failure, the evidence for its cause, the affected skill and a reproducer.
2. Copy the canonical bundle to a candidate with the same directory name; edit that.
3. Add a behavioural regression scenario, with its acceptance checks outside the 
   candidate so the edit cannot change how it is judged.
4. Validate format, links, `sources.md` and eval schema:
   `python -m generation.skills validate <candidate> --project`.
5. Propose, then check old and candidate bundles alike:
   ```bash
   python -m generation.skills propose --run RUN --skill <skill> --candidate <candidate> --evidence "<cause and evidence path>"
   python -m generation.skills check PROPOSAL_PATH --checks trusted-checks.json
   ```
   `trusted-checks.json` lists your own commands; `{skill}` becomes each bundle's path:
   ```json
   [{"argv": ["python", "tests/my_skill_regression.py", "{skill}"], "timeout": 60}]
   ```
6. Apply only a proposal that passed, unchanged: `python -m generation.skills apply
   PROPOSAL_PATH`. A rejected or untested one stays pending; record that with an event.

A passing check proves that check, not a general improvement. A behavioural scenario needs an agent that executes it and an assessment of the evidence; neither a format validator nor reading the scenario counts as "passed". Keep results outside the skill bundle. The helpers log `skill_proposed`, `skill_checked` and `skill_applied` themselves. A change takes effect from the next attempt, never retroactively.
