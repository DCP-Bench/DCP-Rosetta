# Lessons: csplib_011 on jacop_java, attempt 3

- hints.md (coordinator's scratch hints from accepted models of other solvers) was used for the structure.
- Accepted in about 1 s, both emitted solutions valid. Attempts 1 and 2 (9x9x18 reified grid, all dates free) timed out.
- What made it work: only the 9 first dates of the mirror pairs carry variables; the partner date reuses the
  opponent row and gets venue 2 - w through XplusYeqC. Per free date: Alldifferent, involution via
  Element.choose(cfg[i], row, const i, -1), opposite venues via Element.choose + XplusYeqC, bye iff cfg[i]==i,
  1 bye / 4 home / 4 away. Per team: Alldifferent on its column and a Table over its 9 venues listing the
  sequences that pass rules 2-5 (enumerated in Java from 3^9 patterns).
- Search: venue variables team by team, then config rows by date, input order, IndomainMin.
- Conventions (0-based teams in statement order, bye = own index, where 0/1/2) matched the evaluator.
