# jump restructure
- mv solvers/jump_highs -> solvers/jump/julia (id jump_highs unchanged); skill moved to solvers/jump/skills/jump.
- Skill: SKILL.md (shared: concepts, linearisations, statuses, enumeration, shared issues, one-column table), interfaces/julia.md (install, quick start, JSON, call table, settings, printing, binding issues, examples), assets/julia/*, sources.md (header added), evals unchanged (already "jump").
- Fixed: Dockerfile COPY paths, readiness_test parents[3], CONTRACT.md relative links.
- Old julia/standalone-review.json left in place; readiness*.json still hold old paths (record will not match; redo readiness).
- Checks: validate, rosetta-mentions, check_integration --static: all pass (40/0 fail).
- Not done: check_assets, rebuild, readiness, new standalone review.
