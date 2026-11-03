# csplib_015_schurs_lemma: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_015_schurs_lemma.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_015_schurs_lemma.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_015_schurs_lemma.py csplib_015_schurs_lemma.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Put the balls 1 to n into the boxes so that no three balls x, y and z = x + y all lie in
    the same box."""
    n = instance["n"]      # the number of balls
    boxes = instance["c"]  # the number of boxes

    pool = IDPool()

    # balls[i]: the box of ball i + 1, a number from 1 to the number of boxes
    balls = [Integer(f"ball_{i}", 1, boxes, vpool=pool) for i in range(n)]
    engine = IntegerEngine(vars=balls, vpool=pool)
    cnf = engine.clausify()

    # No box holds all three balls of a triple x, y, x + y. Every pair x, y with x + y at most n
    # gives a triple, and x may equal y.
    for x in range(1, n):
        for y in range(1, n - x + 1):
            z = x + y
            for box in range(1, boxes + 1):
                cnf.append([-balls[x - 1].equals(box),
                            -balls[y - 1].equals(box),
                            -balls[z - 1].equals(box)])

    return cnf, {"balls": balls}


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
