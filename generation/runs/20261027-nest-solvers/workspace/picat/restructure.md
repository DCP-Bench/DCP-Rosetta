# picat restructure

- Moved flat solvers/picat/* into solvers/picat/picat/ (all files, incl. readiness records, standalone-review.json left in place) and the skill to solvers/picat/skills/picat/.
- Skill: SKILL.md (shared: intro, interface table, Modelling, Solving outcomes, cp vs sat, all-optimal strategy, solver-level issues, further reading); interfaces/picat.md (install, quick start, calls, errors, enumeration, Writing Picat correctly, Common issues); assets/picat/<examples>; sources.md and evals unchanged (names already "picat"); metadata.interfaces added.
- Dockerfile COPY paths -> solvers/picat/picat/; readiness_test.py parents[2] -> parents[3]; CONTRACT.md links one level deeper.
- Checks: validate --project, rosetta-mentions, check_integration picat --static: all pass (40 passed). Did not rebuild or redo readiness.
- readiness.json still has paths "solvers/picat/readiness-result.json": redo at readiness.
