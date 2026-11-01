# csplib_054_n_queens: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_054_n_queens.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_054_n_queens.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_054_n_queens.py csplib_054_n_queens.json

from pychoco.model import Model


def create_model(instance):
    """Place n queens on an n by n chessboard so that no two of them attack each other."""
    n_queens = instance["n"]  # the board side, and the number of queens

    model = Model()

    # queens[i] is the column, from 1 to n, of the queen in row i
    queens = [model.intvar(1, n_queens, name=f"q{i}") for i in range(n_queens)]

    # No two queens share a column.
    model.all_different(queens).post()

    # down[i] is the column of queen i minus its row i. Queens on one diagonal running
    # down to the right share this value.
    # up[i] is the column of queen i plus its row i. Queens on one diagonal running
    # down to the left share this value.
    down = []
    up = []
    for i in range(n_queens):
        down_i = model.intvar(1 - n_queens, n_queens, name=f"down{i}")
        model.scalar([queens[i], down_i], [1, -1], "=", i).post()
        down.append(down_i)
        up_i = model.intvar(1, 2 * n_queens, name=f"up{i}")
        model.scalar([queens[i], up_i], [1, -1], "=", -i).post()
        up.append(up_i)

    # No two queens share a diagonal running down to the right.
    model.all_different(down).post()
    # No two queens share a diagonal running down to the left.
    model.all_different(up).post()

    return model, {"queens": queens}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
