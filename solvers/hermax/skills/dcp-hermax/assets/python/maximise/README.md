# Maximum-weight independent set (maximise)

**Problem:** Pick vertices of a 6-cycle, with weights 5, 3, 8, 2, 7, 4, so that no two adjacent vertices are picked and the total weight is largest.
**Shows:** maximise by minimising minus the total weight (`m.obj += -total`), reading the total back with `r[expression]`.
**Run:** `python3 model.py`
**Expected:** `best weight 20`
