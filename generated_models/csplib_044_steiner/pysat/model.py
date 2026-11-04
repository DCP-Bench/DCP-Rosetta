# csplib_044_steiner: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_044_steiner.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_044_steiner.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_044_steiner.py csplib_044_steiner.json

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool


def create_model(instance):
    """Find a ternary Steiner system of order n: n * (n - 1) / 6 triples of elements of
    {1, ..., n} such that any two triples have at most one element in common."""
    n = instance["n"]              # the number of elements
    n_triples = n * (n - 1) // 6   # the number of triples in the system

    pool = IDPool()

    # sets[i][j] is true when triple i contains element j
    sets = [[pool.id(("sets", i, j)) for j in range(n)] for i in range(n_triples)]

    cnf = CNF()

    # Each triple has exactly three elements.
    for triple in sets:
        cnf.extend(CardEnc.equals(lits=triple, bound=3, vpool=pool, encoding=EncType.seqcounter).clauses)

    # Two triples share at most one element: no pair of elements lies in two triples.
    # together[i] is true whenever triple i contains both elements p and q.
    for p in range(n):
        for q in range(p + 1, n):
            together = [pool.id(("together", p, q, i)) for i in range(n_triples)]
            for i in range(n_triples):
                cnf.append([-sets[i][p], -sets[i][q], together[i]])
            cnf.extend(CardEnc.atmost(lits=together, bound=1, vpool=pool, encoding=EncType.seqcounter).clauses)

    return cnf, {"sets": sets}


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
