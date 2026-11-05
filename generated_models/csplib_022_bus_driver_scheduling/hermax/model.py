# csplib_022_bus_driver_scheduling: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_022_bus_driver_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_022_bus_driver_scheduling.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_022_bus_driver_scheduling.py csplib_022_bus_driver_scheduling.json

from hermax.model import Model


def create_model(instance):
    """Bus driver scheduling (CSPLib prob022): choose shifts from a given pool so that
    every piece of work is covered by exactly one chosen shift, using as few shifts as
    possible."""
    num_work = instance["num_work"]  # the number of pieces of work to cover, numbered 0..num_work-1
    shifts = instance["shifts"]      # shifts[i]: the pieces of work that shift i covers
    num_shifts = len(shifts)         # the number of candidate shifts in the pool

    m = Model()

    # x[i] is true when shift i is selected for the schedule
    x = m.bool_vector("x", num_shifts)

    # For each piece of work, the candidate shifts that cover it (derived from the shift data).
    covering = [[i for i in range(num_shifts) if t in shifts[i]] for t in range(num_work)]

    # Every piece of work is covered by exactly one selected shift.
    for t in range(num_work):
        m &= (sum(x[i] for i in covering[t]) == 1)

    # Minimise the number of selected shifts.
    num_selected = sum(x[i] for i in range(num_shifts))
    m.obj += num_selected

    # The objective in the problem's terms: the number of selected shifts, the cost minimised above.
    return m, {"x": x}, num_selected


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
        print("objective =", result[objective])
    else:
        print("No solution:", result.status)
