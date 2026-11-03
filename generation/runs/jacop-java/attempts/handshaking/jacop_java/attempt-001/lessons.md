# handshaking, jacop_java, attempt-001

Evaluated, not retained. Record: accepted=true, instances_checked 3 of 5, skipped `example` (8 couples) and `json:4` as `execution_timeout`. Skipping 2 of 5 is below the 80% floor in acceptance.md.

Encoding: people 0 = Hilary, 1 = Jocelyn, spouse = index XOR 1; symmetric BooleanVar handshake matrix; deg[i] = SumInt(row, "==", deg[i]); Alldifferent over all degrees except Jocelyn's; output hil = deg[0]. Accepted on the 1-, 3- and 6-couple instances, so the reading (Jocelyn excluded from the distinctness, degree range 0..2c) matches the reference there.

Performance: the solver does not finish on the 8-couple example in 180 s. Variants tried in scratch, all timing out on the example: default labelling; degrees first with IndomainMin/IndomainMax; redundant sum constraint on the distinct degrees; permutation matrix e[i][k] = (deg[i] == k) with Reified(XeqC) and SumInt == 1 both ways; search order on the degrees with SmallestDomain; search order on the permutation matrix. The unique-solution proof needs the search to exhaust, so the cost is in propagation over the handshake matrix, not in finding a first solution.
