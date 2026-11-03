# csplib_007_all_interval: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_007_all_interval.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_007_all_interval.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_007_all_interval.py csplib_007_all_interval.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Find a series of the pitch-classes 0 to n-1, each occurring once, in which the
    intervals between neighbouring notes are all different and cover 1 to n-1."""
    n = instance["n"]  # the number of pitch-classes, and so of notes in the series

    pool = IDPool()

    # x[i] is the pitch-class of the note at position i
    x = [Integer(f"x_{i}", 0, n - 1, vpool=pool) for i in range(n)]
    # diffs[i] is the interval between the notes at positions i and i + 1
    diffs = [Integer(f"diff_{i}", 1, n - 1, vpool=pool) for i in range(n - 1)]
    # each note and interval takes exactly one of its values
    engine = IntegerEngine(vars=x + diffs, vpool=pool)

    # The series is a permutation of the pitch-classes, and the intervals are a permutation
    # of 1 to n - 1.
    engine.add_alldifferent(x)
    engine.add_alldifferent(diffs)
    cnf = engine.clausify()

    # The interval between two neighbouring notes is the distance between their pitch-classes.
    for i in range(n - 1):
        for a in range(n):
            for b in range(n):
                if a != b:
                    cnf.append([-x[i].equals(a), -x[i + 1].equals(b), diffs[i].equals(abs(a - b))])

    return cnf, {"x": x, "diffs": diffs}


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
