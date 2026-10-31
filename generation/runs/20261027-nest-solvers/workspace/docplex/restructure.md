# docplex restructure
- Integration docplex_cplex moved to solvers/docplex/python/ (id unchanged); old standalone-review.json moved with it (new review pending).
- Skill now solvers/docplex/skills/docplex/: shared SKILL.md (interface table, solving outcomes, all-solutions strategy, 2 shared issues), interfaces/python/{README,program-shape,speed}.md, assets/python/, references/python/encodings.md, sources.md (shared + python), evals unchanged (already "docplex").
- Fixed Dockerfile COPY, readiness_test parents[3], CONTRACT.md links.
- Checks: validate --project, rosetta-mentions, check_integration --static all pass (40/0 failed).
- Not done: image rebuild, readiness redo, new standalone review, check_assets.
- generated_models/*/record.json carry the old skill path (history, untouched).
