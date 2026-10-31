# minizinc restructure
- mv solvers/minizinc_gecode -> solvers/minizinc/minizinc (id minizinc_gecode kept); skill -> solvers/minizinc/skills/minizinc.
- Skill split: SKILL.md (language, modelling, one-sided bounds, CLI statuses, implied constraints, enumeration strategy, shared issues), interfaces/minizinc.md (install, quick start, Python data binding, Python statuses/result reading, enumeration code, Python issues), assets/minizinc/*, sources.md with shared + interface sections, evals renamed.
- Integration fixes: Dockerfile COPY path, readiness_test parents[3], CONTRACT.md relative links.
- Static check 41/41, validate and rosetta-mentions clean. check_assets/skills-ref not run; no rebuild/readiness; old standalone-review.json left in minizinc/minizinc/ (names "minizinc-gecode").
- readiness.json/evidence records still cite solvers/minizinc_gecode/readiness paths (write-once, redo later).
