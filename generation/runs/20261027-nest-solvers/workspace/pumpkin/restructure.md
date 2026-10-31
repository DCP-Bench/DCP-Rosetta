# pumpkin restructure
- solvers/pumpkin_rust/ -> solvers/pumpkin/rust/ (all files kept; id pumpkin_rust unchanged).
- skill solvers/pumpkin_rust/skills/pumpkin-rust -> solvers/pumpkin/skills/pumpkin (name "pumpkin"); SKILL.md (shared + one-column table), interfaces/rust.md (230 lines, Install..Common issues moved), assets/rust/, references/rust/pumpkin-api.md (links fixed), sources.md (shared + Rust), evals renamed.
- Dockerfile COPY paths -> solvers/pumpkin/rust/...; readiness_test.py parents[2] -> parents[3]; CONTRACT.md links to ../../CONTRACT.md and ../../../tests/fixtures.
- Old standalone-review.json left at solvers/pumpkin/rust/ (names skill pumpkin-rust); needs a new review then move to solvers/pumpkin/.
- Checks: validate --project, rosetta-mentions, check_integration pumpkin_rust --static: 42 pass.
- Not done: image rebuild, readiness redo (readiness.json/report paths name old folder), check_assets.
- interfaces/rust.md is ~230 lines, slightly over 200 guideline.
