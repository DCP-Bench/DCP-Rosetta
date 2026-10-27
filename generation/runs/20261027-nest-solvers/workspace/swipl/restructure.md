# swipl restructure
- solvers/swipl_clpfd/ -> solvers/swipl/prolog/ (id swipl_clpfd kept); skill -> solvers/swipl/skills/swipl/.
- SKILL.md (shared: intro, one-column table, search/optimisation, all solutions, scheduling), interfaces/prolog.md (241 lines, rest of old text), assets/prolog/, sources.md split, evals renamed.
- Dockerfile COPY paths, readiness_test parents[3], CONTRACT.md links fixed. old standalone-review.json left in solvers/swipl/prolog/.
- Checks: validate --project, rosetta-mentions, check_integration --static: all pass. Not rebuilt, readiness not redone.
