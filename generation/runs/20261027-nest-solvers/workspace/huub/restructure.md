# huub restructure
- solvers/huub_rust -> solvers/huub/rust (id huub_rust unchanged); skill solvers/huub_rust/skills/huub-rust -> solvers/huub/skills/huub (name huub).
- SKILL.md: intro, interface table, unavailable constraints, 3 solver-level issue rows (2-term eq hang, memory, no_overlap zero-size). Rest (install, quick start, modelling, solving, other issues) in interfaces/rust.md (164 lines). Examples in assets/rust/, links fixed. evals renamed, sources.md split.
- Dockerfile COPY paths, readiness_test.py parents[3], CONTRACT.md links fixed. old standalone-review.json left in solvers/huub/rust/.
- Checks: validate --project, rosetta-mentions, check_integration --static all pass. No rebuild, no readiness redo, no check_assets run.
