# Lessons: session5_grocery, jacop_java, attempt-002 (accepted)

- hints.md (coordinator's retry hints) was used, and the earlier attempt-001 was read.
- Product reading: prices in cents, multiplied as dollars: product = total * 100^(n-1). The dataset's instance notes say "sum and product (in cents)". Attempt-001 used product = total and was unsat.
- Trap: IntDomain.MaxInt is 536870909, below the scaled product for 4 items. Split the items into two halves, multiply each half with XmulYeqZ, and join the halves with a Table of (x, target/x) pairs built in long arithmetic.
- Price domains are the divisors of the target up to total (IntervalDomain.unionAdapt). Non-decreasing order is a valid symmetry break; all 5 instances solve in under 0.2 s.
- Limit: half-product variables are capped at 5e8, so very large instances could lose solutions; the five instances here are far below it.
