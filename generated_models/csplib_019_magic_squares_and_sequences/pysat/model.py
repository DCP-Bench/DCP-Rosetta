# csplib_019_magic_squares_and_sequences: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_019_magic_squares_and_sequences.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_019_magic_squares_and_sequences.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_019_magic_squares_and_sequences.py csplib_019_magic_squares_and_sequences.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """A magic sequence of length n is a sequence of integers x[0], ..., x[n-1], each between
    0 and n-1, such that for every i the number i occurs exactly x[i] times in the sequence."""
    n = instance["n"]  # the length of the sequence; the numbers and the positions run over 0..n-1

    pool = IDPool()

    # x[i] is the i-th number of the sequence
    x = [Integer(f"x{i}", 0, n - 1, vpool=pool) for i in range(n)]
    # occurs[i][j] is 1 when the j-th number of the sequence is i, else 0
    occurs = [[Integer(f"occurs{i}_{j}", 0, 1, vpool=pool) for j in range(n)] for i in range(n)]
    engine = IntegerEngine(vars=x + [flag for row in occurs for flag in row], vpool=pool)

    # The number i occurs exactly x[i] times: the occurs values of i add up to x[i].
    for i in range(n):
        engine.add_linear(sum(occurs[i]) - x[i] == 0)
    cnf = engine.clausify()

    # occurs[i][j] is 1 exactly when the j-th number of the sequence is i.
    for i in range(n):
        for j in range(n):
            cnf.append([-x[j].equals(i), occurs[i][j].equals(1)])
            cnf.append([x[j].equals(i), -occurs[i][j].equals(1)])

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
