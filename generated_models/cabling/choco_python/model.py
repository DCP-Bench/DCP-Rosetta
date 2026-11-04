# cabling: a Choco-solver (Python) model from DCP Rosetta.
# Download the `cabling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cabling.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python cabling.py cabling.json

from pychoco.model import Model


def create_model(instance):
    """Devices are stacked in a rack, one per slot, and some devices are joined by one or
    several cables. Order the devices so that the total cable length is as short as possible."""
    n_devices = instance["n"]          # the number of devices, and of rack slots
    devices = instance["devices"]      # the names of the devices
    cables = instance["cable_struct"]  # the pairs of devices joined by cables, with the number of cables in each pair

    # links[k] is the pair of devices joined by the k-th link, as positions in devices, and the number of cables in it
    links = [(devices.index(a), devices.index(b), count) for a, b, count in cables]

    model = Model()

    # x[d] is the rack slot of device d
    x = [model.intvar(0, n_devices - 1, name=f"x_{d}") for d in range(n_devices)]

    # Every device gets its own slot.
    model.all_different(x).post()

    # distances[k] is the number of slots between the two devices of link k
    distances = []
    for k, (a, b, _) in enumerate(links):
        distance = model.intvar(1, n_devices - 1, name=f"distance_{k}")
        model.distance(x[a], x[b], "=", distance).post()
        distances.append(distance)

    # final_sum is the total cable length: the slot distance of each link times its number of cables.
    final_sum = model.intvar(0, n_devices * n_devices * sum(count for _, _, count in links), name="final_sum")
    model.scalar(distances, [count for _, _, count in links], "=", final_sum).post()

    # Make the total cable length as short as possible.
    return model, {"final_sum": final_sum}, {"objective": final_sum, "maximize": False}


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
