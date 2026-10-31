# maxicp restructure
- solvers/maxicp_java/ -> solvers/maxicp/java/ (all files kept, old standalone-review.json left inside).
- Skill solvers/maxicp/skills/maxicp/: SKILL.md (shared + one-column table), interfaces/java/{README,modelling,issues}.md (split to stay under ~200 lines), assets/java/, evals (renamed), sources.md (shared + Java).
- Dockerfile COPY paths, readiness_test.py parents[3], CONTRACT.md links fixed.
- validate, rosetta-mentions, check_integration --static: clean (42 pass).
- Outside refs: solvers/SKILLS.md line 13 (tree listing). readiness.json/readiness-report.json contain old path strings (readiness redo pending). Standalone review and image rebuild still to do.
