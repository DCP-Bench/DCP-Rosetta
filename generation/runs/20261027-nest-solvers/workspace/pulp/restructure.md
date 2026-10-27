# pulp restructure
- Moved solvers/pulp_cbc/* (Dockerfile, run.py, readiness*, CONTRACT.md, metadata.json, standalone-review.json) to solvers/pulp/python/ (id pulp_cbc unchanged); assets to solvers/pulp/skills/pulp/assets/python/; evals renamed to "pulp".
- New SKILL.md (shared: linear encodings, status meanings, enumeration strategy, shared issues), interfaces/python.md (install, API, solving, issues), sources.md (python section).
- Fixed: Dockerfile COPY, readiness_test parents[3], CONTRACT.md links.
- Checks: validate --project, rosetta-mentions, check_integration --static all pass (40/0).
- Old standalone-review.json left in solvers/pulp/python/; new review needed. Old empty skeleton solvers/pulp_cbc/skills/pulp-cbc/{SKILL.md,sources.md} left for the coordinator to remove.
