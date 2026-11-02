# csplib_024_langford: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_024_langford.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_024_langford.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_024_langford.py csplib_024_langford.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Arrange two copies of each number from 1 to k in one sequence of 2k numbers, so that the
    two 1's appear one number apart, the two 2's two numbers apart, ..., and the two k's k numbers
    apart."""
    k = instance["k"]  # the largest number; the sequence holds two copies of each number from 1 to k

    pool = IDPool()

    # sol[p] is the number at place p of the sequence, with places numbered from 0 to 2k - 1
    sol = [Integer(f"sol{p}", 1, k, vpool=pool) for p in range(2 * k)]
    engine = IntegerEngine(vars=sol, vpool=pool)
    cnf = engine.clausify()

    # first[i][p] is true when the first copy of number i is at place p. The second copy is then at
    # place p + i + 1, so p only runs up to the last place that leaves room for it.
    first = {i: [pool.id(("first", i, p)) for p in range(2 * k - i - 1)] for i in range(1, k + 1)}

    # Each number has its first copy at exactly one place.
    for i in range(1, k + 1):
        cnf.extend(CardEnc.equals(lits=first[i], bound=1, vpool=pool, encoding=EncType.seqcounter).clauses)

    # If the first copy of i is at place p, places p and p + i + 1 both hold i. Each place holds one
    # number, so the copies of different numbers occupy different places.
    for i in range(1, k + 1):
        for p, placed in enumerate(first[i]):
            cnf.append([-placed, sol[p].equals(i)])
            cnf.append([-placed, sol[p + i + 1].equals(i)])

    return cnf, {"sol": sol}


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
