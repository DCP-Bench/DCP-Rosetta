# football, jacop_java: lessons

- attempt-001 (rejected, invalid_solution "Declared outputs cannot extend to a reference solution"):
  prices and z in one `LinearInt` with weight -1 on z. Forcing z = 29999 was accepted, forcing
  z = 30000 was not, so the model admitted a total of 30000 that the reference does not. The
  reference optimum is 29999. The fix in attempt-002 posts `spend[i] = price[i] * buy[i]` with
  `XmulCeqZ` and sums the spends with `SumInt`. Suspected cause: the mixed-weight `LinearInt` over
  Boolean variables and a variable on the right-hand side. Not confirmed in JaCoP's source. Worth
  a reproducer in the solver skill: `LinearInt` with BooleanVar weights and a `-1` term for the result.
- Units: the description says "GBP thousands" and also gives the example "GBP 12,345 million ->
  12345". The two do not agree. The model uses thousands (30 million = 30000), and the reference's
  optimum 29999 confirms it.
- Prices are scaled by 1000 to keep integers. All prices have at most three decimals.
- Brute force on the host (a plain Python subset search over the price lists, not candidate code)
  gave the same optimum 29999 as the reference, with the count rules and the minimum of eleven players.
