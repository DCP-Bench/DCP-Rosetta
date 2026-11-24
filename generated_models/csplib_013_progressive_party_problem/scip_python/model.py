# csplib_013_progressive_party_problem: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_013_progressive_party_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_013_progressive_party_problem.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_013_progressive_party_problem.py csplib_013_progressive_party_problem.json

from itertools import combinations

import numpy as np
from pyscipopt import Model, quicksum


def create_model(instance):
    """The progressive party problem: a yacht club holds a party over several
    half-hour periods. Some boats are chosen as hosts, and their crews stay
    aboard for the whole party. The crews of the other boats (guests) move
    between the host boats, visiting one host in each period. The people aboard
    a boat (its host crew, if it is a host, and the guest crews visiting it) must
    not exceed its capacity. A guest crew visits each host at most once, and two
    guest crews meet at most once. The rally organizer wants as few host boats as
    possible.

    Returns (model, outputs). outputs["is_host"][b] is 1 when boat b is a host.
    outputs["visits"][p][b] is the boat that boat b is aboard in period p, which
    is its own index when b is a host.
    """
    n_boats = instance["n_boats"]  # the number of boats, numbered 0 to n_boats - 1
    n_periods = instance["n_periods"]  # the number of half-hour periods of the party
    capacity = np.array(instance["capacity"])  # capacity[b]: the most people boat b can hold at a time
    crew = np.array(instance["crew_size"])  # crew[b]: the number of people in boat b's crew
    boats = range(n_boats)
    periods = range(n_periods)

    model = Model("csplib_013_progressive_party_problem")

    # is_host[b] is 1 when boat b is a host (its crew stays aboard for the whole party), 0 when it is a guest
    is_host = model.addMatrixVar((n_boats,), vtype="B", name="is_host")
    # visit[p, g, h] is 1 when boat g's crew is aboard boat h in period p. A boat's
    # crew is aboard exactly one boat in each period, so a choice of boat is one-hot
    # over the n_boats boats, and visits is the index that the one-hot selects.
    visit = model.addMatrixVar((n_periods, n_boats, n_boats), vtype="B", name="visit")

    # Every crew is aboard exactly one boat in every period.
    model.addMatrixCons(visit.sum(axis=2) == 1)
    # Crews go aboard only host boats: visit[p, g, h] <= is_host[h]. (On the diagonal this
    # overlaps with the next constraint, which fixes visit[p, b, b] to is_host[b].)
    model.addMatrixCons(visit <= is_host)
    # A host crew stays aboard its own boat, and a guest crew is not: visit[p, b, b] == is_host[b].
    model.addMatrixCons(np.diagonal(visit, axis1=1, axis2=2) == is_host)

    # The people aboard boat h in a period are the guest crews visiting it, plus its own
    # crew when it is a host (visit[p, h, h] is 1 then). They must not exceed capacity[h].
    model.addMatrixCons(crew @ visit <= capacity)

    # A guest crew visits each host at most once over the whole party. The diagonal
    # is left out (its bound is n_periods), because a host's crew is aboard its own boat
    # in every period.
    visits_allowed = np.where(np.eye(n_boats, dtype=bool), n_periods, 1)
    model.addMatrixCons(visit.sum(axis=0) <= visits_allowed)

    # Two guest crews meet at most once. They meet when both are aboard the same
    # boat h in the same period p. Boat h is skipped when it is one of the two
    # crews' own boats: a host crew is aboard its own boat in every period, which
    # is not a meeting of guests. So the sum counts only meetings of guest crews.
    # meet is 1 exactly when both crews are aboard boat h in period p.
    for g1, g2 in combinations(boats, 2):
        meetings = []
        for p in periods:
            for h in boats:
                if h not in (g1, g2):
                    meet = model.addVar(vtype="B", name=f"meet_{g1}_{g2}_{p}_{h}")
                    model.addConsAnd([visit[p, g1, h], visit[p, g2, h]], meet)
                    meetings.append(meet)
        model.addCons(quicksum(meetings) <= 1)

    # Minimise the number of host boats.
    model.setObjective(is_host.sum(), "minimize")

    # visits[p][b] is the sum of index h times visit[p, b, h], which is h for the one boat chosen.
    visits = [[quicksum(h * visit[p, b, h] for h in boats) for b in boats] for p in periods]
    outputs = {"is_host": is_host, "visits": visits}
    return model, outputs


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
