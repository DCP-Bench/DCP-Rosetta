# z3 restructure
- solvers/z3_python/ -> solvers/z3/python/ (id z3_python kept); old folder removed after diff of readiness/.
- Skill solvers/z3/skills/z3/: SKILL.md (intro, one-column table, solving outcomes, enumeration strategy, further reading), interfaces/python.md (rest, moved), assets/python/, evals renamed, sources.md split.
- Dockerfile COPY path, readiness_test.py parents[3], CONTRACT.md links fixed.
- check_integration --static: 40 passed; validate and rosetta-mentions clean.
- standalone-review.json left in solvers/z3/python/ (no new review).
- Outside ref: solvers/SKILLS.md line 29 (z3-python tree entry).
