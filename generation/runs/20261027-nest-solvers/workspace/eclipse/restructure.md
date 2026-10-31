# eclipse restructure
- solvers/eclipse_clp -> solvers/eclipse/prolog (id eclipse_clp kept); skill -> solvers/eclipse/skills/eclipse.
- SKILL.md shared (intro, outcomes, table); interfaces/prolog/{README,encoding,common-issues}.md; assets/prolog/; sources.md split; evals renamed.
- Dockerfile COPY paths, readiness_test parents[3], CONTRACT.md links fixed. Old standalone-review.json left in solvers/eclipse/prolog/ (its "skill" field still eclipse-clp).
- validate, rosetta-mentions, check_integration --static: 41 passed.
- Not done: check_assets run, new standalone review, image rebuild, readiness redo.
