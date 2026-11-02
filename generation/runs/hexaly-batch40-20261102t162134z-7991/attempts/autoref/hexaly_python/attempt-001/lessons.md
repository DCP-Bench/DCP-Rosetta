# autoref attempt-001

Rejected on json:1 (n=3, m=0) with "Declared outputs cannot extend to a reference solution".
The model let each s_j range up to n + 2, which admits (4, 0, 0, 0, 0) besides the intended
(2, 1, 2, 0, 0) (found by brute force on the host under the model's reading). The instance
note says (2, 1, 2, 0, 0) is the only solution, so the entries are bounded by n. Attempt-002
bounds s_0..s_n by n. The reference was not read.
