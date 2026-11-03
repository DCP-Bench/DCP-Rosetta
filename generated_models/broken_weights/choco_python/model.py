# broken_weights: a Choco-solver (Python) model from DCP Rosetta.
# Download the `broken_weights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/broken_weights.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python broken_weights.py broken_weights.json

from pychoco.model import Model


def create_model(instance):
    """A merchant's measuring weight of m pounds broke into n pieces, each a whole number
    of pounds. On a balance scale the pieces must weigh every whole load from 1 to m."""
    m = instance["m"]          # the total weight of the unbroken weight, in pounds
    n_pieces = instance["n"]   # the number of pieces it broke into

    model = Model()

    # weights[j] is the weight of piece j, in pounds
    weights = [model.intvar(1, m, name=f"weights_{j}") for j in range(n_pieces)]

    # The pieces add up to the whole weight.
    model.sum(weights, "=", m).post()

    # Every load from 1 to m can be weighed with the pieces on the two pans.
    for load in range(1, m + 1):
        # contributions[j] is the pounds piece j adds to the balance for this load: its
        # weight on one pan, minus its weight on the other pan, or 0 when it is off the scale.
        contributions = []
        for j in range(n_pieces):
            # side is +1 on one pan, -1 on the other pan, 0 when the piece is off the scale
            side = model.intvar(-1, 1, name=f"side_{load}_{j}")
            contribution = model.intvar(-m, m, name=f"contribution_{load}_{j}")
            model.times(weights[j], side, contribution).post()
            contributions.append(contribution)
        model.sum(contributions, "=", load).post()

    return model, {"weights": weights}, None


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
