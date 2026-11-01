# session5_climbing_stairs: a Choco-solver (Python) model from DCP Rosetta.
# Download the `session5_climbing_stairs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_climbing_stairs.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python session5_climbing_stairs.py session5_climbing_stairs.json

from pychoco.model import Model


def create_model(instance):
    """Climb a stair of n steps, taking between m1 and m2 steps at each move.
    Find the number of steps taken at each move, or 0 once the top is reached."""
    n_steps = instance["n"]  # the number of steps in the stair
    least = instance["m1"]   # the fewest steps taken at a move
    most = instance["m2"]    # the most steps taken at a move

    model = Model()

    # steps[i] is the number of steps taken at move i, or 0 once the top is reached.
    # Each move climbs at least one step, so n_steps moves are enough.
    steps = [model.intvar([0] + list(range(least, most + 1)), name=f"steps_{i}")
             for i in range(n_steps)]

    # The moves add up to the whole stair.
    model.sum(steps, "=", n_steps).post()

    # zero[i] is true when move i takes no steps.
    zero = [model.arithm(steps[i], "=", 0).reify() for i in range(n_steps)]
    # Once a move takes no steps, every later move takes none too.
    for i in range(1, n_steps):
        model.arithm(zero[i - 1], "<=", zero[i]).post()

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
