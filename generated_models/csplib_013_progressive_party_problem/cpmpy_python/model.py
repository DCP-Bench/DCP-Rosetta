# csplib_013_progressive_party_problem: a CPMpy model from DCP Rosetta.
# Download the `csplib_013_progressive_party_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_013_progressive_party_problem.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_013_progressive_party_problem.py csplib_013_progressive_party_problem.json

import cpmpy as cp


def create_model(instance):
    """Timetable a party at a yacht club: some boats are hosts and the crews of the other
    boats visit host boats in successive periods, without exceeding any boat's capacity,
    revisiting a host or meeting another crew twice. Use as few host boats as possible."""
    n_boats = instance["n_boats"]      # the number of boats
    n_periods = instance["n_periods"]  # the number of half-hour periods
    capacity = instance["capacity"]    # capacity[b]: the most people boat b can hold
    crew_size = instance["crew_size"]  # crew_size[b]: the number of people in the crew of boat b

    # is_host[b] is true when boat b is a host boat
    is_host = cp.boolvar(shape=n_boats, name="is_host")
    # visits[p, b] is the boat that the crew of boat b is on in period p (b itself for a host)
    visits = cp.intvar(0, n_boats - 1, shape=(n_periods, n_boats), name="visits")

    model = cp.Model()
    # The crew of a host boat stays on its own boat in every period.
    for b in range(n_boats):
        model.add(is_host[b].implies((visits[:, b] == b).all()))

    # The people aboard a boat in a period (the crews on it, the host crew included)
    # do not outnumber its capacity.
    for p in range(n_periods):
        for b in range(n_boats):
            model.add(cp.sum((visits[p, :] == b) * crew_size) <= capacity[b])

    # A guest crew never visits the same boat twice.
    for b in range(n_boats):
        model.add((~is_host[b]).implies(cp.AllDifferent(visits[:, b])))

    # A boat that is not a host is never visited.
    for b in range(n_boats):
        model.add((~is_host[b]).implies((visits != b).all()))

    # Two crews meet at most once: they are on the same boat in at most one period.
    for c1 in range(n_boats):
        for c2 in range(c1 + 1, n_boats):
            model.add(cp.sum(visits[:, c1] == visits[:, c2]) <= 1)

    # Use as few host boats as possible.
    model.minimize(cp.sum(is_host))

    return model, {"visits": visits, "is_host": is_host}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
