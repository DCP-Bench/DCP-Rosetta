# Knapsack from JSON (maximise)

**Problem:** choose items under a weight capacity to maximise value; the data is read from a JSON file.
**Shows:** a ragged `conflicts` list (rows of different lengths) iterated per row, `json` from the standard library, sizes taken from the data, extra keys ignored, boolean terms with `ite`, maximise by tightening `objective > best` until UNSAT.
**Run:** `python model.py data.json`
**Expected:** `Objective: 23 (optimal)`
