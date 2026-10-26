# 5-queens, every solution

**Problem:** place 5 queens on a 5x5 board so none attacks another; list all placements.
**Shows:** enumeration with a no-good over the output terms (`yices_or` of `yices_arith_neq_atom`), ending on UNSAT as proof of completeness.
**Run:** `cc -std=gnu99 -O2 model.c -o model -lyices && ./model`
**Expected:** `Solutions: 10`
**Expected:** `Last status: UNSAT (complete)`
