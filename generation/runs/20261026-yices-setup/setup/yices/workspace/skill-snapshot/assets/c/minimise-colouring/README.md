# Graph colouring (minimise)

**Problem:** colour the wheel graph with 6 vertices (hub plus a 5-cycle) with as few colours as possible.
**Shows:** `yices_ite` for 0/1 "used" flags, `yices_or`, minimising by tightening `objective < best` until UNSAT proves the optimum.
**Run:** `cc -std=gnu99 -O2 model.c -o model -lyices && ./model`
**Expected:** `Colours: 4 (optimal)`
