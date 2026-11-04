# csplib_067_quasigroup_completion: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_067_quasigroup_completion.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_067_quasigroup_completion.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_067_quasigroup_completion.py csplib_067_quasigroup_completion.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Complete a partially filled N-by-N table so that each of the numbers 1 to N
    occurs exactly once in every row and every column (a quasigroup, or Latin square)."""
    n_numbers = instance["N"]  # order of the quasigroup: the table is N by N and holds 1 to N
    start = instance["start"]  # start[i][j]: the given number in cell (i, j), or 0 if the cell is empty

    pool = IDPool()

    # puzzle[i][j] is the number in the cell at row i, column j
    puzzle = [[Integer(f"puzzle_{i}_{j}", 1, n_numbers, vpool=pool) for j in range(n_numbers)]
              for i in range(n_numbers)]
    engine = IntegerEngine(vars=[cell for row in puzzle for cell in row], vpool=pool)

    # The cells that are already filled keep their given number.
    for i in range(n_numbers):
        for j in range(n_numbers):
            if start[i][j] != 0:
                engine.add_linear(puzzle[i][j] == start[i][j])

    # Each row and each column holds every number once.
    for i in range(n_numbers):
        engine.add_alldifferent(puzzle[i])
        engine.add_alldifferent([puzzle[j][i] for j in range(n_numbers)])

    return engine.clausify(), {"puzzle": puzzle}


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
