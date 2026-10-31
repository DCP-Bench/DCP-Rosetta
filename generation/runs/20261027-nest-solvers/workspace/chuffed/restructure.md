# chuffed restructure
- mv solvers/chuffed_cpp -> solvers/chuffed/cpp (id chuffed_cpp unchanged); skill solvers/chuffed_cpp/skills/chuffed-cpp -> solvers/chuffed/skills/chuffed.
- Skill: new SKILL.md (shared concepts, one-column interface table); interfaces/cpp/README.md + common-issues.md (old SKILL.md text moved, split to stay under ~200 lines); assets/cpp/*; references/cpp/{api-cheatsheet,performance}.md; sources.md with Shared + C++ sections; evals renamed to "chuffed".
- Integration fixes: Dockerfile COPY solvers/chuffed/cpp/...; readiness_test.py parents[2]->parents[3]; CONTRACT.md links.
- Not done: readiness.json/readiness-report.json still hold old paths (redo readiness); standalone-review.json left in solvers/chuffed/cpp/ (new review needed); no rebuild; check_assets not run.
- Checks: validate --project OK, rosetta-mentions OK, check_integration --static 42 pass.
- Outside ref: solvers/SKILLS.md line 8 (chuffed-cpp).
