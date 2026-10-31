# pycsp3 restructure

- solvers/pycsp3_ace/ -> solvers/pycsp3/python/ (id pycsp3_ace unchanged); skill solvers/pycsp3_ace/skills/pycsp3-ace -> solvers/pycsp3/skills/pycsp3.
- SKILL.md (shared: intro, interface table, statuses, all-solutions strategy, lessons, solver-side issues), interfaces/python.md (install, quick start, API, data, solving, enumeration calls, syntax issues; 188 lines), assets/python/, references/python/, sources.md (shared + python), evals renamed.
- Dockerfile COPY paths, readiness_test parents[3], CONTRACT.md relative links fixed.
- Checks: validate --project, rosetta-mentions, check_integration --static (41 passed).
- Left: old standalone-review.json (skill "pycsp3-ace") and readiness records in solvers/pycsp3/python/; new review, rebuild, readiness, check_assets not done.
