# idp_z3 restructure
- Moved flat integration files (Dockerfile, run.py, readiness_test.py, CONTRACT.md, metadata.json, readiness*, standalone-review.json) to solvers/idp_z3/idp/. Skill stays at solvers/idp_z3/skills/idp-z3/.
- Dockerfile COPY -> solvers/idp_z3/idp/run.py; readiness_test.py parents[2] -> parents[3]; CONTRACT.md links gain one `../`.
- Skill: SKILL.md (intro, interface table, Knowledge base, FO(.) syntax, further reading), interfaces/idp.md (install, quick start, solving, all solutions, common issues, example table), assets/idp/*, references/gotchas.md (shared), references/idp/engine.md, sources.md (note on single interface added, not split).
- standalone-review.json left in idp/ (needs new review). Old SKILL.md copy: old-SKILL.md here.
- Checks: validate --project, rosetta-mentions, check_integration --static all pass (41/0). check_assets not run, no image rebuild.
