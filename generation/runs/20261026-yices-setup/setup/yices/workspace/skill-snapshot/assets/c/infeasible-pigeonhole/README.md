# Pigeonhole (infeasible)

**Problem:** put 5 pigeons in 4 holes, one per hole.
**Shows:** `YICES_STATUS_UNSAT` is a result, not an error; there is no model after it.
**Run:** `cc -std=gnu99 -O2 model.c -o model -lyices && ./model`
**Expected:** `Status: unsat (proven infeasible)`
**Expected:** `Model after unsat: none`
