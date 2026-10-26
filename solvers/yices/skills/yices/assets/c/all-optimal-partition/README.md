# Balanced partition (all optimal solutions)

**Problem:** split items of weight 3 1 1 2 2 1 into two groups with minimal weight difference; list every optimal split.
**Shows:** minimisation by tightening a strict bound until UNSAT, `yices_abs`, a fresh context sharing the same terms with `objective == optimum` for enumeration.
**Run:** `cc -std=gnu99 -O2 model.c -o model -lyices && ./model`
**Expected:** `Optimum: 0 (proven)`
**Expected:** `Optimal solutions: 10`
