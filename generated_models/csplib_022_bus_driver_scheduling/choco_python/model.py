# csplib_022_bus_driver_scheduling: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_022_bus_driver_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_022_bus_driver_scheduling.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_022_bus_driver_scheduling.py csplib_022_bus_driver_scheduling.json

from pychoco.model import Model


def create_model(instance):
    """Cover every piece of work with exactly one shift, chosen from a given set of
    possible shifts that each cover some of the pieces of work. Every shift costs
    the same, so use as few shifts as possible."""
    n_work = instance["num_work"]        # the number of pieces of work to cover
    n_shifts = instance["num_shifts"]    # the number of possible shifts
    shifts = instance["shifts"]          # shifts[i]: the pieces of work that shift i covers

    model = Model()

    # x[i] is true when shift i is chosen.
    x = [model.boolvar(name=f"x_{i}") for i in range(n_shifts)]

    # Each piece of work is covered by exactly one chosen shift.
    for work in range(n_work):
        covering = [x[i] for i in range(n_shifts) if work in shifts[i]]
        model.sum(covering, "=", 1).post()

    # n_selected is the number of chosen shifts.
    n_selected = model.intvar(0, n_shifts, name="n_selected")
    model.sum(x, "=", n_selected).post()

    # Use as few shifts as possible.
    return model, {"x": x}, {"objective": n_selected, "maximize": False}


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
