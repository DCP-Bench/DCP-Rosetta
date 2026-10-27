# pysat restructure
- Moved flat integration files into solvers/pysat/python/ (skill stays at solvers/pysat/skills/pysat/). old standalone-review.json left in python/.
- Skill: SKILL.md (shared: idea, interface table, outcomes, enumeration strategy, 2 shared issues); interfaces/python/README.md + scheduling.md (rest of old text); assets/python/, references/python/; sources.md split; evals unchanged (already "pysat").
- Fixed Dockerfile COPY, readiness_test parents[3], CONTRACT.md links.
- readiness.json/readiness-result paths inside records still say solvers/pysat/readiness-result.json (record is write-once; redo readiness).
- Checks: validate, rosetta-mentions, check_integration --static: 40 passed.
