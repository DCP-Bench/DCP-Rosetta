# cabling: a Z3 (Python) model from DCP Rosetta.
# Download the `cabling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cabling.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python cabling.py cabling.json

import z3


def create_model(instance):
    """Devices are placed one above another in a rack, one per slot, and some are joined by
    one or several cables. Order the devices so that the sum of all cable lengths is as short
    as possible."""
    n = instance["n"]                        # the number of devices, and of rack slots
    devices = instance["devices"]            # devices[i]: the name of device i
    cable_struct = instance["cable_struct"]  # each entry [a, b, count]: count cables join devices a and b

    # Cables name devices by their name; turn each into the index of the device.
    links = [(devices.index(a), devices.index(b), count) for a, b, count in cable_struct]

    # slot[d] is the rack slot of device d, counted from the bottom
    slot = [z3.Int(f"slot_{d}") for d in range(n)]
    # length[k] is the total length of the cables of link k
    length = [z3.Int(f"length_{k}") for k in range(len(links))]
    # final_sum is the sum of all cable lengths
    final_sum = z3.Int("final_sum")

    solver = z3.Optimize()

    # Each device sits in one of the n rack slots, and no two devices share a slot.
    solver.add([z3.And(s >= 0, s <= n - 1) for s in slot])
    solver.add(z3.Distinct(slot))

    # below[d][g]: device d sits in a slot under gap g, where gap g lies between slots
    # g - 1 and g. A cable crosses a gap when exactly one of its two devices is under it,
    # so its length is the number of gaps it crosses, and the cables of a link have that
    # length times their number.
    below = [[slot[d] < g for g in range(n)] for d in range(n)]
    for k, (a, b, count) in enumerate(links):
        crossed = [z3.If(below[a][g] != below[b][g], count, 0) for g in range(1, n)]
        solver.add(length[k] == z3.Sum(crossed))

    # Under gap g there are exactly g devices, since the n devices fill the n slots.
    for g in range(1, n):
        solver.add(z3.Sum([z3.If(below[d][g], 1, 0) for d in range(n)]) == g)

    # The sum of all cable lengths is the sum over all links.
    solver.add(final_sum == z3.Sum(length))

    # Reversing the rack (slot p becomes slot n - 1 - p) keeps every cable length, so
    # device 0 can be assumed to sit in one of the first (n + 1) // 2 slots.
    solver.add(slot[0] < (n + 1) // 2)

    # Cables between the same two devices count together. A device can have at most two
    # neighbours one slot away, two neighbours two slots away, and so on, and its cables
    # go to the nearest neighbours first. Each cable is counted from both of its ends,
    # so twice the total length is at least the sum of these best cases.
    pair_counts = {}
    for a, b, count in links:
        key = (min(a, b), max(a, b))
        pair_counts[key] = pair_counts.get(key, 0) + count
    best_case = 0
    for d in range(n):
        counts = sorted((c for (a, b), c in pair_counts.items() if d in (a, b)), reverse=True)
        best_case += sum(c * ((j + 2) // 2) for j, c in enumerate(counts))
    solver.add(2 * final_sum >= best_case)

    # Make the sum of all cable lengths as short as possible.
    solver.minimize(final_sum)

    return solver, {"final_sum": final_sum}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
