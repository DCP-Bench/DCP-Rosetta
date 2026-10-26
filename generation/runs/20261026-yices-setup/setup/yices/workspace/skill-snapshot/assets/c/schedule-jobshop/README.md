# Job shop (minimise makespan, time limit)

**Problem:** 3 jobs on 3 machines, operations in a fixed order per job, one operation at a time per machine.
**Shows:** pairwise disjunction for no-overlap, minimising the makespan by tightening, a time limit with `setitimer` and `yices_stop_search`, telling "optimal" from "best found, not proven" and resetting after INTERRUPTED.
**Run:** `cc -std=gnu99 -O2 model.c -o model -lyices && ./model`
**Expected:** `Makespan: 8 (optimal)`
