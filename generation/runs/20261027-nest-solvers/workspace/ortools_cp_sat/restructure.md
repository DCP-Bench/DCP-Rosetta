# ortools_cp_sat restructure

- Moved solvers/ortools_cp_sat_{cpp,python}/ to solvers/ortools_cp_sat/{cpp,python}/ (plain mv, ids unchanged).
- Merged the two flat skills into solvers/ortools_cp_sat/skills/ortools-cp-sat/: SKILL.md (shared + 2-column table), interfaces/cpp.md (226 lines, mostly code), interfaces/python.md, assets/{cpp,python}/, sources.md, evals/evals.json (skill_name/expected_skill renamed, merged, one solver-only prompt added, old python-for-cpp negative dropped). Old drafts in workspace/ortools_cp_sat/old/.
- Verified in images: enumeration with 8 workers loses solutions in Python too (4 of 7; default and 1 worker give 7); check_assets python 9/9.
- Fixed: Dockerfile COPY paths, readiness_test parents[3], CONTRACT.md relative links.
- Old per-integration standalone-review.json left in cpp/ and python/; a new review of the merged skill is still needed. Images not rebuilt, readiness records not redone (they cite old paths).
- Checks: validate, rosetta-mentions, check_integration --static pass for both ids.
