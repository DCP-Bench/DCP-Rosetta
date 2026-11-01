# session5_climbing_stairs: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `session5_climbing_stairs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_climbing_stairs.html
# Then run it on the first instance (after `pip install ortools`):
#   python session5_climbing_stairs.py session5_climbing_stairs.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Climb a stair, taking between the fewest and the most steps at each move.
    Find the number of steps taken at each move, or 0 once the top is reached."""
    n_steps = instance["n"]   # the number of steps in the stair
    least = instance["m1"]    # the fewest steps taken at a move
    most = instance["m2"]     # the most steps taken at a move

    model = cp_model.CpModel()

    # steps[i] is the number of steps taken at move i, 0 once the top is reached
    steps = [model.new_int_var(0, most, f"steps_{i}") for i in range(n_steps)]
    # taken[i] is true when move i climbs at least one step
    taken = [model.new_bool_var(f"taken_{i}") for i in range(n_steps)]

    # The moves add up to the whole stair.
    model.add(sum(steps) == n_steps)

    # A move takes between the fewest and the most steps, or none at all.
    for step, t in zip(steps, taken):
        model.add(step >= least).only_enforce_if(t)
        model.add(step == 0).only_enforce_if(~t)

    # Once a move takes no steps, every later move takes none too.
    for i in range(1, n_steps):
        model.add_implication(~taken[i - 1], ~taken[i])

    return model, {"steps": steps}


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
