# cabling: an Exact (Python) model from DCP Rosetta.
# Download the `cabling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cabling.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python cabling.py cabling.json

from exact import Exact


def create_model(instance):
    """Devices are stacked one above another in a rack, one device per slot. Some devices are
    joined by one or several cables. Order the devices so that the total cable length is as
    short as possible."""
    n = instance["n"]                  # the number of devices, and of rack slots
    devices = instance["devices"]      # the names of the devices
    cables = instance["cable_struct"]  # the cables: which two devices each group joins, and how many

    # links[k] is the pair of devices joined by link k, and the number of cables in it
    links = [(devices.index(a), devices.index(b), count) for a, b, count in cables]

    solver = Exact()

    # Exact identifies its variables by name.
    # in_slot[d][p] is 1 when device d is in slot p, and 0 when not
    in_slot = [[f"device_{d}_in_{p}" for p in range(n)] for d in range(n)]
    for d in range(n):
        for name in in_slot[d]:
            solver.addVariable(name, 0, 1)
        # Each device has exactly one slot.
        solver.addConstraint([(1, name) for name in in_slot[d]], True, 1, True, 1)
    # Each slot holds exactly one device.
    for p in range(n):
        solver.addConstraint([(1, in_slot[d][p]) for d in range(n)], True, 1, True, 1)

    # distance[k] is the number of slots between the two devices of link k
    distance = [f"distance_{k}" for k in range(len(links))]
    for k, (a, b, _) in enumerate(links):
        solver.addVariable(distance[k], 1, n - 1)
        # apart[k][t] is 1 when the two devices of link k are t slots apart, and 0 when not
        apart = {t: f"apart_{k}_{t}" for t in range(1, n)}
        for name in apart.values():
            solver.addVariable(name, 0, 1)
        # The two devices are a single distance apart.
        solver.addConstraint([(1, name) for name in apart.values()], True, 1, True, 1)
        # distance[k] is the distance that the chosen apart flag names.
        solver.addConstraint([(t, apart[t]) for t in range(1, n)] + [(-1, distance[k])],
                             True, 0, True, 0)
        # If device a is in slot p and device b in slot q, they are |p - q| slots apart.
        for p in range(n):
            for q in range(n):
                if p != q:
                    solver.addConstraint([(1, in_slot[a][p]), (1, in_slot[b][q]), (-1, apart[abs(p - q)])],
                                         False, 0, True, 1)

    # final_sum is the total length of all cables
    solver.addVariable("final_sum", 0, n * n * sum(count for _, _, count in links))
    # Each link's length is its distance times its number of cables, and final_sum adds them up.
    terms = [(count, distance[k]) for k, (_, _, count) in enumerate(links)]
    solver.addConstraint(terms + [(-1, "final_sum")], True, 0, True, 0)

    solver.setObjective(terms, minimize=True)

    return solver, {"final_sum": "final_sum"}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
