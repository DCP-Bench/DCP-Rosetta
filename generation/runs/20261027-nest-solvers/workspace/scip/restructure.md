# scip restructure
- mv solvers/scip_python -> solvers/scip/python (all files kept); skills/pyscipopt -> solvers/scip/skills/scip.
- Skill: SKILL.md (shared + 1-column table), interfaces/python.md, assets/python/*, references/python/encodings.md (links fixed), evals renamed "scip", sources.md has Shared + Python sections.
- Dockerfile COPY paths -> solvers/scip/python/; readiness_test.py parents[2] -> parents[3]; CONTRACT.md relative links one level deeper.
- Checks: validate --project, rosetta-mentions, check_integration --static all pass (only warning: pip pin pre-existing).
- Left: readiness.json paths still name solvers/scip_python (write-once, redo readiness); standalone-review.json still in python/ (skill name "pyscipopt"); image not rebuilt.
