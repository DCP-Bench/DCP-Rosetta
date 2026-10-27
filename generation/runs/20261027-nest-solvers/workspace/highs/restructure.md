# highs restructure
- solvers/highs_cpp/ -> solvers/highs/cpp/ (all files kept; old skills/ folder moved out).
- Skill: solvers/highs/skills/highs/ (SKILL.md shared: concepts, linearisation table, gap options, no-good strategy; interfaces/cpp.md: install, quick start, API, statuses, options, issues; assets/cpp/*; sources.md shared + C++; evals renamed to "highs").
- Fixed: Dockerfile COPY paths, readiness_test.py parents[3], CONTRACT.md links.
- Checks: validate --project, rosetta-mentions, check_integration highs_cpp --static all pass (42 passed).
- Not done: image rebuild, readiness redo, new standalone review (old standalone-review.json left in solvers/highs/cpp/, still names "highs-cpp"), check_assets run.
- Outside refs: solvers/SKILLS.md line 33.
