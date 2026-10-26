# Partition (all optimal solutions)

**Problem:** split eight numbers into two groups so that the sums differ as little as possible, and list all optimal splits.
**Shows:** minimise by tightening a strict bound until UNSAT, then enumerate in a fresh context with `objective == optimum` (terms are shared between contexts).
**Run:** `python model.py`
**Expected:** `Optimal difference: 1`
