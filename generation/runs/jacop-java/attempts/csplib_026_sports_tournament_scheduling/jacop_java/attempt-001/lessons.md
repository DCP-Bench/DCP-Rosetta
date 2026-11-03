# csplib_026 attempt-001 lessons

- Evaluated and rejected: example (n=8) execution_timeout; json:1 (n=6) invalid_solution,
  "Declared outputs cannot extend to a reference solution".
- The json:1 solution in the record was checked by hand and in Python against the
  reference's constraints (home != away, AllDifferent per week, every pair met at least
  once, at most two per team per period). All hold. So either the evaluator is not
  reading the outputs as the brief declares them, or the reference is stricter than its
  printed constraints. Not resolved here; needs a runner/evaluator look.
- Search: SmallestDomain (first-fail) with the IfThen channelling timed out even on n=6;
  input-order labelling solves n=6 in 0.4 s. On n=8 both orders time out. Removing either
  the at-most-twice Count or the opponent Alldistinct makes n=8 fast but then the model is
  under-constrained, so the combination is what is slow.
- Models tried (check only, no attempt spent): Alldifferent vs Alldistinct per week;
  labelling home/away vs opponents first. None solved n=8 in 180 s.
