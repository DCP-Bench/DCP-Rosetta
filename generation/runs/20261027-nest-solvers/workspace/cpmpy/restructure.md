# cpmpy restructure
- mv solvers/cpmpy_python -> solvers/cpmpy/python (id cpmpy_python unchanged); skill moved to solvers/cpmpy/skills/cpmpy (name cpmpy).
- SKILL.md (shared: statuses, enumeration rules, shared issues, interface table), interfaces/python.md (install, quick start, API, scheduling, code for enumeration, python issues), assets/python/*, references/python/api.md, sources.md (shared + Python section), evals renamed.
- Dockerfile COPY path, readiness_test.py parents[3], CONTRACT.md relative links fixed.
- Checks: validate --project, rosetta-mentions, check_integration --static: all pass (41/0 failures).
- Not done: standalone-review.json left at solvers/cpmpy/python/ (needs a new review); check_assets not run; readiness records (contain old paths) and image not redone. interfaces/python.md is ~209 lines.
