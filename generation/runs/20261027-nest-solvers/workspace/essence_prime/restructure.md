# essence_prime restructure
- mv solvers/essence_prime_minion -> solvers/essence_prime/essence_prime; skill moved to solvers/essence_prime/skills/essence-prime.
- SKILL.md split: shared (Modelling rules, Pitfalls, Search, language-level issues, further reading) vs interfaces/essence_prime.md (Install, Quick start, File shape, Run, Objective and enumeration, CLI issues). Assets -> assets/essence_prime/, language.md -> references/essence_prime/, sources.md split, metadata.interfaces added.
- Fixed Dockerfile COPY, readiness_test parents[3], CONTRACT.md links.
- readiness.json/readiness-report.json still carry old paths (record not redone). Old standalone-review.json left inside integration folder.
- Checks: validate --project, rosetta-mentions, check_integration --static: all pass. No build, no asset re-run.
