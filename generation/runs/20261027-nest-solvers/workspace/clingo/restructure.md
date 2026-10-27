# clingo restructure
- mv solvers/clingo_asp -> solvers/clingo/asp (id clingo_asp unchanged); skill solvers/clingo_asp/skills/clingo-asp -> solvers/clingo/skills/clingo.
- SKILL.md split: language/aggregates/outcome/optimisation/enumeration concepts + common issues shared; install, quick start, Python API, optN calls, scheduling, python issues, examples table in interfaces/asp.md (159 lines). Examples moved to assets/asp/.
- sources.md headed, evals renamed to "clingo". Old standalone-review.json left in solvers/clingo/asp/.
- Dockerfile COPY path, readiness_test parents[3], CONTRACT links fixed. Readiness records' evidence paths (solvers/clingo_asp/...) left as-is (write-once); redo readiness later.
- Checks: validate, rosetta-mentions, check_integration --static: all pass (40).
