# python_mip restructure
- solvers/mip_cbc -> solvers/python_mip/python (id mip_cbc kept); skill solvers/mip_cbc/skills/mip-python -> solvers/python_mip/skills/python-mip.
- SKILL.md: intro, one-column interface table, encodings, enumeration strategy, shared issues, CBC speed tips. interfaces/python.md (146 lines): install, quick start, API, numbers, settings/statuses, enumeration code, python issues, examples. assets -> assets/python/. sources.md and evals renamed.
- Dockerfile COPY path, readiness_test parents[3], CONTRACT.md links fixed.
- Checks: validate --project, rosetta-mentions, check_integration --static all pass (41/41).
- Old standalone-review.json left in solvers/python_mip/python/. check_assets not run (needs image).
