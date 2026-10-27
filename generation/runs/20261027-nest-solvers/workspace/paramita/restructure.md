# paramita restructure
- solvers/paramita_python/ -> solvers/paramita/python/ (all files kept); skill moved to solvers/paramita/skills/paramita/.
- Skill: SKILL.md (shared: concepts, solving strategy, solver-level issues, one-column interface table), interfaces/python.md (install, quick start, modelling, solving code, binding issues, 164 lines), assets/python/*, references/python/{api,modelling}.md, sources.md (shared + Python), evals unchanged (already "paramita").
- Integration fixes: Dockerfile COPY run.py path, readiness_test.py parents[3], CONTRACT.md relative links.
- Checks: validate --project, rosetta-mentions, check_integration --static all pass (40 passed).
- Not done: image rebuild, readiness redo, new standalone review (old standalone-review.json left in solvers/paramita/python/), check_assets run.
- Record paths inside readiness-report.json and readiness/superseded/*.json still name solvers/paramita_python/ (evidence, left).
