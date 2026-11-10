# SEND + MORE = MONEY (one Boolean per letter and digit)

**Problem:** replace each letter by a different digit so that SEND + MORE = MONEY, with no leading zero.
**Shows:** a Boolean per (letter, digit) with linear sums, one equation per column with a carry, `minimize(0)` for a satisfaction problem.
**Run:** `python model.py`
**Expected:** `Status: OPTIMAL`
**Expected:** `{'S': 9, 'E': 5, 'N': 6, 'D': 7, 'M': 1, 'O': 0, 'R': 8, 'Y': 2}`
