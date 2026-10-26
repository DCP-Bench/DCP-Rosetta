# Magic square (satisfy)

**Problem:** fill a 3x3 grid with 1..9 so that every row, column and diagonal sums to 15.
**Shows:** bounded integer terms with `yices_new_uninterpreted_term`, `yices_distinct`, `yices_sum`, checking builder results, reading values from a model.
**Run:** `cc -std=gnu99 -O2 model.c -o model -lyices && ./model`
**Expected:** `Status: sat`
**Expected:** `All lines sum to 15: yes`
