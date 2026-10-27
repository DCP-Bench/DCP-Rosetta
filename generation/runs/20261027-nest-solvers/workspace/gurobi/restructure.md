# gurobi restructure
- solvers/gurobipy_python/ -> solvers/gurobi/python/ (all files kept; id unchanged). Skill solvers/gurobipy_python/skills/gurobipy -> solvers/gurobi/skills/gurobi.
- SKILL.md (117 lines): intro, one-column interface table, Modelling concept, outcome table, parameters/MIPGap, pool strategy, shared issues. interfaces/python.md (143 lines): install, quick start, API tables, status constants, pool reading, python issues. assets/python/*, references/python/encodings.md, sources.md (shared + Python sections), evals renamed to "gurobi".
- Fixed: Dockerfile COPY path, readiness_test.py parents[3], CONTRACT.md relative links.
- Not done: readiness.json/readiness-result paths still name solvers/gurobipy_python/ (write-once record; redo readiness after rebuild); standalone review of the new skill; old standalone-review.json left in python/.
- Checks: validate --project, rosetta-mentions, check_integration --static: 40 passed.
