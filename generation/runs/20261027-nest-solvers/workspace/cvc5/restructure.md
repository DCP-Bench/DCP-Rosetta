# cvc5 restructure
- solvers/cvc5_python/ -> solvers/cvc5/python/ (all files kept; old skill folder moved out).
- Skill solvers/cvc5/skills/cvc5/: SKILL.md (shared: concepts, statuses, enumeration, tightening, shared issues, one-column table), interfaces/python/README.md (install, quick start, API, solving options, issues), interfaces/python/encodings.md (encodings + performance, moved verbatim), assets/python/, sources.md (shared + Python), evals renamed to "cvc5".
- Removed image name from sources.md (standalone check). Old SKILL.md copy: old-SKILL.md here.
- Fixed Dockerfile COPY path, readiness_test.py parents[3], CONTRACT.md relative links.
- Checks: validate --project, rosetta-mentions, check_integration --static (41 pass), check_assets 8/8 in existing image.
- Not done: new standalone review (old standalone-review.json still in solvers/cvc5/python/, names skill "cvc5-python"), rebuild, readiness.
