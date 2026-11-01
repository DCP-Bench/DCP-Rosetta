# csplib_022_bus_driver_scheduling: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_022_bus_driver_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_022_bus_driver_scheduling.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_022_bus_driver_scheduling.py csplib_022_bus_driver_scheduling.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Cover every piece of work with exactly one shift, chosen from a given set of
    possible shifts that each cover some of the pieces of work."""
    num_work = instance["num_work"]  # the number of pieces of work to cover
    shifts = instance["shifts"]      # shifts[i]: the pieces of work that shift i covers

    model = cp_model.CpModel()

    # x[i] is true when shift i is chosen
    x = [model.new_bool_var(f"x_{i}") for i in range(len(shifts))]

    # Each piece of work is covered by exactly one chosen shift.
    for work in range(num_work):
        model.add_exactly_one(x[i] for i, covered in enumerate(shifts) if work in covered)

    # Every shift costs the same, so use as few shifts as possible.
    model.minimize(sum(x))

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
