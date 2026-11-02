# csplib_013_progressive_party_problem: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_013_progressive_party_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_013_progressive_party_problem.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_013_progressive_party_problem.py csplib_013_progressive_party_problem.json

import z3


def create_model(instance):
    """Timetable a party at a yacht club: some boats are hosts, and the crews of the other
    boats visit host boats in successive periods, without exceeding any boat's capacity,
    revisiting a host or meeting another crew twice. Use as few host boats as possible."""
    n_boats = instance["n_boats"]      # the number of boats
    n_periods = instance["n_periods"]  # the number of half-hour periods
    capacity = instance["capacity"]    # capacity[b]: the most people boat b can hold
    crew_size = instance["crew_size"]  # crew_size[b]: the number of people in the crew of boat b

    boats = range(n_boats)
    periods = range(n_periods)

    # is_host[b] is true when boat b is a host boat
    is_host = [z3.Bool(f"is_host_{b}") for b in boats]
    # visits[p][b] is the boat that the crew of boat b is on in period p (b itself for a host)
    visits = [[z3.Int(f"visits_{p}_{b}") for b in boats] for p in periods]
    # aboard[p][b][h] is true when crew b is aboard boat h in period p
    aboard = [[[z3.Bool(f"aboard_{p}_{b}_{h}") for h in boats] for b in boats] for p in periods]

    solver = z3.Optimize()

    # Every crew is aboard a boat of the fleet in every period.
    solver.add([visits[p][b] >= 0 for p in periods for b in boats])
    solver.add([visits[p][b] <= n_boats - 1 for p in periods for b in boats])

    # aboard agrees with visits.
    solver.add([aboard[p][b][h] == (visits[p][b] == h)
                for p in periods for b in boats for h in boats])

    # The crew of a host boat stays on its own boat in every period.
    solver.add([z3.Implies(is_host[b], aboard[p][b][b]) for b in boats for p in periods])

    # The people aboard a boat in a period, the host crew included, do not exceed its capacity.
    solver.add([z3.PbLe([(aboard[p][b][h], crew_size[b]) for b in boats], capacity[h])
                for p in periods for h in boats])

    # A guest crew never visits the same host twice.
    solver.add([z3.Implies(z3.Not(is_host[b]),
                           z3.AtMost(*[aboard[p][b][h] for p in periods], 1))
                for b in boats for h in boats])

    # Only host boats are visited: a boat that is not a host has nobody aboard.
    solver.add([z3.Implies(z3.Not(is_host[h]), z3.Not(aboard[p][b][h]))
                for h in boats for p in periods for b in boats])

    # Two crews meet at most once: they are on the same boat in at most one period.
    solver.add([z3.AtMost(*[z3.And(aboard[p][c1][h], aboard[p][c2][h])
                            for p in periods for h in boats], 1)
                for c1 in boats for c2 in range(c1 + 1, n_boats)])

    # In every period the guest crews are aboard the hosts, so their people fit in the
    # room that the host crews leave on the hosts.
    room_on_hosts = z3.Sum([z3.If(is_host[h], capacity[h] - crew_size[h], 0) for h in boats])
    guest_people = z3.Sum([z3.If(is_host[b], 0, crew_size[b]) for b in boats])
    solver.add(room_on_hosts >= guest_people)

    # A guest crew visits a different host in each period, so if any boat is a guest,
    # there are at least n_periods hosts.
    n_hosts = z3.Sum([z3.If(h, 1, 0) for h in is_host])
    solver.add(z3.Implies(z3.Or([z3.Not(h) for h in is_host]), n_hosts >= n_periods))

    # Use as few host boats as possible.
    solver.minimize(n_hosts)

    return solver, {"is_host": is_host, "visits": visits}


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
