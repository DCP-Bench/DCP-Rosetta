# autoref: a PySAT (Python) model from DCP Rosetta.
# Download the `autoref.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/autoref.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python autoref.py autoref.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Find a series s[0], s[1], ..., s[n+1] in which every integer i from 0 to n
    occurs exactly s[i] times, and whose last element s[n+1] equals m."""
    n = instance["n"]  # the largest value in the series; the values 0 to n are counted
    m = instance["m"]  # the required value of the last element
    n_positions = n + 2  # the series has n + 2 elements

    pool = IDPool()

    # s[k] is the k-th element of the series.
    s = [Integer(f"s_{k}", 0, n, vpool=pool) for k in range(n_positions)]
    engine = IntegerEngine(vars=s, vpool=pool)
    # Each element takes one value from 0 to n.
    cnf = engine.clausify()

    # The last element is m.
    cnf.append([s[n + 1].equals(m)])

    # The value i occurs exactly s[i] times. Each possible count c gets its own clauses,
    # which are enforced only while s[i] is c.
    for i in range(n + 1):
        is_i = [s[k].equals(i) for k in range(n_positions)]  # is_i[k] is true when element k is i
        for count in range(n + 1):
            not_count = -s[i].equals(count)  # true when s[i] is not count
            counting = CardEnc.equals(lits=is_i, bound=count, vpool=pool, encoding=EncType.seqcounter)
            for clause in counting.clauses:
                cnf.append([not_count] + clause)

    return cnf, {"s": s}


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
