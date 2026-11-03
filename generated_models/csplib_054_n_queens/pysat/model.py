# csplib_054_n_queens: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_054_n_queens.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_054_n_queens.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_054_n_queens.py csplib_054_n_queens.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Place n queens on an n x n chessboard so that no two queens are on the same
    row, column or diagonal."""
    n_queens = instance["n"]  # the board size, which is also the number of queens

    pool = IDPool()

    # queens[i] is the column, from 1 to n_queens, of the queen in row i
    queens = [Integer(f"q{i}", 1, n_queens, vpool=pool) for i in range(n_queens)]
    engine = IntegerEngine(vars=queens, vpool=pool)

    # No two queens share a column.
    engine.add_alldifferent(queens)
    # Two queens in rows i and j are not on a shared diagonal, so their columns do not
    # differ by exactly the distance between their rows.
    for i in range(n_queens):
        for j in range(i + 1, n_queens):
            engine.add_linear(queens[i] - queens[j] != i - j)
            engine.add_linear(queens[i] - queens[j] != j - i)

    return engine.clausify(), {"queens": queens}


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
