# three_coins: a Choco-solver (Python) model from DCP Rosetta.
# Download the `three_coins.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_coins.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python three_coins.py three_coins.json

from pychoco.model import Model


def create_model(instance):
    """Three coins lie on a table. In exactly the given number of moves, each move turning
    one coin over, make them all face heads or all face tails."""
    init = instance["init"]            # init[j]: 1 when coin j starts tails up, 0 when heads up
    num_moves = instance["num_moves"]  # the number of moves
    n_coins = len(init)                # the number of coins

    model = Model()

    # steps[m][j] is true when coin j shows tails after m moves; m = 0 is the start.
    steps = [[model.boolvar(name=f"steps_{m}_{j}") for j in range(n_coins)] for m in range(num_moves + 1)]

    # The coins start as given.
    for j in range(n_coins):
        model.arithm(steps[0][j], "=", init[j]).post()

    # Each move turns exactly one coin over. turned[j] is true when coin j is turned over in move m.
    for m in range(1, num_moves + 1):
        turned = [model.arithm(steps[m][j], "!=", steps[m - 1][j]).reify() for j in range(n_coins)]
        model.sum(turned, "=", 1).post()

    # n_tails is the number of coins showing tails at the end.
    n_tails = model.intvar(0, n_coins, name="n_tails")
    model.sum(steps[num_moves], "=", n_tails).post()

    # At the end all coins face the same way: either none or all of them show tails.
    model.member(n_tails, [0, n_coins]).post()

    return model, {"steps": steps}, None


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
