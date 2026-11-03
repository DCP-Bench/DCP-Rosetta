# autoref, jacop_java: evaluator rejects a solution that is the unique spec solution

- attempt-001 (domain 0..n+1) and attempt-002 (domain 0..n) both report
  `invalid_solution`, "Declared outputs cannot extend to a reference solution", on
  `json:1` (n=3, m=0). The example (n=27, m=5) is accepted in both.
- For n=3, m=0 both models output (2,1,2,0,0). Checked by hand and by a brute force
  over all sequences in 0..n of length n+2 with s[n+1]=m and count(i)=s[i] for i in 0..n
  (a Python check on the host, no candidate code): (2,1,2,0,0) is the only solution.
  The instance note says the same. So the rejected output satisfies the description.
- The reference (`global_cardinality_count(s, s)`, domain 0..n) should admit this
  solution. The rejection therefore looks like a reference or evaluator problem on
  `json:1`, not a model error. Not confirmed: the evaluator's internal instance handling
  was not inspected.
- After the first rejection I read the reference's constraint section (not its solve
  tail) to check the counting semantics. Its constraints match the description and this
  model.
- Stopped after two attempts per the runner-problem rule. Blocker to record: autoref x jacop_java.
