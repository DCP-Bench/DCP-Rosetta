# csplib_013_progressive_party_problem: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_013_progressive_party_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_013_progressive_party_problem.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_013_progressive_party_problem.py csplib_013_progressive_party_problem.json

from hermax.model import Model


def create_model(instance):
    """Progressive party problem (CSPLib 13). At a yacht club some boats are hosts and
    stay on board for the whole party; the crews of the other boats (guests) visit one
    host boat in each of several successive periods. A boat holds at most its capacity
    of people at a time, host crew included; a guest crew never revisits a host; two
    crews never meet more than once. Minimise the number of host boats."""
    n_boats = instance["n_boats"]      # number of boats, numbered 0..n_boats-1 (each boat has one crew)
    n_periods = instance["n_periods"]  # number of successive half-hour visiting periods
    capacity = instance["capacity"]    # capacity[b]: most people boat b can hold at a time
    crew_size = instance["crew_size"]  # crew_size[b]: number of people in boat b's crew

    m = Model()

    # is_host[b] is true when boat b is a host boat
    is_host = m.bool_vector("is_host", n_boats)
    # visits[p][b] is the boat that crew b is on in period p (a host crew stays on its own boat)
    visits = m.int_matrix("visits", n_periods, n_boats, 0, n_boats - 1)

    # A host boat's crew stays on board: in every period it is on its own boat.
    for b in range(n_boats):
        for p in range(n_periods):
            m &= (visits[p][b] == b).only_if(is_host[b])

    # Crews only visit host boats: a crew on boat g visiting boat v needs v to be a host.
    for g in range(n_boats):
        for p in range(n_periods):
            for v in range(n_boats):
                m &= is_host[v].only_if(visits[p][g] == v)

    # Capacity: in each period, the people aboard boat b (its host crew if it is a host,
    # plus every guest crew visiting it) do not exceed its capacity.
    for p in range(n_periods):
        for b in range(n_boats):
            m &= (sum(crew_size[g] * (visits[p][g] == b) for g in range(n_boats)) <= capacity[b])

    # Two crews never meet more than once. This also gives the no-revisit rule: a host crew
    # sits on its own boat every period, so a guest meeting it means visiting that host, and
    # at most one meeting means at most one visit per host. Crews c1 and c2 meet in period p when they are
    # on the same boat; meet[p] is forced true then, and at most one period may be a meeting.
    for c1 in range(n_boats):
        for c2 in range(c1 + 1, n_boats):
            meet = m.bool_vector(f"meet_{c1}_{c2}", n_periods)  # meet[p]: crews c1 and c2 share a boat in period p
            for p in range(n_periods):
                for v in range(n_boats):
                    m &= (visits[p][c1] != v) | (visits[p][c2] != v) | meet[p]
            m &= meet.at_most_one()

    # Minimise the number of host boats.
    m.obj += sum(is_host[b] for b in range(n_boats))

    return m, {"visits": visits, "is_host": is_host}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
