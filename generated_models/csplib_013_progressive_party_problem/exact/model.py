# csplib_013_progressive_party_problem: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_013_progressive_party_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_013_progressive_party_problem.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_013_progressive_party_problem.py csplib_013_progressive_party_problem.json

from exact import Exact


def create_model(instance):
    """Timetable a party at a yacht club. Some boats are hosts. The crew of every other
    boat visits host boats over several periods, without any boat exceeding its capacity,
    a guest crew visiting the same host twice, or two crews meeting more than once.
    Use as few host boats as possible."""
    n_boats = instance["n_boats"]      # the number of boats, numbered 0 to n_boats - 1
    n_periods = instance["n_periods"]  # the number of half-hour periods
    capacity = instance["capacity"]    # capacity[b]: the most people that fit aboard boat b at once
    crew_size = instance["crew_size"]  # crew_size[b]: the number of people in the crew of boat b

    solver = Exact()

    # Exact identifies its variables by name.
    # is_host[b] is 1 when boat b is a host boat, and 0 when not
    is_host = [f"is_host_{b}" for b in range(n_boats)]
    for name in is_host:
        solver.addVariable(name, 0, 1)

    # visits[p][b] is the boat that the crew of boat b is aboard in period p (its own boat for a host)
    visits = [[f"visits_{p}_{b}" for b in range(n_boats)] for p in range(n_periods)]
    # at[p][b][h] is 1 when the crew of boat b is aboard boat h in period p, and 0 when not
    at = [[[f"at_{p}_{b}_{h}" for h in range(n_boats)] for b in range(n_boats)]
          for p in range(n_periods)]
    for p in range(n_periods):
        for b in range(n_boats):
            solver.addVariable(visits[p][b], 0, n_boats - 1)
            for h in range(n_boats):
                solver.addVariable(at[p][b][h], 0, 1)

            # A crew is aboard exactly one boat in each period.
            solver.addConstraint([(1, at[p][b][h]) for h in range(n_boats)], True, 1, True, 1)
            # visits[p][b] names that boat.
            solver.addConstraint([(h, at[p][b][h]) for h in range(1, n_boats)] + [(-1, visits[p][b])],
                                 True, 0, True, 0)

    # The crew of a host boat stays aboard its own boat in every period.
    for b in range(n_boats):
        for p in range(n_periods):
            solver.addConstraint([(1, at[p][b][b]), (-1, is_host[b])], True, 0)

    # The people aboard a boat in a period, its host crew and the guest crews, stay within its capacity.
    for p in range(n_periods):
        for h in range(n_boats):
            solver.addConstraint([(crew_size[b], at[p][b][h]) for b in range(n_boats)],
                                 False, 0, True, capacity[h])

    # A guest crew visits each other boat at most once.
    for b in range(n_boats):
        for h in range(n_boats):
            if h != b:
                solver.addConstraint([(1, at[p][b][h]) for p in range(n_periods)], False, 0, True, 1)

    # Only host boats are visited.
    for p in range(n_periods):
        for b in range(n_boats):
            for h in range(n_boats):
                solver.addConstraint([(1, at[p][b][h]), (-1, is_host[h])], False, 0, True, 0)

    # meet[p] is 1 when crews c1 and c2 are aboard the same boat in period p.
    # Two crews may share a boat in at most one period.
    for c1 in range(n_boats):
        for c2 in range(c1 + 1, n_boats):
            meet = [f"meet_{p}_{c1}_{c2}" for p in range(n_periods)]
            for p in range(n_periods):
                solver.addVariable(meet[p], 0, 1)
                for h in range(n_boats):
                    solver.addConstraint([(1, meet[p]), (-1, at[p][c1][h]), (-1, at[p][c2][h])],
                                         True, -1)
            solver.addConstraint([(1, name) for name in meet], False, 0, True, 1)

    # Minimise the number of host boats.
    objective = [(1, name) for name in is_host]
    solver.setObjective(objective, minimize=True)

    return solver, {"visits": visits, "is_host": is_host}


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
