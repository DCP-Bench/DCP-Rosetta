# four_numbers: a PySAT (Python) model from DCP Rosetta.
# Download the `four_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_numbers.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python four_numbers.py four_numbers.json

from itertools import product

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Given up to four distinct integers between 1 and 10, find three integers between 1 and 10
    such that every given number is the sum of some of the three."""
    numbers = instance["numbers"]  # numbers[i]: a number that must be the sum of some of the three
    n = 3  # how many integers to find

    pool = IDPool()

    # x[j] is the j-th of the three integers to find
    x = [Integer(f"x_{j}", 1, 10, vpool=pool) for j in range(n)]
    engine = IntegerEngine(vars=x, vpool=pool)
    cnf = engine.clausify()

    # Each given number is the sum of some of the three integers. A triple of values from which
    # no choice of the three adds up to a given number is ruled out.
    for target in numbers:
        for triple in product(range(1, 11), repeat=n):
            reachable = any(sum(v for v, used in zip(triple, mask) if used) == target
                            for mask in product((0, 1), repeat=n))
            if not reachable:
                cnf.append([-x[j].equals(triple[j]) for j in range(n)])

    return cnf, {"x": x}


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
