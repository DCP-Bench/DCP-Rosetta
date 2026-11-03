# session2_subsets_100: a PySAT (Python) model from DCP Rosetta.
# Download the `session2_subsets_100.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subsets_100.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python session2_subsets_100.py session2_subsets_100.json

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.pb import PBEnc


def create_model(instance):
    """Given a set A of different integers, find two disjoint non-empty subsets S and
    T of A whose elements have the same sum."""
    a = instance["A"]  # a[i]: the i-th integer of the set
    n = len(a)  # the number of integers in the set

    pool = IDPool()  # hands out the variable numbers

    # in_S[i] is true when the i-th integer belongs to S
    in_S = [pool.id(("S", i)) for i in range(n)]
    # in_T[i] is true when the i-th integer belongs to T
    in_T = [pool.id(("T", i)) for i in range(n)]

    cnf = CNF()

    # S and T have the same sum, so the sum over S minus the sum over T is zero.
    cnf.extend(PBEnc.equals(lits=in_S + in_T, weights=list(a) + [-v for v in a], bound=0,
                            vpool=pool).clauses)

    # S and T are disjoint: no integer lies in both.
    for s, t in zip(in_S, in_T):
        cnf.append([-s, -t])

    # S is non-empty.
    cnf.extend(CardEnc.atleast(lits=in_S, bound=1, vpool=pool, encoding=EncType.seqcounter).clauses)

    # T is non-empty.
    cnf.extend(CardEnc.atleast(lits=in_T, bound=1, vpool=pool, encoding=EncType.seqcounter).clauses)

    return cnf, {"in_S": in_S, "in_T": in_T}


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
        # a literal is true when it is in the model
        value = np.vectorize(lambda lit: lit in model)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
