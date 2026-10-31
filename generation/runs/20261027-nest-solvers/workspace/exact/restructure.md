# exact restructure
- Flat solvers/exact/* moved to solvers/exact/python/ (all files kept incl. skills/ source of truth moved to solvers/exact/skills/exact/).
- Skill: SKILL.md (shared, one-column table), interfaces/python/README.md + patterns.md (split, ~200 lines), assets/python/*, references/python/exact-api.md, sources.md (Shared + Python), evals unchanged (already "exact").
- Dockerfile COPY solvers/exact/python/run.py; readiness_test.py parents[3]; CONTRACT.md links one level deeper.
- Checks: validate --project, rosetta-mentions, check_integration --static (40 pass), check_assets --interface python 11/11.
- Left: readiness.json paths still say solvers/exact/readiness-result.json (redo readiness); standalone-review.json still in python/ (needs new review, then move to solvers/exact/); image not rebuilt.
