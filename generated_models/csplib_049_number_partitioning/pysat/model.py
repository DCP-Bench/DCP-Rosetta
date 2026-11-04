# csplib_049_number_partitioning: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_049_number_partitioning.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_049_number_partitioning.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_049_number_partitioning.py csplib_049_number_partitioning.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def create_model(instance):
    """Split the numbers 1 to n into two sets A and B of the same size, with the same sum and
    the same sum of squares."""
    n = instance["n"]     # the numbers 1 to n are split
    half = n // 2        # the size of each set

    pool = IDPool()

    # A[i] is the i-th number of set A
    A = [Integer(f"A{i}", 1, n, vpool=pool) for i in range(half)]
    # B[i] is the i-th number of set B
    B = [Integer(f"B{i}", 1, n, vpool=pool) for i in range(half)]
    engine = IntegerEngine(vars=A + B, vpool=pool)

    # No number appears twice, so the entries of A and B together are the numbers 1 to n.
    engine.add_alldifferent(A + B)
    cnf = engine.clausify()

    # the numbers being split
    numbers = range(1, n + 1)

    # in_A[v] is true exactly when v is one of the entries of A, and false when it is one of B.
    in_A = {v: pool.id(("in_A", v)) for v in numbers}
    for v in numbers:
        cnf.append([-in_A[v]] + [entry.equals(v) for entry in A])
        for entry in A:
            cnf.append([-entry.equals(v), in_A[v]])
        cnf.append([in_A[v]] + [entry.equals(v) for entry in B])
        for entry in B:
            cnf.append([-entry.equals(v), -in_A[v]])

    # Set A holds half of the numbers, so the two sets have the same size.
    cnf.extend(CardEnc.equals(lits=list(in_A.values()), bound=half, vpool=pool,
                              encoding=EncType.seqcounter).clauses)

    # Number v adds +v to a total when it is in A and -v when it is in B.
    lits = [in_A[v] for v in numbers] + [-in_A[v] for v in numbers]

    # The sums of A and B are equal, so the signed total of the numbers is zero.
    cnf.extend(PBEnc.equals(lits=lits, weights=[v for v in numbers] + [-v for v in numbers],
                            bound=0, vpool=pool).clauses)

    # The sums of squares of A and B are equal, so the signed total of the squares is zero.
    cnf.extend(PBEnc.equals(lits=lits, weights=[v * v for v in numbers] + [-v * v for v in numbers],
                            bound=0, vpool=pool).clauses)

    return cnf, {"A": A, "B": B}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
