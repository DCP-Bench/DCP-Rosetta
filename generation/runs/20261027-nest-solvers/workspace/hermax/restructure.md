# hermax restructure
- Moved flat solvers/hermax/* (CONTRACT, Dockerfile, metadata, readiness*, readiness_test.py, run.py, standalone-review.json) to solvers/hermax/python/. Old standalone-review.json left there.
- Skill now solvers/hermax/skills/hermax/: SKILL.md (shared + one-column table), interfaces/python/{README,modelling,issues}.md (old text split by section, links fixed), assets/python/*, references/python/model-api.md, sources.md (Shared/Python), evals/evals.json (unchanged names already "hermax").
- Dockerfile COPY -> solvers/hermax/python/run.py; readiness_test.py parents[2] -> parents[3]; CONTRACT.md links one level deeper.
- Checks: validate --project, rosetta-mentions, check_integration --static: all pass.
- Not done: new standalone review, image rebuild, readiness redo. readiness.json/readiness-report.json hold old path strings solvers/hermax/readiness-result.json (record, left as is).
- SKILL.md Solving prose and enumeration strategy were summarised in shared text (short new paragraph); full code is in the interface file.
