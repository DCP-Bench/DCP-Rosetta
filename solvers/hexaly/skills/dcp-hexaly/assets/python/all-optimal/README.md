# Minimum vertex covers (all optimal solutions)

**Problem:** Every minimum vertex cover of a 4-cycle plus an isolated vertex.
**Shows:** `set_gap_limit(0)`, proven optimum, `remove_objective`, pinning the objective to the optimum, then enumerating with soft no-goods.
**Run:** `python model.py`
**Expected:** `Minimum cover size: 2`
**Expected:** `Optimal covers: 2 [[0, 2], [1, 3]]`
**Expected:** `Complete: True`
