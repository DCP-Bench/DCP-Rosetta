# Reading JSON data (one item per group)

**Problem:** Pick one item from each group of a JSON file so the total size fits the capacity; maximum total size.
**Shows:** reading a JSON file with the standard library, ragged lists (one array per group), unused keys ignored, `at` with a decision index.
**Run:** `python model.py data.json`
**Expected:** `Status: OPTIMAL`
**Expected:** `Total size: 11`
