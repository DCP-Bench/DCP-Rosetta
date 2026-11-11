# csplib_013_progressive_party_problem: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_013_progressive_party_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_013_progressive_party_problem.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_013_progressive_party_problem.py csplib_013_progressive_party_problem.json

from pycsp3 import *


def create_model(instance):
    """Timetable a party at a yacht club. Some boats are designated hosts; the crews of the other
    boats visit the host boats in turn over several half-hour periods. A host crew stays on board,
    a guest crew visits several hosts. The total number of people aboard a boat, host and guest
    crews included, must not exceed its capacity. A guest boat cannot revisit a host, and no two
    crews may meet more than once. Minimise the number of host boats."""
    n_boats = instance["n_boats"]       # the number of boats
    n_periods = instance["n_periods"]   # the number of half-hour periods
    capacity = instance["capacity"]     # capacity[b]: the number of people boat b can hold at a time
    crew_size = instance["crew_size"]   # crew_size[b]: the number of people in the crew of boat b

    # is_host[b] is 1 when boat b is a host boat and 0 when it is a guest boat
    is_host = VarArray(size=n_boats, dom={0, 1})

    # visits[p][b] is the boat visited by boat b in period p; a host boat visits itself
    visits = VarArray(size=[n_periods, n_boats], dom=range(n_boats))

    satisfy(
        # A host boat's crew stays on board, so a host visits itself; a guest boat visits another boat.
        is_host[b] == (visits[p][b] == b)
        for p in range(n_periods)
        for b in range(n_boats)
    )

    satisfy(
        # Only host boats can be visited.
        is_host[visits[p][b]] == 1
        for p in range(n_periods)
        for b in range(n_boats)
    )

    satisfy(
        # The people aboard each host boat in each period, its own crew and the guest crews visiting it,
        # do not exceed its capacity.
        Sum(crew_size[b] * (visits[p][b] == h) for b in range(n_boats)) <= capacity[h]
        for p in range(n_periods)
        for h in range(n_boats)
    )

    satisfy(
        # A guest boat cannot revisit a host: its visits in different periods are to different boats.
        imply(is_host[b] == 0, visits[p][b] != visits[q][b])
        for b in range(n_boats)
        for p in range(n_periods)
        for q in range(p + 1, n_periods)
    )

    satisfy(
        # Two crews meet when they are on the same boat in the same period; any two crews meet at most once.
        Sum(visits[p][b1] == visits[p][b2] for p in range(n_periods)) <= 1
        for b1 in range(n_boats)
        for b2 in range(b1 + 1, n_boats)
    )

    # The number of host boats is minimised.
    minimize(Sum(is_host))

    return {"visits": visits, "is_host": is_host}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("visits", "=")
        for row in outputs["visits"]:
            print(values(row))
    else:
        print("No solution:", status())
