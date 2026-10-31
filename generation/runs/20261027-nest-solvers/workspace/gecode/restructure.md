# gecode restructure
- solvers/gecode_cpp -> solvers/gecode/cpp (id gecode_cpp kept); skill moved to solvers/gecode/skills/gecode (name gecode).
- Skill: SKILL.md (shared concepts, interface table, outcomes, enumeration), interfaces/cpp/README.md + constraint-map.md (moved text), assets/cpp/, references/cpp/, sources.md, evals renamed.
- Integration fixes: Dockerfile COPY paths, readiness_test.py parents[3], CONTRACT.md/README.md links, dcp.h comment.
- Checks: validate --project, rosetta-mentions, check_integration --static: 42 pass.
- Left: readiness records (path strings inside readiness.json/report mention old path), old standalone-review.json in solvers/gecode/cpp (skill "gecode-cpp"), image rebuild, check_assets, new review.
- Outside: solvers/SKILLS.md line 11.
