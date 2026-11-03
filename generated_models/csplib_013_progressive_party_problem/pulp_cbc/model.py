# csplib_013_progressive_party_problem: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_013_progressive_party_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_013_progressive_party_problem.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_013_progressive_party_problem.py csplib_013_progressive_party_problem.json

import pulp


def create_model(instance):
    """Timetable a party at a yacht club: some boats are hosts and the crews of the other
    boats visit host boats in successive periods, without exceeding any boat's capacity,
    revisiting a host or meeting another crew twice. Use as few host boats as possible."""
    n_boats = instance["n_boats"]      # the number of boats
    n_periods = instance["n_periods"]  # the number of half-hour periods
    capacity = instance["capacity"]    # capacity[b]: the most people boat b can hold
    crew_size = instance["crew_size"]  # crew_size[b]: the number of people in the crew of boat b

    # the boats
    boats = range(n_boats)
    # the half-hour periods
    periods = range(n_periods)

    problem = pulp.LpProblem("progressive_party", pulp.LpMinimize)

    # is_host[b] is 1 when boat b is a host boat, and 0 when not
    is_host = [pulp.LpVariable(f"is_host_{b}", cat="Binary") for b in boats]
    # aboard[p][b][h] is 1 when the crew of boat b is aboard boat h in period p
    aboard = [[[pulp.LpVariable(f"aboard_{p}_{b}_{h}", cat="Binary") for h in boats]
               for b in boats] for p in periods]
    # visits[p][b] is the boat the crew of boat b is aboard in period p, its own boat for a host
    visits = [[pulp.LpVariable(f"visits_{p}_{b}", 0, n_boats - 1, cat="Integer")
               for b in boats] for p in periods]

    # In every period each crew is aboard exactly one boat, and visits reports which one.
    for p in periods:
        for b in boats:
            problem += pulp.lpSum(aboard[p][b]) == 1
            problem += visits[p][b] == pulp.lpSum(h * aboard[p][b][h] for h in boats)

    # A host's crew stays aboard its own boat in every period. A guest crew does not.
    for p in periods:
        for h in boats:
            problem += aboard[p][h][h] == is_host[h]

    # Crews only go aboard host boats.
    for p in periods:
        for b in boats:
            for h in boats:
                problem += aboard[p][b][h] <= is_host[h]

    # The people aboard a boat in a period, host crew included, do not outnumber its capacity.
    for p in periods:
        for h in boats:
            problem += pulp.lpSum(crew_size[b] * aboard[p][b][h] for b in boats) <= capacity[h]

    # A guest crew visits each host at most once. A host's stay on its own boat is not a visit.
    for b in boats:
        for h in boats:
            if h != b:
                problem += pulp.lpSum(aboard[p][b][h] for p in periods) <= 1

    # Two crews meet in at most one period. meet[p] is forced to 1 when crews a and b are
    # aboard the same boat in period p.
    for a in boats:
        for b in range(a + 1, n_boats):
            meet = [pulp.LpVariable(f"meet_{p}_{a}_{b}", 0, 1) for p in periods]
            for p in periods:
                for h in boats:
                    problem += meet[p] >= aboard[p][a][h] + aboard[p][b][h] - 1
            problem += pulp.lpSum(meet) <= 1

    # The number of host boats, to be made as small as possible.
    problem += pulp.lpSum(is_host)

    return problem, {"visits": visits, "is_host": is_host}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
