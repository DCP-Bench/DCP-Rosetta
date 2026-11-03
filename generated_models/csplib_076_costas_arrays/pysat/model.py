# csplib_076_costas_arrays: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_076_costas_arrays.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_076_costas_arrays.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_076_costas_arrays.py csplib_076_costas_arrays.json

from itertools import combinations

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Place n marks on an n-by-n grid, one per row and one per column, so that the
    n(n-1)/2 vectors between the marks are all different (a Costas array)."""
    n_marks = instance["n"]  # size of the grid, which is also the number of marks

    pool = IDPool()

    # costas[i] is the column (1 to n) of the mark in row i
    costas = [Integer(f"costas{i}", 1, n_marks, vpool=pool) for i in range(n_marks)]
    engine = IntegerEngine(vars=costas, vpool=pool)

    # One mark per column: the columns form a permutation.
    engine.add_alldifferent(costas)
    cnf = engine.clausify()

    # The difference triangle: for each distance l between rows, the differences
    # costas[i + l] - costas[i] are all different, so no two vectors between marks
    # at that distance are equal.
    for l in range(1, n_marks):
        # steps_of[d][i] is the flag for difference d starting at row i
        steps_of = {}
        # step is true whenever costas[i + l] - costas[i] == d
        for i in range(n_marks - l):
            for v in range(1, n_marks + 1):
                for w in range(1, n_marks + 1):
                    if v == w:
                        continue
                    step = pool.id(("step", l, i, w - v))
                    cnf.append([-costas[i].equals(v), -costas[i + l].equals(w), step])
                    steps_of.setdefault(w - v, {})[i] = step

        # No difference occurs at two different starting rows.
        for d, by_start in steps_of.items():
            for i, j in combinations(sorted(by_start), 2):
                cnf.append([-by_start[i], -by_start[j]])

    return cnf, {"costas": costas}


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
