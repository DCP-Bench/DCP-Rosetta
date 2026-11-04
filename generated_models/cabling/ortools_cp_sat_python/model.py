# cabling: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `cabling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cabling.html
# Then run it on the first instance (after `pip install ortools`):
#   python cabling.py cabling.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Devices are stacked in a rack, and some devices are joined by one or several cables.
    Order the devices so that the total cable length is as short as possible."""
    n = instance["n"]                  # the number of devices, and of rack slots
    devices = instance["devices"]      # the names of the devices
    cables = instance["cable_struct"]  # the cables between pairs of devices, with their count

    # links[k] is the pair of devices joined by link k, and the number of cables in it
    links = [(devices.index(a), devices.index(b), count) for a, b, count in cables]

    model = cp_model.CpModel()

    # x[d] is the rack slot of device d
    x = [model.new_int_var(0, n - 1, f"x_{d}") for d in range(n)]

    # distance[k] is the number of slots between the two devices of link k
    distance = [model.new_int_var(1, n - 1, f"distance_{k}") for k in range(len(links))]

    # final_sum is the total length of all cables
    final_sum = model.new_int_var(0, n * n * sum(count for _, _, count in links), "final_sum")

    # Devices do not share a slot.
    model.add_all_different(x)

    # Each link is as long as the slot gap between its two devices.
    for k, (a, b, _) in enumerate(links):
        model.add_abs_equality(distance[k], x[a] - x[b])

    # The total cable length adds up the cables of every link.
    model.add(final_sum == sum(count * distance[k] for k, (_, _, count) in enumerate(links)))

    # Minimize the total cable length.
    model.minimize(final_sum)

    return model, {"final_sum": final_sum}


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
